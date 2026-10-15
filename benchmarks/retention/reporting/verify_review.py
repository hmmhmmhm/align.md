#!/usr/bin/env python3
"""Reconstruct masked packets and verify complete review/quote provenance offline."""
import argparse,hashlib,json
from pathlib import Path

def verify(root):
 errors=[];doc=json.loads((root/'source-snapshot/benchmarks/retention/cases.json').read_text());profiles={p['id']:p for p in doc['profiles']};tasks={t['id']:t for t in doc['tasks']};expected={};keys={}
 for file in sorted((root/'trials').glob('*.json')):
  rec=json.loads(file.read_text())
  for ep in rec['episodes']:
   subs=[t['response'] for t in ep['turns'] if isinstance(t['check']['object'],dict) and t['check']['object'].get('action')=='submit'];ident=hashlib.sha256(('retention-review-20261015:'+rec['id']+':'+ep['task']).encode()).hexdigest()[:16]
   expected[ident]={'id':ident,'task':tasks[ep['task']]['request'],'expected_preferences':profiles[rec['profile']]['criteria'],'confirmed_criteria':profiles[rec['profile']]['answers'],'first_submission':subs[0] if subs else None,'final_submission':subs[-1] if subs else None};keys[ident]={'chain':rec['id'],'task':ep['task']}
 packets=json.loads((root/'review-packets/packets.json').read_text());actual={p['id']:p for p in packets}
 if len(packets)!=24 or actual!=expected:errors.append('packets differ from original responses')
 if json.loads((root/'review-key.json').read_text())!=keys:errors.append('packet key differs')
 manifest=json.loads((root/'review/manifest.json').read_text())
 for name,digest in manifest['sha256'].items():
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:errors.append('review source hash '+name)
 judgments=json.loads((root/'review/judgments.json').read_text());ids=[j['id'] for j in judgments]
 if len(ids)!=24 or set(ids)!=set(expected):errors.append('incomplete or duplicate judgments')
 totals={a:{'first_passes':0,'final_passes':0} for a in ('A','B')};quotes_checked=0
 for j in judgments:
  if j['id'] not in expected:continue
  arm=keys[j['id']]['chain'].split('__')[1]
  for phase in ('first','final'):
   result=j.get(phase,{});source=expected[j['id']][phase+'_submission']
   if any(type(result.get(k)) is not bool for k in ('scope_pass','audience_pass','rationale_pass')):errors.append('invalid judgment types '+j['id'])
   if not isinstance(result.get('evidence'),str) or not result['evidence'].strip():errors.append('missing evidence '+j['id'])
   quotes=result.get('quotes')
   if not isinstance(quotes,list) or not quotes:errors.append('missing quotes '+j['id']);continue
   for quote in quotes:
    if not isinstance(quote,str) or not quote or source is None or quote not in source:errors.append('quote not in source '+j['id'])
    quotes_checked+=1
   totals[arm][phase+'_passes']+=int(all(result.get(k) is True for k in ('scope_pass','audience_pass','rationale_pass')))
 return {'verified':not errors,'errors':errors,'packets':len(expected),'judgments':len(judgments),'quotes_checked':quotes_checked,'totals':totals,'scope':'Verifies packet and review provenance, schema and literal quotations; does not independently validate semantic judgments or prove reviewer model identity.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=verify(a.results.resolve());text=json.dumps(r,indent=2)+'\n';a.output.write_text(text) if a.output else print(text);raise SystemExit(0 if r['verified'] else 1)
