# Scattered preference evidence and transfer

This preregistered synthetic benchmark asks whether the complete ALIGNS method
helps an agent apply scattered user criteria across tasks with fewer scripted
interventions than strong persistent memory instructions. C versus separate
notes B is the primary comparison. C versus AGENTS memory A is secondary.
A tie or regression is a valid result. This experiment remains separate from
the [earlier effort pilot](../../EFFORT_BENCHMARK.md), which found a tie.

The protocol and [cases](cases.json) must be committed and publicly timestamped
before scored execution. The frozen source, public receipt, and run manifest
establish the version evaluated. Editing this working copy does not change an
already frozen run.

## Design

Two authored profiles cover community event planning and implementation plans
for an internal export service. Each profile runs under three conditions with
two repetitions: 12 trajectories and 60 episodes. All five episodes produce an
artifact, including initial setup. There are no human participants.

| Condition | Memory and instructions |
| --- | --- |
| A | Explicitly read and maintain authorized current criteria in AGENTS.md. |
| B | Explicitly read and maintain the same criteria in PREFERENCES.md. |
| C | Read ALIGNS.md and use the frozen ALIGNS skill and recurring-use method. |

A and B receive the same substantive memory instructions. Both must distinguish
confirmed criteria from assumptions, preserve the scope of exceptions, replace
criteria when directed, and ask only about consequential unresolved choices.
All conditions have the same evidence, writable project access, answer
availability, model, reasoning effort, timeouts, and reply budget. C's method
text and context cost are part of the treatment. This design cannot isolate
an effect of the filename from an effect of the method.

Each trajectory begins with three short project records containing explicit
criteria among incidental details. The standing criteria are explicit, expressed in ordinary
language without a preference-key inventory. This tests extraction from
scattered evidence, consequential clarification, and transfer. It does not
test discovering unspoken preferences. The user authorizes saving the
stated criteria. The source records remain available in every later episode;
competent agents in every condition can reread them.

| Episode | Work and measurement |
| --- | --- |
| Setup | Produce a useful plan from scattered records and resolve one consequential choice absent from those records. |
| Exception | Honor an explicitly authorized exception for one named task. |
| Transfer and change | Apply prior criteria in a different task context and save an explicit lasting change. |
| Reuse and clarification | Apply the changed criterion and resolve a newly introduced consequential choice. |
| Neutral | Complete a calculation that needs no personal criteria. |

The event profile tests access, fee limits, private rosters, allocation, and
cancellation remedies. The service profile tests dependencies, compatibility,
useful failure messages, performance, and diagnostics. A concrete venue or
implementation choice must meet both task facts and user criteria. Neutral
calculations check whether personalization adds needless questions or corrupts
a straightforward answer. Incidental ink color, a weekday, and fixture size
are not standing preferences.

Every episode starts a fresh conversation. Only the trajectory's project files
persist; transcripts and generated conversation summaries do not. Follow-up
replies within an episode keep its conversation. The environment is already
provisioned, so installation, client discovery, and method updates are outside
the measurement. Setup, preference maintenance, questions, and corrections
are included.

## Fixed simulated user

Actors ask natural-language questions through this interface:

```json
{"action":"ask","questions":["If we cancel, should attendees receive a refund or credit?"]}
```

They submit a saved `output.json` with:

```json
{"action":"submit"}
```

The actor sees task requests and source records, but not route IDs, matching
patterns, expected outputs, or the answer inventory. All questions must use
the interface, including confirmations. Questions in commentary are audited
and cannot silently disappear from the burden count.

Each episode's `question_routes` in cases.json defines a fixed answer inventory.
A separate Astra classifier receives the natural-language question, shared
task request, and available inventory, without a condition label, actor
artifact, or memory files.
It selects the answers actually requested; a batch receives the stable union.
It cannot compose new answers. Each route appears at most once in a reply. The
runtime retains the original question, classifier receipt, selected routes,
exact reply, and disclosed units. An unmatched question receives the fixed
no-information response and still consumes a reply. Broad requests for every
preference do not reveal the inventory. The frozen runtime defines classifier
settings and handling of invalid responses.

Initial engineering tests found that lexical routing mishandled paraphrases,
negation, and incidental topic mentions. Its pretest receipt remains available;
no scored actor results preceded the switch to semantic classification. Legacy
pattern fields in the cases are not the scored routing policy.

Independently authored engineering checks cover paraphrases, unrelated topics,
negation, and compound questions before the freeze. The same checks were reused
to develop and assess the semantic replacement, so they are not held-out
validation and cannot establish its general accuracy. All scored route decisions
also receive a condition-blind audit. An unresolved routing error blocks a
benefit claim; retain the affected trajectory in descriptive totals. No
maintainer may rewrite an answer or silently repair routing after seeing a
scored response. A routing change requires a new frozen version and separate
run. Classifier calls and resource costs are reported separately from actor
calls. The classifier is part of this synthetic measurement system and can
make mistakes.

Standing answers explicitly authorize saving. One-event exceptions appear in
the relevant initial request. Lasting changes appear in the next request and
explicitly replace a standing policy. The newly introduced answers become
available only in their episode. Other standing routes remain available in
later episodes, including neutral tasks, so needless questions remain visible.

At most two additional user replies are allowed per episode. Questions,
unknown requests, malformed messages, artifact corrections, and required-choice
corrections all consume this budget. A failed submission receives the fixed
correction generated by the frozen runtime. Correction text and its disclosed
preference units are public evidence. No free behavioral retry follows a
failure or timeout. A full run takes 60 to 180 actor calls, excluding separate router and
review calls.

## Quality assessment

`output.json` contains the task's concrete decision fields and a short
`rationale`. The exact checks compare the decision fields with `expected` in
the cases, require a nonempty rationale, and check that unresolved consequential
choices were asked about. The source records do not answer those required
choices. Correct guessing does not satisfy their clarification check.

Call these outcomes **bounded artifact passes**. They establish correctness
of the requested decisions and calculations, but do not establish semantic
quality of the explanation. Report first-submission and final passes, each
field failure, and protocol failures separately. First submission means the
first deliverable after any clarification, not necessarily the first turn.
Setup receives the same checks as the other episodes.

Two separate condition-blind Astra review sessions assess each submitted
artifact under the frozen [review rubric](review-rubric.md). Each reviewer
assigns two binary scores: criterion fit and useful explanation. Both must be
1 for both reviewers to count as a substantive pass. The rubric defines the
anchors and packets, including the simpler explanation needed for neutral
calculations. Reviewers receive task facts, applicable criteria, disclosed user
evidence, and the output, with treatment labels and memory filenames removed.
Keep both scores and reasons; do not resolve disagreements by choosing the
more favorable score.

Review unsupported preference invention and durable memory updates separately.
Do not interpret virtual-user cooperation, correct routing, or a model review
score as human approval. These reviewers are part of a maintainer evaluation
and use the same model family; they are not independent human validation.

## Counts and comparisons

Report all planned profile/repetition cells, including failed and capped ones.
Keep quality outcomes separate from interaction counts. For each trajectory,
record additional replies, asked questions, corrections, protocol errors,
terminal failures, supplied preference units, repeated units, and text volume.
Show setup and later episodes separately and together, with cumulative totals
after each episode. Preserve costs before a repaired submission.

A preference unit is one criterion ID supplied in a user message or the initial
project evidence. `initial_preference_units` identifies disclosures in each
initial request, including the setup files. Count each distinct unit once per
message. Batch answers may disclose several units in one reply. A reply
repeating an already supplied criterion counts as a repeated unit. Explicit
exceptions and lasting changes supplied in initial requests contribute to
total units but are not themselves repeated units; asking again about them is.
These are authored units, not a validated measure of cognitive effort.

Also publish initial user and source-file characters, reply characters,
condition-instruction characters, actor and reviewer calls, wall-clock durations,
input/output tokens when present, and tool use. Keep missing usage missing.
Do not convert token counts, questions, or simulated replies into human minutes,
satisfaction, or money saved.

The descriptive benefit rule for C versus B requires all of the following:

1. At least a 20% reduction in additional replies and at least one fewer reply
   per planned trajectory on average, including setup.
2. No increase in repeated preference units or additional replies on neutral
   episodes.
3. Every planned C episode passes bounded artifact checks and substantive
   review, with no execution failure. Every paired episode that B passes must
   also pass in C.
4. No unresolved routing error, uncounted question, hidden-answer exposure, or
   unsupported durable preference update affecting the comparison.

Use totals across the four planned trajectories per condition. Relative reply
reduction is `(R_B - R_C) / R_B`; mean reduction is `(R_B - R_C) / 4`. A zero
baseline denominator makes the relative reduction undefined and the benefit
rule unmet. Report total preference units alongside replies without turning
them into a weighted composite. C versus A uses the same rule and remains
secondary. Publish paired wins, ties, and losses and both raw totals even when
the rule fails. These thresholds are descriptive project choices, not
significance tests. There is no prespecified expectation of a positive effect.

## Freeze, failures, and public evidence

Freeze cases, protocol, runtime, verifier, tests, review rubric and tools,
routing challenge set, and full skill snapshot before scored execution. Record
the source commit and SHA-256 hashes, public timestamp receipt, model, reasoning
effort, CLI version and binary hash, settings, shuffled schedule seed, timeouts,
and retry policy. Run offline tests and a distinct smoke fixture first; never
tune scored cases after inspecting their behavior while retaining a version.

Each trajectory uses its own HOME and CODEX_HOME. Disable network access,
record session IDs, and audit fresh conversations. Keep expected outputs and
answer banks outside actor fixtures. Audit visible reads outside the fixture
and document the actual operating-system boundary; do not claim complete
filesystem isolation without evidence.

Publish prompts, initial files, answers, route receipts, all submissions,
observable traces, snapshots, timings, failures, reviewer packets and scores,
redaction manifests, and the complete planned matrix. Exclude credentials and
private reasoning. The offline verifier must recompute automatic decisions
and counts from that archive. Human or model audits remain separately labeled.

Failed cells remain in the matrix. Diagnostic reruns get distinct IDs and are
excluded from primary totals. Preserve evidence of infrastructure failures and
any later correction. Do not pool this benchmark with the earlier pilots.
Actual user effort requires a separate study with consenting people, measured
setup and maintenance time, workload, useful deliverables, and abandoned work.
