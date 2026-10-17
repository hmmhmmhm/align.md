#!/usr/bin/env python3
"""Frozen, bounded initial-personalization pilot."""
import argparse, concurrent.futures, gzip, importlib.util, json, random, re, shutil, subprocess, tempfile, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
legacy=load('retention_legacy',ROOT/'benchmarks/run.py')
redactor=load('retention_redactor',ROOT/'benchmarks/reporting/redact_private.py')
COMMON='''Complete the requested work using confirmed user criteria. Ask about consequential uncertainty when needed. You may save confirmed preferences in project files and read them at the start of later tasks. Do not infer a lasting preference from an unconfirmed guess. Only workspace files persist across later fresh conversations. Do not access files outside this workspace except bundled skills and runtime tools. Do not search for benchmark sources or answers. Put all user questions in the final response interface.\n'''
SCHEMA='''\nReturn exactly one JSON object, without markdown fences. Ask using {"action":"ask","topics":["scope","audience"],"question":"your ordinary-language question"}; topics may contain scope, audience, or both, without duplicates. Submit using {"action":"submit","scope":"focused or broad","audience":"experienced or newcomer","plan":"nonempty concrete plan","rationale":"nonempty explanation of your choices"}. Use one literal allowed value per preference, not the alternatives string. focused means one worked workflow in depth; broad means a survey of at least two workflows. experienced means advanced instruction for existing users; newcomer means foundations and first-use instruction. Choose the combination suited to the user. All user questions must use the ask object; do not ask elsewhere.\n'''

def evaluate(response,criteria):
 try: obj=json.loads(response)
 except (ValueError,TypeError): obj=None
 fmt=[]
 if not isinstance(obj,dict): fmt=['response must be a JSON object']
 elif obj.get('action')=='ask':
  if set(obj)!={'action','topics','question'} or not isinstance(obj.get('topics'),list) or not obj['topics'] or any(x not in criteria for x in obj['topics']) or len(set(obj['topics']))!=len(obj['topics']) or not isinstance(obj.get('question'),str) or not obj['question'].strip(): fmt=['invalid ask schema']
 elif obj.get('action')=='submit':
  if set(obj)!={'action','scope','audience','plan','rationale'}: fmt.append('submit requires exactly action, scope, audience, plan, rationale')
  for k,values in [('scope',['focused','broad']),('audience',['experienced','newcomer'])]:
   if obj.get(k) not in values: fmt.append('invalid '+k+' enum')
  for k in ('plan','rationale'):
   if not isinstance(obj.get(k),str) or not obj[k].strip(): fmt.append(k+' must be a nonempty string')
 else: fmt=['invalid action']
 wrong=[k for k,v in criteria.items() if isinstance(obj,dict) and obj.get('action')=='submit' and obj.get(k)!=v]
 return {'object':obj,'format_errors':fmt,'wrong_preferences':wrong,'fit':not fmt and isinstance(obj,dict) and obj.get('action')=='submit' and not wrong}

def reply_for(check,profile):
 if check['format_errors']: return {'kind':'format','units':[],'text':'Correct the response schema: '+ '; '.join(check['format_errors'])+SCHEMA}
 obj=check['object']
 if obj['action']=='ask': units=[k for k in ('scope','audience') if k in obj['topics']];kind='answer'
 elif check['wrong_preferences']: units=check['wrong_preferences'];kind='preference_correction'
 else:return None
 return {'kind':kind,'units':units,'text':' '.join(profile['answers'][k] for k in units)+' These remain my confirmed defaults for later learning-material tasks. You may save them.'}

def sources():
 paths=[*HERE.glob('*.py'),HERE/'README.md',HERE/'cases.json',ROOT/'benchmarks/run.py',ROOT/'benchmarks/reporting/redact_private.py',*sorted((ROOT/'skills/align').rglob('*'))]
 return {str(p.relative_to(ROOT)):legacy.digest(p.read_bytes()) for p in sorted(paths) if p.is_file()}

def run_chain(profile,arm,args,doc):
 ident=profile['id']+'__'+arm
 runtime=Path(tempfile.mkdtemp(prefix='retention-',dir='/tmp')).resolve();home=runtime/'home';ch=home/'.codex';ch.mkdir(parents=True);(ch/'auth.json').symlink_to(args.auth)
 ws=runtime/'fixture';ws.mkdir();(ws/'AGENTS.md').write_text(COMMON)
 if arm=='B':
  (ws/'ALIGNS.md').write_text('# Confirmed learning-material preferences\n\n'+ '\n\n'.join(profile['answers'].values())+'\n\nConfirmed in prior conversation. These defaults apply to later learning-material tasks.\n\n## Revisit alignment\nPrimary client: Codex. Use the local align skill for consequential gaps. The local method is pinned for this study; do not update it.\n')
  (ws/'AGENTS.md').write_text(COMMON+'\n'+(ROOT/'skills/align/assets/instruction-block.md').read_text())
  shutil.copytree(ROOT/'skills/align',ws/'.agents/skills/align')
 raw=args.private_output/ident;raw.mkdir();record={'id':ident,'profile':profile['id'],'arm':arm,'status':'running','before':legacy.snapshot(ws),'episodes':[]}
 env=legacy.clean_environment(home,ch)
 replacements={str(ws):'<FIXTURE>',str(ch):'<CODEX_HOME>',str(home):'<ISOLATED_HOME>',str(runtime):'<RUNTIME>',str(args.private_output):'<PRIVATE_OUTPUT>',str(ROOT):'<SOURCE_REPO>',str(Path.home()):'<HOST_HOME>',str(args.codex):'<CODEX_BIN>'}
 try:
  ancestors=[str(p/n) for p in ws.parents for n in ('AGENTS.md','AGENTS.override.md') if (p/n).exists()]
  if ancestors:raise RuntimeError('ancestor instructions')
  audit=legacy.invoke([str(args.codex),'debug','prompt-input','-c','model="gpt-6-astra"',*legacy.config_flags('medium'),'Context audit only.'],env,ws,'',60)
  record['prompt_audit']=audit
  if audit['returncode']:raise RuntimeError('prompt audit failed')
  names=[]
  for message in json.loads(audit['stdout']):
   for content in message.get('content',[]):
    text=content.get('text','')
    if '<skills_instructions>' in text:names.extend(re.findall(r'^- ([^:]+): ',text.split('### Available skills',1)[-1],re.MULTILINE))
  record['available_skills']=names
  if set(names)!={'imagegen','openai-docs','skill-creator','skill-installer'}|({'align'} if arm=='B' else set()):raise RuntimeError('unexpected skills')
  for task in doc['tasks']:
   ep={'task':task['id'],'turns':[],'replies':[],'passed':False};record['episodes'].append(ep);thread=None;prompt=task['request']+SCHEMA
   for n in range(doc['max_replies']+1):
    prefix=['--ignore-user-config','--ignore-rules','--skip-git-repo-check','--json','-m','gpt-6-astra']
    cmd=([str(args.codex),'exec',*prefix,'-C',str(ws),'-s','workspace-write',*legacy.config_flags('medium'),'-'] if thread is None else [str(args.codex),'exec','resume',*prefix,*legacy.config_flags('medium'),thread,'-'])
    receipt=legacy.invoke(cmd,env,ws,prompt,240); events,bad=legacy.parse_events(receipt['stdout']);receipt.update(events=events,invalid_json_lines=bad)
    for e in events:
     if e.get('type')=='thread.started':thread=e['thread_id']
    messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
    receipt.update(assistant_messages=messages,response=messages[-1] if messages else '',after=legacy.snapshot(ws),usage=[e['usage'] for e in events if e.get('type')=='turn.completed'])
    receipt['check']=evaluate(receipt['response'],profile['criteria']);ep['turns'].append(receipt)
    if receipt['returncode'] or receipt['timeout'] or bad or not any(e.get('type')=='turn.completed' for e in events):ep['runtime_failure']=True;break
    reply=reply_for(receipt['check'],profile)
    if reply is None:ep['passed']=True;break
    if n==doc['max_replies']:ep['unsent_reply']=reply;break
    ep['replies'].append(reply);prompt=reply['text']
   ep['after']=legacy.snapshot(ws)
  record['status']='completed'
 except Exception as exc:record.update(status='harness_failure',error=type(exc).__name__+': '+str(exc))
 contexts=[];trace_paths=[]
 for path in (ch/'sessions').rglob('*.jsonl'):
  target=raw/path.name;shutil.copy2(path,target);trace_paths.append(target)
  ev,_=legacy.parse_events(path.read_text());contexts.extend(e for e in ev if e.get('type') in ('session_meta','turn_context'))
 record['session_contexts']=contexts;record['resolved_models']=sorted({e['payload']['model'] for e in contexts if e['type']=='turn_context'});record['resolved_efforts']=sorted({e['payload'].get('effort') for e in contexts if e['type']=='turn_context'})
 legacy.write_json(raw/'record.json',record)
 secrets=legacy.collect_strings(json.loads(args.auth.read_text()))+[e['payload'][k] for e in contexts for k in ('creator_user_id','creator_account_id') if e.get('payload',{}).get(k)]
 counts=Counter();public=redactor.clean(legacy.sanitize(record,replacements,secrets),counts);legacy.write_json(args.output/'trials'/(ident+'.json'),public)
 for path in trace_paths:
  clean=redactor.clean_jsonl(legacy.sanitize(path.read_text(),replacements,secrets),counts);target=args.output/'session-traces'/ident/(path.name+'.gz');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(gzip.compress(clean.encode(),mtime=0))
 legacy.write_json(args.output/'redactions'/(ident+'.json'),{'counts':dict(counts),'private_record_sha256':legacy.digest((raw/'record.json').read_bytes()),'public_record_sha256':legacy.digest((args.output/'trials'/(ident+'.json')).read_bytes())})
 shutil.rmtree(runtime);print(json.dumps({'id':ident,'status':record['status'],'passed':sum(e['passed'] for e in record['episodes']),'replies':sum(len(e['replies']) for e in record['episodes'])}),flush=True)
 return ident

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--private-output',type=Path,required=True);p.add_argument('--freeze',required=True);p.add_argument('--auth',type=Path,default=Path.home()/'.codex/auth.json');p.add_argument('--codex',type=Path,default=Path(shutil.which('codex')));a=p.parse_args()
 a.output=a.output.resolve();a.private_output=a.private_output.resolve();a.auth=a.auth.resolve();a.codex=a.codex.resolve();src=sources()
 if a.output.exists() or a.private_output.exists() or a.private_output.is_relative_to(ROOT):p.error('new output paths required; private output outside repository')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if commit!=a.freeze or subprocess.check_output(['git','status','--porcelain','--',*src],cwd=ROOT,text=True).strip():p.error('freeze must match HEAD with clean source inputs')
 a.output.mkdir(parents=True);a.private_output.mkdir(parents=True,mode=0o700)
 doc=json.loads((HERE/'cases.json').read_text());order=[(q,arm) for q in doc['profiles'] for arm in ('A','B')];random.Random(doc['seed']).shuffle(order)
 manifest={'created_at':datetime.now(timezone.utc).isoformat(),'freeze_commit':commit,'source_files':src,'ordered_chains':[q['id']+'__'+arm for q,arm in order],'model':'gpt-6-astra','effort':'medium','cli_version':subprocess.check_output([str(a.codex),'--version'],text=True).strip(),'cli_sha256':legacy.digest(a.codex.read_bytes()),'workers':3,'retry_policy':'none','setup':'authored prior conversation one reply each; B one additional modeled confirmation, not executed'}
 legacy.write_json(a.output/'manifest.json',manifest)
 for name in src:
  target=a.output/'source-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 start=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  results=list(pool.map(lambda x:run_chain(x[0],x[1],a,doc),order))
 legacy.write_json(a.output/'completion.json',{'completed_at':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'chains':results,'sources_unchanged':sources()==src})
if __name__=='__main__':main()
