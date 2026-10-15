# Public evidence review

The corrected report supports its narrow descriptive claims. I found no
remaining blocking evidence-integrity issue in the published run. It does
not establish general reliability, reduced user effort, or an independently
replicated benefit from ALIGN.

This review was performed by a separate-context Astra agent using public
repository artifacts and GitHub receipts. It is a simulated outside-reader
review within the maintainer's evaluation, not external human or organizational
validation. I did not inspect private originals or run additional inference.
I identified the original judging-context defect and checked the correction,
so this final review also follows up on my own finding.

## Verified results

Independent calculations from trial records and corrected judge batches agree
with [the report](report.json) and [BENCHMARK.md](../../../BENCHMARK.md).

| Measure | A | B | C |
| --- | ---: | ---: | ---: |
| Objective checks | 33/33 | 33/33 | 33/33 |
| Semantic checks, judge 1 | 67/75 | 67/75 | 70/75 |
| Semantic checks, judge 2 | 70/75 | 70/75 | 74/75 |
| Combined checks, judge 1 | 100/108 | 100/108 | 103/108 |
| Combined checks, judge 2 | 103/108 | 103/108 | 107/108 |
| Fully passed scenarios, judge 1 | 30/36 | 30/36 | 31/36 |
| Fully passed scenarios, judge 2 | 31/36 | 31/36 | 35/36 |

B and A tie in all 36 paired case/repetition cells under both judges. C has
3 wins, 33 ties, and no losses against either baseline under judge 1; judge 2
records 4 wins, 32 ties, and no losses. Differences occur only in cases 04 and
06. The two judges disagree on 10 of 225 semantic checks: all nine case 04
access-explanation checks and the case 06 rehearsal check for C repetition 2.
Both judgments remain visible.

I also recomputed the per-case and per-repetition totals, request counts, token
summaries, tool counts, and scenario timings. Median scenario times are
19.0735, 18.4115, and 21.807 seconds for A, B, and C. Completed tool items are
144, 144, and 156. Request counts are 15/16/24 under judge 1 and 27/16/24 under
judge 2. These counts reflect model interpretations of requests, not measured
user effort.

## Evidence checks

All 108 scheduled trial IDs are present, with 144 completed turns and 144
actor trace files. Recomputing the seeded schedule reproduces its order.
Recorded contexts identify Astra at medium effort in every actor session;
session IDs are distinct within each scenario. The 24 corrected judge traces
also identify Astra at medium effort, with no observed tool calls.

All 16 files in [source-snapshot](source-snapshot) match both the manifest's
SHA-256 hashes and the Git blobs at `90faecb7ec00bf4065f6b53152bc4f89d7285f81`.
The [GitHub push receipt](https://github.com/hmmhmmhm/align.md/actions/runs/38656260670)
records that commit at 2026-10-14 23:47:56 UTC, before the actor manifest's
23:48:06 UTC timestamp. This checks publication ordering against the recorded
local run time; it does not authenticate provider-side execution.

I reconstructed 1,380 text snapshot hashes. Five generated ZIP snapshots
cannot reproduce their original bytes because the runner used replacement
UTF-8 decoding. Their limitation is disclosed, and the narrow file checks do
not assess ZIP contents. Published hashes in all three redaction ledgers match
the files. I cannot verify private pre-redaction bytes from public hashes alone.

Sample inspection covered trials `03__C__r1`, `04__A__r3`, `06__B__r3`,
`09__A__r2`, and `12__C__r2`, including actions, replies, and relevant file
snapshots. The samples support the reported distinctions between saved
criteria, temporary changes, local preparation, and hypothetical discussion.

## Defect and correction

The original packets removed the shared actor instructions. Judge 1 then
penalized `06__C__r1` for treating publication as prohibited, although the
actor's shared instructions explicitly prohibited publishing. That was a
material defect in the evidence supplied to judges.

Before corrected judging began, I checked every packet diff: all 108 retained
the same IDs and existing fields, adding only the exact frozen
`common_instructions` string. The
[repair push receipt](https://github.com/hmmhmmhm/align.md/actions/runs/38658653720)
is timestamped 00:12:07 UTC, before the corrected manifest at 00:12:27 UTC.
All cases were judged again, and the original context-deficient run remains
available. The false publication rationale does not recur in the corrected
case 06 judgments. No original score was silently substituted into the primary
result.

## Reproduce the checks

From the repository root, the offline report command in
[BENCHMARK.md](../../../BENCHMARK.md) reproduces `report.json` exactly. It
reports no errors or pending evidence, with five disclosed ZIP warnings.
The separate exact-source quote check is:

```sh
python3 benchmarks/reporting/check_quote_sources.py \
  benchmarks/results/2026-10-15-astra-v1/review-packets-v2 \
  benchmarks/results/2026-10-15-astra-v1/judgments-v2
```

It checks 24 batches, 450 score records, 812 evidence quotes at their declared
source paths, and 122 clarification quotes. All pass. Verbatim grounding does
not prove that a quote supports its interpretation. The unresolved case 04
disagreements illustrate that distinction.

An exact online rerun still depends on access to the recorded alpha CLI and
model alias. The public metadata does not identify immutable serving weights.
The benchmark's strong baseline, small synthetic tasks, shared model family,
and imperfect blinding limit what the observed point differences can support.
