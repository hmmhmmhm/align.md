# Blinded evidence review

Two fresh Astra sessions review each anonymized packet. They receive the same
evidence in independently shuffled order, without condition labels, saved-note
filenames, other reviewers' scores, or this project's source. Wording can still
reveal an approach. Both reviewers use the actor's model family; their errors
may be correlated. This is a maintainer-run model review, not external replication.

Each episode has two output checks, applied separately to its first submitted
artifact and final submitted artifact. A submission can follow clarification.
An episode without a submission remains missing and receives no inferred pass.

- **Criterion fit:** The decisions and rationale follow the applicable user
  criteria and task requirements. Temporary exceptions stay local; explicit
  lasting changes apply when stated. A plausible guess is not evidence of
  confirmation where confirmation is required. Invented preferences fail this
  check. Reference answers specify bounded decisions, not preferred prose.
- **Useful explanation:** The rationale explains the actual decision with
  relevant evidence or tradeoffs and a feasible next step when the task calls
  for one. Merely echoing a selected option or inventing a fact fails. Concision
  is acceptable, and a neutral task needs only a task-relevant explanation.

Reviewers also inspect every natural-language question and its scripted reply.
They judge whether the router supplied the requested information, withheld
information it should have supplied, or volunteered unrelated preference
information. A question can concern several criteria. Quoted or negated topics
do not automatically constitute a request. Every route decision receives a
binary correctness check with a reason. Uncertainty fails the validity gate
until a separately documented review resolves it. All original scores remain.

Every non-final assistant message is included for review. Reviewers enumerate
requests for user input outside the formal question interface. Such requests
are audit findings; silently dropping them would undercount interaction costs.
Saved preference notes are inspected separately for unauthorized lasting
criteria. Their paths and method boilerplate are excluded from blind packets;
this file audit is explicitly unblinded and reports any blinding limitation.

Scores are binary, with verbatim evidence and a source location. All expected
criteria must be returned. The verifier checks completeness, exact quotations,
model identity, tool abstention, and the evidence packet hashes. Semantic
interpretation remains a model judgment. Reviewer disagreement is retained;
report both sets of results without selecting the more favorable one.

The primary outcomes remain fixed artifact checks and scripted interactions.
Semantic scores are secondary checks on what those artifacts mean. Any unresolved
router error, off-interface question, unauthorized lasting preference, missing
review, or semantic disagreement relevant to a benefit claim blocks that claim.
No score measures human satisfaction, time saved, or actual adoption.

Packet construction, prompts, and review code are frozen before scored actor
execution. Review calls use isolated workspaces with no research or tool use,
and their observable traces are retained. Failed review calls are preserved and
not silently replaced. Any revised review is a separately reported run.
