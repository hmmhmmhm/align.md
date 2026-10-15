# Pre-run methods review

This review concerns the discovery protocol. The earlier effort pilot remains a
tie and keeps its frozen sources, results, and interpretation. The reviewers and
case authors are agents working for the maintainer. This is not an independent
replication or a study with human participants.

The primary comparison is the complete ALIGN setup against a competent agent
with explicit persistent notes. The ordinary-instruction arm is secondary.
All arms receive the same task prompts, observations, answer availability,
correction policy, model settings, episode limits, and file persistence. The
benchmark changes the alignment support, not the private user's criteria.

## What the measurements support

A scripted answer is a disclosure of an authored criterion. It is not a user
rating. Count every supplied preference unit and every additional reply,
including setup, repeated questions, unknown questions, and corrections. Report
those counts with first-submission and final quality, failure counts, and the
neutral control. Asking more questions earns no quality credit by itself.
Necessary permission questions may be prerequisites for authorized action.

Transfer tasks must require applying a criterion in another context. Temporary
exceptions must expire, and lasting changes must require explicit direction.
An indirect observation can motivate a question or a provisional task decision.
It cannot establish a permanent preference by itself. Review saved project
files as well as deliverables for unsupported lasting claims.

Exact decision and content checks establish conformance to the authored cases.
They do not establish that free-form reasoning is useful. Separate reviewers
must assess that reasoning against task facts and private criteria without
condition labels. Retain disagreements, allow ties, and show their effect on
any reported benefit. Both reviewers are model-based maintainer checks.

## Question routing

The actor writes natural-language questions. A treatment-blind classifier selects
route identifiers from a frozen inventory without seeing the treatment or
saved files. The runner supplies only the fixed answers attached to those
identifiers. Classification calls and receipts are separate from actor calls. Publish the raw questions, matching routes, exact answers, and
unmatched questions so routing can be replayed offline.

An independently authored pre-run challenge set found that the draft lexical
router matched intended disclosures in 14 of 26 examples. It missed ordinary
paraphrases and disclosed unrelated criteria when questions mentioned settled
or negated topics. The original fixture and output remain in
`router-validation.json` and `lexical-router-pretest.json`. These are
engineering pretests, not scored actor results or a general accuracy estimate.
The production router was changed before the freeze in response to this check.
Reusing this fixture to validate the replacement is development validation;
it does not make the fixture held out. The replacement selected all 26 intended
route sets in one call per question. The [receipts and source note](pretests/semantic-router-v1/README.md)
retain the results, the exact pretest runner, and the source-change flag.
All classifier contexts showed Astra at medium effort, with no tool events.

The classifier can also make semantic errors. It must select only known route
identifiers and must not compose user answers. Invalid output or a failed
classification call is a harness failure, not an opportunity for a favorable
retry. Validation receipts and the frozen prompt make its behavior inspectable.

After the run, audit every question and disclosure without treatment labels.
Any material incorrect disclosure, withheld available answer, or treatment
information in the routing process blocks a favorable comparison claim.
Preserve the affected trajectory and report the fault. Do not repair the
router and replace only an unfavorable behavioral attempt.

## Evidence and claim gates

Freeze and publish the protocol, cases, router, validation fixtures, runner,
verifier, and review rubric before scored actor calls. A local hash proves
byte identity, not publication time. Retain a public commit and timestamped
receipt that precede the manifest. Infrastructure-only smoke tests must be
labeled and excluded from scored outcomes.

The offline verifier reconstructs prompts, responses, disclosures, artifact
checks, session boundaries, episode outcomes, and costs from published
records. It includes failed and missing work in planned denominators. A
successful replay means the archive agrees with its frozen rules; it does not
clear the separate quality and routing audits. Final benefit eligibility also
requires the prespecified comparison threshold and all audit guardrails.

The visible evidence must support a check for hidden-answer reads, side-channel
questions, and unauthorized preference persistence. Archive privacy review is
separate. A lack of a visible violation is not proof of complete operating
system isolation.

The case set is small and authored by the maintainer. Repetitions are stochastic
runs, not independent people. Report per-case outcomes, ties, regressions, and
the neutral control even if aggregate costs improve. These results cannot
support claims about measured human effort, satisfaction, broad deployment
reliability, or an independent third party's endorsement.
