#!/usr/bin/env python3
"""Plan or collect PR feedback with gh. Does not infer or save preferences."""
import argparse
import json
import math
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from history_common import date_value, estimate, now, output_path, save, summary


class GitHub:
    def __init__(self):
        self.latencies = []
        self.remaining = None
        self.reset = None

    def get(self, endpoint):
        if endpoint.startswith('https://api.github.com/'):
            endpoint = endpoint[len('https://api.github.com/'):]
        if endpoint.startswith(('http:', 'https:', '/')) or '..' in endpoint:
            raise ValueError('Unexpected API pagination target')
        if self.remaining is not None and self.remaining < 1:
            raise RuntimeError(f'API quota exhausted; reset at {self.reset}')
        start = time.monotonic()
        try:
            result = subprocess.run(['gh', 'api', '--hostname', 'github.com', '--include', endpoint],
                                    text=True, capture_output=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError('GitHub request unavailable or timed out') from exc
        self.latencies.append(time.monotonic() - start)
        # Do not echo gh stderr, which may contain account or transport details.
        if result.returncode:
            raise RuntimeError('GitHub request failed; check authentication, access or rate limits. No automatic retry.')
        header, separator, body = result.stdout.replace('\r\n', '\n').partition('\n\n')
        if not separator:
            raise RuntimeError('Missing GitHub response headers')
        headers = dict((k.lower(), v.strip()) for k, v in
                       (line.split(':', 1) for line in header.splitlines() if ':' in line))
        self.remaining = int(headers['x-ratelimit-remaining']) if 'x-ratelimit-remaining' in headers else None
        self.reset = headers.get('x-ratelimit-reset')
        return json.loads(body), headers

    def pages(self, endpoint):
        seen = set()
        while endpoint:
            if endpoint in seen:
                raise RuntimeError('Repeated pagination cursor')
            seen.add(endpoint)
            rows, headers = self.get(endpoint)
            if not isinstance(rows, list):
                raise RuntimeError('Expected an API list')
            yield from rows
            endpoint = link(headers, 'next')


def link(headers, rel):
    for url, relation in re.findall(r'<([^>]+)>;\s*rel="([^"]+)"', headers.get('link', '')):
        if relation == rel:
            return url
    return None


def plan(api, repo, limit=50, rate=None):
    rows, headers = api.get(f'repos/{repo}/pulls?state=all&per_page=1&sort=created&direction=desc')
    last = link(headers, 'last')
    count = int(parse_qs(urlparse(last).query)['page'][0]) if last else len(rows)
    latency = statistics.median(api.latencies)
    choices = []
    for mode, n in [('recent', min(limit, count)), ('all', count)]:
        # One page per feedback stream is a lower bound. No hidden sample of bodies.
        minimum = math.ceil(n / 100) + n * 3
        choices.append({'mode': mode, 'prs': n, 'minimum_requests': minimum,
                        'collection_minutes': [round(minimum * latency / 60, 1),
                                               round(minimum * latency * 3 / 60, 1)],
                        'collection_basis': 'measured metadata latency; 1-3 pages per stream assumed; large PRs can exceed range',
                        'analysis_estimate': estimate(n * 6000, rate),
                        'analysis_size_basis': 'unmeasured assumption: 6,000 feedback characters per PR',
                        'quota_may_interrupt': api.remaining is not None and minimum > api.remaining})
    return {'source': 'github', 'repository': repo, 'total_prs_at_plan': count,
            'remaining_requests': api.remaining, 'quota_reset_epoch': api.reset,
            'choices': choices, 'feedback_read': False,
            'note': 'Choose sources and scope before collection. Estimates exclude quota waits; analysis is performed by the agent.'}


def select_prs(api, repo, mode, limit, since, snapshot):
    # Full collection uses creation order so old PR activity does not move pages.
    sort = 'updated' if mode == 'recent' else 'created'
    selected, seen = [], set()
    for pr in api.pages(f'repos/{repo}/pulls?state=all&per_page=100&sort={sort}&direction=desc'):
        if pr['number'] in seen:
            continue
        seen.add(pr['number'])
        if date_value(pr['created_at']) > date_value(snapshot):
            continue
        if since and date_value(pr['updated_at']) < date_value(since):
            if mode == 'recent':
                break
            continue
        selected.append({k: pr.get(k) for k in ('number', 'title', 'html_url', 'state',
                         'created_at', 'updated_at', 'merged_at') } | {'author': pr.get('user', {}).get('login')})
        if mode == 'recent' and len(selected) >= limit:
            break
    return selected


def feedback(row, stream, pr, bots):
    user = row.get('user') or {}
    login = user.get('login', '')
    if user.get('type') == 'Bot' or login.casefold() in bots or not row.get('body'):
        return None
    return {'source': stream, 'id': row.get('id'), 'url': row.get('html_url'),
            'author': login, 'is_pr_author': login == pr['author'],
            'created_at': row.get('created_at') or row.get('submitted_at'),
            'updated_at': row.get('updated_at'), 'body': row['body'],
            'path': row.get('path'), 'line': row.get('line') or row.get('original_line'),
            'reply_to': row.get('in_reply_to_id'), 'review_state': row.get('state'),
            'commit_id': row.get('commit_id'), 'diff_hunk': row.get('diff_hunk'),
            'adoption': 'unverified'}


def collect(api, repo, mode, limit, since, bots, path, resume=False, rate=None):
    config = {'repo': repo, 'mode': mode, 'limit': limit, 'since': since, 'bots': sorted(bots)}
    if path.exists():
        if not resume:
            raise ValueError('Output exists; use --resume with the same selection or choose a new path')
        report = json.loads(path.read_text())
        if report.get('config') != config or report.get('source') != 'github':
            raise ValueError('Resume selection differs from saved collection')
    else:
        if resume:
            raise ValueError('Resume output does not exist')
        report = {'source': 'github', 'config': config, 'started_at': now(),
                  'selection': None, 'items': [], 'complete': False}
    started = time.monotonic()
    report.pop('error', None)
    report.pop('_run_finished', None)
    report['complete'] = False
    try:
        if report['selection'] is None:
            report['selection'] = select_prs(api, repo, mode, limit, since, report['started_at'])
            save(path, report)
        report['selected_prs'] = len(report['selection'])
        report['completed_prs'] = len(report['items'])
        done = {item['pr']['number'] for item in report['items']}
        for pr in report['selection']:
            if pr['number'] in done:
                continue
            n = pr['number']
            entries = []
            for stream, endpoint in [('inline', f'pulls/{n}/comments'),
                                     ('reviews', f'pulls/{n}/reviews'),
                                     ('conversation', f'issues/{n}/comments')]:
                seen = set()
                for row in api.pages(f'repos/{repo}/{endpoint}?per_page=100'):
                    if row['id'] in seen:
                        continue
                    seen.add(row['id'])
                    item = feedback(row, stream, pr, bots)
                    if item:
                        entries.append(item)
            report['items'].append({'pr': pr, 'feedback': entries})
            done.add(n)
            report['completed_prs'] = len(done)
            report['selected_prs'] = len(report['selection'])
            chars = sum(len(f['body']) for item in report['items'] for f in item['feedback'])
            report['analysis_estimate'] = estimate(chars, rate)
            report['analysis_scope'] = 'collected feedback only; unresolved adoption checks are additional'
            finished_this_run = report.get('_run_finished', 0) + 1
            report['_run_finished'] = finished_this_run
            remaining = len(report['selection']) - len(done)
            seconds = (time.monotonic() - started) / finished_this_run * remaining
            report['remaining_collection_minutes'] = [round(seconds * .5 / 60, 1), round(seconds * 2 / 60, 1)]
            save(path, report)
            print(json.dumps({'completed_prs': len(done), 'selected_prs': len(report['selection']),
                              'remaining_collection_minutes': report['remaining_collection_minutes']}), file=sys.stderr)
        report['complete'] = True
    except (RuntimeError, ValueError, KeyError, KeyboardInterrupt) as exc:
        report['complete'] = False
        report['error'] = str(exc) or 'Interrupted; resume to continue'
    report.pop('_run_finished', None)
    report['finished_at'] = now()
    report['remaining_requests'] = api.remaining
    report['quota_reset_epoch'] = api.reset
    report['coverage_note'] = 'Selected PRs and all available feedback pages; live API data is not an atomic historical snapshot. Adoption needs separate diff review.'
    save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--collect', action='store_true', help='Run only after source/scope selection; otherwise print a metadata-only plan')
    parser.add_argument('--mode', choices=['recent', 'all'], default='recent')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--since', help='Include PRs updated on/after an ISO date; retain their full feedback context')
    parser.add_argument('--exclude-bot', action='append', default=[])
    parser.add_argument('--output')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--analysis-chars-per-minute', type=float)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo) or '..' in args.repo:
            raise ValueError('Use an owner/repository name on github.com')
        if args.limit < 1:
            raise ValueError('Limit must be positive')
        if args.since:
            date_value(args.since)
        estimate(0, args.analysis_chars_per_minute)
        api = GitHub()
        if not args.collect:
            if args.resume or args.output:
                raise ValueError('--output/--resume require --collect')
            result = plan(api, args.repo, args.limit, args.analysis_chars_per_minute)
        else:
            if not args.output:
                raise ValueError('--collect requires a private --output path outside Git')
            result = summary(collect(api, args.repo, args.mode, args.limit, args.since,
                             {b.casefold() for b in args.exclude_bot}, output_path(args.output),
                             args.resume, args.analysis_chars_per_minute))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('complete') is False else 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
