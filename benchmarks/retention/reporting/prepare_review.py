#!/usr/bin/env python3
"""Make condition-masked packets without modifying response text."""
import argparse,hashlib,json,random
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('results',type=Path);a=p.parse_args();root=a.results.resolve();doc=json.loads((root/'source-snapshot/benchmarks/retention/cases.json').read_text());profiles={q['id']:q for q in doc['profiles']};tasks={t['id']:t for t in doc['tasks']};packets=[];key={}
for file in sorted((root/'trials').glob('*.json')):
 rec=json.loads(file.read_text())
 for ep in rec['episodes']:
  submissions=[t['response'] for t in ep['turns'] if isinstance(t['check']['object'],dict) and t['check']['object'].get('action')=='submit']
  ident=hashlib.sha256(('retention-review-20261015:'+rec['id']+':'+ep['task']).encode()).hexdigest()[:16]
  packets.append({'id':ident,'task':tasks[ep['task']]['request'],'expected_preferences':profiles[rec['profile']]['criteria'],'confirmed_criteria':profiles[rec['profile']]['answers'],'first_submission':submissions[0] if submissions else None,'final_submission':submissions[-1] if submissions else None})
  key[ident]={'chain':rec['id'],'task':ep['task']}
random.Random(7015).shuffle(packets);out=root/'review-packets';out.mkdir(exist_ok=True)
(out/'packets.json').write_text(json.dumps(packets,indent=2)+'\n');(root/'review-key.json').write_text(json.dumps(key,indent=2)+'\n')
(out/'rubric.md').write_text('''# Condition-masked semantic review

Review only packets.json here. Each packet contains the original full response
text. Labels and execution metadata are masked; text may reveal storage choices.
Do not inspect other result files or infer a condition label. Apply this rubric
from the frozen protocol to first and final submissions separately:

- Scope passes if the plan covers one workflow for focused or at least two for broad.
- Audience passes if newcomer content teaches foundations and first use, or experienced content teaches advanced choices without an introductory teaching segment.
- Rationale passes if it explains choices without inventing user history. Confirmed criteria are supplied. A storage claim is not independently verified by these packets; mark it unverifiable, not invented, unless the text contradicts supplied evidence.
- A contradiction causes a semantic failure even when enum fields match. Missing submissions fail all three checks. Do not replace exact scores or discard any packet.

Return a JSON array of 24 records, each with id, first and final objects. Each
object has scope_pass, audience_pass, rationale_pass booleans and evidence
(a short string with actual quoted wording and explanation). Include a separate
limitations paragraph noting any clues to condition, ambiguity, or unverifiable
storage claims. This is a maintainer-run model review, not human validation.
''')
print(json.dumps({'packets':len(packets),'sha256':hashlib.sha256((out/'packets.json').read_bytes()).hexdigest()}))
