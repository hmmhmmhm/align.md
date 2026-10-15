#!/usr/bin/env python3
"""Remove private reasoning from publication copies, retaining originals privately."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

DROP = object()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def is_reasoning(node):
    if not isinstance(node, dict):
        return False
    if str(node.get('type', '')).lower() == 'reasoning':
        return True
    if node.get('channel') == 'analysis' or node.get('phase') == 'analysis':
        return True
    for key in ('payload', 'item'):
        if isinstance(node.get(key), dict) and is_reasoning(node[key]):
            return True
    return False


def encrypted_fields(node):
    if isinstance(node, dict):
        return int('encrypted_content' in node) + sum(encrypted_fields(v) for v in node.values())
    if isinstance(node, list):
        return sum(encrypted_fields(v) for v in node)
    return 0


def clean_jsonl(text, counts):
    lines = []
    for line in text.splitlines(keepends=True):
        try:
            node = json.loads(line)
        except json.JSONDecodeError:
            lines.append(line)
            continue
        before = counts.copy()
        new = clean(node, counts)
        if new is DROP:
            continue
        lines.append(line if counts == before else json.dumps(new, ensure_ascii=False, separators=(',', ':')) + '\n')
    return ''.join(lines)


def clean(node, counts):
    if is_reasoning(node):
        counts['private_reasoning_records'] += 1
        counts['encrypted_content_fields'] += encrypted_fields(node)
        return DROP
    if isinstance(node, list):
        result = []
        for value in node:
            new = clean(value, counts)
            if new is not DROP:
                result.append(new)
        return result
    if isinstance(node, dict):
        result = {}
        for key, value in node.items():
            if key == 'encrypted_content':
                counts['encrypted_content_fields'] += 1
                continue
            if key == 'stdout' and isinstance(value, str):
                result[key] = clean_jsonl(value, counts)
                continue
            new = clean(value, counts)
            if new is not DROP:
                result[key] = new
        return result
    return node


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('publication_root', type=Path)
    parser.add_argument('--private-backup', type=Path, required=True)
    args = parser.parse_args()
    root = args.publication_root.resolve()
    backup = args.private_backup.resolve()
    repo = Path(__file__).resolve().parents[2]
    if backup.is_relative_to(repo) or backup.exists():
        parser.error('Private backup must be new and outside the repository.')
    if (root / 'publication-redactions.json').exists():
        parser.error('Already processed; use original copies instead of rewriting the audit trail.')
    backup.mkdir(parents=True, mode=0o700)
    rows, total = [], Counter()
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix not in ('.json', '.jsonl', '.gz'):
            continue
        original = path.read_bytes()
        raw = gzip.decompress(original) if path.suffix == '.gz' else original
        text = raw.decode('utf-8')
        counts = Counter()
        if path.suffix == '.json':
            new = clean(json.loads(text), counts)
            changed = b'' if new is DROP else (json.dumps(new, indent=2, ensure_ascii=False) + '\n').encode()
        else:
            changed = clean_jsonl(text, counts).encode()
        if not counts:
            continue
        relative = path.relative_to(root)
        dest = backup / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        published = gzip.compress(changed, mtime=0) if path.suffix == '.gz' else changed
        path.write_bytes(published)
        total.update(counts)
        rows.append({'file': str(relative), 'original_sha256': sha(original), 'published_sha256': sha(published), 'removed': dict(counts)})
    report = {'policy_version': 1, 'processed_at': datetime.now(timezone.utc).isoformat(),
              'policy': 'Remove complete private Reasoning/reasoning and analysis-channel records, including nested event payloads, and all encrypted_content fields. Apply the same removal to embedded Codex stdout JSONL. Preserve observable prompts, context, actions, tool outputs, assistant replies, and token usage. Original changed files remain in the private backup; actor and judge raw evidence remains separate.',
              'script_sha256': sha(Path(__file__).read_bytes()), 'counts': dict(total), 'files': rows}
    (root / 'publication-redactions.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'changed_files': len(rows), 'removed_categories': dict(total)}))

if __name__ == '__main__':
    main()
