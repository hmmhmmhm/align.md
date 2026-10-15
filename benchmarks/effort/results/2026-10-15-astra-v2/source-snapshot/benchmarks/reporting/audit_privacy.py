#!/usr/bin/env python3
"""Check publication files without printing credential values or private payloads."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def strings(value):
    if isinstance(value, str):
        return [value] if len(value) >= 16 else []
    if isinstance(value, dict):
        return [s for v in value.values() for s in strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in strings(v)]
    return []


def private_fields(value):
    if isinstance(value, dict):
        own = int('encrypted_content' in value or str(value.get('type', '')).lower() == 'reasoning' or value.get('channel') == 'analysis' or value.get('phase') == 'analysis')
        embedded = 0
        if isinstance(value.get('stdout'), str):
            for line in value['stdout'].splitlines():
                try:
                    embedded += private_fields(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return own + embedded + sum(private_fields(v) for v in value.values())
    if isinstance(value, list):
        return sum(private_fields(v) for v in value)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('publication_root', type=Path)
    p.add_argument('--private-raw', type=Path, required=True)
    p.add_argument('--auth', type=Path, default=Path.home() / '.codex/auth.json')
    args = p.parse_args()
    probes = strings(json.loads(args.auth.read_text()))
    for path in args.private_raw.rglob('*.jsonl'):
        with path.open() as handle:
            first = handle.readline()
        try:
            meta = json.loads(first).get('payload', {})
        except json.JSONDecodeError:
            continue
        probes.extend(meta[k] for k in ('creator_user_id', 'creator_account_id') if meta.get(k))
    probes = set(probes)
    rows = []
    total = 0
    for path in sorted(args.publication_root.rglob('*')):
        if not path.is_file() or path.name == 'privacy-audit.json':
            continue
        data = path.read_bytes()
        text = (gzip.decompress(data) if path.suffix == '.gz' else data).decode('utf-8')
        hits = sum(probe in text for probe in probes)
        host_paths = int(str(Path.home()) in text or '/private/var/folders/' in text or '/var/folders/' in text)
        private = 0
        if path.suffix == '.json':
            private = private_fields(json.loads(text))
        elif path.suffix in ('.jsonl', '.gz'):
            for line in text.splitlines():
                try:
                    private += private_fields(json.loads(line))
                except json.JSONDecodeError:
                    pass
        total += 1
        if hits or host_paths or private:
            rows.append({'file': str(path.relative_to(args.publication_root)), 'credential_or_identity_matches': hits, 'host_path_match': host_paths, 'private_reasoning_fields': private})
    report = {'method': 'Literal scan for current auth JSON string values of 16+ characters and session creator account/user IDs, plus host-home and macOS temporary-root paths. Parse JSON/JSONL for private reasoning records and encrypted_content fields. Probe values are never emitted.',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'files_checked': total,
              'flagged_files': rows, 'passed': not rows}
    (args.publication_root / 'privacy-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'files_checked': total, 'flagged_file_count': len(rows), 'passed': not rows}))
    if rows:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
