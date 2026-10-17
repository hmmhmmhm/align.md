#!/usr/bin/env python3
"""Run isolated Codex trials; keep private raw evidence and publish sanitized copies."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import gzip
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('A', 'B', 'C')


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def safe_path(root, name):
    path = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Unsafe fixture path: {name}')
    return path


def snapshot(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_file() and not path.is_symlink():
            data = path.read_bytes()
            result[str(path.relative_to(root))] = {'sha256': digest(data), 'bytes': len(data), 'text': data.decode('utf-8', errors='replace')}
    return result


def source_manifest(cases_path):
    paths = [cases_path, *sorted((ROOT / 'benchmarks').glob('*.py'))]
    paths += sorted((ROOT / 'skills/align').rglob('*'))
    paths += sorted((ROOT / 'benchmarks').glob('*.md'))
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name: digest(p.read_bytes()) for p in paths if p.is_file()}


def prepare_fixture(workspace, case, common, arm):
    workspace.mkdir(parents=True)
    for name, content in case['files'].items():
        path = safe_path(workspace, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if arm == 'A':
        (workspace / 'AGENTS.md').write_text(common + '\n\n' + case['criteria'])
    else:
        (workspace / 'AGENTS.md').write_text(common + '\n\nRead ALIGNS.md before work. It contains current project criteria.\n')
        (workspace / 'ALIGNS.md').write_text(case['criteria'])
    if arm == 'C':
        with (workspace / 'AGENTS.md').open('a') as handle:
            handle.write('\n' + (ROOT / 'skills/align/assets/instruction-block.md').read_text())
        shutil.copytree(ROOT / 'skills/align', workspace / '.agents/skills/align')
    return snapshot(workspace)


def clean_environment(home, codex_home):
    # No host plugin, model, API-key, shell startup, or Codex session variables.
    env = {k: os.environ[k] for k in ('PATH', 'LANG', 'LC_ALL', 'TERM') if k in os.environ}
    env.update(HOME=str(home), CODEX_HOME=str(codex_home), XDG_CONFIG_HOME=str(home / '.config'), XDG_DATA_HOME=str(home / '.local/share'))
    return env


def config_flags(effort):
    values = ['approval_policy="never"', 'sandbox_mode="workspace-write"', f'model_reasoning_effort="{effort}"',
              'web_search="disabled"', 'sandbox_workspace_write.network_access=false',
              'sandbox_workspace_write.exclude_tmpdir_env_var=true', 'sandbox_workspace_write.exclude_slash_tmp=true']
    return [part for value in values for part in ('-c', value)]


def parse_events(text):
    parsed = []
    invalid = []
    for line in text.splitlines():
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            invalid.append(line)
    return parsed, invalid


def collect_strings(value):
    if isinstance(value, str):
        return [value] if len(value) >= 16 else []
    if isinstance(value, dict):
        return [s for v in value.values() for s in collect_strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in collect_strings(v)]
    return []


def sanitize(value, replacements, secrets=()):
    if isinstance(value, str):
        for old, new in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
            value = value.replace(old, new)
        for secret in secrets:
            value = value.replace(secret, '<REDACTED_AUTH>')
        return value
    if isinstance(value, list):
        return [sanitize(v, replacements, secrets) for v in value]
    if isinstance(value, dict):
        return {sanitize(k, replacements, secrets): sanitize(v, replacements, secrets) for k, v in value.items()}
    return value


def invoke(command, env, cwd, prompt, timeout):
    start = time.monotonic()
    proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        import signal
        timed_out = True
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
    return {'command': command, 'prompt': prompt, 'stdout': stdout, 'stderr': stderr, 'returncode': proc.returncode,
            'timeout': timed_out, 'duration_seconds': round(time.monotonic() - start, 3)}


def run_trial(case, arm, repeat, args, common, auth_secrets):
    trial_id = f'{case["id"]}__{arm}__r{repeat}'
    raw_dir = args.private_output / trial_id
    raw_dir.mkdir(parents=True)
    runtime = Path(tempfile.mkdtemp(prefix='align-trial-')).resolve()
    home = runtime / 'home'
    codex_home = home / '.codex'
    codex_home.mkdir(parents=True)
    (codex_home / 'auth.json').symlink_to(args.auth)
    workspace = runtime / 'fixture'
    env = clean_environment(home, codex_home)
    replacements = {str(workspace): '<FIXTURE>', str(codex_home): '<CODEX_HOME>', str(home): '<ISOLATED_HOME>',
                    str(runtime): '<RUNTIME>', str(args.private_output): '<PRIVATE_OUTPUT>', str(ROOT): '<SOURCE_REPO>',
                    str(Path.home()): '<HOST_HOME>', str(args.codex): '<CODEX_BIN>'}
    ancestor_instructions = [str(parent / name) for parent in workspace.parents for name in ('AGENTS.md', 'AGENTS.override.md') if (parent / name).exists()]
    if ancestor_instructions:
        raise RuntimeError('Unexpected ancestor instructions: ' + repr(ancestor_instructions))
    before = prepare_fixture(workspace, case, common, arm)
    audit = invoke([str(args.codex), 'debug', 'prompt-input', '-c', f'model="{args.model}"', *config_flags(args.effort), 'Benchmark context audit; do not execute.'], env, workspace, '', 60)
    if audit['returncode']:
        raise RuntimeError('Prompt context audit failed')
    skill_names = []
    for message in json.loads(audit['stdout']):
        for content in message.get('content', []):
            text = content.get('text', '')
            if '<skills_instructions>' in text:
                skill_names.extend(re.findall(r'^- ([^:]+): ', text.split('### Available skills', 1)[-1], re.MULTILINE))
    expected_skills = {'imagegen', 'openai-docs', 'skill-creator', 'skill-installer'} | ({'align'} if arm == 'C' else set())
    if set(skill_names) != expected_skills:
        raise RuntimeError('Unexpected available skills: ' + repr(skill_names))
    audit['available_skills'] = skill_names
    audit['ancestor_instruction_files'] = ancestor_instructions
    write_json(raw_dir / 'prompt-audit.json', audit)
    write_json(args.output / 'prompt-audits' / (trial_id + '.json'), sanitize(audit, replacements, auth_secrets))
    write_json(raw_dir / 'before.json', before)
    record = {'id': trial_id, 'case_id': case['id'], 'arm': arm, 'repeat': repeat, 'status': 'running', 'turns': []}
    thread_id = None
    for i, turn in enumerate(case['turns']):
        prefix = ['--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '--json', '-m', args.model]
        if i == 0 or turn.get('new_session', False):
            command = [str(args.codex), 'exec', *prefix, '-C', str(workspace), '-s', 'workspace-write', *config_flags(args.effort), '-']
        else:
            command = [str(args.codex), 'exec', 'resume', *prefix, *config_flags(args.effort), thread_id, '-']
        result = invoke(command, env, workspace, turn['prompt'], args.timeout)
        events, invalid = parse_events(result['stdout'])
        result.update(index=i, new_session=i == 0 or turn.get('new_session', False), events=events, invalid_json_lines=invalid)
        for event in events:
            if event.get('type') == 'thread.started':
                thread_id = event['thread_id']
        result['response'] = '\n\n'.join(e['item']['text'] for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message')
        result['usage'] = [e['usage'] for e in events if e.get('type') == 'turn.completed']
        result['completed'] = any(e.get('type') == 'turn.completed' for e in events)
        result['after'] = snapshot(workspace)
        record['turns'].append(result)
        write_json(raw_dir / f'turn-{i}.json', result)
        if result['returncode'] or result['timeout'] or not result['completed']:
            record['status'] = 'runtime_failure'
            break
    if record['status'] == 'running':
        record['status'] = 'completed'
    # Session logs retain the actual model context and complete input/output evidence.
    sessions = codex_home / 'sessions'
    if sessions.exists():
        shutil.copytree(sessions, raw_dir / 'sessions')
    session_contexts = []
    for path in (raw_dir / 'sessions').rglob('*.jsonl') if (raw_dir / 'sessions').exists() else []:
        events, _ = parse_events(path.read_text())
        session_contexts.extend(e for e in events if e.get('type') in ('session_meta', 'turn_context'))
    identity_values = []
    for context in session_contexts:
        payload = context.get('payload', {})
        for key in ('creator_user_id', 'creator_account_id'):
            if payload.get(key):
                identity_values.append(payload[key])
    auth_secrets = [*auth_secrets, *identity_values]
    record['resolved_models'] = sorted({c['payload']['model'] for c in session_contexts if c.get('type') == 'turn_context'})
    record['model_verified'] = record['resolved_models'] == [args.model]
    if not record['model_verified'] and record['status'] == 'completed':
        record['status'] = 'model_verification_failure'
    record['session_contexts'] = session_contexts
    record['before'] = before
    write_json(raw_dir / 'record.json', record)
    public = sanitize(record, replacements, auth_secrets)
    write_json(args.output / 'trials' / (trial_id + '.json'), public)
    # Publish all session events with the same literal substitutions, without auth files.
    for path in (raw_dir / 'sessions').rglob('*.jsonl') if (raw_dir / 'sessions').exists() else []:
        target = args.output / 'session-traces' / trial_id / (path.name + '.gz')
        target.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(target, 'wt') as handle:
            handle.write(sanitize(path.read_text(), replacements, auth_secrets))
    shutil.rmtree(runtime)
    print(json.dumps({'trial': trial_id, 'status': record['status'], 'seconds': sum(t['duration_seconds'] for t in record['turns'])}), flush=True)
    return {'id': trial_id, 'status': record['status']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, default=ROOT / 'benchmarks/cases.json')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--private-output', type=Path, required=True)
    p.add_argument('--auth', type=Path, default=Path.home() / '.codex/auth.json')
    p.add_argument('--codex', type=Path, default=Path(shutil.which('codex') or 'codex'))
    p.add_argument('--model', default='gpt-6-astra')
    p.add_argument('--effort', choices=('low', 'medium', 'high', 'xhigh'), default='medium')
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--workers', type=int, choices=(1, 2, 3), default=3)
    p.add_argument('--timeout', type=int, default=240)
    p.add_argument('--seed', type=int, default=20261015)
    p.add_argument('--case', action='append')
    p.add_argument('--expected-source-digest', help='Require exact SHA-256 of canonical source manifest JSON before executing')
    p.add_argument('--manifest-only', action='store_true')
    args = p.parse_args()
    args.output = args.output.resolve()
    args.private_output = args.private_output.resolve()
    args.auth = args.auth.resolve()
    if args.model != 'gpt-6-astra':
        p.error('This preregistered benchmark requires gpt-6-astra; substitutions need a new protocol.')
    if args.private_output.is_relative_to(ROOT):
        p.error('Private evidence must be outside the repository.')
    cases_doc = json.loads(args.cases.read_text())
    cases = [c for c in cases_doc['cases'] if not args.case or c['id'] in args.case]
    sources = source_manifest(args.cases.resolve())
    source_hash = digest(json.dumps(sources, sort_keys=True))
    if args.expected_source_digest and source_hash != args.expected_source_digest:
        p.error(f'Source changed: expected {args.expected_source_digest}, got {source_hash}')
    if not args.manifest_only and not args.expected_source_digest:
        p.error('Execution requires --expected-source-digest from the frozen manifest.')
    order = [(case, arm, repeat) for case in cases for arm in ARMS for repeat in range(1, args.repeats + 1)]
    random.Random(args.seed).shuffle(order)
    manifest = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(), 'source_files': sources,
                'source_digest': source_hash, 'preregistered_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'cli_sha256': digest(args.codex.read_bytes()), 'model': args.model, 'reasoning_effort': args.effort,
                'cli_version': subprocess.check_output([str(args.codex), '--version'], text=True).strip(),
                'config_flags': config_flags(args.effort), 'seed': args.seed, 'repeats': args.repeats, 'workers': args.workers,
                'timeout_seconds_per_turn': args.timeout, 'retry_policy': 'none',
                'ordered_trials': [f'{c["id"]}__{a}__r{r}' for c, a, r in order],
                'sanitization': 'Literal runtime, fixture, binary, source-repo and host-home paths replaced with named placeholders; auth JSON string values of 16+ characters and session creator account/user IDs replaced if present. Gzip session traces. No other trace normalization.',
                'isolation': 'Fresh HOME and CODEX_HOME per scenario, auth-only symlink, empty inherited config, no ancestor project instructions, workspace-write sandbox, network tools disabled. OS sandbox permits reads outside fixture; held-out rubric is never supplied to the actor.'}
    if args.manifest_only:
        print(json.dumps(manifest, indent=2))
        return
    dirty_inputs = subprocess.check_output(['git', 'status', '--porcelain', '--', *sources.keys()], cwd=ROOT, text=True)
    if dirty_inputs.strip():
        p.error('Benchmark inputs must match the preregistered commit before execution.')
    if args.output.exists() or args.private_output.exists():
        p.error('Output locations must be new; failed trials are never overwritten or silently retried.')
    args.output.mkdir(parents=True)
    args.private_output.mkdir(parents=True, mode=0o700)
    write_json(args.output / 'manifest.json', manifest)
    auth_secrets = collect_strings(json.loads(args.auth.read_text()))
    outcomes = []
    run_started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_trial, c, a, r, args, cases_doc['common_instructions'], auth_secrets): f'{c["id"]}__{a}__r{r}' for c, a, r in order}
        for future in concurrent.futures.as_completed(futures):
            try:
                outcomes.append(future.result())
            except Exception as exc:
                outcomes.append({'id': futures[future], 'status': 'harness_failure', 'error': type(exc).__name__ + ': ' + str(exc)})
            write_json(args.output / 'outcomes.json', outcomes)
    final_sources = source_manifest(args.cases.resolve())
    write_json(args.output / 'source-verification.json', {'matches_start': final_sources == sources, 'final_source_files': final_sources})
    write_json(args.output / 'completion.json', {'finished_at': datetime.now(timezone.utc).isoformat(), 'wall_seconds': round(time.monotonic() - run_started, 3), 'completed_scenarios': sum(o['status'] == 'completed' for o in outcomes), 'planned_scenarios': len(order)})
    print(json.dumps({'completed': sum(o['status'] == 'completed' for o in outcomes), 'total': len(order), 'source_unchanged': final_sources == sources}))

if __name__ == '__main__':
    main()
