# Evidence audit

This is a maintainer-run, unblinded model audit. The evidence cross-check was separate from execution and semantic review. It is not independent external validation.

All 24 planned episodes and 33 actor calls are accounted for. Eight calls were recovered from native completion receipts; 25 were executed after resumption. Each public response, observable assistant-message list, task prompt, and delivered reply matches its native session. Exact checks and scripted replies replay correctly. All episodes ended in matching valid submissions, with no runtime failures or unresolved episodes. A received nine replies containing 18 criterion units; B received none.

The seven recovered episodes preserve their original outputs. No completed call was rerun. P2/A resumes with the same saved workspace and a fresh conversation. Recovered subprocess stdout, stderr, exit code, timeout, wall duration, original prompt audit, and intermediate snapshots remain unavailable. Native completion establishes model-turn completion; it does not reconstruct missing process receipts. The duration adapter is a disclosed recovery change to verification.

The audit reviewed all 24 native sessions, including 21 command executions, four file changes, and 15 commentary messages. No off-interface user request or hidden-answer read was observed. All commands list or read workspace files. Each preference write follows an explicit authored reply permitting storage. P1/A and P4/A saved LEARNING_PREFERENCES.md; P2/A and P3/A updated AGENTS.md. Those writes contain the supplied defaults, without additional unsupported user preferences. Available workspace snapshots have internally consistent content hashes. Missing recovered snapshots were not inferred.

Public actor records and decompressed traces contain no observed private reasoning, unredacted creator identity, account quota metadata, or host-path leakage. This check covers the artifacts hashed in evidence-audit.json. It does not assert a filesystem security boundary or audit later semantic-review artifacts.

## Resource accounting

CLI usage on resumed conversations can contain cumulative session counters. Adding those receipts counts earlier turns again. For resumed A calls, raw CLI sums are 454,628 input and 5,466 output tokens; native per-turn differences are 357,526 input and 4,892 output tokens. The raw CLI sums must not be described as additive per-call consumption.

Native token differences use the last token_count.info.total_token_usage before each task_complete, minus the preceding completed turn total in the same session, starting at zero. The audit ledger retains recovered and resumed subtotals and all receipt bindings.

| Arm | Recovered native input/output | Resumed native input/output | All native input/output |
| --- | ---: | ---: | ---: |
| A | 62,606 / 742 | 357,526 / 4,892 | 420,132 / 5,634 |
| B | 151,826 / 1,804 | 151,609 / 1,817 | 303,435 / 3,621 |

Recovered native durations and observed subprocess durations are different measurements. Full uninterrupted wall time is unavailable. These records support descriptive resource accounting, without a compute-benefit claim or a conversion to human effort.

The comparison remains a synthetic information-gap retention-package pilot: A may learn and persist preferences; B starts with confirmed criteria and the align method. This audit does not judge semantic plan quality, establish a population effect, or isolate the value of a file name from retained information and method instructions.
