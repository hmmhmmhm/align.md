"""Synthetic offline replay and tampering tests; no model calls."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import run
import verify


def fixture():
    doc = run.smoke_document(json.loads((run.HERE / 'cases.json').read_text()))
    case = doc['cases'][0]
    row = {'id': 'NON_SCORED_SMOKE__A__r1', 'case_id': case['id'], 'arm': 'A', 'repeat': 1,
           'status': 'completed', 'turns': [], 'episodes': [], 'interventions': [],
           'session_contexts': [{'type': 'turn_context', 'payload': {'model': 'gpt-6-astra'}}],
           'resolved_models': ['gpt-6-astra'], 'metrics': {}}
    for stage in [{'id': 'setup', 'prompt': case['setup_prompt'], 'expected': None,
                   'required_questions': ['tone'], 'provided_preferences': []}, *case['episodes']]:
        responses = ['{"action":"ask","keys":["tone"]}', '{"action":"submit"}'] if stage['id'] == 'setup' else ['{"action":"submit"}']
        for followup, response in enumerate(responses):
            prompt = stage['prompt'] + run.PROTOCOL if not followup else case['setup_answers']['tone']
            events = [{'type': 'thread.started', 'thread_id': stage['id']}, {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': response}}, {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 5}}]
            with tempfile.TemporaryDirectory() as temp:
                work = Path(temp)
                if stage['expected'] is not None:
                    (work / 'output.json').write_text(json.dumps(stage['expected']))
                after, check = run.legacy.snapshot(work), run.artifact_result(work, stage['expected'])
            turn = {'episode': stage['id'], 'followup': followup, 'prompt': prompt, 'user_text': stage['prompt'] if not followup else prompt, 'stdout': '\n'.join(map(json.dumps, events)), 'events': events, 'invalid_json_lines': [], 'assistant_messages': [response], 'response': response, 'usage': [events[-1]['usage']], 'completed': True, 'new_session': not followup, 'command': ['codex', 'exec'] + (['resume', stage['id']] if followup else []), 'duration_seconds': 1.0, 'after': after, 'returncode': 0, 'timeout': False, 'artifact_check': check}
            row['turns'].append(turn)
        row['episodes'].append({'id': stage['id'], 'passed': True, 'actor_turns': len(responses), 'provided_preferences': stage['provided_preferences'], 'required_questions': stage['required_questions'], 'answered_questions': ['tone'] if stage['id'] == 'setup' else [], 'terminal_check': check})
    row['interventions'] = [{'kind': 'answer', 'text': case['setup_answers']['tone'], 'preference_units': ['tone'], 'episode': 'setup', 'repeated_preference_units': 0}]
    # Populate expected metrics once; the independent assertions below fix key costs.
    derived, _, _ = verify.replay(row, case, doc, run)
    row['metrics'] = derived['metrics']
    return row, case, doc


class ReplayTests(unittest.TestCase):
    def replay(self, row, case, doc):
        return verify.replay(row, case, doc, run)

    def test_valid_and_initial_preference_cost(self):
        row, case, doc = fixture()
        derived, errors, pending = self.replay(row, case, doc)
        self.assertEqual(errors, [])
        self.assertEqual(pending, [])
        self.assertEqual(derived['metrics']['preference_units'], 2)
        self.assertEqual(derived['metrics']['intervention_turns'], 1)
        self.assertEqual(derived['metrics']['duration_seconds'], 3)
        self.assertEqual(derived['cumulative'][-1]['preference_units'], 2)

    def test_changed_output_even_if_snapshot_hash_updated(self):
        row, case, doc = fixture()
        output = row['turns'][-1]['after']['output.json']
        output['text'] = '{"tone":"wrong","body":"Smoke only."}'
        output['sha256'] = run.legacy.digest(output['text'])
        output['bytes'] = len(output['text'].encode())
        self.assertTrue(self.replay(row, case, doc)[1])

    def test_wrong_oracle_reply(self):
        row, case, doc = fixture()
        row['interventions'][0]['text'] = 'Something easier'
        row['turns'][1]['prompt'] = 'Something easier'
        row['turns'][1]['user_text'] = 'Something easier'
        self.assertTrue(self.replay(row, case, doc)[1])

    def test_missing_task_does_not_pass(self):
        row, case, doc = fixture()
        row['turns'].pop()
        row['episodes'].pop()
        self.assertTrue(self.replay(row, case, doc)[1])

    def test_forged_units_and_required_question(self):
        row, case, doc = fixture()
        row['interventions'][0]['preference_units'] = []
        row['metrics']['preference_units'] = 1
        self.assertTrue(self.replay(row, case, doc)[1])
        row, case, doc = fixture()
        row['episodes'][0]['answered_questions'] = []
        self.assertTrue(self.replay(row, case, doc)[1])

    def test_preflight_failure_keeps_all_planned_episodes(self):
        row, case, doc = fixture()
        row.update(status='harness_failure', turns=[], episodes=[], interventions=[],
                   session_contexts=[], resolved_models=[], metrics={})
        derived, _, _ = self.replay(row, case, doc)
        row['metrics'] = derived['metrics']
        derived, errors, _ = self.replay(row, case, doc)
        self.assertEqual(errors, [])
        self.assertEqual(derived['metrics']['actor_turns'], 0)
        self.assertEqual(derived['metrics']['failed_or_missing_episodes'], 2)
        self.assertEqual(derived['metrics']['passed_episodes'], 0)

    def test_nonfinal_prose_always_needs_audit(self):
        row, case, doc = fixture()
        turn = row['turns'][0]
        turn['events'].insert(1, {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Please confirm the defaults.'}})
        turn['stdout'] = '\n'.join(map(json.dumps, turn['events']))
        turn['assistant_messages'].insert(0, 'Please confirm the defaults.')
        _, _, pending = self.replay(row, case, doc)
        self.assertEqual(len(pending), 1)


if __name__ == '__main__':
    unittest.main()
