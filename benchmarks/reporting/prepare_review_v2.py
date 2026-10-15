#!/usr/bin/env python3
"""Add omitted shared instructions to fixed anonymous review packets."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packets', type=Path, required=True)
    p.add_argument('--cases', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('Output must be new; original packets are never overwritten.')
    cases_data = args.cases.read_bytes()
    common = json.loads(cases_data)['common_instructions']
    args.output.mkdir(parents=True)
    rows = []
    for path in sorted(args.packets.glob('*.json')):
        before = path.read_bytes()
        packet = json.loads(before)
        if 'common_instructions' in packet:
            raise ValueError('Input already contains common instructions')
        packet['common_instructions'] = common
        after = (json.dumps(packet, indent=2, ensure_ascii=False) + '\n').encode()
        (args.output / path.name).write_bytes(after)
        rows.append({'review_id': packet['review_id'], 'file': path.name,
                     'before_sha256': sha(before), 'after_sha256': sha(after),
                     'added_fields': ['common_instructions']})
    manifest = {'version': 2, 'created_at': datetime.now(timezone.utc).isoformat(),
        'reason': 'Original review packets omitted the shared actor instructions. Reviewers therefore lacked a common policy needed to interpret some actions. Add the exact shared instructions to every packet and repeat all semantic reviews; retain the original reviews as a context-deficient run.',
        'cases_sha256': sha(cases_data), 'common_instructions_sha256': sha(common.encode()),
        'script_sha256': sha(Path(__file__).read_bytes()), 'packet_count': len(rows),
        'changes': rows, 'unchanged': 'Review IDs, case IDs, rubric, actor prompts, responses, file evidence, runtime metadata, and all other existing packet values.'}
    (args.output.parent / 'context-repair-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'packets': len(rows), 'added_field': 'common_instructions', 'cases_sha256': manifest['cases_sha256']}))

if __name__ == '__main__':
    main()
