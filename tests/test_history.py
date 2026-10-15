import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/align/scripts'
sys.path.insert(0, str(SCRIPTS))
import collect_pr_feedback as prs
import collect_chat_feedback as chats
import history_common as common


def pr(number, updated='2026-10-01T00:00:00Z'):
    return {'number': number, 'title': f'PR {number}', 'user': {'login': 'owner'},
            'created_at': '2026-01-01T00:00:00Z', 'updated_at': updated,
            'html_url': f'https://github.com/test/repo/pull/{number}'}


def comment(number, author='person', kind='User', body='Keep this simple.'):
    return {'id': number, 'user': {'login': author, 'type': kind}, 'body': body,
            'html_url': f'https://github.com/test/repo/pull/1#comment-{number}'}


class FakeAPI:
    remaining = 5000
    reset = '1792000000'
    def __init__(self, rows, fail=None):
        self.rows, self.fail, self.calls = rows, fail, []
    def pages(self, endpoint):
        self.calls.append(endpoint)
        if endpoint == self.fail:
            raise RuntimeError('simulated interruption')
        if '/pulls?' in endpoint:
            yield from self.rows
        else:
            yield comment(1)


class PRTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / 'evidence.json'

    def test_all_is_not_capped_at_1000(self):
        api = FakeAPI([pr(n) for n in range(1101)])
        selected = prs.select_prs(api, 'test/repo', 'all', 50, None, common.now())
        self.assertEqual(len(selected), 1101)
        self.assertIn('sort=created', api.calls[0])

    def test_recent_deduplicates_and_limits(self):
        api = FakeAPI([pr(1), pr(1), pr(2), pr(3)])
        selected = prs.select_prs(api, 'test/repo', 'recent', 2, None, common.now())
        self.assertEqual([p['number'] for p in selected], [1, 2])
        self.assertIn('sort=updated', api.calls[0])

    def test_date_filter_checks_all_creation_order_rows(self):
        api = FakeAPI([pr(3, '2026-01-01T00:00:00Z'), pr(2), pr(1)])
        selected = prs.select_prs(api, 'test/repo', 'all', 50, '2026-09-01', common.now())
        self.assertEqual([p['number'] for p in selected], [2, 1])

    def test_pages_follows_next_and_rejects_repeated_cursor(self):
        api = prs.GitHub()
        api.get = lambda endpoint: ([comment(1)], {'link':'<repos/test/repo/comments?page=2>; rel="next"'})
        with self.assertRaisesRegex(RuntimeError, 'Repeated'):
            list(api.pages('repos/test/repo/comments?page=1'))
        pages = iter([([comment(1)], {'link':'<https://api.github.com/repos/test/repo/comments?page=2>; rel="next"'}),
                      ([comment(2)], {})])
        api.get = lambda endpoint: next(pages)
        self.assertEqual([c['id'] for c in api.pages('first')], [1, 2])

    def test_bot_matching_is_exact_and_short_human_replies_remain(self):
        p = {'author': 'owner'}
        self.assertIsNone(prs.feedback(comment(1, 'agent', 'Bot'), 'inline', p, set()))
        self.assertIsNone(prs.feedback(comment(1, 'CI'), 'inline', p, {'ci'}))
        result = prs.feedback(comment(1, 'cindy', body='No'), 'inline', p, {'ci'})
        self.assertEqual(result['body'], 'No')
        self.assertEqual(result['adoption'], 'unverified')
        self.assertTrue(prs.feedback(comment(2, 'owner'), 'inline', p, set())['is_pr_author'])

    def test_partial_resume_keeps_completed_prs_and_refetches_incomplete(self):
        failed = FakeAPI([pr(1), pr(2)], 'repos/test/repo/pulls/2/reviews?per_page=100')
        report = prs.collect(failed, 'test/repo', 'all', 50, None, set(), self.output)
        self.assertFalse(report['complete'])
        self.assertEqual(len(report['items']), 1)
        resumed = FakeAPI([])
        result = prs.collect(resumed, 'test/repo', 'all', 50, None, set(), self.output, True)
        self.assertTrue(result['complete'])
        self.assertEqual(len(result['items']), 2)
        self.assertEqual(len(resumed.calls), 3)
        self.assertTrue(all('/2/' in call for call in resumed.calls))
        with self.assertRaisesRegex(ValueError, 'selection differs'):
            prs.collect(resumed, 'test/repo', 'recent', 50, None, set(), self.output, True)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)

    def test_paginated_feedback_is_not_lost(self):
        class Many(FakeAPI):
            def pages(self, endpoint):
                if '/pulls?' in endpoint:
                    yield pr(1)
                else:
                    yield from [comment(n) for n in range(205)]
        report = prs.collect(Many([]), 'test/repo', 'all', 50, None, set(), self.output)
        self.assertEqual(len(report['items'][0]['feedback']), 615)

    def test_quota_stops_without_subprocess(self):
        api = prs.GitHub();api.remaining = 0
        with patch.object(prs.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'exhausted'):
                api.get('repos/test/repo')
            run.assert_not_called()

    def test_plan_reads_metadata_only_and_uses_actual_quota(self):
        api = prs.GitHub();api.latencies = [1];api.remaining = 25
        api.get = lambda e: ([pr(1)], {'link': '<https://api.github.com/repos/test/repo/pulls?per_page=1&page=1200>; rel="last"'})
        report = prs.plan(api, 'test/repo', 50)
        self.assertEqual(report['total_prs_at_plan'], 1200)
        self.assertFalse(report['feedback_read'])
        self.assertTrue(report['choices'][1]['quota_may_interrupt'])
        self.assertIn('unmeasured', report['choices'][0]['analysis_estimate']['basis'])

    def test_api_parses_headers_without_disclosing_stderr(self):
        api = prs.GitHub()
        response = subprocess.CompletedProcess([], 0, 'HTTP/2.0 200 OK\nX-RateLimit-Remaining: 9\n\n[]\n', '')
        with patch.object(prs.subprocess, 'run', return_value=response):
            rows, headers = api.get('repos/test/repo/pulls')
        self.assertEqual(rows, [])
        self.assertEqual(api.remaining, 9)
        with self.assertRaises(ValueError):
            api.get('https://evil.test/private')


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = (self.root / 'project');self.project.mkdir()
        self.project = self.project.resolve()

    def write(self, name, records):
        path = self.root / name
        path.write_text('\n'.join(json.dumps(row) for row in records) + '\n')
        return path

    def test_codex_project_switch_and_tool_text_exclusion(self):
        def msg(role, content):
            return {'type':'response_item','payload':{'type':'message','role':role,'content':content}}
        path = self.write('codex.jsonl', [
            {'type':'session_meta','payload':{'id':'s1','cwd':str(self.project)}},
            msg('user',[{'type':'input_text','text':'Prefer small dependencies.'}]),
            {'type':'event_msg','payload':{'type':'user_message','message':'Prefer small dependencies.'}},
            msg('assistant',[{'type':'output_text','text':'I suggest a rule.'}]),
            msg('user',[{'type':'tool_result','text':'DO NOT INCLUDE'}]),
            msg('developer',[{'type':'input_text','text':'NOT A USER PREFERENCE'}]),
            {'type':'turn_context','payload':{'cwd':'/different/project'}},
            msg('user',[{'type':'input_text','text':'PRIVATE OTHER PROJECT'}])])
        records, details = chats.read_transcript(path, self.project, 'codex')
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]['evidence_kind'], 'assistant-context-only')
        self.assertEqual(details['skipped_other_or_unknown_project'], 1)
        self.assertNotIn('PRIVATE', json.dumps(records))

    def test_claude_metadata_dedup_and_malformed_record(self):
        user = {'type':'user','cwd':str(self.project),'sessionId':'c1','uuid':'u1',
                'message':{'role':'user','content':'Keep the API stable.'}}
        path = self.write('claude.jsonl', [user, user, {**user,'uuid':'u2','isCompactSummary':True},
                    {'type':'assistant','cwd':str(self.project),'message':{'role':'assistant','content':[{'type':'thinking','thinking':'secret'}]}}])
        with path.open('a') as stream:stream.write('{bad\n')
        report = chats.collect([path], self.project, 'claude', self.root/'result.json')
        self.assertFalse(report['complete'])
        self.assertEqual(report['collected_messages'], 1)
        self.assertEqual(report['files'][0]['skipped_synthetic_messages'], 1)
        self.assertEqual((self.root/'result.json').stat().st_mode & 0o777, 0o600)

    def test_missing_scope_does_not_leak(self):
        path = self.write('unknown.jsonl',[{'type':'user','message':{'role':'user','content':'private'}}])
        records, details = chats.read_transcript(path,self.project,'claude')
        self.assertFalse(records)
        self.assertTrue(details['warnings'])

    def test_inventory_does_not_parse_bodies_and_recent_is_mtime(self):
        old = self.write('old.jsonl',[]);new = self.write('new.jsonl',[])
        old.write_text('unparseable private payload')
        os.utime(old,(100,100));os.utime(new,(200,200))
        with patch.object(Path,'open',side_effect=AssertionError('read body')):
            selected = chats.discover([],str(self.root),'recent',1,None)
        self.assertEqual(selected,[new.resolve()])

    def test_cross_file_duplicate_and_source_preservation(self):
        row = {'type':'user','cwd':str(self.project),'sessionId':'c1','uuid':'same',
               'message':{'role':'user','content':'Prefer portable tools.'}}
        a=self.write('a.jsonl',[row]);b=self.write('b.jsonl',[row])
        report=chats.collect([a,b],self.project,'claude',self.root/'out.json')
        self.assertTrue(report['complete'])
        self.assertEqual(report['collected_messages'],1)
        self.assertEqual(report['records'][0]['line'],1)

    def test_output_rejects_git_and_parent_symlink_bypass(self):
        (self.project/'.git').mkdir()
        with self.assertRaises(ValueError):common.output_path(str(self.project/'evidence.json'))
        alias=self.root/'alias';alias.symlink_to(self.project,target_is_directory=True)
        with self.assertRaises(ValueError):common.output_path(str(alias/'evidence.json'))

    def test_malformed_context_cannot_inherit_previous_project(self):
        for client in ('codex', 'claude'):
            if client == 'codex':
                rows = [
                    {'type':'session_meta','payload':{'id':'a','cwd':str(self.project)}},
                    {'type':'response_item','payload':{'type':'message','role':'user','content':'valid'}},
                    {'type':'turn_context','payload':'invalid'},
                    {'type':'response_item','payload':{'type':'message','role':'user','content':'private'}}]
            else:
                rows = [
                    {'type':'user','sessionId':'a','cwd':str(self.project),'message':{'role':'user','content':'valid'}},
                    {'type':'user','sessionId':'b','message':{'role':'user','content':'private'}}]
            path = self.write(client+'.jsonl', rows)
            records, details = chats.read_transcript(path, self.project, client)
            self.assertEqual([r['text'] for r in records], ['valid'])
            self.assertEqual(details['skipped_other_or_unknown_project'], 1)

    def test_unknown_content_reports_partial_coverage(self):
        path = self.write('unknown-shape.jsonl', [
            {'type':'session_meta','payload':{'id':'a','cwd':str(self.project)}},
            {'type':'response_item','payload':{'type':'message','role':'user','content':'valid'}},
            {'type':'response_item','payload':{'type':'message','role':'user','content':{'new_text':'missing'}}},
            {'type':'response_item','payload':'broken'},
            {'type':'response_item','payload':[]},
            {'type':'response_item','payload':''},
            {'type':'response_item','payload':None},
            {'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'tool_result','content':'omitted'}]}}])
        result = chats.collect([path], self.project, 'codex', self.root/'partial.json')
        self.assertFalse(result['complete'])
        self.assertEqual(result['files'][0]['unsupported_messages'], 5)
        self.assertEqual(result['collected_messages'], 1)

    def test_cli_plan_and_collection_work_without_network(self):
        path=self.write('session.jsonl',[{'type':'session_meta','payload':{'id':'s','cwd':str(self.project)}},
             {'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'input_text','text':'Prefer portability.'}]}}])
        base=[sys.executable,str(SCRIPTS/'collect_chat_feedback.py'),'--client','codex','--project',str(self.project),'--file',str(path)]
        planned=subprocess.run(base,text=True,capture_output=True,check=True)
        self.assertFalse(json.loads(planned.stdout)['contents_read'])
        output=self.root/'cli.json'
        done=subprocess.run(base+['--collect','--output',str(output)],text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(done.stdout)['collected_messages'],1)
        self.assertNotIn('Prefer portability',done.stdout)


if __name__ == '__main__':
    unittest.main()
