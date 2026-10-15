# Infrastructure failure before actor execution

All 12 planned trajectories stopped at the ancestor-instruction check before any actor call. The run delivered no task or setup prompts, received no model responses, and completed none of its 72 planned episodes (12 setup episodes and 60 task episodes).

| Condition | Planned trajectories | Harness failures | Actor calls | Scripted replies | Supplied preference units | Passed / planned episodes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 4 | 4 | 0 | 0 | 0 | 0 / 24 |
| B | 4 | 4 | 0 | 0 | 0 | 0 / 24 |
| C | 4 | 4 | 0 | 0 | 0 | 0 / 24 |

The zero costs reflect failure before execution. They provide no evidence about behavior, reduced intervention burden, or human effort. Relative reductions are undefined because both baselines have zero supplied preference units and replies. Neither comparison meets the decision rule. No token usage was observed.

The original frozen sources and execution records remain in this archive. The original privacy scan rejected literal scanner patterns in its own archived source. The corrected publication scope scans runtime evidence and separately verifies the exact frozen source inventory and hashes. See [publication-correction.json](publication-correction.json), [privacy-audit-original.json](privacy-audit-original.json), and [source-archive-verification.json](source-archive-verification.json). The correction does not change a task, answer, threshold, or outcome.

[verification.json](verification.json) contains the offline replay, including all planned denominators. Version 2 is a separate run after infrastructure repair; this failed run must not be pooled with it.
