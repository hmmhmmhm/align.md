#!/usr/bin/env python3
"""Replay discovery counts from retained actor events and frozen case labels."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()

def summarize(records, cases):
    rows={}
    for d in records:
        case=cases[d['case_id']]
        for key in (case['expected_routing'],case['expected_routing']+'/'+case['language']):
            r=rows.setdefault(key,{'completed':0,'read':0,'runtime_failures':0})
            if d['completed']:
                r['completed']+=1;r['read']+=bool(d['read_evidence'])
            else:r['runtime_failures']+=1
    return rows

def verify(root):
    m=json.loads((root/'manifest.json').read_text());errors=[]
    for name,expected in m['source_hashes'].items():
        p=root/'source'/name
        if not p.is_file() or sha(p.read_bytes())!=expected:errors.append('Source hash mismatch: '+name)
    if sha(json.dumps(m['source_hashes'],sort_keys=True).encode())!=m['source_digest']:errors.append('Source manifest digest mismatch')
    spec=importlib.util.spec_from_file_location('frozen_activation_runner',root/'source/run.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    cases={c['id']:c for c in json.loads((root/'source/cases.json').read_text())['cases']}
    records=[]
    for p in sorted((root/'trials').glob('*.json')):
        d=json.loads(p.read_text());records.append(d)
        if d['prompt']!=cases[d['case_id']]['prompt']:errors.append('Prompt mismatch: '+d['id'])
        evidence=runner.observe_read(d['events'])
        if evidence!=d['read_evidence'] or bool(evidence)!=d['method_read_observed']:errors.append('Read evidence mismatch: '+d['id'])
        completed=d['returncode']==0 and not d['timeout'] and any(e.get('type')=='turn.completed' for e in d['events'])
        if completed!=d['completed']:errors.append('Completion mismatch: '+d['id'])
        if completed and {c.get('model') for c in d['context']}!={m['model']}:errors.append('Model context missing or inconsistent: '+d['id'])
        if completed and not any(s[0].startswith('align: ') for s in d['catalog']):errors.append('Skill catalog missing: '+d['id'])
    expected=set(m['ordered_trials']);actual=[d['id'] for d in records]
    if len(actual)!=len(set(actual)):errors.append('Duplicate trial')
    missing=sorted(expected-set(actual));extra=sorted(set(actual)-expected)
    if extra:errors.append('Unexpected trials: '+str(extra))
    outcomes=json.loads((root/'outcomes.json').read_text())
    complete=len(actual)==len(expected) and all(d['completed'] for d in records) and len(outcomes)==len(expected)
    for outcome in outcomes:
        if outcome.get('error'):errors.append('Runtime error: '+outcome['id']+': '+outcome['error'])
    return {'planned':len(expected),'records':len(records),'completed':sum(d['completed'] for d in records),
            'all_completed':complete,'missing':missing,'errors':errors,'counts':summarize(records,cases)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--require-complete',action='store_true');args=p.parse_args()
    result=verify(args.run);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['errors'] or (args.require_complete and not result['all_completed']) else 0)
