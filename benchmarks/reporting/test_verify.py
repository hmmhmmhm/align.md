"""Synthetic utility checks; these are not benchmark observations."""
import json
from pathlib import Path
import tempfile
import unittest
from verify import canonical, file_check, sha, totals, verify


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def file(text):
    return {'text': text, 'bytes': len(text.encode()), 'sha256': sha(text.encode())}


class ReportingTests(unittest.TestCase):
    def test_negative_check_requires_file(self):
        self.assertFalse(file_check({'type': 'file_not_contains', 'path': 'x', 'text': 'bad'}, {}, {}))

    def test_missing_grades_are_not_zero(self):
        self.assertEqual(totals([1, None], 3), {'earned': 1, 'graded': 1, 'planned': 3, 'rate_among_graded': 1.0, 'ungraded': 2})

    def test_replay_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root / 'results'
            case = {'id': '01', 'turns': [{'prompt': 'Fix x.', 'new_session': True}],
                    'rubric': [{'id': 'fixed', 'points': 1, 'check': {'type': 'file_contains', 'path': 'x', 'text': 'ok'}}]}
            write(root / 'benchmarks/cases.json', {'cases': [case]})
            sources = {'benchmarks/cases.json': sha((root / 'benchmarks/cases.json').read_bytes())}
            schedule = ['01__' + a + '__r1' for a in 'ABC']
            write(run / 'manifest.json', {'ordered_trials': schedule, 'repeats': 1, 'source_files': sources,
                'source_digest': canonical(sources), 'model': 'test-model', 'reasoning_effort': 'medium'})
            write(run / 'source-verification.json', {'matches_start': True, 'final_source_files': sources})
            write(run / 'outcomes.json', [{'id': t, 'status': 'completed'} for t in schedule])
            grades = []
            for arm, trial in zip('ABC', schedule):
                record = {'id': trial, 'case_id': '01', 'arm': arm, 'repeat': 1, 'status': 'completed',
                    'resolved_models': ['test-model'], 'session_contexts': [{'type': 'turn_context', 'payload': {'effort': 'medium'}}],
                    'before': {'x': file('bad')}, 'turns': [{'index': 0, 'prompt': 'Fix x.', 'new_session': True,
                    'duration_seconds': 2, 'completed': True, 'events': [{'type': 'thread.started', 'thread_id': trial}],
                    'usage': [{'input_tokens': 10, 'cached_input_tokens': 4, 'output_tokens': 2}], 'after': {'x': file('ok')}}]}
                write(run / 'trials' / (trial + '.json'), record)
                grades.append({'trial_id': trial, 'checks': [{'criterion': 'fixed', 'earned': 1}]})
            write(run / 'deterministic-grades.json', grades)
            report = verify(run, root=root)
            self.assertTrue(report['validation']['complete_and_consistent'])
            self.assertEqual(report['scores_by_arm']['deterministic']['A']['earned'], 1)
            self.assertEqual(report['paired_scenario_scores']['deterministic']['C_vs_A']['tie'], 1)
            self.assertEqual(report['actor_resources']['A']['tokens']['input_tokens'], 10)
            grades[0]['checks'][0]['earned'] = 0
            write(run / 'deterministic-grades.json', grades)
            self.assertIn('Deterministic replay mismatch', ' '.join(verify(run, root=root)['validation']['errors']))
            grades[0]['checks'][0]['earned'] = 1
            write(run / 'deterministic-grades.json', grades)
            archived = run / 'source-snapshot/benchmarks/cases.json'
            archived.parent.mkdir(parents=True)
            archived.write_bytes((root / 'benchmarks/cases.json').read_bytes())
            write(root / 'benchmarks/cases.json', {'cases': []})
            historical = verify(run, root=root)
            self.assertTrue(historical['validation']['complete_and_consistent'])
            self.assertEqual(historical['scores_by_arm']['deterministic']['A']['earned'], 1)
            self.assertFalse(historical['current_checkout_comparison']['matches_frozen_sources'])
            self.assertTrue(historical['reporting_provenance']['archived_source_snapshot_used'])


if __name__ == '__main__':
    unittest.main()
