#!/usr/bin/env python3
"""Deterministic tests; these tests never call an actor model."""
import json
from pathlib import Path
import tempfile
import shutil
import subprocess
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import run


class RouterTests(unittest.TestCase):
    def test_protocol_rejects_prose_unknown_duplicate_and_wrong_shape(self):
        for text in ('Okay {"action":"submit"}', '{"action":"ask","questions":[]}', '{"action":"ask","questions":["x","x"]}', '{"action":"submit","extra":1}', '[]'):
            self.assertIsNone(run.parse_response(text))
        reply = run.oracle('{"action":"ask","questions":["unknown"]}', {}, [], {}, {}, {'route_ids': [], 'unanswered_questions': ['unknown']})
        self.assertEqual(reply['kind'], 'answer')
        self.assertEqual(reply['preference_units'], [])
        self.assertEqual(reply['unmatched_questions'], ['unknown'])

    def test_batched_questions_count_all_units(self):
        routes = [{'id': 'one', 'patterns': ['tone'], 'answer': 'Plain.', 'preference_units': ['tone']},
                  {'id': 'two', 'patterns': ['contact'], 'answer': 'Email.', 'preference_units': ['contact']}]
        reply = run.route_questions(['Tone and contact?', 'Tone again?'], routes, {'route_ids': ['one', 'two'], 'unanswered_questions': []})
        self.assertEqual(reply['preference_units'], ['tone', 'contact'])
        self.assertEqual(reply['answered_routes'], ['one', 'two'])
        self.assertEqual(reply['text'], 'Plain.\nEmail.')

    def test_router_selection_rejects_unknown_ids_and_invented_questions(self):
        routes = [{'id': 'one', 'patterns': ['tone'], 'answer': 'Plain.', 'preference_units': ['tone']}]
        questions = ['Which tone?']
        for selection in ({'route_ids': ['bad'], 'unanswered_questions': []},
                          {'route_ids': ['one', 'one'], 'unanswered_questions': []},
                          {'route_ids': [], 'unanswered_questions': ['invented']},
                          {'route_ids': [], 'unanswered_questions': []}):
            self.assertIsNone(run.parse_selection(json.dumps(selection), questions, routes))
        self.assertEqual(run.request_candidates(['Could you confirm this?', 'Working.']), ['Could you confirm this?'])
        self.assertNotIn('patterns', run.router_prompt(questions, routes))
        self.assertTrue(run.router_tool_events([{'type': 'response_item', 'payload': {'type': 'function_call'}}]))
        self.assertEqual(run.router_tool_events([{'type': 'item.completed', 'item': {'type': 'agent_message'}}]), [])

    def test_classifier_is_blind_isolated_and_rejects_tool_use(self):
        with tempfile.TemporaryDirectory() as temp:
            auth = Path(temp) / 'auth.json'
            auth.write_text('{}')
            args = SimpleNamespace(auth=auth, model='gpt-6-astra', codex=Path('/fake/codex'), timeout=5)
            routes = [{'id': 'tone', 'patterns': ['secret lexical pattern'], 'answer': 'Plain.', 'preference_units': ['tone']}]
            tool_used = [False]
            def invoke(command, env, cwd, prompt, timeout):
                self.assertEqual(cwd.parent.parent, Path('/tmp').resolve())
                self.assertNotIn('secret lexical pattern', prompt)
                self.assertNotIn('AGENTS.md', prompt)
                self.assertIn('read-only', command)
                sessions = Path(env['CODEX_HOME']) / 'sessions'
                sessions.mkdir()
                (sessions / 'trace.jsonl').write_text(json.dumps({'type': 'turn_context', 'payload': {'model': args.model}}))
                events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"route_ids":["tone"],"unanswered_questions":[]}'}}, {'type': 'turn.completed', 'usage': {'input_tokens': 12}}]
                if tool_used[0]:
                    events.insert(0, {'type': 'item.completed', 'item': {'type': 'command_execution', 'command': 'ls'}})
                return {'command': command, 'prompt': prompt, 'stdout': '\n'.join(map(json.dumps, events)), 'stderr': '', 'returncode': 0, 'timeout': False, 'duration_seconds': 1.0}
            with patch.object(run.legacy, 'invoke', side_effect=invoke):
                receipt = run.classify_questions(['Which tone?'], routes, 'Write a note.', args, {})
                self.assertTrue(receipt['valid'])
                self.assertEqual(receipt['selection']['route_ids'], ['tone'])
                tool_used[0] = True
                receipt = run.classify_questions(['Which tone?'], routes, 'Write a note.', args, {})
                self.assertFalse(receipt['valid'])
                self.assertTrue(receipt['tool_events'])

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
            (root / 'output.json').write_text('{"x":1,"rationale":"Use the supplied value."}')
            self.assertTrue(run.artifact_result(root, {'x': 1})['passed'])
            (root / 'output.json').unlink()
            (root / 'other.json').write_text('{"x":1,"rationale":"Use the supplied value."}')
            (root / 'output.json').symlink_to(root / 'other.json')
            self.assertFalse(run.artifact_result(root, {'x': 1})['passed'])

    def test_json_types_are_exact(self):
        self.assertFalse(run.json_equal({'days': 14.0}, {'days': 14}))
        self.assertFalse(run.json_equal({'x': True}, {'x': 1}))
        self.assertTrue(run.json_equal({'a': 1, 'b': 2}, {'b': 2, 'a': 1}))

    def test_runtime_is_outside_instruction_bearing_log_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            log_parent = Path(temp)
            (log_parent / 'AGENTS.md').write_text('Host instructions must not enter actor context.')
            runtime = run.create_runtime()
            try:
                self.assertFalse(runtime.is_relative_to(log_parent))
                self.assertEqual(runtime.parent, Path('/tmp').resolve())
                self.assertEqual(runtime.stat().st_mode & 0o777, 0o700)
            finally:
                shutil.rmtree(runtime)

    def test_public_source_literals_excluded_only_with_verified_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            archive, stage = base / 'archive', base / 'stage'
            archive.mkdir(); stage.mkdir()
            (archive / 'scanner.py').write_text('PATH_PROBE = "/var/folders/"')
            sources = {'scanner.py': run.legacy.digest((archive / 'scanner.py').read_bytes())}
            auth = base / 'auth.json'; auth.write_text('{}')
            (stage / 'manifest.json').write_text('{}')
            audit = subprocess.run(['python3', '-B', str(run.ROOT / 'benchmarks/reporting/audit_privacy.py'), str(stage), '--private-raw', str(base / 'raw'), '--auth', str(auth)], capture_output=True)
            self.assertEqual(audit.returncode, 0)
            run.attach_verified_archive(archive, stage, sources)
            self.assertTrue(json.loads((stage / 'source-archive-verification.json').read_text())['matches_manifest'])
            (archive / 'scanner.py').write_text('tampered')
            with self.assertRaises(RuntimeError):
                run.verify_archive(archive, sources)

    def test_manifest_hashes_imports(self):
        sources = run.source_manifest(run.HERE / 'cases.json')
        for path in ('benchmarks/run.py', 'benchmarks/reporting/redact_private.py', 'benchmarks/reporting/audit_privacy.py', 'benchmarks/discovery/run.py', 'benchmarks/discovery/verify.py'):
            self.assertIn(path, sources)

    def test_shared_inputs_are_not_condition_specific(self):
        doc = json.loads((run.HERE / 'cases.json').read_text())
        self.assertEqual(set(doc['conditions']), {'A', 'B', 'C'})
        for case in doc['cases']:
            for episode in case['episodes']:
                self.assertTrue(set(episode['required_routes']) <= {r['id'] for r in episode['question_routes']})
                self.assertFalse(any(arm in episode for arm in ('A', 'B', 'C')))

    def test_no_free_retries_and_durable_notes_survive_cold_session(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            auth = base / 'auth.json'
            auth.write_text('{}')
            args = SimpleNamespace(private_output=base / 'private', staging=base / 'stage', auth=auth, model='gpt-6-astra', codex=Path('/fake/codex'), timeout=5)
            args.private_output.mkdir()
            doc = run.smoke_document({'common_instructions': 'Do the task.', 'conditions': {'A': 'Use AGENTS.md.', 'B': 'Use PREFERENCES.md.', 'C': 'Use ALIGN.md.'}, 'protocol': {'repetitions': 1}})
            doc['protocol']['max_replies_per_episode'] = 2
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
                        (cwd / 'output.json').write_text(json.dumps({**doc['cases'][0]['episodes'][1]['expected'], 'rationale': 'The saved preference says plain.'}))
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
