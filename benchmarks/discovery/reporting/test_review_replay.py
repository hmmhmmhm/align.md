"""Offline archive-replay regressions added after freeze; no model calls."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n')


class ReviewArchiveReplay(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='discovery-review-regression-')
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.results, self.packets, self.reviews = base / 'actor', base / 'packets', base / 'reviews'
        archive = self.results / 'source-snapshot'
        runtime = load('test_discovery_runtime', ROOT / 'benchmarks/discovery/run.py')
        for relative in runtime.source_manifest(ROOT / 'benchmarks/discovery/cases.json'):
            target = archive / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        tiny = {'common_instructions': 'Compute the count.', 'cases': [{'id': 'fixture', 'files': {}, 'episodes': [
            {'id': 'setup', 'prompt': 'What is two plus three?', 'expected': {'count': 5}, 'question_routes': [], 'required_routes': []}]}]}
        write(archive / 'benchmarks/discovery/cases.json', tiny)
        hashes = {str(p.relative_to(archive)): hashlib.sha256(p.read_bytes()).hexdigest() for p in archive.rglob('*') if p.is_file()}
        write(self.results / 'manifest.json', {'source_files': hashes})
        action = '{"action":"submit"}'
        write(self.results / 'trials/fixture.json', {'id': 'fixture__B__r1', 'case_id': 'fixture', 'arm': 'B', 'status': 'completed', 'turns': [
            {'episode': 'setup', 'response': action, 'completed': True, 'user_text': 'What is two plus three?',
             'assistant_messages': [action], 'after': {'output.json': {'text': '{"count":5,"rationale":"Two plus three equals five."}'}}}]})
        prepare = load('test_frozen_prepare', archive / 'benchmarks/discovery/prepare_reviews.py')
        review = load('test_frozen_review', archive / 'benchmarks/discovery/review.py')
        packets, key = prepare.build_packets(self.results)
        for packet in packets:
            write(self.packets / (packet['review_id'] + '.json'), packet)
        packet_hashes = {p['review_id']: review.digest(json.dumps(p, sort_keys=True)) for p in packets}
        write(self.packets.with_name('packets-manifest.json'), {'key': key, 'packet_sha256': packet_hashes})
        seed = 20261017
        schedule = ['judge-1__case-1', 'judge-2__case-1']
        write(self.reviews / 'manifest.json', {**review.harness_manifest(), 'packet_sha256': packet_hashes,
              'model': 'gpt-6-astra', 'reasoning_effort': 'medium', 'batches': schedule, 'seed': seed})
        records = []
        for judge, batch in enumerate(schedule, start=1):
            ordered = sorted(packets, key=lambda p: p['review_id'])
            random.Random(seed + judge * 1000 + 1).shuffle(ordered)
            judgments = {'reviews': [{'review_id': p['review_id'], 'scores': [
                {'criterion': criterion, 'score': 1, 'evidence': [{'source': 'turns[0].artifact', 'quote': 'Two plus three equals five.'}], 'reason': 'The result and arithmetic agree.'}
                for criterion in sorted(review.eligible(p))], 'clarification_requests': []} for p in ordered]}
            response = json.dumps(judgments)
            events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': response}}, {'type': 'turn.completed', 'usage': {}}]
            contexts = [{'type': 'session_meta', 'payload': {'id': f'test-session-{judge}'}},
                        {'type': 'turn_context', 'payload': {'model': 'gpt-6-astra', 'effort': 'medium'}}]
            trace = self.reviews / 'session-traces' / batch / 'trace.jsonl.gz'
            trace.parent.mkdir(parents=True)
            trace.write_bytes(gzip.compress(('\n'.join(json.dumps(e) for e in contexts) + '\n').encode()))
            record = {'judge': judge, 'case_id': '1', 'prompt': review.PROMPT + json.dumps(ordered, ensure_ascii=False, indent=2),
                      'stdout': '\n'.join(json.dumps(e) for e in events) + '\n', 'events': events, 'invalid_json_lines': [],
                      'response': response, 'session_contexts': contexts, 'resolved_models': ['gpt-6-astra'], 'resolved_efforts': ['medium'],
                      'tool_items': [], 'status': 'completed', 'returncode': 0, 'timeout': False, 'judgments': judgments}
            write(self.reviews / 'batches' / (batch + '.json'), record)
            records.append(record)
        write(self.reviews / 'comparison.json', review.comparison(records, packets))
        self.verifier = load('test_frozen_review_verifier', archive / 'benchmarks/discovery/verify_reviews.py')

    def replay(self):
        return self.verifier.verify(self.results, self.packets, self.reviews)

    def test_complete_offline_archive_passes(self):
        result = self.replay()
        self.assertTrue(result['verified'], result['errors'])
        self.assertEqual(result['completed_review_batches'], 2)
        self.assertEqual(result['arms']['B']['1']['final_substantive_passes'], 1)
        self.assertEqual(result['pending'], [])

    def test_mutated_packet_rejected(self):
        path = next(self.packets.glob('*.json'))
        packet = json.loads(path.read_text())
        packet['task'] = 'A different task.'
        write(path, packet)
        result = self.replay()
        self.assertFalse(result['verified'])
        self.assertIn('Packets differ from deterministic actor evidence reconstruction', result['errors'])

    def test_duplicate_judge_identity_rejected(self):
        path = self.reviews / 'batches/judge-2__case-1.json'
        record = json.loads(path.read_text())
        record['judge'] = 1
        write(path, record)
        result = self.replay()
        self.assertFalse(result['verified'])
        self.assertTrue(any('batch identity differs' in e for e in result['errors']))


if __name__ == '__main__':
    unittest.main()
