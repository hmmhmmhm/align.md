#!/usr/bin/env python3
"""Replay discovery counts from retained actor events and frozen case labels."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()

def body_visible(events):
    # A later command in a shell group can fail after cat has already returned the method.
    return any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'
               and '# Align\n' in e['item'].get('aggregated_output','')
               and '## Read before asking' in e['item'].get('aggregated_output','') for e in events)

def summarize(records, cases):
    rows={}
    for d in records:
        case=cases[d['case_id']]
        for key in (case['expected_routing'],case['expected_routing']+'/'+case['language']):
            r=rows.setdefault(key,{'completed':0,'read':0,'body_visible':0,'runtime_failures':0})
            if d['completed']:
                r['completed']+=1;r['read']+=bool(d['read_evidence']);r['body_visible']+=body_visible(d.get('events',[]))
            else:r['runtime_failures']+=1
    return rows

def file_checks(record, case):
    """Check narrow file invariants separately from skill discovery."""
    before=record['before'];after=record['after'];topic=case['topic']
    issues=[]
    if topic in ('loop_stop','goal_scope','loop_quota','loop_pause','goal_known','loop_code'):
        if before!=after:issues.append('Review or explanation changed project files or run state')
    if topic=='loop_config':
        try:
            expected=json.loads(before['loop.json']['text']);expected['iterations']=3
            if json.loads(after['loop.json']['text'])!=expected:issues.append('Incorrect loop configuration repair')
        except (KeyError,ValueError,TypeError):issues.append('Missing or invalid loop configuration')
        for key in set(before)|set(after):
            if key!='loop.json' and before.get(key)!=after.get(key):issues.append('Unrelated file or run state changed: '+key)
    if topic=='stop_preference':
        prior=before.get('ALIGNS.md',{}).get('text','');current=after.get('ALIGNS.md',{}).get('text','')
        if prior==current:issues.append('Explicit completion preference not saved')
        # Confirming one new criterion is not confirmation of the whole agreement.
        dates=lambda text:[line for line in text.splitlines() if line.startswith('Last aligned:')]
        if dates(prior)!=dates(current):issues.append('Full alignment date changed')
        if 'Keep changes within the workshop site. No external publication without approval.' not in current:
            issues.append('Existing scope or publication criterion changed')
        for key in set(before)|set(after):
            if key!='ALIGNS.md' and before.get(key)!=after.get(key):issues.append('Unrelated file or run state changed: '+key)
    if topic in ('one_off','rehearsal','repeat','uncertain','direction','context','history_typo','explicit','short','brand_typo','concept_only','alignment_homonym'):
        if before!=after:issues.append('Unexpected file mutation while clarifying, explaining or rehearsing')
    if topic=='vague' and ('ALIGNS.md' in after or 'ALIGN.md' in after):
        issues.append('Vague request produced a lasting agreement')
    if topic in ('typo','declined'):
        expected={**before,'index.html':dict(before['index.html'])}
        expected['index.html']['text']=before['index.html']['text'].replace('Wrokshop','Workshop')
        expected['index.html']['sha256']=sha(expected['index.html']['text'].encode())
        if expected!=after:issues.append('Typo-only request changed more than the specified text')
    if topic=='clear_violation':
        if 'analytics.js' in after.get('index.html',{}).get('text',''):issues.append('Tracking reference remains')
        for key in ('ALIGNS.md','AGENTS.md'):
            if before.get(key)!=after.get(key):issues.append('Existing agreement or instructions changed: '+key)
    if topic=='context_available':
        if '<h1>Find your next workshop</h1>' not in after.get('index.html',{}).get('text',''):issues.append('Approved heading not applied')
        for key in set(before)|set(after):
            if key!='index.html' and before.get(key)!=after.get(key):issues.append('Unrelated file changed: '+key)
    if topic in ('remember','casual_context') and 'ALIGNS.md' not in after:
        issues.append('Explicit lasting preference not saved')
    return issues

def verify(root):
    m=json.loads((root/'manifest.json').read_text());errors=[]
    publication=root/'publication.json'
    if publication.exists():
        for name,expected in json.loads(publication.read_text())['files'].items():
            if not (root/name).is_file() or sha((root/name).read_bytes())!=expected:errors.append('Publication hash mismatch: '+name)
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
        # Stored output digests refer to private raw output, before literal path redaction.
        signature=lambda xs:[(x['event_index'],x['command']) for x in xs]
        if signature(evidence)!=signature(d['read_evidence']) or bool(evidence)!=d['method_read_observed']:errors.append('Read evidence mismatch: '+d['id'])
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
            'all_completed':complete,'missing':missing,'errors':errors,'counts':summarize(records,cases),
            'file_check_findings':{d['id']:found for d in records if d['completed'] and (found:=file_checks(d,cases[d['case_id']]))}}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--require-complete',action='store_true');p.add_argument('--require-clean-files',action='store_true');args=p.parse_args()
    result=verify(args.run);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if result['errors'] or (args.require_complete and not result['all_completed']) or (args.require_clean_files and result['file_check_findings']) else 0)
