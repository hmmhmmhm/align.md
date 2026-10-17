#!/usr/bin/env python3
"""Apply narrow file checks and prepare anonymized evidence for semantic review."""
import argparse
import random
import uuid
import json
from pathlib import Path


def check_file(check, before, after):
    kind, name = check['type'], check.get('path')
    if kind == 'manual':
        return None
    if name not in after:
        return False  # Deleting a target cannot satisfy a negative-text check.
    if kind == 'file_exists':
        return True
    if kind == 'file_unchanged':
        return name in before and after[name]['sha256'] == before[name]['sha256']
    if kind == 'file_contains':
        return check['text'] in after[name]['text']
    if kind == 'file_not_contains':
        return check['text'] not in after[name]['text']
    raise ValueError(f'Unsupported check type: {kind}')


def criteria_only(files, common):
    if 'ALIGNS.md' in files:
        return files['ALIGNS.md']['text']
    text = files.get('AGENTS.md', {}).get('text', '')
    return text.removeprefix(common).lstrip()


def criteria_evidence(files, common):
    """Retain every criteria source, including conflicting newly created files."""
    block = (Path(__file__).resolve().parents[1] / 'skills/align/assets/instruction-block.md').read_text()
    instruction = files.get('AGENTS.md', {}).get('text', '')
    residue = instruction.replace(common, '', 1).replace('Read ALIGNS.md before work. It contains current project criteria.', '', 1).replace(block, '', 1).strip()
    documents = [residue] if residue else []
    if 'ALIGNS.md' in files:
        documents.append(files['ALIGNS.md']['text'])
    return {'documents': documents, 'common_instructions_intact': common in instruction}


def review_files(files):
    return {name: value['text'] for name, value in files.items()
            if name not in ('AGENTS.md', 'ALIGNS.md') and not name.startswith('.agents/')}


def grade(record, case):
    rows = []
    for rule in case['rubric']:
        index = rule.get('turn', len(case['turns']) - 1)
        invalid_setup = record.get('status') in ('model_verification_failure', 'harness_failure')
        observed = not invalid_setup and len(record['turns']) > index and record['turns'][index].get('completed', False)
        result = check_file(rule['check'], record['before'], record['turns'][index]['after']) if observed else None
        rows.append({'criterion': rule['id'], 'turn': index, 'possible': rule['points'],
                     'status': 'invalid_setup' if invalid_setup else 'runtime_failure' if not observed else 'pending_review' if result is None else 'pass' if result else 'fail',
                     'earned': None if result is None else rule['points'] if result else 0})
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run', type=Path)
    p.add_argument('--cases', type=Path, default=Path(__file__).with_name('cases.json'))
    p.add_argument('--review-output', type=Path, required=True)
    args = p.parse_args()
    doc = json.loads(args.cases.read_text())
    cases = {c['id']: c for c in doc['cases']}
    args.review_output.mkdir(parents=True, exist_ok=True)
    grades, mapping = [], {}
    paths = sorted((args.run / 'trials').glob('*.json'))
    random.SystemRandom().shuffle(paths)
    for path in paths:
        record = json.loads(path.read_text())
        case = cases[record['case_id']]
        review_id = uuid.uuid4().hex
        mapping[review_id] = record['id']
        grades.append({'trial_id': record['id'], 'review_id': review_id, 'status': record['status'], 'checks': grade(record, case)})
        packet = {'review_id': review_id, 'case_id': case['id'], 'title': case['title'], 'rubric': case['rubric'], 'expected_turn_count': len(case['turns']), 'runtime_status': record['status'],
                  'before': {'criteria': criteria_evidence(record['before'], doc['common_instructions']), 'files': review_files(record['before'])},
                  'turns': [{'index': t['index'], 'prompt': t['prompt'], 'response': t['response'], 'completed': t['completed'],
                             'after': {'criteria': criteria_evidence(t['after'], doc['common_instructions']), 'files': review_files(t['after'])}}
                            for t in record['turns']],
                  'review_instruction': 'Score each manual criterion 0 or 1 with concrete evidence. Do not infer missing work. File checks are narrow checks, not full semantic judgments. Treatment labels and installed method files are withheld; response wording may still reveal treatment. Runtime failures remain separate from behavioral scores.'}
        (args.review_output / (review_id + '.json')).write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n')
    present = {row['trial_id'] for row in grades}
    for outcome in json.loads((args.run / 'outcomes.json').read_text()):
        if outcome['id'] not in present:
            case = cases[outcome['id'].split('__')[0]]
            grades.append({'trial_id': outcome['id'], 'review_id': None, 'status': outcome['status'],
                           'checks': grade({'status': 'harness_failure', 'before': {}, 'turns': []}, case)})
    (args.run / 'deterministic-grades.json').write_text(json.dumps(grades, indent=2) + '\n')
    (args.run / 'review-key.json').write_text(json.dumps(mapping, indent=2) + '\n')
    statuses = {}
    for row in grades:
        for check in row['checks']:
            statuses[check['status']] = statuses.get(check['status'], 0) + 1
    print(json.dumps({'trials': len(grades), 'criterion_statuses': statuses, 'semantic_scores': 'pending model review'}))

if __name__ == '__main__':
    main()
