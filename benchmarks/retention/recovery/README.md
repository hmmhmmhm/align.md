# Interrupted-run recovery

The user paused this study to finish site work, then explicitly resumed it.
The original study is frozen at c07a880. This recovery procedure changes
orchestration and evidence handling; it does not change tasks, scoring,
preferences, reply budgets, or the model setting.

The interrupted orchestrator had not serialized its chain records. Private
native session traces and exact workspaces were copied before termination.
Eight calls in seven conversations have native `task_complete` receipts:
P1/B and P2/B each completed three tasks; P2/A completed the workshop with one
question and one submission. All eight responses are retained without reruns.
No observed call lacks a completion receipt. Subprocess exit codes, stdout,
stderr, original prompt-audit stdout, and intermediate workspace snapshots
were lost. Missing fields remain null. Native completion duration and token
counters are reported separately from subprocess duration and CLI usage.

Recovery reconstructs those seven episodes from native user-message and
completion records. It verifies exact task prompts and scripted replies,
and checks model/effort from turn contexts. Derived compatibility events are
explicitly marked as reconstructed, never represented as captured stdout.
The final saved workspace is retained once per recovered chain; it is not
presented as a snapshot at every earlier turn.

P2/A resumes at guide in a copy of its saved workspace, with a fresh
conversation. The five untouched chains run through the frozen runner in
original planned order with up to three workers. P1/B and P2/B receive no
further actor calls. This yields the original 24 episodes, including the seven
recovered episodes. A new execution-lineage record links the original freeze,
this recovery commit, private source trace hashes, and resumed calls. Original
private copies remain untouched. No completed response is selected out or
replaced based on its score.

Offline verification first checks each reconstructed turn against its published
native trace. It then replays the original scorer and reply policy. Resource
reporting must count recovered trace durations separately; full uninterrupted
wall time is unavailable. The recovery code and this procedure are published
before any resumed actor call. The original source snapshot remains unchanged.
