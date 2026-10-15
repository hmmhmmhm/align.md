#!/usr/bin/env python3
"""Comparable native per-turn tokens, with non-additive CLI receipts separate."""
import argparse,gzip,importlib.util,json
from collections import Counter
from pathlib import Path
s=importlib.util.spec_from_file_location('recovery_resume',Path(__file__).parents[1]/'recovery/resume.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();arms={}
for arm in ('A','B'):
 native=Counter();cli_raw=Counter();dur=Counter();rows=[]
 for file in sorted((a.results/'trials').glob('*__'+arm+'.json')):
  rec=json.loads(file.read_text());recovered_ids={t['native_source']['turn_id'] for e in rec['episodes'] for t in e['turns'] if t.get('recovered')}
  for e in rec['episodes']:
   for t in e['turns']:
    if t['duration_seconds'] is not None:dur['known_subprocess_seconds']+=t['duration_seconds']
    else:dur['missing_subprocess_durations']+=1
    for u in t['usage']:cli_raw.update(u)
  for trace in sorted((a.results/'session-traces'/rec['id']).glob('*.gz')):
   events=[json.loads(line) for line in gzip.decompress(trace.read_bytes()).decode().splitlines()]
   for t in m.native_turns(events):
    native.update(t['usage']);dur['native_task_seconds_all_calls']+=t['duration_ms']/1000
    rows.append({'chain':rec['id'],'turn_id':t['turn_id'],'recovered':t['turn_id'] in recovered_ids,'native_usage_delta':t['usage'],'native_task_seconds':t['duration_ms']/1000})
 arms[arm]={'native_token_totals':dict(native),'raw_resumed_cli_usage_sum_not_additive':dict(cli_raw),'duration_observations':dict(dur),'calls':rows}
out={'method':'Native token_count cumulative session counters are differenced between successive completed turns, then summed across all sessions. Cached input is already within input tokens. CLI resume receipts may repeat prior-turn totals; their raw sum is retained for audit and is not consumed-token usage. Native task duration differs from subprocess duration; interruption prevents a full original wall-clock total.','arms':arms}
a.output.write_text(json.dumps(out,indent=2)+'\n')
