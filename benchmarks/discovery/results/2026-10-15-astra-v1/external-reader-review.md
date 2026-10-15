# Public evidence audit

A separate methods-review agent inspected all 12 trajectories and 60 episodes in
this archive. The review covered 120 actor turns, all 246 assistant messages,
visible tool actions, and 55 changes to persistent notes. All 126 non-final
messages were read for requests outside the formal question interface. The
reviewer worked within the maintainer's evaluation, knew the conditions, and
had contributed the pre-run methods review and verifier. This is an unblinded
maintainer audit, not an independent external replication.

## Questions and visible access

No non-final message requested a user answer. The two automatic request
candidates were progress narration: `community__A__r1`, turn 6, said it would
check which decisions were settled; `service__C__r2`, turn 6, said it would
identify choices needing input. The actual questions appeared in the formal
JSON interface. There were 24 delivered information answers, and no questions
on the neutral calculation episodes. This audit does not classify every formal
question as necessary or every disclosure as correctly routed; those judgments
belong to the separate blinded review.

The visible event records contain 246 command executions and 98 file-change
items. Compressed session traces also record 19 local write attempts rejected
because the shell could not create a temporary file for a heredoc. Those
attempts are absent from the command-execution item count but retained in the
trace audit. The agent recovered within the same turn. The trace tool inputs
contain 265 `exec_command` calls and 98 `apply_patch` calls. No network,
connector, hidden-answer-bank, or benchmark-source access was observed.

Reads concerned the fixture's instructions, source notes, saved criteria,
outputs, and C's bundled alignment skill. Git availability checks and failed
`python` commands also appear. A visible absence of forbidden reads does not
establish complete filesystem isolation or rule out unlogged activity.

## Persistent criteria

The saved notes distinguish source criteria from unresolved choices. The
lottery, latency target, cancellation remedy, and diagnostic rules are saved
after the corresponding authored answer. Temporary event fees and the archive
importer dependency exception remain scoped. The standing fee ceiling changes
from $10 to $20, and the export compatibility window changes from 30 to 7 days,
after explicit replacement instructions. Historical exceptions sometimes remain
in notes with their limited scope stated.

No inspected note promoted incidental poster color, snack spending, incident
weekday, or fixture size into a lasting preference. No unauthorized lasting
criterion was observed. C's files leave full alignment unconfirmed. These
findings concern saved criteria; they do not certify the usefulness of every
plan or the semantic accuracy of every router answer.

## Exact-check corrections

All 36 delivered corrective replies were classified as schema-only after
reading the rejected values and their replacements. Every trajectory had three
such replies. The [correction ledger](correction-classification.json) retains all
60 delivered replies, the affected fields, exact values, and task prompts.

In community tasks, the rejected values already described a lottery; some
outputs represented the absence of public attendee names as an empty list.
The checker required the literal string `lottery` and the boolean `false`.
In service tasks, the rejected values described plain failure messages with
useful next steps; the checker required `actionable-text`. The later task
prompts named these fields without repeating the setup enum or type contract.
Each corrective edit changed only the named fields, leaving the other output
content intact.

This classification is a post-run diagnostic. It does not replace the frozen
exact scores or subtract replies from the primary totals. The protocol's
preference-unit totals include this exact-value feedback, so they cannot be
read as a count of purely semantic preference misunderstandings. The observed
correction burden is substantially shaped by the output contract.

## Evidence integrity

The inspected staged trial records match the published files byte for byte.
All 12 planned trajectories are present. Actor contexts identify
`gpt-6-astra` with medium effort, and 60 distinct episode sessions are recorded.
The manifest names freeze commit
`0975de3a3ee967dc6d1c2aeb5c0893ec61c5ac83`. Archived source hashes match the
manifest, the run's source check reports no changes, and offline actor replay
passes. These checks establish internal consistency, not an independent proof
of publication time.

The [audit ledger](side-channel-audit.json) records trial and trace hashes,
every non-final message, visible tool items, note changes, recovered heredoc
failures, and metadata checks. It clears the observed off-interface and saved-
preference concerns within this evidence scope. Blinded substantive and routing
reviews remain separate; this audit alone does not permit a benefit claim or
measure human effort or satisfaction.
