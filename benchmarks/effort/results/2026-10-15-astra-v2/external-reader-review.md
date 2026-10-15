# Public evidence review

ALIGN did not reduce scripted user intervention in this run. All three conditions tied on replies, supplied preferences, repeated disclosures, and task success. The prespecified reduction rule was not met against either comparator.

This is a simulated outside-reader review by a separate Astra agent session within the maintainer's evaluation. The reviewer inspected public saved evidence and independently recomputed counts. This is not validation by a human participant, an external organization, or a different model. No private raw logs were inspected.

## Recomputed result

| Condition | Setup replies | Later replies | Total replies | Supplied preference units | Repeated units | First-submission task success | Episodes passed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A: ordinary writable project | 4 | 4 | 8 | 24 | 0 | 20/20 | 24/24 |
| B: explicit persistent notes | 4 | 4 | 8 | 24 | 0 | 20/20 | 24/24 |
| C: ALIGN | 4 | 4 | 8 | 24 | 0 | 20/20 | 24/24 |

Every condition used 32 actor calls across four trajectories. Each trajectory asked for three setup preferences in one reply and one new choice in one later reply. The temporary exception and lasting change each supplied one preference unit in their initial task prompt. That gives six supplied units and two replies per trajectory. Every one of the four paired cells tied. Cumulative replies per trajectory were 1, 1, 1, 1, 1, 2 after setup and the five tasks; cumulative supplied units were 3, 3, 4, 4, 5, 6. There was no observed setup payback or later advantage.

C versus B, the primary comparison, had 0% preference-unit reduction, 0% reply reduction, and zero fewer replies per trajectory. C versus A had the same result. Both baselines had nonzero denominators. The repeated-unit and quality requirements passed; the reduction requirements failed. All 60 task artifacts matched the frozen expected objects at first submission, including required questions. All 12 setups passed. No missing cell, capped episode, malformed action, or replacement run was needed to obtain these totals.

The arithmetic was reconstructed from structured asks, initial preference disclosures, saved output.json contents, and frozen cases. It did not use the aggregate metrics as its input. The [machine-readable audit](side-channel-audit.json) preserves all trajectory totals, source checks, message classifications, and trace references.

## Questions outside the interface

The audit covered all 96 actor calls and all 185 visible assistant messages. The 96 final messages were structured actions: 24 asks and 72 submissions. The other 89 messages were statements about the actor's work. None requested an answer, confirmation, permission, or review, including through a declarative or imperative sentence without a question mark. The visible messages in trial stdout matched the messages in all 72 session traces.

For example, notice__A__r1 turn 0 item_0 says, "I’ll check the project notes for existing defaults before asking for any missing preferences." This announces the subsequent structured question; it does not separately ask for input. Notice__C__r1 turn 6 item_0 says, "I’ll read the project agreement and use the align skill to check which preferences remain unresolved." Its channel question appears in the final JSON and is counted. Software__C__r2 turn 7 item_0 says, "I’ll use 14 days for this page and keep the existing hosting, dependency, and analytics preferences." This acknowledges an answer already supplied.

Every message has its exact text, trial path, turn index, and item ID in the audit JSON. There are zero off-interface requests and zero unresolved side-channel questions. No reply or preference count adjustment is required. Progress text still has potential reading cost for a person; the reply metric does not measure that cost.

## Tool use and isolation

The public traces contain 202 orchestration tool calls and 221 nested invocations: 162 shell commands and 59 patch calls. The audit found project-note reads, bundled skill reads, local artifact writes, and Git availability checks. It found no observable read of the oracle, expected-answer bank, benchmark source, another trajectory, or a private transcript. Fixture snapshots started with condition instructions and, where applicable, empty notes and the bundled skill. They did not contain the authored preference values.

Tool diagnostics were not uniformly clean. The public traces preserve 24 shell heredoc failures caused by denied temporary-file creation, two patch verification failures, 14 Git probes reporting that the fixture was not a repository, and one Python runtime cache warning. The actor repaired artifact-writing errors within its existing turn, without an oracle reply or an extra actor call. These events belong in tool/resource reporting; they do not add simulated user interventions. Zero actor-process failures must not be described as zero tool errors.

All 72 episodes had distinct session IDs. Each trace began with three developer messages, the current project instructions/environment, and the current episode request before any assistant message or tool call. Follow-up replies remained inside that episode. The records support cold conversations with persistent project files. They do not establish complete filesystem read isolation. Git probes may inspect parent metadata, and runtime tools attempted temporary/cache operations outside the fixture. No hidden-answer exposure was observed.

## Frozen source and timing

All 19 source files matched both their manifest SHA-256 hashes and Git commit `1386c5ecf79924e4337066e3d9fa5af812001e53`. The manifest was created at `2026-10-15T00:40:52.236141+00:00`. The public [GitHub workflow receipt](https://github.com/hmmhmmhm/align.md/actions/runs/38661382573) identifies that commit; its API record gives creation at `00:40:36Z` and successful completion by `00:40:45Z`, before the manifest and scored sessions. This provides public timing evidence beyond content hashes.

This v2 run followed a disclosed isolation correction. The frozen [infrastructure correction](source-snapshot/benchmarks/effort/infrastructure-correction.md) and earlier evidence must remain available. V2 should not be presented as an untouched first attempt, nor should its successful results erase the earlier preflight failure.

## What a reader can conclude

These fixtures show that all three configured agents remembered and applied the scripted preferences successfully. A already allowed notes and instructed the agent to reuse answers. Calling it a memory-free or instruction-free baseline would misdescribe the comparison. The small, explicit tasks left all conditions at the minimum reply and preference-unit counts permitted by the protocol.

A graph should show the tie and retain all A/B/C conditions, with B identified as the prespecified primary comparator. A caption such as "All three workflows completed 20/20 tasks on first submission with eight scripted replies each, including setup" is supported. A reduction headline, a satisfaction rating, or a claim that users preferred ALIGN is unsupported. The experiment recorded no human time, workload, frustration, enjoyment, or willingness to use the method. Criterion checking can establish that an artifact matches stated choices; it cannot supply those missing observations.

The published draft of [the main report](../../../../EFFORT_BENCHMARK.md) and its SVG/PNG graph were checked against these totals. The graph shows the tie, includes setup replies, identifies B as primary, and states that no human satisfaction or time was measured. Its PNG was also visually inspected. No blocking inconsistency was found. The audit JSON records hashes of the reviewed presentation files.
