#!/usr/bin/env python3
"""Rebuild blinded packets and validate preserved reviewer evidence offline."""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify(results, packets_dir, reviews_dir):
    actor_manifest = json.loads((results / 'manifest.json').read_text())
    archive = results / 'source-snapshot'
    actual_sources = {str(p.relative_to(archive)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in archive.rglob('*') if p.is_file()}
    if actual_sources != actor_manifest['source_files'] or any(p.is_symlink() for p in archive.rglob('*')):
        raise ValueError('Frozen source archive differs from actor manifest; refusing imports')
    frozen = results / 'source-snapshot/benchmarks/discovery'
    prepare = load('frozen_discovery_prepare', frozen / 'prepare_reviews.py')
    review = load('frozen_discovery_review', frozen / 'review.py')
    packets, key = prepare.build_packets(results)
    errors, pending = [], []
    def require(value, message):
        if not value:
            errors.append(message)
    expected = {p['review_id']: p for p in packets}
    actual = {p.stem: json.loads(p.read_text()) for p in packets_dir.glob('*.json')}
    require(expected == actual, 'Packets differ from deterministic actor evidence reconstruction')
    packet_manifest = json.loads((packets_dir.parent / (packets_dir.name + '-manifest.json')).read_text())
    require(packet_manifest['key'] == key, 'Treatment key differs from reconstructed key')
    hashes = {p['review_id']: review.digest(json.dumps(p, sort_keys=True)) for p in packets}
    require(packet_manifest['packet_sha256'] == hashes, 'Packet manifest hashes differ')
    manifest = json.loads((reviews_dir / 'manifest.json').read_text())
    for field, value in review.harness_manifest().items():
        require(manifest.get(field) == value, 'Frozen reviewer manifest differs: ' + field)
    require(manifest.get('packet_sha256') == hashes, 'Reviewer input packet hashes differ')
    require(manifest.get('model') == 'gpt-6-astra' and manifest.get('reasoning_effort') == 'medium', 'Reviewer model declaration')
    groups = {}
    for packet in packets:
        groups.setdefault(packet['case_id'], []).append(packet)
    # The runner loads packet files in filename order before shuffling.
    for group in groups.values():
        group.sort(key=lambda x: x['review_id'])
    planned = {f'judge-{j}__case-{c}' for j in (1, 2) for c in groups}
    require(set(manifest['batches']) == planned and len(manifest['batches']) == len(planned), 'Reviewer schedule differs')
    records = {p.stem: json.loads(p.read_text()) for p in (reviews_dir / 'batches').glob('*.json')}
    require(set(records) == planned, 'Missing or extra review batches')
    completed = []
    for batch_id, record in sorted(records.items()):
        judge, group = record['judge'], record['case_id']
        require(judge in (1, 2) and batch_id == f'judge-{judge}__case-{group}', batch_id + ': batch identity differs')
        if group not in groups:
            errors.append('Unknown review group ' + batch_id)
            continue
        ordered = list(groups[group])
        random.Random(manifest['seed'] + judge * 1000 + int(group)).shuffle(ordered)
        require(record['prompt'] == review.PROMPT + json.dumps(ordered, ensure_ascii=False, indent=2), batch_id + ': actual review prompt differs')
        events, invalid = review.parse_events(record['stdout'])
        require(events == record['events'] and invalid == record['invalid_json_lines'], batch_id + ': event replay differs')
        messages = [e['item']['text'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
        response = messages[-1] if messages else ''
        require(response == record['response'], batch_id + ': final response differs')
        contexts = []
        session_events = []
        for path in (reviews_dir / 'session-traces' / batch_id).glob('*.gz'):
            trace_events, bad = review.parse_events(gzip.decompress(path.read_bytes()).decode())
            require(not bad, batch_id + ': invalid trace')
            session_events.extend(trace_events)
            contexts.extend(e for e in trace_events if e.get('type') in ('session_meta', 'turn_context'))
        require(contexts == record['session_contexts'], batch_id + ': contexts differ from traces')
        models = sorted({e['payload']['model'] for e in contexts if e['type'] == 'turn_context'})
        efforts = sorted({e['payload'].get('effort') for e in contexts if e['type'] == 'turn_context'}, key=str)
        require(models == record['resolved_models'] and efforts == record['resolved_efforts'], batch_id + ': effective model metadata differs')
        tools = [e for e in events if e.get('type') in ('item.started', 'item.completed') and e.get('item', {}).get('type') not in ('agent_message', 'reasoning')]
        trace_calls = [e for e in session_events if e.get('type') == 'response_item' and e.get('payload', {}).get('type') in ('function_call', 'custom_tool_call', 'web_search_call')]
        require(tools == record['tool_items'], batch_id + ': tool event mismatch')
        if record['status'] != 'completed':
            pending.append({'batch': batch_id, 'status': record['status']})
            continue
        require(not tools and not trace_calls and not invalid and not record['returncode'] and not record['timeout'], batch_id + ': invalid completed review')
        require(models == ['gpt-6-astra'] and efforts == ['medium'], batch_id + ': wrong model/effort')
        require(any(e.get('type') == 'turn.completed' for e in events), batch_id + ': incomplete turn')
        try:
            parsed = json.loads(response)
            require(parsed == record['judgments'], batch_id + ': judgments differ')
            review.validate(parsed, groups[group])
            completed.append(record)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(batch_id + ': invalid judgments: ' + str(exc))
    comparison = review.comparison(completed, packets)
    require(comparison == json.loads((reviews_dir / 'comparison.json').read_text()), 'Saved comparison differs')
    rows = {k['review_id']: k for k in key}
    scores = {}
    off_interface = []
    for batch in completed:
        j = str(batch['judge'])
        for item in batch['judgments']['reviews']:
            rid = item['review_id']
            scores[(rid, j)] = {s['criterion']: s['score'] for s in item['scores']}
            for request in item['clarification_requests']:
                turn = expected[rid]['turns'][request['turn']]
                if any(request['quote'] in message for message in turn['assistant_messages'][:-1]):
                    off_interface.append({'review_id': rid, 'judge': j, **request})
    arms = {}
    for arm in ('A', 'B', 'C'):
        arm_rows = [k for k in key if k['arm'] == arm]
        arms[arm] = {}
        for j in ('1', '2'):
            totals = Counter()
            for row in arm_rows:
                values = scores.get((row['review_id'], j), {})
                for phase in ('first', 'final'):
                    totals[phase + '_substantive_passes'] += int(values.get(phase + '_criterion_fit') == 1 and values.get(phase + '_useful_explanation') == 1)
                for name, value in values.items():
                    if name.startswith('route_'):
                        totals['route_checks'] += 1
                        totals['route_correct'] += value
            arms[arm][j] = dict(totals)
    disagreements = [r for r in comparison['criteria'] if r['status'] != 'agreement']
    routing_errors = [r for r in comparison['criteria'] if r['criterion'].startswith('route_') and any(j['score'] == 0 for j in r['judges'].values())]
    return {'verified': not errors, 'errors': errors, 'pending': pending,
            'packet_count': len(packets), 'planned_review_batches': len(planned), 'completed_review_batches': len(completed),
            'arms': arms, 'disagreements': disagreements, 'routing_errors': routing_errors,
            'off_interface_requests': off_interface,
            'audit_note': 'Independent offline replay of model evidence. Semantic correctness, saved-memory authorization, and hidden-source reads still need human or model audit. No human satisfaction measurement.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('results', type=Path)
    p.add_argument('--packets', type=Path, required=True)
    p.add_argument('--reviews', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    report = verify(args.results, args.packets, args.reviews)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'verified': report['verified'], 'errors': report['errors'], 'pending_batches': len(report['pending'])}))
    raise SystemExit(0 if report['verified'] and not report['pending'] else 1)


if __name__ == '__main__':
    main()
