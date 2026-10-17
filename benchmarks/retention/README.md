# Preference retention pilot

This study asks whether carrying confirmed preferences into a fresh conversation
reduces the need to restate them. It compares two packages with deliberately
different information. It cannot establish that ALIGNS.md is better than another
file, a memory system, or supplying the same preferences in the task prompt.
Earlier information-equivalent benchmark results remain separate and unchanged.

## Frozen design

Four synthetic profiles cross two opposing preferences: one workflow in depth
or several workflows in a survey, and experienced or first-time audiences.
Each receives three later learning-material tasks. Every combination fits the
stated budget; no generic answer can satisfy all four profiles. There is one
repetition, yielding 24 episodes. Profiles are authored examples, not people.
The task order is workshop, guide, demo. Trajectory execution order is shuffled
with the seed in cases.json. The model is gpt-6-astra at medium reasoning effort.

A uses generic AGENTS.md and the current request. B has the same instructions
and request, plus confirmed preferences in ALIGNS.md, the maintained align skill,
and its instruction block. Both start an isolated home and workspace per profile and retain their files
across three fresh conversations. Both receive the same generic guidance and
permission to save confirmed preferences and read them in later sessions.
A can therefore learn and retain criteria from its first task. Only B starts
with confirmed personalization from the prior dialogue and the align method.
Neither receives the earlier conversation itself. Public source includes that authored conversation so the
origin of the retained criteria can be checked.

Both arms may ask about scope, audience, or both, with ordinary-language
questions accompanied by explicit topic IDs. The fixed answer inventory returns
only the requested criteria. This bounded interface avoids a separate question
classifier; it does not measure discovery of unknown topics. A wrong decision
receives the same authored preference correction in either arm: return only
the answer for each mismatching valid preference field, in scope/audience order. Each episode
allows three user replies and four actor calls, with 240 seconds per call.
No retry or replacement is allowed for a failed scored call.

Every task shows the complete response schema and all allowed values. A submit
contains scope, audience, a nonempty plan, and a nonempty rationale. Formatting
errors receive a schema reminder without revealing preferences. A valid enum
that conflicts with the profile is a preference correction. A semantically
correct enum with an empty explanation is a format/content-completeness issue,
not a preference error. Mixed errors are repaired in separate rounds, schema
first. Formatting and preference replies are counted separately.

## Outcomes

Primary descriptive outcomes are zero-reply preference fit (the first actor
response is a valid submission choosing both target preferences), first
submission preference fit after any clarification, replies to a fully valid
matching submission, and repeated criterion units. A criterion unit is one of
the two preferences supplied in a later reply; all such units repeat a criterion
from the authored prior conversation. Asking both in one message counts as one
reply and two units. A never-submitted task fails first-submission fit. Runtime
failures and budget exhaustion remain in the denominator, with replies spent
and an unresolved indicator; they are not treated as cheap successes.

These exact decision checks do not establish that the written plan actually
implements them. A separate gpt-6-astra medium reviewer receives shuffled, condition-blind first
and final submissions, expected preferences, and task text, and checks whether
plan and rationale implement both choices without contradicting them. Report
its results separately, retaining reasons and disagreements with exact checks.
The frozen rubric requires the plan to cover one workflow for focused or at
least two for broad, and introductory content for newcomer or advanced content
without an introductory teaching segment for experienced. A rationale must
explain the choices without inventing user history. Report each criterion and
rationale as pass/fail with an evidence quote. A contradiction causes a semantic
fail even if enum fields match. Exact and semantic outcomes remain separate;
no adjudication replaces either. No aggregate quality or benefit claim is
permitted if substantive contradictions remain unresolved. The reviewer is a maintainer-run model, not external human
validation. Any accidental exposure of conditions must be disclosed.

Report every paired profile and task, cumulative later replies, and all failures.
No significance test or population effect is claimed from this pilot. There is
no threshold chosen to declare victory. More zero-reply fit with fewer repeated
criteria describes this synthetic retention package only.

## Setup and payback

The authored prior preference conversation contains one user reply in both
workflows and is a common sunk cost. B additionally models one confirmation
reply approving storage. Files are built deterministically from that confirmed
text; no model elicitation or installation session is executed. Report this
assumed one-reply incremental setup cost separately from observed later replies,
and show cumulative totals with it included. Also report payback sensitivity
for zero through three assumed setup replies. Payback is the first later-task
index where cumulative saved replies meet or exceed that assumed cost, per
profile and pooled (four times the per-profile setup cost). If any episode is
unresolved, report payback as indeterminate for that profile and the pool. Do not convert replies, characters, tokens, or model runtime
into minutes of human effort. Installation, reading, maintenance, and abandoned
work are unmeasured.

## Execution and verification

Commit and push protocol, cases, runner, verifier, and all imported source
before scored execution. The runner requires clean frozen inputs, records the
commit and SHA-256 hashes, and keeps a copy of the source. Fresh HOME and
CODEX_HOME use only an auth symlink; host settings and ancestor instructions are
excluded. Tool/network settings follow the existing CLI harness. This is not a
complete filesystem security boundary. Archive public prompts, all responses,
tool outputs, session traces, scripted replies, model identity, resource receipts,
and failures, with credential/identity/path redaction and private reasoning
removed by the existing redactor. Audit traces for off-interface user requests
and hidden-answer reads before publication. Keep raw private evidence outside
the repository. Offline verification reconstructs every reply, check, and total
from the public records and checks source hashes and the full planned matrix.

Run with `python3 benchmarks/retention/run.py --output NEW_DIRECTORY
--private-output NEW_PRIVATE_DIRECTORY --freeze COMMIT`. Replay with
`python3 benchmarks/retention/verify.py RESULTS_DIRECTORY`.

Workspace files persist; conversation contents are not injected into the next
session. HOME/CODEX_HOME remain per trajectory for authentication and trace
collection, but actors are instructed not to read outside the workspace.
Corrections are delivered only while another actor call remains in the budget.
An unsent correction at exhaustion is recorded and supplies no information.
Missing submissions receive semantic failures. The same methods reviewer may
review shuffled outputs without condition labels; its knowledge of the study
is disclosed. Review does not alter exact scoring or exclude unfavorable runs.
