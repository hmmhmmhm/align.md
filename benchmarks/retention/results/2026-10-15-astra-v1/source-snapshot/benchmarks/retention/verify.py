#!/usr/bin/env python3
"""Replay archived preference checks, scripted replies, and resource counts."""
import argparse,json,hashlib,importlib.util
from collections import Counter
from pathlib import Path

def verify(root):
 manifest=json.loads((root/'manifest.json').read_text()); snap=root/'source-snapshot'
 errors=[]
 for name,digest in manifest['source_files'].items():
  if hashlib.sha256((snap/name).read_bytes()).hexdigest()!=digest:errors.append('source hash '+name)
 spec=importlib.util.spec_from_file_location('frozen_retention_run',snap/'benchmarks/retention/run.py');run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run)
 doc=json.loads((snap/'benchmarks/retention/cases.json').read_text());profiles={p['id']:p for p in doc['profiles']};rows=[];totals={a:Counter() for a in ('A','B')}
 expected={p+'__'+a for p in profiles for a in ('A','B')}
 actual={p.stem for p in (root/'trials').glob('*.json')}
 if actual!=expected:errors.append('matrix differs')
 for file in sorted((root/'trials').glob('*.json')):
  rec=json.loads(file.read_text());profile=profiles[rec['profile']];arm=rec['arm'];stats=totals[arm]
  if rec['resolved_models']!=['gpt-6-astra'] or rec['resolved_efforts']!=['medium']:errors.append('model/effort '+rec['id'])
  if [e['task'] for e in rec['episodes']]!=[t['id'] for t in doc['tasks']]:errors.append('task order '+rec['id'])
  threads=[]
  for ep in rec['episodes']:
   first=None;fit=False
   for i,t in enumerate(ep['turns']):
    c=run.evaluate(t['response'],profile['criteria'])
    if c!=t['check']:errors.append('check mismatch '+rec['id']+ep['task'])
    if isinstance(c['object'],dict) and c['object'].get('action')=='submit' and first is None:first=c
    if i<len(ep['replies']) and run.reply_for(c,profile)!=ep['replies'][i]:errors.append('reply mismatch '+rec['id']+ep['task'])
    fit=c['fit']
    stats['actor_calls']+=1;stats['duration_seconds']+=t['duration_seconds']
    for u in t['usage']:
     for k,v in u.items():stats['tokens_'+k]+=v
    for event in t['events']:
     if event.get('type')=='thread.started' and i==0:threads.append(event['thread_id'])
   if bool(ep['passed'])!=bool(fit and not ep.get('runtime_failure')):errors.append('terminal mismatch '+rec['id']+ep['task'])
   row={'profile':rec['profile'],'arm':arm,'task':ep['task'],'zero_reply_fit':bool(ep['turns'] and ep['turns'][0]['check']['fit']),'first_submission_fit':bool(first and first['fit']),'final_fit':ep['passed'],'replies':len(ep['replies']),'repeated_units':sum(len(r['units']) for r in ep['replies']),'format_replies':sum(r['kind']=='format' for r in ep['replies']),'preference_corrections':sum(r['kind']=='preference_correction' for r in ep['replies']),'answer_replies':sum(r['kind']=='answer' for r in ep['replies']),'runtime_failure':bool(ep.get('runtime_failure'))}
   rows.append(row)
   for k,v in row.items():
    if isinstance(v,(int,bool)):stats[k]+=int(v)
   stats['episodes']+=1
  if len(threads)!=3 or len(set(threads))!=3:errors.append('fresh thread check '+rec['id'])
 cumulative={a:[sum(r['replies'] for r in rows if r['arm']==a and [t['id'] for t in doc['tasks']].index(r['task'])<=i) for i in range(3)] for a in ('A','B')}
 payback={}
 for pid in [*profiles,'pooled']:
  subset=[r for r in rows if pid=='pooled' or r['profile']==pid];n=4 if pid=='pooled' else 1;ok=all(r['final_fit'] for r in subset)
  savings=[sum((1 if r['arm']=='A' else -1)*r['replies'] for r in subset if [t['id'] for t in doc['tasks']].index(r['task'])<=i) for i in range(3)]
  payback[pid]={'cumulative_saved_replies':savings,'setup_sensitivity':{str(s):('indeterminate' if not ok else next((i+1 for i,v in enumerate(savings) if v>=s*n),'not reached')) for s in range(4)}}
 return {'verified':not errors,'errors':errors,'rows':rows,'totals':{a:dict(v) for a,v in totals.items()},'cumulative_later_replies':cumulative,'payback':payback}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();result=verify(a.results.resolve());text=json.dumps(result,indent=2)+'\n';a.output.write_text(text) if a.output else print(text);raise SystemExit(0 if result['verified'] else 1)
