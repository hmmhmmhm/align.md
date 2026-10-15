import importlib.util
import unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class Protocol(unittest.TestCase):
 def setUp(self):self.p={'criteria':{'scope':'broad','audience':'newcomer'},'answers':{'scope':'Survey.','audience':'Basics.'}}
 def test_schema_does_not_leak_preferences(self):
  c=r.evaluate('{"action":"submit","scope":"nonsense"}',self.p['criteria']);reply=r.reply_for(c,self.p)
  self.assertEqual(reply['kind'],'format');self.assertEqual(reply['units'],[]);self.assertNotIn('Survey.',reply['text'])
 def test_only_mismatch_returned(self):
  import json
  c=r.evaluate(json.dumps({'action':'submit','scope':'broad','audience':'experienced','plan':'Plan','rationale':'Reason'}),self.p['criteria'])
  self.assertEqual(r.reply_for(c,self.p)['units'],['audience'])
 def test_ask_order_and_fit(self):
  c=r.evaluate('{"action":"ask","topics":["audience","scope"],"question":"Which?"}',self.p['criteria'])
  self.assertEqual(r.reply_for(c,self.p)['units'],['scope','audience']);self.assertFalse(c['fit'])
if __name__=='__main__':unittest.main()
