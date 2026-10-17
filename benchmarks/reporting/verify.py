#!/usr/bin/env python3
"""Offline evidence verification and descriptive reporting. No inference calls.

This reporting utility was written after the actor protocol freeze. It does
not add criteria or adjudicate semantic judgments. Requires only Python 3.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(path.read_text())


def canonical(value):
    return sha(json.dumps(value, sort_keys=True).encode())


def file_check(rule, before, after):
    kind = rule['type']
    name = rule.get('path')
    if kind == 'manual':
        return None
    if name not in after:
        return False
    if kind == 'file_exists':
        return True
    if kind == 'file_unchanged':
        return name in before and before[name]['sha256'] == after[name]['sha256']
    if kind == 'file_contains':
        return rule['text'] in after[name]['text']
    if kind == 'file_not_contains':
        return rule['text'] not in after[name]['text']
    raise ValueError('Unknown frozen check: ' + kind)


def totals(values, planned):
    observed = [v for v in values if v is not None]
    return {'earned': sum(observed), 'graded': len(observed), 'planned': planned,
            'rate_among_graded': sum(observed) / len(observed) if observed else None,
            'ungraded': planned - len(observed)}


def timing(values):
    return {'count': len(values), 'sum': sum(values),
            'mean': statistics.mean(values) if values else None,
            'median': statistics.median(values) if values else None}


def strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for item in value.values() for s in strings(item)]
    if isinstance(value, list):
        return [s for item in value for s in strings(item)]
    return []


def verify(run, judges=None, packets=None, root=ROOT):
    errors, pending, warnings = [], [], []
    redaction_summaries = {}
    for label, directory in [('actors', run), ('judges', judges)]:
        if directory is None:
            continue
        publication = directory / 'publication-redactions.json'
        if publication.exists():
            redaction = read(publication)
            for row in redaction['files']:
                path = directory / row['file']
                if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file() or sha(path.read_bytes()) != row['published_sha256']:
                    errors.append('Published redaction hash mismatch: ' + label + '/' + row['file'])
            redaction_summaries[label] = {'changed_files': len(redaction['files']), 'counts': redaction['counts'],
                                          'policy': redaction['policy']}
    manifest = read(run / 'manifest.json')
    frozen_root = run / 'source-snapshot' if (run / 'source-snapshot').is_dir() else root
    case_doc = read(frozen_root / 'benchmarks/cases.json')
    cases = {c['id']: c for c in case_doc['cases']}
    schedule = manifest['ordered_trials']
    if len(schedule) != len(set(schedule)):
        errors.append('Duplicate planned trial IDs')
    expected = {f'{case}__{arm}__r{repeat}' for case in cases for arm in 'ABC'
                for repeat in range(1, manifest['repeats'] + 1)}
    if set(schedule) != expected:
        errors.append('Schedule does not cover the case/arm/repetition matrix')
    if canonical(manifest['source_files']) != manifest['source_digest']:
        errors.append('Actor source manifest digest mismatch')
    for name, expected_hash in manifest['source_files'].items():
        path = frozen_root / name
        if not path.is_file() or sha(path.read_bytes()) != expected_hash:
            errors.append('Frozen source mismatch: ' + name)
    current_differences = [name for name, expected_hash in manifest['source_files'].items()
                           if not (root / name).is_file() or sha((root / name).read_bytes()) != expected_hash]
    end = run / 'source-verification.json'
    if not end.exists():
        pending.append('Actor final source verification absent')
    else:
        final = read(end)
        if not final['matches_start'] or final.get('final_source_files') != manifest['source_files']:
            errors.append('Actor sources changed during execution')
    outcomes_list = read(run / 'outcomes.json') if (run / 'outcomes.json').exists() else []
    outcomes = {o['id']: o for o in outcomes_list}
    if len(outcomes) != len(outcomes_list):
        errors.append('Duplicate actor outcomes')
    if set(outcomes) - expected:
        errors.append('Unexpected actor outcomes')
    if expected - set(outcomes):
        pending.append(f'{len(expected - set(outcomes))} planned actor outcomes absent')
    records = {}
    for path in sorted((run / 'trials').glob('*.json')):
        record = read(path)
        if record['id'] in records:
            errors.append('Duplicate record: ' + record['id'])
        records[record['id']] = record
    if set(records) - expected:
        errors.append('Unexpected actor records')
    cells, semantic_expected = {}, set()
    arm_times, arm_usage = defaultdict(list), defaultdict(Counter)
    trial_times, trial_tokens = defaultdict(list), defaultdict(lambda: defaultdict(list))
    usage_coverage, tools = Counter(), Counter()
    model_counts, status_counts = Counter(), Counter()
    snapshot_checks = Counter()
    non_roundtrippable_snapshots = set()
    for trial in schedule:
        case_id, arm, repeat = trial.split('__')
        case = cases[case_id]
        record = records.get(trial)
        status_counts[outcomes.get(trial, {}).get('status', 'not_recorded')] += 1
        if not record:
            if trial in outcomes and outcomes[trial]['status'] != 'harness_failure':
                errors.append('Outcome without record: ' + trial)
        else:
            if (record['case_id'], record['arm'], record['repeat']) != (case_id, arm, int(repeat[1:])):
                errors.append('Trial identity mismatch: ' + trial)
            if trial in outcomes and outcomes[trial]['status'] != record['status']:
                errors.append('Outcome/record status mismatch: ' + trial)
            models = record.get('resolved_models', [])
            model_counts.update(models)
            if record['status'] == 'completed' and models != [manifest['model']]:
                errors.append('Completed actor model mismatch: ' + trial)
            contexts = [x['payload'] for x in record.get('session_contexts', []) if x['type'] == 'turn_context']
            if any(x.get('effort') != manifest['reasoning_effort'] for x in contexts):
                errors.append('Actor effort mismatch: ' + trial)
            threads = []
            current_tokens = Counter()
            current_fields = set()
            trial_times[arm].append(sum(t['duration_seconds'] for t in record['turns']))
            for turn in record['turns']:
                index = turn['index']
                if turn['prompt'] != case['turns'][index]['prompt']:
                    errors.append('Prompt mismatch: ' + trial)
                if not turn.get('new_session'):
                    errors.append('Non-cold turn: ' + trial)
                threads.extend(e['thread_id'] for e in turn['events'] if e.get('type') == 'thread.started')
                if turn['completed'] and sum(e.get('type') == 'thread.started' for e in turn['events']) != 1:
                    errors.append('Completed turn lacks exactly one session start: ' + trial)
                arm_times[arm].append(turn['duration_seconds'])
                for usage in turn.get('usage', []):
                    for key, value in usage.items():
                        if isinstance(value, (int, float)):
                            arm_usage[arm][key] += value
                            current_tokens[key] += value
                            current_fields.add(key)
                            usage_coverage[(arm, key)] += 1
                tools[arm] += sum(e.get('type') == 'item.completed' and e.get('item', {}).get('type') not in ('agent_message', 'reasoning') for e in turn['events'])
            for key in current_fields:
                trial_tokens[arm][key].append(current_tokens[key])
            if len(threads) != len(set(threads)):
                errors.append('Reused session thread: ' + trial)
            audit_path = run / 'prompt-audits' / (trial + '.json')
            if 'common_instructions' in case_doc:
                if not audit_path.exists():
                    errors.append('Actor prompt audit absent: ' + trial)
                else:
                    audit = read(audit_path)
                    required_skills = {'imagegen', 'openai-docs', 'skill-creator', 'skill-installer'} | ({'align'} if arm == 'C' else set())
                    if set(audit.get('available_skills', [])) != required_skills or audit.get('ancestor_instruction_files'):
                        errors.append('Actor context inventory mismatch: ' + trial)
                common = case_doc['common_instructions']
                initial = {**case['files']}
                if arm == 'A':
                    initial['AGENTS.md'] = common + '\n\n' + case['criteria']
                else:
                    # Use the frozen protocol, not today's branding, to replay old evidence.
                    runner = (frozen_root / 'benchmarks/run.py').read_text()
                    agreement = 'ALIGNS.md' if "workspace / 'ALIGNS.md'" in runner else 'ALIGN.md'
                    initial['AGENTS.md'] = common + f'\n\nRead {agreement} before work. It contains current project criteria.\n'
                    initial[agreement] = case['criteria']
                if arm == 'C':
                    initial['AGENTS.md'] += '\n' + (frozen_root / 'skills/align/assets/instruction-block.md').read_text()
                for name, value in initial.items():
                    if record['before'].get(name, {}).get('sha256') != sha(value.encode()):
                        errors.append('Initial treatment/fixture mismatch: ' + trial + '/' + name)
                skill_files = {name: value for name, value in record['before'].items() if name.startswith('.agents/skills/align/')}
                expected_skills = {name.replace('skills/align/', '.agents/skills/align/', 1): value for name, value in manifest['source_files'].items() if name.startswith('skills/align/')} if arm == 'C' else {}
                if {name: value['sha256'] for name, value in skill_files.items()} != expected_skills:
                    errors.append('Initial installed skill mismatch: ' + trial)
            for files in [record['before']] + [t['after'] for t in record['turns']]:
                for name, value in files.items():
                    text = value['text'].encode('utf-8')
                    if len(text) == value['bytes'] and sha(text) == value['sha256']:
                        snapshot_checks['text_reconstruction_matches'] += 1
                    else:
                        snapshot_checks['text_reconstruction_does_not_match'] += 1
                        non_roundtrippable_snapshots.add(trial + '/' + name)
                        # Binary snapshots use replacement decoding; redaction can also alter text.
                        warnings.append('Snapshot bytes cannot be reconstructed from published text: ' + trial + '/' + name)
        for rule in case['rubric']:
            index = rule.get('turn', len(case['turns']) - 1)
            valid = record is not None and record['status'] not in ('model_verification_failure', 'harness_failure')
            observed = valid and len(record['turns']) > index and record['turns'][index]['completed']
            value = file_check(rule['check'], record['before'], record['turns'][index]['after']) if observed else None
            cells[(trial, rule['id'])] = {'kind': rule['check']['type'], 'value': int(value) if value is not None else None,
                                        'observed': bool(observed), 'arm': arm, 'case_id': case_id, 'repeat': repeat}
            if observed and rule['check']['type'] == 'manual':
                semantic_expected.add((trial, rule['id']))
    grades_path = run / 'deterministic-grades.json'
    if grades_path.exists():
        seen = set()
        for row in read(grades_path):
            for check in row['checks']:
                key = (row['trial_id'], check['criterion'])
                if key in seen or key not in cells:
                    errors.append('Duplicate/unexpected grade cell: ' + str(key))
                    continue
                seen.add(key)
                if check['earned'] != cells[key]['value']:
                    errors.append('Deterministic replay mismatch: ' + str(key))
        if seen != set(cells):
            errors.append('Published grade matrix incomplete')
    else:
        pending.append('Published deterministic grades absent')
    score_maps = {'deterministic': {k: v['value'] for k, v in cells.items() if v['kind'] != 'manual'}}
    judge_diagnostics = {}
    if judges:
        jm = read(judges / 'manifest.json')
        jbase = {k: jm[k] for k in ('version', 'files', 'prompt_sha256', 'schema_sha256')}
        if canonical(jbase) != jm['harness_digest']:
            errors.append('Judge manifest digest mismatch')
        for name, value in jm['files'].items():
            if sha((frozen_root / 'benchmarks' / name).read_bytes()) != value:
                errors.append('Judge source mismatch: ' + name)
        for name, key in [('prompt.txt', 'prompt_sha256'), ('schema.json', 'schema_sha256')]:
            actual = sha((judges / name).read_bytes()) if name.endswith('.txt') else canonical(read(judges / name))
            if actual != jm[key]:
                errors.append('Judge prompt/schema mismatch: ' + name)
        if not (judges / 'source-verification.json').exists():
            pending.append('Judge final source verification absent')
        elif not read(judges / 'source-verification.json')['matches_start']:
            errors.append('Judge source changed during execution')
        keymap = read(run / 'review-key.json')
        if len(set(keymap.values())) != len(keymap) or set(keymap.values()) != expected:
            errors.append('Review key does not cover the full schedule exactly once')
        packet_data = {}
        common_context_count = 0
        repair_verified = False
        if packets:
            for path in packets.glob('*.json'):
                packet = read(path)
                packet_data[packet['review_id']] = packet
            if set(packet_data) != set(jm['packet_sha256']):
                errors.append('Judge packet inventory mismatch')
            for rid, packet in packet_data.items():
                if canonical(packet) != jm['packet_sha256'].get(rid):
                    errors.append('Judge packet hash mismatch: ' + rid)
                if case_doc.get('common_instructions') in strings(packet):
                    common_context_count += 1
            if common_context_count != len(packet_data):
                warnings.append('Shared actor instructions absent from some judge packets; semantic interpretations may be invalid')
            repair_path = run / 'context-repair-manifest.json'
            if common_context_count == len(packet_data) and repair_path.exists():
                repair = read(repair_path)
                if repair['cases_sha256'] != sha((frozen_root / 'benchmarks/cases.json').read_bytes()) or repair['common_instructions_sha256'] != sha(case_doc['common_instructions'].encode()):
                    errors.append('Context repair source mismatch')
                if len(repair['changes']) != len(packet_data):
                    errors.append('Context repair inventory mismatch')
                for change in repair['changes']:
                    old_path = run / 'review-packets' / change['file']
                    new_path = packets / change['file']
                    if sha(old_path.read_bytes()) != change['before_sha256'] or sha(new_path.read_bytes()) != change['after_sha256']:
                        errors.append('Context repair file hash mismatch: ' + change['file'])
                    original, amended = read(old_path), read(new_path)
                    common = amended.pop('common_instructions', None)
                    if common != case_doc['common_instructions'] or original != amended:
                        errors.append('Context repair changed evidence beyond shared instructions: ' + change['file'])
                if datetime.fromisoformat(repair['created_at']) > datetime.fromisoformat(jm['created_at']):
                    errors.append('Context repair recorded after corrected judging began')
                repair_verified = True
        else:
            pending.append('Packet hashes not checked; supply --packets')
        for j in (1, 2):
            score_maps['judge_' + str(j)] = {}
        batches = {}
        reviews_seen = {1: set(), 2: set()}
        request_counts = {str(j): {a: Counter() for a in 'ABC'} for j in (1, 2)}
        judge_status = Counter()
        for path in sorted((judges / 'batches').glob('*.json')):
            batch = read(path)
            bid = batch['batch_id']
            if bid in batches:
                errors.append('Duplicate judge batch: ' + bid)
            batches[bid] = batch
            judge_status[batch['status']] += 1
            if batch['status'] != 'completed':
                continue
            if batch['resolved_models'] != [jm['model']] or batch.get('tool_items'):
                errors.append('Invalid completed judge setup: ' + bid)
            if batch.get('resolved_efforts') != [jm['reasoning_effort']]:
                errors.append('Judge effort mismatch: ' + bid)
            scores = score_maps['judge_' + str(batch['judge'])]
            for review in batch['judgments']['reviews']:
                rid = review['review_id']
                if rid not in keymap:
                    errors.append('Unknown review ID: ' + rid)
                    continue
                trial = keymap[rid]
                if rid in reviews_seen[batch['judge']]:
                    errors.append('Duplicate review packet: ' + bid + '/' + rid)
                reviews_seen[batch['judge']].add(rid)
                if trial.split('__')[0] != batch['case_id']:
                    errors.append('Review in wrong case batch: ' + bid + '/' + rid)
                packet = packet_data.get(rid)
                leaves = strings(packet) if packet else []
                for row in review['scores']:
                    key = (trial, row['criterion'])
                    if key in scores or key not in semantic_expected or type(row['score']) is not int or row['score'] not in (0, 1):
                        errors.append('Invalid/duplicate judge score: ' + str(key))
                    scores[key] = row['score']
                    if packet:
                        for evidence in row['evidence']:
                            if not evidence['quote'] or not any(evidence['quote'] in leaf for leaf in leaves):
                                errors.append('Non-verbatim judge evidence: ' + bid + '/' + rid + '/' + row['criterion'])
                for request in review['clarification_requests']:
                    request_counts[str(batch['judge'])][trial.split('__')[1]][request['classification']] += 1
                    if packet:
                        matching = [t for t in packet['turns'] if t['index'] == request['turn'] and t['completed']]
                        if not matching or not request['quote'] or request['quote'] not in matching[0]['response']:
                            errors.append('Ungrounded clarification quote: ' + bid + '/' + rid)
        if set(batches) - set(jm['batches']):
            errors.append('Unexpected judge batches')
        if set(jm['batches']) - set(batches):
            pending.append('Missing judge batch records: ' + str(len(set(jm['batches']) - set(batches))))
        for j in (1, 2):
            if set(score_maps['judge_' + str(j)]) != semantic_expected:
                pending.append(f'Judge {j} missing {len(semantic_expected - set(score_maps["judge_" + str(j)]))} eligible semantic scores')
            if reviews_seen[j] != set(keymap):
                pending.append(f'Judge {j} missing {len(set(keymap) - reviews_seen[j])} review packets')
        one, two = score_maps['judge_1'], score_maps['judge_2']
        shared = set(one) & set(two)
        disagreements = [{'trial_id': k[0], 'criterion': k[1], 'judge_1': one[k], 'judge_2': two[k]} for k in sorted(shared) if one[k] != two[k]]
        comparison_path = judges / 'comparison.json'
        if comparison_path.exists():
            compared = set()
            for row in read(comparison_path)['criteria']:
                key = (keymap[row['review_id']], row['criterion'])
                if key in compared or key not in semantic_expected:
                    errors.append('Duplicate/unexpected comparison cell: ' + str(key))
                compared.add(key)
                expected_status = 'missing_review' if key not in shared else 'agreement' if one[key] == two[key] else 'needs_independent_adjudication'
                if row['status'] != expected_status:
                    errors.append('Published judge comparison mismatch: ' + str(key))
            if compared != semantic_expected:
                errors.append('Published judge comparison inventory mismatch')
        else:
            pending.append('Published judge comparison absent')
        judge_diagnostics = {'statuses': dict(judge_status), 'eligible_semantic_cells': len(semantic_expected),
            'packets_with_exact_shared_instructions': common_context_count,
            'packets_checked': len(packet_data),
            'additive_context_repair_checked': repair_verified,
            'jointly_scored': len(shared), 'agreements': len(shared) - len(disagreements),
            'agreement_rate': (len(shared) - len(disagreements)) / len(shared) if shared else None,
            'disagreements': disagreements, 'clarification_request_counts': request_counts}
    for j in (1, 2):
        name = 'judge_' + str(j)
        if name in score_maps:
            score_maps['combined_' + name] = {**score_maps['deterministic'], **score_maps[name]}
    arm_results, per_case, per_repeat, pairs, full_pass = {}, {}, {}, {}, {}
    for mode, scores in score_maps.items():
        relevant = {k for k, v in cells.items() if mode.startswith('combined_') or (v['kind'] != 'manual') == (mode == 'deterministic')}
        arm_results[mode] = {a: totals([scores.get(k) for k in relevant if cells[k]['arm'] == a], sum(cells[k]['arm'] == a for k in relevant)) for a in 'ABC'}
        per_case[mode] = {case: {a: totals([scores.get(k) for k in relevant if cells[k]['arm'] == a and cells[k]['case_id'] == case], sum(cells[k]['arm'] == a and cells[k]['case_id'] == case for k in relevant)) for a in 'ABC'} for case in cases}
        per_repeat[mode] = {str(r): {a: totals([scores.get(k) for k in relevant if cells[k]['arm'] == a and cells[k]['repeat'] == 'r' + str(r)], sum(cells[k]['arm'] == a and cells[k]['repeat'] == 'r' + str(r) for k in relevant)) for a in 'ABC'} for r in range(1, manifest['repeats'] + 1)}
        if mode.startswith('combined_'):
            full_pass[mode] = {}
            for a in 'ABC':
                trials = [t for t in schedule if t.split('__')[1] == a]
                values = [[scores.get(k) for k in relevant if k[0] == t] for t in trials]
                complete = [v for v in values if all(x is not None for x in v)]
                full_pass[mode][a] = {'passed': sum(all(x == 1 for x in v) for v in complete), 'graded_scenarios': len(complete), 'planned_scenarios': len(trials)}
        mode_pairs = {}
        for higher, lower in [('B', 'A'), ('C', 'B'), ('C', 'A')]:
            result = Counter(win=0, tie=0, loss=0, incomplete=0, not_applicable=0)
            for case in cases:
                for repeat in range(1, manifest['repeats'] + 1):
                    ids = [f'{case}__{a}__r{repeat}' for a in (higher, lower)]
                    values = [[scores.get(k) for k in relevant if k[0] == trial] for trial in ids]
                    if not values[0]:
                        result['not_applicable'] += 1
                    elif any(v is None for vv in values for v in vv):
                        result['incomplete'] += 1
                    else:
                        diff = sum(values[0]) - sum(values[1])
                        result['win' if diff > 0 else 'loss' if diff < 0 else 'tie'] += 1
            mode_pairs[higher + '_vs_' + lower] = dict(result)
        pairs[mode] = mode_pairs
    return {'reporting_provenance': {'utility_sha256': sha(Path(__file__).read_bytes()), 'status': 'post-freeze reporting utility; frozen rubric unchanged',
                                    'archived_source_snapshot_used': frozen_root != root},
        'current_checkout_comparison': {'matches_frozen_sources': not current_differences, 'different_files': current_differences,
            'scope': 'Informational only. Historical scores use archived frozen sources, not the current skill.'},
        'validation': {'errors': errors, 'pending': pending, 'warnings': sorted(set(warnings)),
                       'scope': 'Evidence integrity and coverage; does not certify semantic interpretations or benchmark validity',
                       'judge_checks_requested': judges is not None, 'complete_and_consistent': not errors and not pending},
        'coverage': {'planned_scenarios': len(schedule), 'planned_sessions': sum(len(cases[t.split('__')[0]]['turns']) for t in schedule),
                     'recorded_scenarios': len(records), 'statuses': dict(status_counts), 'models': dict(model_counts)},
        'scores_by_arm': arm_results, 'scores_by_case': per_case, 'scores_by_repeat': per_repeat,
        'fully_passed_scenarios': full_pass, 'paired_scenario_scores': pairs,
        'judging': judge_diagnostics,
        'publication_redactions': redaction_summaries,
        'snapshot_verification': {'counts': dict(snapshot_checks), 'non_roundtrippable_files': sorted(non_roundtrippable_snapshots),
            'limitation': 'Snapshots retain original hashes and replacement-decoded text, not binary bytes. Published redaction may also change text. Only exact text reconstruction is independently hash-verified here.'},
        'actor_resources': {a: {'turn_seconds': timing(arm_times[a]), 'scenario_seconds': timing(trial_times[a]),
            'scenario_token_summaries': {key: timing(values) for key, values in trial_tokens[a].items()}, 'tokens': dict(arm_usage[a]),
            'token_field_observations': {key: n for (arm, key), n in usage_coverage.items() if arm == a},
            'completed_tool_items': tools[a]} for a in 'ABC'},
        'wall_clock': read(run / 'completion.json') if (run / 'completion.json').exists() else None,
        'notes': ['Rates use graded cells only; planned and missing counts remain explicit.',
                  'Judge modes contain semantic checks only; combined modes add deterministic checks.',
                  'Input tokens include cached input tokens; cached tokens are not added again.',
                  'Paired results compare summed scores within the same case/repetition and omit incomplete pairs.',
                  'A paired check category with no criteria in a case is not applicable, not incomplete.',
                  'No confidence intervals, inferred prices, or semantic adjudication are produced.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--judges', type=Path)
    parser.add_argument('--packets', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-complete', action='store_true', help='Also fail on missing evidence; intended for CI')
    args = parser.parse_args()
    report = verify(args.run, args.judges, args.packets)
    text = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end='')
    return 1 if report['validation']['errors'] or (args.require_complete and report['validation']['pending']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
