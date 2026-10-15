#!/usr/bin/env python3
"""Run the independent router challenge before freezing scored trajectories."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--private-output', type=Path, required=True)
    parser.add_argument('--codex', type=Path, required=True)
    parser.add_argument('--auth', type=Path, default=Path.home() / '.codex/auth.json')
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    args.model = 'gpt-6-astra'
    args.output, args.private_output, args.auth, args.codex = [p.resolve() for p in (args.output, args.private_output, args.auth, args.codex)]
    if args.output.exists() or args.private_output.exists() or args.private_output.is_relative_to(run.ROOT) or args.output.is_relative_to(args.private_output) or args.private_output.is_relative_to(args.output):
        parser.error('Use new disjoint outputs and private output outside the repository')
    args.private_output.mkdir(parents=True, mode=0o700)
    stage = args.private_output / 'stage'
    stage.mkdir()
    doc = json.loads((run.HERE / 'cases.json').read_text())
    fixture = json.loads((run.HERE / 'router-validation.json').read_text())
    cases = {c['id']: c for c in doc['cases']}
    sources = run.source_manifest(run.HERE / 'cases.json')
    secrets = run.legacy.collect_strings(json.loads(args.auth.read_text()))
    def classify(item):
        episode = next(e for e in cases[item['case_id']]['episodes'] if e['id'] == item['episode'])
        replacements = {str(args.private_output): '<PRIVATE_OUTPUT>', str(args.codex): '<CODEX_BIN>', str(run.ROOT): '<SOURCE_REPO>', str(Path.home()): '<HOST_HOME>'}
        receipt = run.classify_questions(item['questions'], episode['question_routes'], episode['prompt'], args, replacements)
        run.legacy.write_json(args.private_output / 'raw' / (item['id'] + '.json'), receipt)
        extra_secrets = [e['payload'][key] for e in receipt['session_events'] for key in ('creator_user_id', 'creator_account_id') if e.get('payload', {}).get(key)]
        counts = Counter()
        public = run.redactor.clean(run.legacy.sanitize(receipt, replacements, secrets + extra_secrets), counts)
        run.legacy.write_json(stage / 'receipts' / (item['id'] + '.json'), public)
        run.legacy.write_json(stage / 'redactions' / (item['id'] + '.json'), {'counts': dict(counts)})
        selected = receipt['selection']['route_ids'] if receipt['selection'] else []
        return {'id': item['id'], 'valid': receipt['valid'], 'selected_routes': selected,
                'expected_routes': item['expected_routes'], 'matched': receipt['valid'] and sorted(selected) == sorted(item['expected_routes'])}
    with ThreadPoolExecutor(max_workers=3) as pool:
        outcomes = list(pool.map(classify, fixture['items']))
    report = {'non_scored_development_validation': True, 'created_at': datetime.now(timezone.utc).isoformat(),
              'model': args.model, 'reasoning_effort': 'medium', 'source_files': sources,
              'source_unchanged': run.source_manifest(run.HERE / 'cases.json') == sources,
              'total': len(outcomes), 'matched': sum(r['matched'] for r in outcomes), 'outcomes': outcomes}
    run.legacy.write_json(stage / 'report.json', report)
    audit = subprocess.run(['python3', '-B', str(run.ROOT / 'benchmarks/reporting/audit_privacy.py'), str(stage), '--private-raw', str(args.private_output / 'raw'), '--auth', str(args.auth)], capture_output=True, text=True)
    if audit.returncode:
        raise SystemExit('Privacy scan failed; evidence remains in private staging')
    shutil.copytree(stage, args.output)
    print(json.dumps({'output': str(args.output), 'total': report['total'], 'matched': report['matched']}))


if __name__ == '__main__':
    main()
