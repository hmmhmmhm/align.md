# Skill discovery checks

Run an installed align skill against short, informal requests in English, Korean
and Japanese. Positive requests do not name the skill. Negative controls cover
ordinary fixes and other meanings of alignment. Ambiguous requests are reported
separately so a vague complaint is not automatically treated as an alignment task.

Read [the protocol](PROTOCOL.md) before running. The actor uses fresh project
folders and conversations with the authenticated local Codex CLI. Model calls
consume the account's normal usage. Fixtures and expected labels are synthetic;
the actor receives only the request and fixture files.

```sh
python3 tests/activation/run.py \
  --output tests/activation/results/new-run \
  --private-output /absolute/path/outside-the-repository/private-evidence

python3 tests/activation/run.py \
  --cases tests/activation/holdout-cases.json \
  --output tests/activation/results/new-additional-run \
  --private-output /absolute/path/outside-the-repository/additional-private-evidence
```

The runner refuses existing output directories. No trial is silently retried.
The additional wording set is maintainer-authored and must not be described as
independent validation. Both sets are frozen before their runs.

To check retained evidence without model calls:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/activation -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 tests/activation/verify.py tests/activation/results/2026-10-17-baseline --require-complete
PYTHONDONTWRITEBYTECODE=1 python3 tests/activation/verify.py tests/activation/results/2026-10-17-additional --require-complete
PYTHONDONTWRITEBYTECODE=1 python3 tests/activation/verify.py tests/activation/results/2026-10-17-regression --require-complete --require-clean-files
```

The replay checks frozen source hashes, requests, model context, skill catalog,
completion and method-output evidence. It also checks narrow file invariants.
It does not judge every response's usefulness or establish another client's
runtime behavior. Public paths are redacted; original command-output hashes
refer to private raw text before that substitution.

For loop and goal setup, stopping and completion cases, see
[the follow-up report](LOOP-GOAL-RESULTS.md) and `loop-goal-cases.json`.
The report retains the rejected description candidate as well as the final
method, and distinguishes discovery from actual runtime control.

```sh
python3 tests/activation/verify.py tests/activation/results/2026-10-17-loop-final --require-complete --require-clean-files
python3 tests/activation/verify.py tests/activation/results/2026-10-17-general-v052 --require-complete --require-clean-files
```
