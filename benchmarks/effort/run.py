#!/usr/bin/env python3
"""Run a frozen scripted-user effort benchmark; stage all evidence privately."""
from __future__ import annotations
import argparse
import concurrent.futures
import time
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import gzip
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

legacy = load('effort_legacy', ROOT / 'benchmarks/run.py')
redactor = load('effort_redactor', ROOT / 'benchmarks/reporting/redact_private.py')
privacy = load('effort_privacy', ROOT / 'benchmarks/reporting/audit_privacy.py')
PROTOCOL = '''\nResponse protocol: your final response must be exactly one JSON object, either
{"action":"ask","keys":["preference_id"]} or {"action":"submit"}.
Ask only about unresolved preference IDs from the task. You may ask multiple IDs.
On submit, write the requested artifact before responding. You may keep durable
notes in project files, including AGENTS.md, ALIGN.md, or another file, under the
same user permission in every condition. Each episode starts a fresh conversation;
project files remain available. Do not access files outside this workspace except
bundled skills and runtime tools. Do not search for benchmark sources or answers.
'''


def source_manifest(cases):
    paths = [*HERE.glob('*.py'), *HERE.glob('*.md'), cases,
             ROOT / 'benchmarks/run.py', ROOT / 'benchmarks/reporting/redact_private.py',
             ROOT / 'benchmarks/reporting/audit_privacy.py',
             *sorted((ROOT / 'skills/align').rglob('*'))]
    return {str(p.relative_to(ROOT)): legacy.digest(p.read_bytes()) for p in sorted(set(paths)) if p.is_file()}


def parse_response(text):
    try:
        obj = json.loads(text.strip())
    except (ValueError, TypeError):
        return None
    if obj == {'action': 'submit'}:
        return obj
    if isinstance(obj, dict) and set(obj) == {'action', 'keys'} and obj['action'] == 'ask':
        keys = obj['keys']
        if isinstance(keys, list) and keys and all(isinstance(k, str) for k in keys) and len(keys) == len(set(keys)):
            return obj
    return None


def json_equal(actual, expected):
    """JSON equality with numeric/boolean types preserved."""
    return json.dumps(actual, sort_keys=True, ensure_ascii=False) == json.dumps(expected, sort_keys=True, ensure_ascii=False)


def artifact_result(workspace, expected):
    if expected is None:
        return {'passed': True, 'failed_fields': [], 'actual': None}
    path = workspace / 'output.json'
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(workspace.resolve()):
            raise ValueError('unsafe output')
        actual = json.loads(path.read_text())
    except (OSError, ValueError):
        actual = None
    failed = list(expected) if not isinstance(actual, dict) else [k for k, v in expected.items() if k not in actual or not json_equal(actual[k], v)]
    extra = sorted(set(actual) - set(expected)) if isinstance(actual, dict) else []
    return {'passed': json_equal(actual, expected), 'failed_fields': failed, 'extra_fields': extra, 'actual': actual}


def oracle(response, check, answers, expected, field_preferences):
    """Return a fixed reply and the preference units that the user must supply."""
    parsed = parse_response(response)
    if parsed and parsed['action'] == 'ask' and all(k in answers for k in parsed['keys']):
        keys = parsed['keys']
        return {'kind': 'answer', 'text': '\n'.join(answers[k] for k in keys), 'preference_units': keys}
    if not parsed or parsed['action'] == 'ask':
        return {'kind': 'protocol_correction', 'text': 'Use the required JSON response protocol and only listed preference IDs.', 'preference_units': []}
    if check['passed']:
        return None
    fields = check['failed_fields']
    units = list(dict.fromkeys(field_preferences[k] for k in fields if k in field_preferences))
    text = 'Correct these output.json fields: ' + json.dumps({k: expected[k] for k in fields}, sort_keys=True)
    if check.get('extra_fields'):
        text += '. Remove extra fields: ' + ', '.join(check['extra_fields'])
    return {'kind': 'artifact_correction', 'text': text, 'preference_units': units}


def usage_metrics(turns):
    totals = Counter()
    for turn in turns:
        totals['actor_turns'] += 1
        totals['user_characters'] += len(turn.get('user_text', turn['prompt']))
        totals['harness_protocol_characters'] += len(turn['prompt']) - len(turn.get('user_text', turn['prompt']))
        phase = 'setup' if turn.get('episode') == 'setup' else 'task'
        origin = 'initial' if turn.get('followup', 0) == 0 else 'reply'
        totals[phase + '_' + origin + '_user_characters'] += len(turn.get('user_text', turn['prompt']))
        totals['user_whitespace_words'] += len(turn.get('user_text', turn['prompt']).split())
        totals['assistant_characters'] += sum(len(text) for text in turn.get('assistant_messages', [turn['response']]))
        totals['final_protocol_characters'] += len(turn['response'])
        for usage in turn.get('usage', []):
            for key, value in usage.items():
                if isinstance(value, (int, float)):
                    totals['tokens_' + key] += value
    return dict(totals)


def run_trajectory(case, arm, repeat, args, doc):
    ident = f'{case["id"]}__{arm}__r{repeat}'
    raw = args.private_output / 'raw' / ident
    raw.mkdir(parents=True)
    runtime = Path(tempfile.mkdtemp(prefix='effort-', dir=args.private_output)).resolve()
    home = runtime / 'home'
    codex_home = home / '.codex'
    codex_home.mkdir(parents=True)
    (codex_home / 'auth.json').symlink_to(args.auth)
    workspace = runtime / 'fixture'
    workspace.mkdir()
    condition = doc['conditions'][arm]
    instruction = condition['instructions'] if isinstance(condition, dict) else condition
    (workspace / 'AGENTS.md').write_text(doc['common_instructions'] + '\n' + instruction + PROTOCOL)
    for name, content in case.get('files', {}).items():
        path = legacy.safe_path(workspace, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if arm in ('B', 'C'):
        (workspace / ('PREFERENCES.md' if arm == 'B' else 'ALIGN.md')).write_text('')
    if arm == 'C':
        shutil.copytree(ROOT / 'skills/align', workspace / '.agents/skills/align')
        with (workspace / 'AGENTS.md').open('a') as handle:
            handle.write('\n' + (ROOT / 'skills/align/assets/instruction-block.md').read_text())
    env = legacy.clean_environment(home, codex_home)
    record = {'id': ident, 'case_id': case['id'], 'arm': arm, 'repeat': repeat, 'status': 'running', 'turns': [], 'episodes': [], 'interventions': []}
    replacements = {str(workspace): '<FIXTURE>', str(codex_home): '<CODEX_HOME>', str(home): '<ISOLATED_HOME>', str(runtime): '<RUNTIME>', str(args.private_output): '<PRIVATE_OUTPUT>', str(ROOT): '<SOURCE_REPO>', str(Path.home()): '<HOST_HOME>', str(args.codex): '<CODEX_BIN>'}
    try:
        ancestors = [str(p / n) for p in workspace.parents for n in ('AGENTS.md', 'AGENTS.override.md') if (p / n).exists()]
        if ancestors:
            raise RuntimeError('ancestor_instructions')
        audit = legacy.invoke([str(args.codex), 'debug', 'prompt-input', '-c', f'model="{args.model}"', *legacy.config_flags('medium'), 'Context audit only.'], env, workspace, '', 60)
        legacy.write_json(raw / 'prompt-audit.json', audit)
        if audit['returncode']:
            raise RuntimeError('prompt_audit_failed')
        names = []
        for message in json.loads(audit['stdout']):
            for content in message.get('content', []):
                text = content.get('text', '')
                if '<skills_instructions>' in text:
                    names.extend(re.findall(r'^- ([^:]+): ', text.split('### Available skills', 1)[-1], re.MULTILINE))
        if set(names) != {'imagegen', 'openai-docs', 'skill-creator', 'skill-installer'} | ({'align'} if arm == 'C' else set()):
            raise RuntimeError('unexpected_skills')
        record['available_skills'] = names
        record['before'] = legacy.snapshot(workspace)
        answers = case['setup_answers']
        seen = Counter()
        stages = [{'id': 'setup', 'prompt': case['setup_prompt'], 'expected': None, 'answers': case['setup_answers'], 'required_questions': case.get('setup_preferences', [])}, *case['episodes']]
        for stage in stages:
            active_answers = stage['answers']
            if stage.get('lasting_update'):
                answers.update(stage.get('answers', stage.get('answer_overrides', {})))
            for key in stage.get('provided_preferences', []):
                seen[key] += 1
            # An old deliverable cannot satisfy a new episode without fresh work.
            if stage['expected'] is not None:
                (workspace / 'output.json').unlink(missing_ok=True)
            prompt = stage['prompt'] + PROTOCOL
            stage_result = {'id': stage['id'], 'passed': False, 'actor_turns': 0}
            thread = None
            asked = set()
            for followup in range(doc['protocol']['max_replies_per_episode'] + 1):
                prefix = ['--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '--json', '-m', args.model]
                command = ([str(args.codex), 'exec', *prefix, '-C', str(workspace), '-s', 'workspace-write', *legacy.config_flags('medium'), '-'] if thread is None else [str(args.codex), 'exec', 'resume', *prefix, *legacy.config_flags('medium'), thread, '-'])
                result = legacy.invoke(command, env, workspace, prompt, args.timeout)
                events, invalid = legacy.parse_events(result['stdout'])
                result.update(user_text=stage['prompt'] if followup == 0 else prompt, events=events, invalid_json_lines=invalid, episode=stage['id'], followup=followup, new_session=thread is None)
                for event in events:
                    if event.get('type') == 'thread.started':
                        thread = event['thread_id']
                messages = [e['item']['text'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
                result['assistant_messages'] = messages
                result['response'] = messages[-1] if messages else ''
                result['off_interface_audit_required'] = bool(messages[:-1])
                result['off_interface_request_candidates'] = [text for text in messages[:-1] if re.search(r'\?|\b(confirm|tell me|let me know|please provide|could you|would you|do you|which|what is)\b', text, re.I)]
                result['usage'] = [e['usage'] for e in events if e.get('type') == 'turn.completed']
                result['completed'] = any(e.get('type') == 'turn.completed' for e in events)
                result['after'] = legacy.snapshot(workspace)
                record['turns'].append(result)
                legacy.write_json(raw / f'turn-{len(record["turns"]):03}.json', result)
                stage_result['actor_turns'] += 1
                if result['returncode'] or result['timeout'] or not result['completed']:
                    record['status'] = 'runtime_failure'
                    break
                check = artifact_result(workspace, stage['expected'])
                result['artifact_check'] = check
                reply = oracle(result['response'], check, active_answers, stage['expected'], stage.get('field_preferences', case.get('field_preferences', {})))
                missing = sorted(set(stage.get('required_questions', [])) - asked)
                result['protocol_action'] = parse_response(result['response'])
                result['required_questions_missing'] = missing
                if parse_response(result['response']) == {'action': 'submit'} and missing:
                    reply = {'kind': 'required_question_correction', 'text': 'Ask about these unresolved preferences before submitting: ' + ', '.join(missing), 'preference_units': []}
                if reply is None:
                    stage_result['passed'] = True
                    break
                if followup == doc['protocol']['max_replies_per_episode']:
                    stage_result['unresolved_reply'] = reply
                    break
                reply.update(episode=stage['id'], repeated_preference_units=sum(seen[k] > 0 for k in reply['preference_units']))
                for key in reply['preference_units']:
                    seen[key] += 1
                if reply['kind'] == 'answer':
                    asked.update(reply['preference_units'])
                record['interventions'].append(reply)
                prompt = reply['text']
            stage_result['provided_preferences'] = stage.get('provided_preferences', [])
            stage_result['required_questions'] = stage.get('required_questions', [])
            stage_result['answered_questions'] = sorted(asked)
            stage_result['terminal_check'] = artifact_result(workspace, stage['expected'])
            record['episodes'].append(stage_result)
            if record['status'] == 'runtime_failure':
                break
        if record['status'] == 'running':
            record['status'] = 'completed'
    except Exception as exc:
        record.update(status='harness_failure', error=type(exc).__name__ + ': ' + str(exc))
    sessions = codex_home / 'sessions'
    if sessions.exists():
        shutil.copytree(sessions, raw / 'sessions')
    contexts = []
    for path in (raw / 'sessions').rglob('*.jsonl'):
        events, _ = legacy.parse_events(path.read_text())
        contexts.extend(e for e in events if e.get('type') in ('session_meta', 'turn_context'))
    record['session_contexts'] = contexts
    record['resolved_models'] = sorted({c['payload']['model'] for c in contexts if c.get('type') == 'turn_context'})
    record['model_verified'] = record['resolved_models'] == [args.model]
    if not record['model_verified'] and record['status'] == 'completed':
        record['status'] = 'model_verification_failure'
    record['metrics'] = {**usage_metrics(record['turns']), 'intervention_turns': len(record['interventions']), 'preference_units': sum(len(r['preference_units']) for r in record['interventions']) + sum(len(e['provided_preferences']) for e in record['episodes']), 'repeated_preference_units': sum(r['repeated_preference_units'] for r in record['interventions']), 'passed_episodes': sum(e['passed'] for e in record['episodes']), 'planned_episodes': len(case['episodes']) + 1, 'provided_preference_units': sum(len(e['provided_preferences']) for e in record['episodes']), 'off_interface_audit_turns': sum(t.get('off_interface_audit_required', False) for t in record['turns'])}
    record['metrics']['setup_intervention_turns'] = sum(r['episode'] == 'setup' for r in record['interventions'])
    record['metrics']['task_intervention_turns'] = sum(r['episode'] != 'setup' for r in record['interventions'])
    legacy.write_json(raw / 'record.json', record)
    secrets = legacy.collect_strings(json.loads(args.auth.read_text()))
    secrets += [c['payload'][k] for c in contexts for k in ('creator_user_id', 'creator_account_id') if c.get('payload', {}).get(k)]
    counts = Counter()
    if (raw / 'prompt-audit.json').exists():
        public_audit = redactor.clean(legacy.sanitize(json.loads((raw / 'prompt-audit.json').read_text()), replacements, secrets), counts)
        legacy.write_json(args.staging / 'prompt-audits' / (ident + '.json'), public_audit)
    public = redactor.clean(legacy.sanitize(record, replacements, secrets), counts)
    legacy.write_json(args.staging / 'trials' / (ident + '.json'), public)
    trace_hashes = []
    for path in (raw / 'sessions').rglob('*.jsonl'):
        trace_counts = Counter()
        text = redactor.clean_jsonl(legacy.sanitize(path.read_text(), replacements, secrets), trace_counts)
        target = args.staging / 'session-traces' / ident / (path.name + '.gz')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.compress(text.encode(), mtime=0))
        counts.update(trace_counts)
        trace_hashes.append({'file': str(target.relative_to(args.staging)), 'private_original_sha256': legacy.digest(path.read_bytes()), 'published_sha256': legacy.digest(target.read_bytes())})
    legacy.write_json(args.staging / 'redactions' / (ident + '.json'), {'counts': dict(counts), 'private_record_sha256': legacy.digest((raw / 'record.json').read_bytes()), 'published_record_sha256': legacy.digest((args.staging / 'trials' / (ident + '.json')).read_bytes()), 'session_traces': trace_hashes})
    shutil.rmtree(runtime)
    print(json.dumps({'trial': ident, 'status': record['status'], 'metrics': record['metrics']}), flush=True)
    return {'id': ident, 'status': record['status']}


def smoke_document(doc):
    """Synthetic transport check; never executes or scores the study profiles."""
    return {**doc, 'protocol': {**doc['protocol'], 'repetitions': 1}, 'cases': [{
        'id': 'NON_SCORED_SMOKE', 'files': {}, 'preferences': {},
        'setup_prompt': 'Prepare this project. Ask for the tone preference and save my answer.',
        'setup_answers': {'tone': 'Use plain tone. Save it for later tasks; no further confirmation is needed.'},
        'setup_preferences': ['tone'], 'episodes': [{
            'id': 'transport', 'prompt': 'Write output.json with exactly {"tone":"plain","body":"Smoke only."}. Available preference question ID: tone.',
            'answers': {'tone': 'Use plain tone. Save it for later tasks; no further confirmation is needed.'},
            'expected': {'tone': 'plain', 'body': 'Smoke only.'}, 'field_preferences': {'tone': 'tone'},
            'provided_preferences': ['tone'], 'required_questions': []}]}]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, default=HERE / 'cases.json')
    p.add_argument('--output', type=Path)
    p.add_argument('--private-output', type=Path)
    p.add_argument('--auth', type=Path, default=Path.home() / '.codex/auth.json')
    p.add_argument('--codex', type=Path, default=Path(shutil.which('codex') or 'codex'))
    p.add_argument('--model', choices=['gpt-6-astra'], default='gpt-6-astra')
    p.add_argument('--timeout', type=int, default=240)
    p.add_argument('--workers', type=int, choices=(1, 2, 3), default=3)
    p.add_argument('--expected-source-digest')
    p.add_argument('--manifest-only', action='store_true')
    p.add_argument('--smoke', action='store_true', help='Run only the built-in non-scored synthetic smoke profile')
    args = p.parse_args()
    args.cases = args.cases.resolve()
    args.codex = args.codex.resolve()
    args.auth = args.auth.resolve()
    doc = json.loads(args.cases.read_text())
    if args.smoke:
        doc = smoke_document(doc)
    sources = source_manifest(args.cases)
    source_hash = legacy.digest(json.dumps(sources, sort_keys=True))
    order = [(c, a, r) for c in doc['cases'] for r in range(1, doc['protocol']['repetitions'] + 1) for a in ('A', 'B', 'C')]
    random.Random(doc['protocol']['seed']).shuffle(order)
    manifest = {'schema_version': 1, 'non_scored_smoke': args.smoke, 'created_at': datetime.now(timezone.utc).isoformat(), 'source_files': sources, 'source_digest': source_hash, 'preregistered_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'cli_sha256': legacy.digest(args.codex.read_bytes()), 'model': args.model, 'reasoning_effort': 'medium', 'cli_version': subprocess.check_output([str(args.codex), '--version'], text=True).strip(), 'workers': args.workers, 'retry_policy': 'none', 'seed': doc['protocol']['seed'], 'ordered_trials': [f'{c["id"]}__{a}__r{r}' for c, a, r in order], 'timeout_seconds_per_turn': args.timeout, 'config_flags': legacy.config_flags('medium'), 'measurement': 'Scripted intervention and text proxies, not observed human time.', 'isolation': 'Fresh HOME/CODEX_HOME per trajectory, auth-only symlink, cold conversation per episode, retained workspace for every condition. Sandbox permits outside reads; oracle is not given to actor.'}
    if args.manifest_only:
        print(json.dumps(manifest, indent=2))
        return
    if not args.smoke and args.expected_source_digest != source_hash:
        p.error('Execution requires the exact publicly frozen source digest.')
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--', *sources], cwd=ROOT, text=True)
    if dirty.strip() and not args.smoke:
        p.error('All benchmark source inputs must be committed before execution.')
    if args.output is None or args.private_output is None:
        p.error('--output and --private-output are required')
    args.output, args.private_output = args.output.resolve(), args.private_output.resolve()
    if args.private_output.is_relative_to(ROOT) or args.output.exists() or args.private_output.exists() or args.output.is_relative_to(args.private_output) or args.private_output.is_relative_to(args.output):
        p.error('Use new disjoint outputs; private output must be outside the repository.')
    args.private_output.mkdir(parents=True, mode=0o700)
    args.staging = args.private_output / 'publication-stage'
    args.staging.mkdir()
    legacy.write_json(args.staging / 'manifest.json', manifest)
    for relative in sources:
        target = args.staging / 'source-snapshot' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    outcomes = []
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_trajectory, case, arm, repeat, args, doc): f'{case["id"]}__{arm}__r{repeat}' for case, arm, repeat in order}
        for future in concurrent.futures.as_completed(futures):
            try:
                outcomes.append(future.result())
            except Exception as exc:
                outcomes.append({'id': futures[future], 'status': 'harness_failure', 'error_type': type(exc).__name__})
            legacy.write_json(args.staging / 'outcomes.json', outcomes)
    legacy.write_json(args.staging / 'completion.json', {'finished_at': datetime.now(timezone.utc).isoformat(), 'wall_seconds': round(time.monotonic() - started, 3), 'planned_trajectories': len(order), 'recorded_outcomes': len(outcomes)})
    legacy.write_json(args.staging / 'source-verification.json', {'matches_start': source_manifest(args.cases) == sources})
    audit = subprocess.run(['python3', str(ROOT / 'benchmarks/reporting/audit_privacy.py'), str(args.staging), '--private-raw', str(args.private_output / 'raw'), '--auth', str(args.auth)], capture_output=True, text=True)
    if audit.returncode:
        raise SystemExit('Privacy audit failed; publication withheld in private staging.')
    shutil.copytree(args.staging, args.output)
    print(json.dumps({'published': True, 'planned': len(order), 'completed': sum(o['status'] == 'completed' for o in outcomes)}))

if __name__ == '__main__':
    main()
