# Offline evidence report

`verify.py` reads saved evidence with Python 3.9 or later and its standard library. It makes no
model calls and needs no authentication. It replays the frozen file checks,
verifies the scheduled matrix and source hashes, and reports each model
reviewer's semantic scores separately. It does not adjudicate disagreements.

This utility was written after the actor protocol freeze. Its hash appears in
the generated report. It adds no scoring criteria.

```sh
python3 benchmarks/reporting/verify.py benchmarks/results/2026-10-15-astra-v1 \
  --judges benchmarks/results/2026-10-15-astra-v1/judgments-v2 \
  --packets benchmarks/results/2026-10-15-astra-v1/review-packets-v2 \
  --require-complete \
  --output /tmp/align-evidence-report.json
```

Omit `--judges` and `--packets` to inspect actor evidence while it is arriving.
Missing results stay explicit. A nonzero exit code indicates an integrity
error; inspect the report's `pending` list as well before claiming completion.
Add `--require-complete` to make missing evidence fail the command in CI.
Use a published results revision when reproducing the report. The utility
verifies the archived `source-snapshot` and uses its cases, policies, and checks.
Later changes to the current skill are reported separately and do not invalidate
historical evidence. The earlier protocol freeze commit has neither the results
nor this reporting utility. No Git history or model access is needed offline.

The corrected review includes the shared actor instructions omitted from the
first review. To inspect that original run's integrity, replace `judgments-v2`
and `review-packets-v2` with `judgments` and `review-packets`. Its omitted context
is reported as a warning; its semantic scores are not the primary comparison.
The verifier checks that the correction added only the exact shared instructions
to the same packets before corrected judging began.

`input_tokens` includes cached input tokens. The report preserves cached
tokens as a separate field without adding them to input tokens again. Scenario
timings sum that scenario's turns; concurrent execution wall time is reported
separately. No dollar costs are inferred.

Public copies omit private reasoning records and opaque encrypted payloads.
Unredacted trace originals stay outside the repository. Observable prompts, actions, tool
outputs, replies, and usage are preserved. Each `publication-redactions.json`
lists the changed files, their original and published SHA-256 hashes, and
removal counts by category. The offline verifier checks the published hashes.
The final `privacy-audit.json` records the supplied audit script's scan of the
actor and judge publication files; it is a check for the documented patterns,
not a guarantee against every possible sensitive string.

The actor snapshot format stores file hashes and UTF-8 text with replacement
decoding. Five generated ZIP files therefore cannot be reconstructed from
their published snapshots. The verifier lists them as warnings and reports
how many text snapshots match their original hashes. The frozen checks do
not assess the contents of those ZIP files.

Run the synthetic utility tests with:

```sh
python3 -m unittest discover -s benchmarks/reporting -p 'test_*.py' -v
```

`check_quote_sources.py` independently checks each corrected review quote at
its declared packet location. CI runs it as well:

```sh
python3 benchmarks/reporting/check_quote_sources.py \
  benchmarks/results/2026-10-15-astra-v1/review-packets-v2 \
  benchmarks/results/2026-10-15-astra-v1/judgments-v2
```

Matching quoted text establishes its location, not the correctness of the
reviewer's interpretation.
