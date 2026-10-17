import importlib.util
from pathlib import Path
import unittest
HERE=Path(__file__).parent

def module(name):
 s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=module('run');verifier=module('verify')
class EvidenceTests(unittest.TestCase):
 def test_mentions_and_file_lists_do_not_count(self):
  events=[{'type':'item.completed','item':{'type':'agent_message','text':'I will use align.'}},
          {'type':'item.completed','item':{'type':'command_execution','exit_code':0,'aggregated_output':'.agents/skills/align/SKILL.md'}}]
  self.assertEqual(runner.observe_read(events),[])
 def test_only_successful_method_output_counts(self):
  item={'type':'command_execution','command':'cat .agents/skills/align/SKILL.md','exit_code':1,'aggregated_output':'# Align\n\n## Read before asking\n'}
  self.assertEqual(runner.observe_read([{'type':'item.completed','item':item}]),[])
  item['exit_code']=0
  self.assertEqual(len(runner.observe_read([{'type':'item.completed','item':item}])),1)
 def test_later_shell_failure_does_not_hide_returned_method(self):
  item={'type':'command_execution','command':'cat .agents/skills/align/SKILL.md; git status',
        'exit_code':128,'aggregated_output':'# Align\n\n## Read before asking\nfatal: not a git repository'}
  events=[{'type':'item.completed','item':item}]
  self.assertEqual(runner.observe_read(events),[])
  self.assertTrue(verifier.body_visible(events))
  item['aggregated_output']='cat: .agents/skills/align/SKILL.md: No such file'
  self.assertFalse(verifier.body_visible(events))
 def test_failures_are_not_counted_as_successful_nonreads(self):
  cases={'x':{'expected_routing':'avoid','language':'ko'}}
  records=[{'case_id':'x','completed':False,'read_evidence':[]},{'case_id':'x','completed':True,'read_evidence':[{}]}]
  r=verifier.summarize(records,cases)
  self.assertEqual(r['avoid'],{'completed':1,'read':1,'body_visible':0,'runtime_failures':1})
if __name__=='__main__':unittest.main()
