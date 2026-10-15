#!/usr/bin/env python3
"""Remove account-level quota/balance metadata; preserve per-call token usage."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
from collections import Counter

def clean(v,c):
 if isinstance(v,list):return [clean(x,c) for x in v]
 if isinstance(v,dict):
  result={}
  for k,x in v.items():
   if k=='rate_limits':c['account_rate_limit_fields']+=1;continue
   if k=='stdout' and isinstance(x,str):result[k]=clean_lines(x,c)
   else:result[k]=clean(x,c)
  return result
 return v

def clean_lines(text,c):
 lines=[]
 for line in text.splitlines(keepends=True):
  try:obj=json.loads(line)
  except ValueError:lines.append(line);continue
  before=sum(c.values());obj=clean(obj,c);lines.append(json.dumps(obj,ensure_ascii=False)+'\n' if sum(c.values())!=before else line)
 return ''.join(lines)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--backup',type=Path,required=True);a=p.parse_args()
 if a.backup.exists():raise SystemExit('New backup required')
 a.backup.mkdir(parents=True,mode=0o700);rows=[]
 for file in sorted(a.results.rglob('*')):
  if not file.is_file() or 'source-snapshot' in file.parts or file.suffix not in ('.json','.gz'):continue
  data=file.read_bytes();text=(gzip.decompress(data) if file.suffix=='.gz' else data).decode();c=Counter()
  new=clean_lines(text,c) if file.suffix=='.gz' else json.dumps(clean(json.loads(text),c),indent=2,ensure_ascii=False)+'\n'
  if not c:continue
  rel=file.relative_to(a.results);dest=a.backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest);encoded=gzip.compress(new.encode(),mtime=0) if file.suffix=='.gz' else new.encode();file.write_bytes(encoded)
  rows.append({'file':str(rel),'before_sha256':hashlib.sha256(data).hexdigest(),'after_sha256':hashlib.sha256(encoded).hexdigest(),'removed':dict(c)})
 (a.results/'account-metadata-redactions.json').write_text(json.dumps({'policy':'Remove account-level rate_limits including quota and balance. Preserve per-call token usage and observable actions. Originals retained privately.','files':rows},indent=2)+'\n')
 print(json.dumps({'changed_files':len(rows)}))
