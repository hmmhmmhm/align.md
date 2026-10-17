import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location('test_discovery_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review = load('review')
prepare = load('prepare_reviews')


class ReviewTest(unittest.TestCase):
    def packet(self):
        return {'review_id': 'p1', 'runtime_status': 'completed', 'expected_turn_count': 1,
                'turns': [{'index': 0, 'completed': True, 'response': '{"action":"submit"}',
                           'assistant_messages': ['Please confirm the budget.', '{"action":"submit"}'],
                           'artifact': 'The budget is 10.'}],
                'rubric': [{'id': 'fit', 'turn': 0, 'check': {'type': 'manual'}}]}

    def judgment(self):
        return {'reviews': [{'review_id': 'p1', 'scores': [{'criterion': 'fit', 'score': 1,
            'reason': 'The supplied criterion is met.',
            'evidence': [{'source': 'turns[0].artifact', 'quote': 'budget is 10'}]}],
            'clarification_requests': [{'turn': 0, 'quote': 'Please confirm the budget.',
                'classification': 'unclear', 'reason': 'A non-final request.'}]}]}

    def test_nonfinal_question_is_retained(self):
        review.validate(self.judgment(), [self.packet()])

    def test_quote_must_match_declared_source(self):
        result = self.judgment()
        result['reviews'][0]['scores'][0]['evidence'][0]['source'] = 'turns[0].response'
        with self.assertRaises(ValueError):
            review.validate(result, [self.packet()])

    def test_missing_criterion_fails(self):
        result = self.judgment()
        result['reviews'][0]['scores'] = []
        with self.assertRaises(ValueError):
            review.validate(result, [self.packet()])

    def test_blinding_only_normalizes_note_names(self):
        self.assertEqual(prepare.blind({'text': 'AGENTS.md and ALIGNS.md say 10.'}),
                         {'text': 'project-notes.md and project-notes.md say 10.'})


if __name__ == '__main__':
    unittest.main()
