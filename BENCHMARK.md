# Behavioral benchmark

The complete align setup gained 3 or 4 rubric points out of 108 over both
baselines in this synthetic pilot, depending on the model reviewer. The gains
came from two scenarios. Separating criteria into ALIGN.md alone produced no
score change. This small result does not establish general reliability or a
reduction in user effort.

The separate [scripted user intervention pilot](EFFORT_BENCHMARK.md) measures setup, repeated explanations, and corrections across cold sessions. Its results are not pooled with this behavioral score.

## What was compared

This maintainer-authored pilot used 12 synthetic scenarios, three conditions,
and three repetitions per condition: 108 scenario runs and 144 fresh CLI
conversations. Every condition received the same project criteria, files,
user requests, and shared rules for preserving agreements, reusing answers,
and handling unresolved decisions.
Results apply to the frozen align 0.2.0 source at commit `90faecb`, not to
later method versions.

| Condition | Setup |
| --- | --- |
| A | Criteria and ordinary operating rules in AGENTS.md; no align skill. |
| B | The same criteria in ALIGN.md, referenced neutrally from AGENTS.md; no align skill. |
| C | B plus the installed align skill and its recommended recurring-use instruction block. |

A is a strong instruction baseline. B tests separating the criteria into a
referenced file. C tests the complete maintained setup, including additional
context and invocation guidance. The design cannot isolate those components.
No score rewards a filename, a skill invocation, or the skill's preferred
document structure. The [protocol](benchmarks/README.md) and
[cases](benchmarks/cases.json) specify every check.

## Results

The corrected review is the primary result. Each condition has 33 deterministic
file checks and 75 semantic checks. Both model reviewers scored the same
semantic checks independently; their scores are retained separately.

| Condition | File checks | Semantic, judge 1 | Semantic, judge 2 | Combined, judge 1 | Combined, judge 2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A: AGENTS.md | 33/33 | 67/75 | 70/75 | 100/108 | 103/108 |
| B: separate ALIGN.md | 33/33 | 67/75 | 70/75 | 100/108 | 103/108 |
| C: maintained setup | 33/33 | 70/75 | 74/75 | 103/108 | 107/108 |

Fully passed scenarios were A 30/36, B 30/36, C 31/36 under judge 1, and
A 31/36, B 31/36, C 35/36 under judge 2. File checks are narrow facts such as
the presence of required text; passing them does not establish full task success.

Pairing each case and repetition gives the following combined-score outcomes.
Wins and losses refer to the first condition named.

| Comparison | Judge 1: wins / ties / losses | Judge 2: wins / ties / losses |
| --- | ---: | ---: |
| B versus A | 0 / 36 / 0 | 0 / 36 / 0 |
| C versus A | 3 / 33 / 0 | 4 / 32 / 0 |
| C versus B | 3 / 33 / 0 | 4 / 32 / 0 |

Only cases 04 and 06 lost points. Each row below combines three repetitions,
with nine possible points per condition. Values show judge 1 / judge 2.

| Case | A | B | C |
| --- | ---: | ---: | ---: |
| 04: prepare an archive while access remains undecided | 4 / 7 | 4 / 7 | 6 / 9 |
| 06: rehearse decisions before autonomous work | 6 / 6 | 6 / 6 | 7 / 8 |
| Each of the other ten cases | 9 / 9 | 9 / 9 | 9 / 9 |

In case 04, some A and B runs asked about access but did not make concrete
local preparation or provide a concrete preparation plan. In case 06, several
runs failed to supply two concrete hypothetical decisions on the specified
topics. C also failed this rehearsal check in one run under both reviewers,
and in another under judge 1.

The reviewers agreed on 215/225 semantic checks. Nine disagreements concerned
whether case 04 responses sufficiently explained why the access choice mattered.
The tenth concerned whether one C response supplied a second concrete rehearsal
scenario. No adjudication replaces either review.

Combined points by repetition, out of 36, were:

| Repetition | A: judge 1 / judge 2 | B: judge 1 / judge 2 | C: judge 1 / judge 2 |
| --- | ---: | ---: | ---: |
| 1 | 33 / 34 | 33 / 34 | 35 / 36 |
| 2 | 33 / 34 | 33 / 34 | 34 / 36 |
| 3 | 34 / 35 | 34 / 35 | 34 / 35 |

The [computed report](benchmarks/results/2026-10-15-astra-v1/report.json)
contains every case, repetition, denominator, and resource summary. The
[review comparison](benchmarks/results/2026-10-15-astra-v1/judgments-v2/comparison.json)
retains the disagreements, and the
[review batches](benchmarks/results/2026-10-15-astra-v1/judgments-v2/batches)
contain the exact evidence and reasons.
A [separate model-context evidence review](benchmarks/results/2026-10-15-astra-v1/external-reader-review.md)
recomputed the results and checked quotes at their declared source locations.
It is part of this maintainer evaluation, not external validation.

Reviewer counts of requests for user input were A 15, B 16, C 24 under judge 1,
and A 27, B 16, C 24 under judge 2. All were classified as consequential and
unresolved. The difference in A's counts illustrates the uncertainty in this
diagnostic. These counts do not measure real user replies or reduced user effort.

## Execution and review

The actor run used `gpt-6-astra` at medium reasoning effort through Codex CLI
`0.162.0-alpha.17.2`. All 108 scenarios completed; no failed attempt was
replaced. Each scenario had a fresh HOME and CODEX_HOME. Its later turn used a
new conversation with the scenario's files and isolated home retained.
The [cold-session audit](benchmarks/results/2026-10-15-astra-v1/cold-session-audit.json)
checked all 36 followups for distinct session IDs and no prior prompt in the
recorded initial context.

All conditions exposed the same four bundled system skills: imagegen,
openai-docs, skill-creator, and skill-installer. C also exposed align. User
configuration, personal skills, and ancestor project instructions were excluded
and checked. Web search and task network access were disabled. The OS sandbox
still allowed reads outside the fixture, so this is not a claim of complete
filesystem isolation.

Two fresh Astra reviewer sessions per case applied the semantic rubric to
packets with treatment labels withheld. Each saw nine trial packets for its
case in a separately shuffled order. Responses can reveal the approach, and
same-model errors can be correlated. These are model judgments within a
maintainer-authored evaluation, not independent external or human validation.
The [judging protocol](benchmarks/judging.md) records the prompt, schema,
evidence requirements, and disagreement policy.

## Correction to the review context

The first packet generator omitted the shared actor instructions. An evidence
review caught a concrete consequence: a reviewer treated the shared prohibition
on publication as an unsupported restriction in the autonomy rehearsal case.
The original semantic scores therefore do not provide a sound primary
comparison.

The [correction record](benchmarks/results/2026-10-15-astra-v1/context-correction.md)
adds the exact frozen shared instructions to every packet. Separate code
checks confirmed that all 108 packet IDs, rubrics, responses, file evidence,
and other fields stayed unchanged. The correction was recorded in
[commit f24ac8a](https://github.com/hmmhmmhm/align.md/commit/f24ac8a0f769e63ea64a60eb98dc9717161f920c)
before two fresh reviewers were assigned all 225 semantic checks again. The
[original reviews](benchmarks/results/2026-10-15-astra-v1/judgments) remain
available. Actor outputs and deterministic checks were not rerun or changed.
The [original-review report](benchmarks/results/2026-10-15-astra-v1/report-original-review.json)
preserves its scores with an explicit context warning; they are not mixed into
the primary totals above.
The correction's
[CI receipt](https://github.com/hmmhmmhm/align.md/actions/runs/38658653720)
was created at 2026-10-15 00:12:07 UTC. The
[corrected review manifest](benchmarks/results/2026-10-15-astra-v1/judgments-v2/manifest.json)
was created at 00:12:27 UTC.

## Resource use

Each condition contains 36 scenarios and 48 conversations. Scenario duration
is the sum of its turn durations. These descriptive figures do not establish
a general speed or cost difference.

| Condition | Median scenario seconds | Median input tokens | Median output tokens | Completed tool items |
| --- | ---: | ---: | ---: | ---: |
| A | 19.07 | 50,827.5 | 385.5 | 144 |
| B | 18.41 | 43,812.5 | 379.5 | 144 |
| C | 21.81 | 61,536.5 | 395.5 | 156 |

Token counts sum model calls across each scenario's turns; they are not peak
context lengths. Input tokens include cached input tokens; cached tokens are
not added again.
The full actor run took 857.062 seconds of wall time with three concurrent
workers. Judge calls are separate. No dollar cost is inferred from these
token counts.

## Limits

These are small synthetic tasks, many with explicit cues about the desired
decision. Their behavior categories informed skill development. Three
repetitions on one model and client cannot establish statistical significance,
long-term user benefit, fewer real user corrections, or reliability on unseen
projects. The rehearsal case is a discussion about autonomy, not an afternoon
of autonomous execution. No real users, live external actions, or other clients
were tested.

The snapshot format preserves original file hashes and UTF-8 text. Five
generated ZIP snapshots used replacement decoding, so their binary contents
cannot be reconstructed. The 1,380 text file snapshots match their recorded hashes;
the frozen checks do not assess ZIP contents.

## Inspect or reproduce

The [freeze commit](https://github.com/hmmhmmhm/align.md/commit/90faecb7ec00bf4065f6b53152bc4f89d7285f81)
preceded the scored actor run. Its
[CI receipt](https://github.com/hmmhmmhm/align.md/actions/runs/38656260670)
was created at 2026-10-14 23:47:56 UTC; the actor manifest was created at
23:48:06 UTC. The
[run manifest](benchmarks/results/2026-10-15-astra-v1/manifest.json)
records the source hashes, model identifier, CLI version and binary hash,
randomized schedule, time limit, and retry policy.

Use the published results revision for offline verification. The earlier
freeze commit does not contain the results or reporting utility. Python 3.9
or later is sufficient; no credentials, model access, or network are needed.

```sh
python3 benchmarks/reporting/verify.py benchmarks/results/2026-10-15-astra-v1 \
  --judges benchmarks/results/2026-10-15-astra-v1/judgments-v2 \
  --packets benchmarks/results/2026-10-15-astra-v1/review-packets-v2 \
  --require-complete \
  --output /tmp/align-evidence-report.json
```

The reporting utility was written after the protocol freeze. It replays the
frozen checks and verifies evidence integrity without adding scoring criteria.
All 16 frozen source files are preserved in the
[source snapshot](benchmarks/results/2026-10-15-astra-v1/source-snapshot).
Offline verification uses that archive, so future skill changes do not alter
this historical result. Current-checkout differences are reported separately.
CI runs its tests and verifies both the retained original review and the
corrected review, including the locations of quoted evidence. Passing these checks does not certify a model's interpretations
or establish a benefit from ALIGN.

An online rerun needs access to the recorded alpha CLI and model. The model
alias does not identify immutable serving weights; availability and later
outputs may differ. Offline inspection remains possible from the saved
evidence.

Public evidence omits credentials, private reasoning records, and opaque
encrypted payloads. Observable prompts, actions, tool outputs, replies, and
usage remain available. Redaction manifests retain original and published
hashes for changed files. See the
[publication policy](benchmarks/reporting/README.md) and the
[privacy scan](benchmarks/results/2026-10-15-astra-v1/privacy-audit.json)
for the exact scope of those checks.
