#!/usr/bin/env python3
"""Deterministic tests; these tests never call an actor model."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import run


class RouterTests(unittest.TestCase):
    def test_protocol_rejects_prose_unknown_duplicate_and_wrong_shape(self):
        for text in ('Okay {"action":"submit"}', '{"action":"ask","keys":[]}', '{"action":"ask","keys":["x","x"]}', '{"action":"submit","extra":1}', '[]'):
            self.assertIsNone(run.parse_response(text))
        reply = run.oracle('{"action":"ask","keys":["unknown"]}', {}, {'x': 'X'}, {}, {})
        self.assertEqual(reply['kind'], 'protocol_correction')

    def test_batched_questions_count_all_units(self):
        reply = run.oracle('{"action":"ask","keys":["x","y"]}', {}, {'x': 'X', 'y': 'Y'}, {}, {})
        self.assertEqual(reply['preference_units'], ['x', 'y'])
        self.assertEqual(reply['text'], 'X\nY')

    def test_partial_correction_does_not_reveal_other_answers(self):
        reply = run.oracle('{"action":"submit"}', {'passed': False, 'failed_fields': ['title']}, {}, {'title': 'NEW', 'contact': 'SECRET'}, {'title': 'heading', 'contact': 'contact'})
        self.assertEqual(reply['preference_units'], ['heading'])
        self.assertNotIn('SECRET', reply['text'])

    def test_exact_artifact_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertFalse(run.artifact_result(root, {'x': 1})['passed'])
            (root / 'output.json').write_text('{"x":1,"extra":2}')
            self.assertFalse(run.artifact_result(root, {'x': 1})['passed'])
            (root / 'output.json').write_text('{"x":1}')
            self.assertTrue(run.artifact_result(root, {'x': 1})['passed'])
            (root / 'output.json').unlink()
            (root / 'other.json').write_text('{"x":1}')
            (root / 'output.json').symlink_to(root / 'other.json')
            self.assertFalse(run.artifact_result(root, {'x': 1})['passed'])

    def test_json_types_are_exact(self):
        self.assertFalse(run.json_equal({'days': 14.0}, {'days': 14}))
        self.assertFalse(run.json_equal({'x': True}, {'x': 1}))
        self.assertTrue(run.json_equal({'a': 1, 'b': 2}, {'b': 2, 'a': 1}))

    def test_manifest_hashes_imports(self):
        sources = run.source_manifest(run.HERE / 'cases.json')
        for path in ('benchmarks/run.py', 'benchmarks/reporting/redact_private.py', 'benchmarks/reporting/audit_privacy.py', 'benchmarks/effort/run.py', 'benchmarks/effort/verify.py'):
            self.assertIn(path, sources)

    def test_shared_inputs_are_not_condition_specific(self):
        doc = json.loads((run.HERE / 'cases.json').read_text())
        self.assertEqual(set(doc['conditions']), {'A', 'B', 'C'})
        for case in doc['cases']:
            self.assertEqual(set(case['setup_answers']), set(case['setup_preferences']))
            for episode in case['episodes']:
                self.assertTrue(set(episode['required_questions']) <= set(episode['answers']))
                self.assertFalse(any(arm in episode for arm in ('A', 'B', 'C')))

    def test_no_free_retries_and_durable_notes_survive_cold_session(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            auth = base / 'auth.json'
            auth.write_text('{}')
            args = SimpleNamespace(private_output=base / 'private', staging=base / 'stage', auth=auth, model='gpt-6-astra', codex=Path('/fake/codex'), timeout=5)
            args.private_output.mkdir()
            doc = run.smoke_document(json.loads((run.HERE / 'cases.json').read_text()))
            calls = []
            def invoke(command, env, cwd, prompt, timeout):
                if 'debug' in command:
                    skills = '\n'.join('- ' + x + ': stub' for x in ('imagegen', 'openai-docs', 'skill-creator', 'skill-installer'))
                    stdout = json.dumps([{'content': [{'text': '<skills_instructions>### Available skills\n' + skills}]}])
                else:
                    calls.append(command)
                    if len(calls) == 1:
                        (cwd / 'notes.txt').write_text('persist')
                        (cwd / 'output.json').write_text('{"stale":true}')
                        response = 'malformed'
                    elif len(calls) <= 3:
                        response = 'malformed'
                    else:
                        self.assertEqual((cwd / 'notes.txt').read_text(), 'persist')
                        self.assertFalse((cwd / 'output.json').exists())
                        (cwd / 'output.json').write_text(json.dumps(doc['cases'][0]['episodes'][0]['expected']))
                        response = '{"action":"submit"}'
                    events = [{'type':'thread.started','thread_id':'thread'}, {'type':'item.completed','item':{'type':'agent_message','text':response}}, {'type':'turn.completed','usage':{}}]
                    stdout = '\n'.join(json.dumps(e) for e in events)
                return {'command':command, 'prompt':prompt, 'stdout':stdout, 'stderr':'', 'returncode':0, 'timeout':False, 'duration_seconds':0}
            with patch.object(run.legacy, 'invoke', side_effect=invoke):
                run.run_trajectory(doc['cases'][0], 'A', 1, args, doc)
            record = json.loads((args.staging / 'trials/NON_SCORED_SMOKE__A__r1.json').read_text())
            self.assertEqual(len(calls), 4)
            self.assertEqual(record['metrics']['intervention_turns'], 2)
            self.assertFalse(record['episodes'][0]['passed'])
            self.assertTrue(record['turns'][3]['new_session'])
            self.assertNotIn('resume', calls[3])

if __name__ == '__main__':
    unittest.main()
