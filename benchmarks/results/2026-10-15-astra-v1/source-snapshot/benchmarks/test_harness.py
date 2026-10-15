import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

runner, grader = module('run'), module('grade')

class HarnessTests(unittest.TestCase):
    def test_fixture_arms_have_identical_criteria(self):
        doc = json.loads((HERE / 'cases.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            for arm in runner.ARMS:
                files = runner.prepare_fixture(Path(folder) / arm, doc['cases'][0], doc['common_instructions'], arm)
                self.assertEqual(grader.criteria_only(files, doc['common_instructions']), doc['cases'][0]['criteria'])
                self.assertEqual(any(p.startswith('.agents/') for p in files), arm == 'C')

    def test_fixture_cannot_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ('../secret', '/tmp/secret'):
                with self.assertRaises(ValueError):
                    runner.safe_path(Path(folder), name)

    def test_negative_check_does_not_reward_deletion(self):
        self.assertFalse(grader.check_file({'type': 'file_not_contains', 'path': 'x', 'text': 'bad'}, {}, {}))

    def test_semantic_check_remains_pending(self):
        self.assertIsNone(grader.check_file({'type': 'manual'}, {}, {}))

    def test_environment_does_not_inherit_host_credentials(self):
        env = runner.clean_environment(Path('/isolated'), Path('/isolated/.codex'))
        self.assertNotIn('OPENAI_API_KEY', env)
        self.assertNotIn('CODEX_THREAD_ID', env)
        self.assertEqual(env['HOME'], '/isolated')

    def test_sanitization_is_literal_and_recursive(self):
        raw = {'p': '/tmp/trial/work/x', 'r': ['token-value-secret', 'unaltered 1.2']}
        result = runner.sanitize(raw, {'/tmp/trial/work': '<FIXTURE>'}, ['token-value-secret'])
        self.assertEqual(result, {'p': '<FIXTURE>/x', 'r': ['<REDACTED_AUTH>', 'unaltered 1.2']})
        self.assertEqual(raw['p'], '/tmp/trial/work/x')

    def test_rule_turn_selects_earlier_state(self):
        case = {'turns': [{}, {}], 'rubric': [{'id': 'x', 'points': 1, 'turn': 0, 'check': {'type': 'file_contains', 'path': 'x', 'text': 'first'}}]}
        rec = {'before': {}, 'turns': [{'completed': True, 'after': {'x': {'text': 'first'}}}, {'completed': True, 'after': {'x': {'text': 'second'}}}]}
        self.assertEqual(grader.grade(rec, case)[0]['status'], 'pass')

    def test_failed_session_is_not_behavioral_zero(self):
        case = {'turns': [{}], 'rubric': [{'id': 'x', 'points': 1, 'check': {'type': 'file_exists', 'path': 'x'}}]}
        row = grader.grade({'before': {}, 'turns': []}, case)[0]
        self.assertEqual(row['status'], 'runtime_failure')
        self.assertIsNone(row['earned'])

if __name__ == '__main__':
    unittest.main()
