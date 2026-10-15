#!/usr/bin/env python3
"""Offline evidence replay for scripted intervention proxies, not human effort."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import sys
import tempfile
import run


def replay(row, case, doc, frozen):
    """Rebuild decisions and costs from prompts, events and artifact snapshots."""
    errors, episodes, replies, turns, pending = [], [], [], [], []
    def require(ok, message):
        if not ok:
            errors.append(row['id'] + ': ' + message)
    stages = [{'id': 'setup', 'prompt': case['setup_prompt'], 'answers': case['setup_answers'],
               'expected': None, 'required_questions': case.get('setup_preferences', [])}, *case['episodes']]
    seen, cursor, sessions = set(), 0, set()
    runtime_failure = False
    for stage in stages:
        if cursor >= len(row['turns']):
            break
        asked, passed, first_submission = set(), False, None
        provided = list(dict.fromkeys(stage.get('provided_preferences', [])))
        seen.update(provided)
        prompt = stage['prompt'] + frozen.PROTOCOL
        start, reply_start = cursor, len(replies)
        thread = None
        check = None
        unresolved = None
        for followup in range(doc['protocol']['max_replies_per_episode'] + 1):
            require(cursor < len(row['turns']), 'missing follow-up in ' + stage['id'])
            if cursor >= len(row['turns']):
                break
            turn = row['turns'][cursor]
            cursor += 1
            require(turn['episode'] == stage['id'] and turn['followup'] == followup, 'turn order')
            require(turn['prompt'] == prompt, 'prompt/fixed reply mismatch')
            user_text = stage['prompt'] if followup == 0 else prompt
            require(turn.get('user_text') == user_text, 'user text mismatch')
            events, invalid = frozen.legacy.parse_events(turn['stdout'])
            require(events == turn['events'] and invalid == turn.get('invalid_json_lines', []), 'event stream mismatch')
            messages = [e['item']['text'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
            response = messages[-1] if messages else ''
            usage = [e['usage'] for e in events if e.get('type') == 'turn.completed']
            completed = any(e.get('type') == 'turn.completed' for e in events)
            require(response == turn['response'] and messages == turn.get('assistant_messages'), 'visible response mismatch')
            require(usage == turn.get('usage') and completed == turn.get('completed'), 'completion/usage mismatch')
            require(turn.get('new_session') == (followup == 0), 'cold session flag')
            ids = [e['thread_id'] for e in events if e.get('type') == 'thread.started']
            if followup == 0:
                require(len(ids) == 1 and ids[0] not in sessions, 'missing/reused episode session')
                thread = ids[0] if ids else None
                sessions.add(thread)
            else:
                require(not ids or ids == [thread], 'follow-up changed session')
            command = turn.get('command', [])
            require(('resume' in command) == (followup > 0), 'resume boundary')
            if followup:
                require(thread in command, 'resume thread mismatch')
            require(isinstance(turn.get('duration_seconds'), (int, float)) and turn['duration_seconds'] >= 0, 'invalid duration')
            if messages[:-1]:
                pending.append({'trial': row['id'], 'turn': cursor, 'messages': messages[:-1]})
            rebuilt = dict(turn, response=response, assistant_messages=messages, usage=usage, user_text=user_text)
            turns.append(rebuilt)
            with tempfile.TemporaryDirectory() as temp:
                workspace = Path(temp)
                output = turn.get('after', {}).get('output.json')
                if output:
                    text = output.get('text')
                    require(isinstance(text, str), 'output snapshot lacks text')
                    if isinstance(text, str):
                        require(frozen.legacy.digest(text) == output.get('sha256') and len(text.encode()) == output.get('bytes'), 'output snapshot hash')
                        (workspace / 'output.json').write_text(text)
                check = frozen.artifact_result(workspace, stage['expected'])
            if turn['returncode'] or turn['timeout'] or not completed:
                runtime_failure = True
                break
            require(turn.get('artifact_check') == check, 'artifact check differs from snapshot')
            parsed = frozen.parse_response(response)
            reply = frozen.oracle(response, check, stage['answers'], stage['expected'], stage.get('field_preferences', case.get('field_preferences', {})))
            missing = sorted(set(stage.get('required_questions', [])) - asked)
            if parsed == {'action': 'submit'}:
                if first_submission is None:
                    first_submission = check['passed'] and not missing
                if missing:
                    reply = {'kind': 'required_question_correction', 'text': 'Ask about these unresolved preferences before submitting: ' + ', '.join(missing), 'preference_units': []}
            if reply is None:
                passed = True
                break
            if followup == doc['protocol']['max_replies_per_episode']:
                unresolved = reply
                break
            reply.update(episode=stage['id'], repeated_preference_units=sum(k in seen for k in reply['preference_units']))
            seen.update(reply['preference_units'])
            if reply['kind'] == 'answer':
                asked.update(reply['preference_units'])
            replies.append(reply)
            prompt = reply['text']
        episode = {'id': stage['id'], 'passed': passed, 'actor_turns': cursor - start,
                   'provided_preferences': provided, 'required_questions': stage.get('required_questions', []),
                   'answered_questions': sorted(asked), 'terminal_check': check}
        if unresolved is not None:
            episode['unresolved_reply'] = unresolved
        episodes.append(episode)
        # Keep diagnostics separate from the runner's stored episode schema.
        episode['_derived'] = {'first_submission_passed': first_submission,
            'intervention_turns': len(replies) - reply_start,
            'preference_units': len(provided) + sum(len(r['preference_units']) for r in replies[reply_start:]),
            'repeated_preference_units': sum(r['repeated_preference_units'] for r in replies[reply_start:])}
        if runtime_failure:
            break
    require(cursor == len(row['turns']), 'unexpected extra turns')
    require(replies == row['interventions'], 'intervention ledger mismatch')
    require(len(episodes) == len(row['episodes']), 'episode ledger length')
    for derived, recorded in zip(episodes, row['episodes']):
        require(all(recorded.get(k) == v for k, v in derived.items() if k != '_derived'), 'episode outcome mismatch: ' + derived['id'])
    if row['status'] in ('completed', 'model_verification_failure'):
        require(len(episodes) == len(stages) and not runtime_failure, 'completed trajectory missing tasks')
    require((row['status'] == 'runtime_failure') == runtime_failure, 'runtime status mismatch')
    contexts = row.get('session_contexts', [])
    models = sorted({c['payload']['model'] for c in contexts if c.get('type') == 'turn_context'})
    require(models == row.get('resolved_models'), 'model context mismatch')
    metrics = frozen.usage_metrics(turns)
    metrics.update(intervention_turns=len(replies), preference_units=sum(len(r['preference_units']) for r in replies) + sum(len(e['provided_preferences']) for e in episodes), repeated_preference_units=sum(r['repeated_preference_units'] for r in replies), passed_episodes=sum(e['passed'] for e in episodes), planned_episodes=len(stages), provided_preference_units=sum(len(e['provided_preferences']) for e in episodes), off_interface_audit_turns=len(pending), setup_intervention_turns=sum(r['episode'] == 'setup' for r in replies), task_intervention_turns=sum(r['episode'] != 'setup' for r in replies))
    require(all(row['metrics'].get(k) == v for k, v in metrics.items()), 'metric mismatch')
    for key in ('actor_turns', 'user_characters', 'assistant_characters'):
        metrics.setdefault(key, 0)
    for phase in ('setup', 'task'):
        phase_episodes = [e for e in episodes if (e['id'] == 'setup') == (phase == 'setup')]
        metrics[phase + '_preference_units'] = sum(e['_derived']['preference_units'] for e in phase_episodes)
        metrics[phase + '_repeated_preference_units'] = sum(e['_derived']['repeated_preference_units'] for e in phase_episodes)
    metrics['repeated_question_units'] = sum(r['repeated_preference_units'] for r in replies if r['kind'] == 'answer')
    metrics['new_question_units'] = sum(len(r['preference_units']) - r['repeated_preference_units'] for r in replies if r['kind'] == 'answer')
    metrics['failed_or_missing_episodes'] = len(stages) - sum(e['passed'] for e in episodes)
    metrics.update(duration_seconds=sum(t['duration_seconds'] for t in turns), usage_missing_turns=sum(not t['usage'] for t in turns), correction_rounds=sum(r['kind'] != 'answer' for r in replies), protocol_errors=sum(r['kind'] == 'protocol_correction' for r in replies))
    cumulative, costs = [], Counter()
    for episode in episodes:
        costs.update({k: v for k, v in episode['_derived'].items() if k != 'first_submission_passed'})
        cumulative.append({'episode': episode['id'], **dict(costs), 'passed': episode['passed']})
    return {'id': row['id'], 'arm': row['arm'], 'case_id': row['case_id'], 'repeat': row['repeat'], 'status': row['status'], 'metrics': metrics, 'episodes': episodes, 'cumulative': cumulative, 'models': models}, errors, pending


def verify(root):
    root = Path(root)
    errors, rows, pending = [], [], []
    def read(path):
        return json.loads((root / path).read_text())
    manifest = read('manifest.json')
    snapshot = root / 'source-snapshot'
    for relative, expected in manifest['source_files'].items():
        path = snapshot / relative
        if not path.is_file() or not path.resolve().is_relative_to(snapshot.resolve()) or run.legacy.digest(path.read_bytes()) != expected:
            errors.append('Frozen source missing or changed: ' + relative)
    archived_files = {str(p.relative_to(snapshot)) for p in snapshot.rglob('*') if p.is_file()}
    if archived_files != set(manifest['source_files']):
        errors.append('Frozen source archive inventory differs from manifest')
    receipt_path = root / 'source-archive-verification.json'
    if manifest.get('privacy_scope') or receipt_path.exists():
        receipt = read('source-archive-verification.json')
        if not receipt.get('matches_manifest') or receipt.get('source_files') != manifest['source_files']:
            errors.append('Source archive receipt mismatch')
    if run.legacy.digest(json.dumps(manifest['source_files'], sort_keys=True)) != manifest['source_digest']:
        errors.append('Source digest mismatch')
    # Do not import altered archived Python. Only the hash-verified frozen helpers run.
    if errors:
        return {'verified': False, 'errors': errors, 'favorable_effort_claim_permitted': False}
    bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        frozen = run.load('frozen_effort_run', snapshot / 'benchmarks/effort/run.py')
    finally:
        sys.dont_write_bytecode = bytecode_setting
    doc = json.loads((snapshot / 'benchmarks/effort/cases.json').read_text())
    if manifest.get('non_scored_smoke'):
        doc = frozen.smoke_document(doc)
    cases = {c['id']: c for c in doc['cases']}
    planned = [f'{c["id"]}__{a}__r{r}' for c in doc['cases'] for r in range(1, doc['protocol']['repetitions'] + 1) for a in ('A', 'B', 'C')]
    random.Random(doc['protocol']['seed']).shuffle(planned)
    if manifest['ordered_trials'] != planned or manifest['seed'] != doc['protocol']['seed']:
        errors.append('Frozen planned schedule mismatch')
    outcomes = read('outcomes.json')
    if sorted(o['id'] for o in outcomes) != sorted(planned):
        errors.append('Outcome matrix incomplete or duplicated')
    if sorted(p.stem for p in (root / 'trials').glob('*.json')) != sorted(planned):
        errors.append('Trial evidence matrix incomplete or duplicated')
    for ident in planned:
        path = root / 'trials' / (ident + '.json')
        if not path.exists():
            continue
        row = json.loads(path.read_text())
        try:
            case_id, arm, repeat = ident.split('__')
            if (row['id'], row['case_id'], row['arm'], row['repeat']) != (ident, case_id, arm, int(repeat[1:])):
                errors.append('Trial identity mismatch: ' + ident)
            outcome = next((o for o in outcomes if o['id'] == ident), {})
            if row['status'] != outcome.get('status'):
                errors.append('Outcome status mismatch: ' + ident)
            if frozen.privacy.private_fields(row):
                errors.append('Private reasoning retained: ' + ident)
            derived, issues, audit = replay(row, cases[case_id], doc, frozen)
            rows.append(derived)
            errors.extend(issues)
            pending.extend(audit)
            if row.get('model_verified') != (derived['models'] == [manifest['model']]):
                errors.append('Model verification flag mismatch: ' + ident)
            traces = list((root / 'session-traces' / ident).glob('*.gz'))
            contexts = []
            for trace in traces:
                text = gzip.decompress(trace.read_bytes()).decode()
                events, invalid = frozen.legacy.parse_events(text)
                if invalid or frozen.privacy.private_fields(events):
                    errors.append('Invalid/private public trace: ' + ident)
                contexts.extend(e for e in events if e.get('type') in ('session_meta', 'turn_context'))
            if contexts != row.get('session_contexts'):
                # File iteration order is not a protocol fact.
                if sorted(map(lambda x: json.dumps(x, sort_keys=True), contexts)) != sorted(map(lambda x: json.dumps(x, sort_keys=True), row.get('session_contexts', []))):
                    errors.append('Public trace contexts mismatch: ' + ident)
            if row['turns'] and not traces:
                errors.append('Missing public session traces: ' + ident)
            redactions = read('redactions/' + ident + '.json')
            if redactions.get('published_record_sha256') != frozen.legacy.digest(path.read_bytes()):
                errors.append('Published record hash mismatch: ' + ident)
            trace_hashes = redactions.get('session_traces', [])
            if sorted(h['file'] for h in trace_hashes) != sorted(str(p.relative_to(root)) for p in traces):
                errors.append('Public trace hash inventory mismatch: ' + ident)
            for h in trace_hashes:
                trace_path = root / h['file']
                if not trace_path.resolve().is_relative_to(root.resolve()) or frozen.legacy.digest(trace_path.read_bytes()) != h['published_sha256']:
                    errors.append('Public trace hash mismatch: ' + ident)
            audit_path = root / 'prompt-audits' / (ident + '.json')
            if row['turns'] and not audit_path.exists():
                errors.append('Missing prompt context audit: ' + ident)
            if audit_path.exists():
                audit = json.loads(audit_path.read_text())
                if audit.get('returncode') or frozen.privacy.private_fields(audit):
                    errors.append('Invalid prompt context audit: ' + ident)
            for turn in row['turns']:
                command = turn.get('command', [])
                if '-m' not in command or command[command.index('-m') + 1] != manifest['model']:
                    errors.append('Command model mismatch: ' + ident)
                if not all(flag in command for flag in manifest['config_flags']):
                    errors.append('Command configuration mismatch: ' + ident)
        except (KeyError, ValueError, TypeError, OSError) as exc:
            errors.append('Malformed evidence ' + ident + ': ' + str(exc))
    if not read('source-verification.json').get('matches_start'):
        errors.append('Source changed during execution')
    privacy = read('privacy-audit.json')
    if not privacy.get('passed') or privacy.get('script_sha256') != manifest['source_files']['benchmarks/reporting/audit_privacy.py']:
        errors.append('Privacy audit failed or wrong source')
    completion = read('completion.json')
    if completion.get('planned_trajectories') != len(planned) or completion.get('recorded_outcomes') != len(outcomes):
        errors.append('Completion matrix mismatch')
    arms = {}
    for arm in ('A', 'B', 'C'):
        group = [r for r in rows if r['arm'] == arm]
        count = len(planned) // 3
        totals = Counter()
        for row in group:
            totals.update(row['metrics'])
        arms[arm] = {'planned_trajectories': count, 'recorded_trajectories': len(group), 'execution_failures': count - sum(r['status'] == 'completed' for r in group), 'totals': dict(totals)}
    quality = len([r for r in rows if r['arm'] == 'C']) == arms['C']['planned_trajectories'] and all(r['status'] == 'completed' and r['models'] == [manifest['model']] and r['metrics']['passed_episodes'] == r['metrics']['planned_episodes'] for r in rows if r['arm'] == 'C')
    comparisons, paired = {}, []
    rule = doc['protocol']['decision_rule']
    for baseline in ('B', 'A'):
        c, x = arms['C']['totals'], arms[baseline]['totals']
        relative = lambda key: (x.get(key, 0) - c.get(key, 0)) / x[key] if x.get(key) else None
        units, replies = relative('preference_units'), relative('intervention_turns')
        delta = (x.get('intervention_turns', 0) - c.get('intervention_turns', 0)) / arms['C']['planned_trajectories']
        thresholds = units is not None and units >= rule['preference_unit_relative_reduction_min'] and replies is not None and replies >= rule['reply_relative_reduction_min'] and delta >= rule['reply_mean_reduction_min'] and (not rule['repeated_preference_units_must_not_increase'] or c.get('repeated_preference_units', 0) <= x.get('repeated_preference_units', 0))
        comparisons['C_vs_' + baseline] = {'relative_preference_unit_reduction': units, 'relative_reply_reduction': replies, 'mean_reply_reduction': delta, 'numeric_thresholds_met': thresholds, 'decision_rule_met_before_manual_audits': thresholds and quality and not errors, 'decision_rule_met': thresholds and quality and not errors and not pending and not manifest.get('non_scored_smoke', False)}
        for case in cases:
            for repeat in range(1, doc['protocol']['repetitions'] + 1):
                pair = {a: next((r for r in rows if r['arm'] == a and r['case_id'] == case and r['repeat'] == repeat), None) for a in ('C', baseline)}
                entry = {'comparison': 'C_vs_' + baseline, 'profile': case, 'repeat': repeat, 'arms': {a: {'status': r['status'], 'metrics': r['metrics'], 'cumulative': r['cumulative']} if r else None for a, r in pair.items()}}
                if all(pair.values()):
                    diff = pair[baseline]['metrics']['preference_units'] - pair['C']['metrics']['preference_units']
                    entry['preference_unit_result'] = 'win' if diff > 0 else 'loss' if diff < 0 else 'tie'
                    entry['first_observed_preference_cost_lead_episode'] = next((c['episode'] for c, b in zip(pair['C']['cumulative'], pair[baseline]['cumulative']) if c['preference_units'] < b['preference_units']), None)
                paired.append(entry)
    return {'verified': not errors, 'errors': errors, 'non_scored_smoke': manifest.get('non_scored_smoke', False), 'arms': arms, 'trajectories': rows, 'paired': paired, 'comparisons': comparisons, 'C_quality_guardrail': quality, 'off_interface_audit_pending': pending, 'favorable_effort_claim_permitted': False, 'scripted_proxy_decision_rule_met': comparisons['C_vs_B']['decision_rule_met'], 'claim_gate': 'Non-final assistant prose requires separate human/model audit; no automatic keyword clearance. External-read and privacy redaction completeness also require review. Hashes establish integrity, not preregistration time or authenticity.', 'interpretation': 'Scripted reply, preference-unit and text proxies only; no measured human effort or population inference.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('publication_root', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.publication_root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'verified': False, 'errors': ['Incomplete or malformed archive: ' + str(exc)], 'favorable_effort_claim_permitted': False}
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
    if not result['verified']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
