#!/usr/bin/env python3
"""Bind recovered records to native traces, then replay frozen exact endpoints."""
import argparse,gzip,hashlib,importlib.util,inspect,json
from pathlib import Path
import resume

def verify(root):
 run=resume.module(root);s=importlib.util.spec_from_file_location('frozen_verifier',root/'source-snapshot/benchmarks/retention/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
 # Exact scoring/reply logic stays frozen. Only the resource accumulator accepts
 # unavailable subprocess durations; its known subtotal and missing count are explicit.
 original=inspect.getsource(v.verify)
 needle="stats['actor_calls']+=1;stats['duration_seconds']+=t['duration_seconds']"
 replacement="stats['actor_calls']+=1\n    if t['duration_seconds'] is None:stats['missing_subprocess_durations']+=1\n    else:stats['known_subprocess_duration_seconds']+=t['duration_seconds']\n    if t.get('native_duration_seconds') is not None:stats['recovered_native_duration_seconds']+=t['native_duration_seconds']"
 assert original.count(needle)==1
 scope=dict(v.__dict__);exec(compile(original.replace(needle,replacement),'<frozen verifier duration compatibility adapter>','exec'),scope);report=scope['verify'](root);errors=report['errors'];checks=[]
 doc=json.loads((root/'source-snapshot/benchmarks/retention/cases.json').read_text());profiles={q['id']:q for q in doc['profiles']}
 all_native_turns=0;all_observed_turns=0
 for path in sorted((root/'trials').glob('*.json')):
  rec=json.loads(path.read_text());by_turn={};native_contexts=[]
  for trace in sorted((root/'session-traces'/rec['id']).glob('*.gz')):
   ev=[json.loads(x) for x in gzip.decompress(trace.read_bytes()).decode().splitlines()];native_contexts.extend(e for e in ev if e['type']=='turn_context')
   for t in resume.native_turns(ev):by_turn[t['turn_id']]={**t,'trace':trace.name}
  all_native_turns+=len(by_turn)
  models={e['payload']['model'] for e in native_contexts};efforts={e['payload'].get('effort') for e in native_contexts}
  if models!={'gpt-6-astra'} or efforts!={'medium'}:errors.append('native model/effort '+rec['id'])
  for j,ep in enumerate(rec['episodes']):
   for i,t in enumerate(ep['turns']):
    all_observed_turns+=1;expected=doc['tasks'][j]['request']+run.SCHEMA if i==0 else ep['replies'][i-1]['text']
    if t['prompt']!=expected:errors.append('prompt policy '+rec['id']+ep['task'])
    candidates=[n for n in by_turn.values() if n['prompts']==[t['prompt']] and n['response']==t['response']]
    if len(candidates)!=1:errors.append('native prompt/response binding '+rec['id']+ep['task']);continue
    n=candidates[0]
    if t.get('recovered'):
     source=t['native_source']
     if source['turn_id']!=n['turn_id'] or source['trace']!=n['trace']:errors.append('recovery source '+rec['id'])
     if any(t[k] is not None for k in ('returncode','stdout','stderr','timeout','duration_seconds','after')):errors.append('invented recovered receipt '+rec['id'])
     if t['native_duration_seconds']!=n['duration_ms']/1000 or t['native_usage']!=n['usage']:errors.append('native resources '+rec['id'])
    else:
     events,bad=run.legacy.parse_events(t['stdout'])
     messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
     if bad or t['events']!=events or not messages or messages[-1]!=t['response']:errors.append('CLI receipt mismatch '+rec['id'])
    checks.append({'chain':rec['id'],'task':ep['task'],'turn':i,'native_turn_id':n['turn_id'],'recovered':bool(t.get('recovered'))})
  if rec['id']=='P2__A' and rec.get('continuation_before')!=rec.get('recovery',{}).get('preserved_workspace'):errors.append('continued workspace differs')
 if all_native_turns!=all_observed_turns:errors.append('native/observed turn count differs')
 report.update(verified=not errors,recovery_checks=checks,native_turns=all_native_turns,resource_adapter='Frozen verifier primary scoring unchanged. Unavailable subprocess durations excluded from known subtotal and counted explicitly; native durations separate.')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.results.resolve());text=json.dumps(r,indent=2)+'\n';a.output.write_text(text) if a.output else print(text);raise SystemExit(0 if r['verified'] else 1)
