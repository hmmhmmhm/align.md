#!/usr/bin/env python3
"""Check each published judge quote at its declared packet source, offline.

Written after the run by the separate-context evidence reviewer. This checks
locations and verbatim text, not whether a quotation supports a judgment.
"""
import argparse
import json
from pathlib import Path
import re


def resolve(value, source):
    if not source:
        return value
    if isinstance(value, dict):
        # File names contain dots. Prefer the longest matching dictionary key.
        for key in sorted(value, key=len, reverse=True):
            if source == key:
                return value[key]
            if source.startswith(key + '.'):
                return resolve(value[key], source[len(key) + 1:])
            if source.startswith(key + '['):
                return resolve(value[key], source[len(key):])
    if isinstance(value, list):
        match = re.fullmatch(r'\[(\d+)\](?:\.(.*))?', source)
        if match:
            return resolve(value[int(match[1])], match[2] or '')
    raise ValueError('Cannot resolve source: ' + source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packets', type=Path)
    parser.add_argument('judgments', type=Path)
    args = parser.parse_args()
    packets = {p.stem: json.loads(p.read_text()) for p in args.packets.glob('*.json')}
    counts = dict(batches=0, score_records=0, evidence_quotes=0, clarification_quotes=0)
    for path in sorted((args.judgments / 'batches').glob('*.json')):
        batch = json.loads(path.read_text())
        if batch['status'] != 'completed':
            raise ValueError('Incomplete batch: ' + str(path))
        counts['batches'] += 1
        for review in batch['judgments']['reviews']:
            packet = packets[review['review_id']]
            for score in review['scores']:
                counts['score_records'] += 1
                for evidence in score['evidence']:
                    text = resolve(packet, evidence['source'])
                    if not isinstance(text, str) or not evidence['quote'] or evidence['quote'] not in text:
                        raise ValueError(f'{path.name}/{review["review_id"]}/{score["criterion"]}: quote absent from {evidence["source"]}')
                    counts['evidence_quotes'] += 1
            for request in review['clarification_requests']:
                turns = [t for t in packet['turns'] if t['index'] == request['turn'] and t['completed']]
                if len(turns) != 1 or not request['quote'] or request['quote'] not in turns[0]['response']:
                    raise ValueError('Clarification source mismatch: ' + review['review_id'])
                counts['clarification_quotes'] += 1
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
