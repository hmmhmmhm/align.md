#!/usr/bin/env python3
"""Attach selected native skill-input evidence and hash the public corpus."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(s):return hashlib.sha256(s if isinstance(s,bytes) else s.encode()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--private-output',type=Path,required=True);a=p.parse_args()
 root=a.run;native={};raw_hashes={}
 skill=(root/'source/skill/SKILL.md').read_text()
 for path in sorted((root/'trials').glob('*.json')):
  d=json.loads(path.read_text());raw=a.private_output/path.name
  private=json.loads(raw.read_text());raw_hashes[path.name]=digest(raw.read_bytes())
  workspace=private['command'][private['command'].index('-C')+1]
  for e in d['events']:
   if e.get('type')!='thread.started':continue
   for trace in (Path.home()/'.codex/sessions').rglob('*'+e['thread_id']+'*.jsonl'):
    for line in trace.read_text().splitlines():
     row=json.loads(line);q=row.get('payload',{})
     if row.get('type')!='response_item' or q.get('role')!='user':continue
     for c in q.get('content',[]):
      text=c.get('text','')
      if text.startswith('<skill>') and '<name>align</name>' in text:
       native.setdefault(d['id'],[]).append({'role':'user','text':text.replace(workspace,'<PROJECT>').replace(str(Path.home()),'<HOST_HOME>'),
          'raw_input_sha256':digest(text),'matches_frozen_skill':skill.strip() in text,'skill_sha256':digest(skill)})
 (root/'native-inputs.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
 paths=[*sorted((root/'trials').glob('*.json')),root/'native-inputs.json',root/'manifest.json',root/'completion.json',root/'outcomes.json']
 report={'files':{str(x.relative_to(root)):digest(x.read_bytes()) for x in paths},'private_raw_record_hashes':raw_hashes,
  'native_input_trials':sorted(native),'redaction':'Public trial records use the runner-defined literal path replacements. Native skill input paths are replaced with <PROJECT> and <HOST_HOME>. Raw digests describe pre-redaction text.'}
 (root/'publication.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'public_files':len(paths),'native_input_trials':len(native)}))
if __name__=='__main__':main()
