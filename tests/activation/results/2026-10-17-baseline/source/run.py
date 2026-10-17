#!/usr/bin/env python3
"""Run fresh installed-skill discovery trials without expected labels in actor input."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def snapshot(root):
    return {str(p.relative_to(root)): {'sha256':digest(p.read_bytes()), 'text':p.read_text(errors='replace')}
            for p in sorted(root.rglob('*')) if p.is_file() and '.agents' not in p.parts}

def observe_read(events):
    evidence=[]
    for index,e in enumerate(events):
        i=e.get('item',{})
        if e.get('type')!='item.completed' or i.get('type')!='command_execution' or i.get('exit_code')!=0:
            continue
        out=i.get('aggregated_output','')
        # Successful output must contain actual method body, not just a catalog entry or filename.
        if '# Align\n' in out and '## Read before asking' in out:
            evidence.append({'event_index':index,'command':i.get('command'),'output_sha256':digest(out)})
    return evidence

def run_case(case, repeat, args, source, common):
    ident=f'{case["id"]}__r{repeat}'
    runtime=Path(tempfile.mkdtemp(prefix='aligns-routing-')).resolve()
    workspace=runtime/'project';workspace.mkdir()
    ancestors=[str(p/n) for p in workspace.parents for n in ('AGENTS.md','AGENTS.override.md') if (p/n).exists()]
    if ancestors: raise RuntimeError('Unexpected ancestor instructions')
    shutil.copytree(source/'skill',workspace/'.agents/skills/align')
    (workspace/'AGENTS.md').write_text(common)
    for name,content in case['files'].items():
        p=workspace/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
    before=snapshot(workspace)
    command=[args.codex,'exec','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--json',
             '-m',args.model,'-C',str(workspace),'-s','workspace-write',
             '-c','approval_policy="never"','-c','model_reasoning_effort="medium"',
             '-c','web_search="disabled"','-c','sandbox_workspace_write.network_access=false','-']
    start=time.monotonic()
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    timed_out=False
    try: stdout,stderr=proc.communicate(case['prompt'],timeout=args.timeout)
    except subprocess.TimeoutExpired:
        timed_out=True;os_signal=signal.SIGTERM;__import__('os').killpg(proc.pid,os_signal)
        try:stdout,stderr=proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            __import__('os').killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate()
    events=[];invalid=[]
    for line in stdout.splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: invalid.append(line)
    completed=proc.returncode==0 and not timed_out and any(e.get('type')=='turn.completed' for e in events)
    threads=[e['thread_id'] for e in events if e.get('type')=='thread.started']
    context=[];catalog=[]
    for tid in threads:
        for p in (Path.home()/'.codex/sessions').rglob(f'*{tid}*.jsonl'):
            for line in p.read_text().splitlines():
                try:e=json.loads(line)
                except json.JSONDecodeError:continue
                payload=e.get('payload',{})
                if e.get('type')=='turn_context':
                    context.append({k:payload[k] for k in ('model','effort','cwd','approval_policy') if k in payload})
                if e.get('type')=='response_item':
                    for c in payload.get('content',[]):
                        txt=c.get('text','')
                        if '<skills_instructions>' in txt:
                            catalog.extend(re.findall(r'^- ([^\n]+?) \(file: ([^\n]+)\)$',txt,re.M))
    read=observe_read(events)
    response='\n\n'.join(e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message')
    record={'id':ident,'case_id':case['id'],'repeat':repeat,'completed':completed,'returncode':proc.returncode,
            'timeout':timed_out,'seconds':round(time.monotonic()-start,3),'command':command,'prompt':case['prompt'],
            'events':events,'invalid_json_lines':invalid,'stderr':stderr,'response':response,'read_evidence':read,
            'method_read_observed':bool(read),'before':before,'after':snapshot(workspace),'context':context,
            'catalog':sorted(set(catalog)),'usage':[e['usage'] for e in events if e.get('type')=='turn.completed']}
    write(args.private_output/(ident+'.json'),record)
    # All requests and project files are synthetic. Keep public literal path substitutions documented.
    text=json.dumps(record,ensure_ascii=False)
    for old,new in sorted({str(workspace):'<PROJECT>',str(runtime):'<RUNTIME>',str(Path.home()):'<HOST_HOME>',str(ROOT):'<SOURCE_REPO>'}.items(),key=lambda x:-len(x[0])):
        text=text.replace(old,new)
    write(args.output/'trials'/(ident+'.json'),json.loads(text))
    shutil.rmtree(runtime)
    print(json.dumps({'id':ident,'completed':completed,'read':bool(read),'seconds':record['seconds']}),flush=True)
    return {'id':ident,'completed':completed,'read':bool(read)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--private-output',type=Path,required=True)
    p.add_argument('--model',default='gpt-6-astra');p.add_argument('--repeats',type=int,default=2)
    p.add_argument('--workers',type=int,choices=(1,2,3),default=3);p.add_argument('--timeout',type=int,default=180)
    p.add_argument('--codex',default=shutil.which('codex'));p.add_argument('--case',action='append');args=p.parse_args()
    args.output=args.output.resolve();args.private_output=args.private_output.resolve()
    if args.private_output.is_relative_to(ROOT):p.error('Private output must be outside repository')
    if args.output.exists() or args.private_output.exists():p.error('Use new paths; never overwrite or silently retry trials')
    cases_doc=json.loads((HERE/'cases.json').read_text());cases=[c for c in cases_doc['cases'] if not args.case or c['id'] in args.case]
    args.output.mkdir(parents=True);args.private_output.mkdir(parents=True,mode=0o700)
    source=args.output/'source';shutil.copytree(ROOT/'skills/align',source/'skill');shutil.copy(HERE/'cases.json',source/'cases.json');shutil.copy(__file__,source/'run.py')
    hashes={str(x.relative_to(source)):digest(x.read_bytes()) for x in sorted(source.rglob('*')) if x.is_file()}
    order=[(c,r) for c in cases for r in range(1,args.repeats+1)];random.Random(20261017).shuffle(order)
    write(args.output/'manifest.json',{'started_at':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_hashes':hashes,'source_digest':digest(json.dumps(hashes,sort_keys=True)),'cli_version':subprocess.check_output([args.codex,'--version'],text=True).strip(),
        'cli_sha256':digest(Path(args.codex).read_bytes()),'model':args.model,'effort':'medium','repeats':args.repeats,'workers':args.workers,
        'timeout':args.timeout,'ordered_trials':[f'{c["id"]}__r{r}' for c,r in order],
        'isolation':'Fresh project and conversation per trial; current host authentication and installed skill catalog retained. User config and execpolicy ignored. No HOME or CODEX_HOME overrides. No ancestor project instructions. Workspace-write; network tools disabled. Expected labels never passed to actor.',
        'read_metric':'Successful command output includes # Align and ## Read before asking. Mentions and catalog presence are not sufficient. Unobserved read is not proof of non-use.',
        'retry_policy':'None; infrastructure failures remain separate.','redaction':'Literal runtime, project, source repository and host home paths replaced; no other event normalization.'})
    outcomes=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending={pool.submit(run_case,c,r,args,source,cases_doc['common_instructions']):f'{c["id"]}__r{r}' for c,r in order}
        for f in as_completed(pending):
            try:outcomes.append(f.result())
            except Exception as e:outcomes.append({'id':pending[f],'completed':False,'error':str(e)});print(str(e),flush=True)
            write(args.output/'outcomes.json',outcomes)
    write(args.output/'completion.json',{'finished_at':datetime.now(timezone.utc).isoformat(),'planned':len(order),'completed':sum(x['completed'] for x in outcomes)})

if __name__=='__main__':main()
