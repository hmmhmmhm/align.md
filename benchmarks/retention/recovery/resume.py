#!/usr/bin/env python3
"""Recover completed native receipts, then execute only untouched episodes."""
import argparse,concurrent.futures,gzip,hashlib,importlib.util,json,shutil,subprocess,tempfile,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DEFAULT=ROOT/'benchmarks/retention/results/2026-10-15-astra-v1'
MAPPING={'retention-rclw3ca5':'P1__B','retention-7qc4x8oj':'P2__B','retention-7mwaejv2':'P2__A'}

def module(root):
 s=importlib.util.spec_from_file_location('frozen_runner',root/'source-snapshot/benchmarks/retention/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def native_turns(events):
 """Return captured prompts/completions and native resource counters only."""
 meta=next(e['payload'] for e in events if e['type']=='session_meta');turns=[];active=None;previous_usage={}
 for e in events:
  p=e.get('payload',{})
  if e['type']=='event_msg' and p.get('type')=='task_started':
   if active is not None:raise ValueError('native turn lacks completion')
   active={'turn_id':p['turn_id'],'thread_id':meta['id'],'messages':[],'prompts':[],'started':e['timestamp'],'usage_total':previous_usage}
  if active is None:continue
  if e['type']=='response_item' and p.get('type')=='message':
   text=''.join(c.get('text','') for c in p.get('content',[]))
   if p.get('role')=='user' and p.get('internal_chat_message_metadata_passthrough',{}).get('content_item_kinds')==['user.text']:active['prompts'].append(text)
   if p.get('role')=='assistant' and p.get('phase')!='analysis' and p.get('channel')!='analysis':active['messages'].append(text)
  if e['type']=='event_msg' and p.get('type')=='token_count' and p.get('info'):active['usage_total']=p['info']['total_token_usage']
  if e['type']=='event_msg' and p.get('type')=='task_complete':
   if active['turn_id']!=p['turn_id']:raise ValueError('native turn id mismatch')
   active.update(response=p['last_agent_message'],duration_ms=p['duration_ms'],completed=e['timestamp'],usage={k:v-previous_usage.get(k,0) for k,v in active['usage_total'].items()})
   previous_usage=active['usage_total'];turns.append(active);active=None
 if active is not None:raise ValueError('incomplete native turn; no replacement allowed')
 return turns

def reconstruct(run,ident,runtime,doc):
 profile=next(p for p in doc['profiles'] if p['id']==ident.split('__')[0]);arm=ident.split('__')[1]
 rec={'id':ident,'profile':profile['id'],'arm':arm,'status':'recovered_complete' if arm=='B' else 'recovered_partial','before':None,'prompt_audit':None,'available_skills':None,'episodes':[], 'recovery':{'missing':['subprocess stdout','subprocess stderr','subprocess exit codes','prompt audit stdout','initial and per-turn workspace snapshots'],'preserved_workspace':run.legacy.snapshot(runtime/'fixture')}}
 contexts=[]
 for index,trace in enumerate(sorted((runtime/'home/.codex/sessions').rglob('*.jsonl'))):
  events=[json.loads(x) for x in trace.read_text().splitlines()];contexts.extend(e for e in events if e['type'] in ('session_meta','turn_context'));turns=native_turns(events);task=doc['tasks'][index]
  ep={'task':task['id'],'turns':[],'replies':[],'passed':False,'after':None}
  for i,t in enumerate(turns):
   expected=task['request']+run.SCHEMA if i==0 else ep['replies'][-1]['text']
   if t['prompts']!=[expected]:raise ValueError('recovered prompt mismatch '+ident)
   check=run.evaluate(t['response'],profile['criteria'])
   receipt={'command':None,'prompt':expected,'stdout':None,'stderr':None,'returncode':None,'timeout':None,'duration_seconds':None,'native_duration_seconds':t['duration_ms']/1000,'usage':[],'native_usage':t['usage'],'events':[{'type':'thread.started','thread_id':t['thread_id'],'reconstructed':True},{'type':'turn.completed','reconstructed':True}], 'assistant_messages':t['messages'],'response':t['response'],'after':None,'check':check,'recovered':True,'native_source':{'trace':trace.name+'.gz','turn_id':t['turn_id']}}
   ep['turns'].append(receipt)
   reply=run.reply_for(check,profile)
   if i<len(turns)-1:
    if reply is None:raise ValueError('extra native turn after pass')
    ep['replies'].append(reply)
   elif reply is None:ep['passed']=True
   else:raise ValueError('unfinished episode requires explicit recovery policy')
  rec['episodes'].append(ep)
 rec['session_contexts']=contexts;rec['resolved_models']=sorted({e['payload']['model'] for e in contexts if e['type']=='turn_context'});rec['resolved_efforts']=sorted({e['payload'].get('effort') for e in contexts if e['type']=='turn_context'})
 return rec

def publish(run,rec,runtime,args):
 ident=rec['id'];raw=args.private_output/ident;raw.mkdir(parents=True,exist_ok=True)
 contexts=[];paths=[]
 for src in (runtime/'home/.codex/sessions').rglob('*.jsonl'):
  dst=raw/src.name;shutil.copy2(src,dst);paths.append(dst);contexts.extend(e for e in map(json.loads,src.read_text().splitlines()) if e['type'] in ('session_meta','turn_context'))
 rec['session_contexts']=contexts;rec['resolved_models']=sorted({e['payload']['model'] for e in contexts if e['type']=='turn_context'});rec['resolved_efforts']=sorted({e['payload'].get('effort') for e in contexts if e['type']=='turn_context'})
 run.legacy.write_json(raw/'record.json',rec)
 replacements={str(runtime/'fixture'):'<FIXTURE>',str(runtime/'home/.codex'):'<CODEX_HOME>',str(runtime/'home'):'<ISOLATED_HOME>',str(runtime):'<RUNTIME>',str(args.private_output):'<PRIVATE_OUTPUT>',str(ROOT):'<SOURCE_REPO>',str(Path.home()):'<HOST_HOME>',str(args.codex):'<CODEX_BIN>'}
 for e in contexts:
  old=e['payload'].get('cwd')
  if old:
   oldrt=Path(old).parent;replacements.update({str(oldrt/'fixture'):'<FIXTURE>',str(oldrt/'home/.codex'):'<CODEX_HOME>',str(oldrt/'home'):'<ISOLATED_HOME>',str(oldrt):'<RUNTIME>'})
 secrets=run.legacy.collect_strings(json.loads(args.auth.read_text()))+[e['payload'][k] for e in contexts for k in ('creator_user_id','creator_account_id') if e.get('payload',{}).get(k)]
 counts=Counter();run.legacy.write_json(args.output/'trials'/(ident+'.json'),run.redactor.clean(run.legacy.sanitize(rec,replacements,secrets),counts))
 hashes=[]
 for path in paths:
  text=run.redactor.clean_jsonl(run.legacy.sanitize(path.read_text(),replacements,secrets),counts);target=args.output/'session-traces'/ident/(path.name+'.gz');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(gzip.compress(text.encode(),mtime=0));hashes.append({'file':str(target.relative_to(args.output)),'private_sha256':run.legacy.digest(path.read_bytes()),'published_sha256':run.legacy.digest(target.read_bytes())})
 run.legacy.write_json(args.output/'redactions'/(ident+'.json'),{'counts':dict(counts),'traces':hashes,'private_record_sha256':run.legacy.digest((raw/'record.json').read_bytes()),'public_record_sha256':run.legacy.digest((args.output/'trials'/(ident+'.json')).read_bytes())})


def continue_chain(run,rec,runtime,args,doc):
 profile=next(p for p in doc['profiles'] if p['id']==rec['profile']);ws=runtime/'fixture';home=runtime/'home';ch=home/'.codex';env=run.legacy.clean_environment(home,ch)
 rec['continuation_before']=run.legacy.snapshot(ws)
 if rec['continuation_before']!=rec['recovery']['preserved_workspace']:raise ValueError('continuation workspace mismatch')
 for task in doc['tasks'][len(rec['episodes']):]:
  ep={'task':task['id'],'turns':[],'replies':[],'passed':False};rec['episodes'].append(ep);thread=None;prompt=task['request']+run.SCHEMA
  for n in range(doc['max_replies']+1):
   prefix=['--ignore-user-config','--ignore-rules','--skip-git-repo-check','--json','-m','gpt-6-astra']
   cmd=([str(args.codex),'exec',*prefix,'-C',str(ws),'-s','workspace-write',*run.legacy.config_flags('medium'),'-'] if thread is None else [str(args.codex),'exec','resume',*prefix,*run.legacy.config_flags('medium'),thread,'-'])
   receipt=run.legacy.invoke(cmd,env,ws,prompt,240);events,bad=run.legacy.parse_events(receipt['stdout']);receipt.update(events=events,invalid_json_lines=bad)
   for e in events:
    if e.get('type')=='thread.started':thread=e['thread_id']
   messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
   receipt.update(assistant_messages=messages,response=messages[-1] if messages else '',after=run.legacy.snapshot(ws),usage=[e['usage'] for e in events if e.get('type')=='turn.completed']);receipt['check']=run.evaluate(receipt['response'],profile['criteria']);ep['turns'].append(receipt)
   # Persist each resumed call privately before progressing, unlike the interrupted runner.
   run.legacy.write_json(args.private_output/rec['id']/('continued-'+task['id']+'-'+str(n)+'.json'),receipt)
   if receipt['returncode'] or receipt['timeout'] or bad or not any(e.get('type')=='turn.completed' for e in events):ep['runtime_failure']=True;break
   reply=run.reply_for(receipt['check'],profile)
   if reply is None:ep['passed']=True;break
   if n==doc['max_replies']:ep['unsent_reply']=reply;break
   ep['replies'].append(reply);prompt=reply['text']
  ep['after']=run.legacy.snapshot(ws)
 rec['status']='completed_after_recovery';publish(run,rec,runtime,args);print(json.dumps({'id':rec['id'],'status':rec['status']}),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=DEFAULT);p.add_argument('--backup',type=Path,default=Path('/tmp/align-retention-private-20261015-v1/interruption'));p.add_argument('--private-output',type=Path,default=Path('/tmp/align-retention-resumed-private-20261015-v1'));p.add_argument('--execute',action='store_true');a=p.parse_args();a.output=a.output.resolve();a.backup=a.backup.resolve();a.private_output=a.private_output.resolve();a.auth=(Path.home()/'.codex/auth.json').resolve();a.codex=Path(shutil.which('codex')).resolve();run=module(a.output);doc=json.loads((a.output/'source-snapshot/benchmarks/retention/cases.json').read_text());manifest=json.loads((a.output/'manifest.json').read_text())
 for name,digest in manifest['source_files'].items():
  if run.legacy.digest((a.output/'source-snapshot'/name).read_bytes())!=digest:raise ValueError('frozen source changed')
 if run.legacy.digest(a.codex.read_bytes())!=manifest['cli_sha256']:raise ValueError('CLI binary changed')
 recovered={ident:reconstruct(run,ident,a.backup/name,doc) for name,ident in MAPPING.items()}
 plan={'original_freeze':manifest['freeze_commit'],'recovery_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recovered':{k:{'episodes':len(v['episodes']),'calls':sum(len(e['turns']) for e in v['episodes'])} for k,v in recovered.items()},'remaining_order':['P2__A',*[x for x in manifest['ordered_chains'] if x not in recovered]],'private_trace_hashes':{str(p.relative_to(a.backup)):run.legacy.digest(p.read_bytes()) for p in a.backup.rglob('*.jsonl')},'missing_receipts_policy':'null; no subprocess receipt fabricated','created_at':datetime.now(timezone.utc).isoformat()}
 if not a.execute:print(json.dumps(plan,indent=2));return
 if a.private_output.exists() or (a.output/'execution-lineage.json').exists():raise ValueError('recovery already started; do not rerun')
 dirty=subprocess.check_output(['git','status','--porcelain','--',str(Path(__file__).parent)],cwd=ROOT,text=True)
 if dirty.strip():raise ValueError('commit recovery sources before execution')
 a.private_output.mkdir(parents=True,mode=0o700);run.legacy.write_json(a.output/'execution-lineage.json',plan)
 for name,ident in MAPPING.items():
  if ident!='P2__A':publish(run,recovered[ident],a.backup/name,a)
 rt=Path(tempfile.mkdtemp(prefix='retention-resume-',dir='/tmp')).resolve();shutil.copytree(a.backup/'retention-7mwaejv2',rt,symlinks=True,dirs_exist_ok=True)
 def work(ident):
  if ident=='P2__A':continue_chain(run,recovered[ident],rt,a,doc)
  else:run.run_chain(next(q for q in doc['profiles'] if q['id']==ident.split('__')[0]),ident.split('__')[1],a,doc)
 start=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(work,plan['remaining_order']))
 run.legacy.write_json(a.output/'completion.json',{'completed_at':datetime.now(timezone.utc).isoformat(),'resumed_wall_seconds':time.monotonic()-start,'original_wall_seconds':None,'chains':manifest['ordered_chains'],'original_source_snapshot_unchanged':all(run.legacy.digest((a.output/'source-snapshot'/name).read_bytes())==d for name,d in manifest['source_files'].items())})
if __name__=='__main__':main()
