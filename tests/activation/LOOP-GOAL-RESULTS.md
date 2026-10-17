# Loop and goal review

The existing skill already loaded for the nine requests about unresolved loop
stopping criteria, goal scope, and lasting completion preferences in this set.
Version 0.5.2 adds a specific review procedure and future-session reminders.
This evaluation does not show that the new procedure improves real-world
completion or user effort.

## What changed

The method compares the user's request, configured objective and boundaries,
reported run state, and actual results. It separates unresolved judgment from
known configuration errors, ignored instructions, usage limits and requested
pauses. A review does not authorize a restart, larger budget or broader scope.
Confirmed lasting criteria can be saved without repeating the question; the
full alignment date stays unchanged.

Discovery still requires an active agent turn. The skill does not listen for
stop events or wake a terminated process. A later turn can inspect available
state and address the mismatch.

## Test design

Each version receives the same 24 maintainer-authored requests: eight situations
in English, Korean and Japanese. Nine should load align; fifteen should answer
or repair directly. All requests use fresh Codex conversations with the skill
installed locally, gpt-6-astra at medium effort, and one trial per wording.
Expected labels never reach the actor. The complete skill, fixtures and runner
are frozen for each run.

Run records are synthetic local files. The actor is prohibited from invoking
real goal, scheduler or loop controls. File checks verify that records remain
unchanged, exact repairs affect only the requested setting, and saved criteria
preserve existing boundaries and the full alignment date. The maintainer reads
responses separately from counting method loads. This is not independent review
or a test of live runtime recovery.

## Loop and goal results

| Version | Required: method loaded | Controls: method loaded | File-check findings |
| --- | ---: | ---: | ---: |
| 0.5.1 baseline | 9/9 | 0/15 | 0 |
| Rejected broad-description candidate | 9/9 | 7/15 | 0 |
| Final 0.5.2 candidate | 9/9 | 0/15 | 0 |

All 72 loop/goal trials completed without runtime failure. Each final-candidate
language had three required reads and zero reads across five controls. The
successful-command and body-visible counts agree for these runs.

Across all three versions, the six unresolved requests per run left files
unchanged and identified missing scope or completion criteria. Three explicit
lasting requests saved the supplied completion criterion, preserving the
existing scope, publication boundary and full alignment date. Three configuration
repairs changed only the iteration count. The remaining twelve controls only
reported or explained existing information. No synthetic run record changed.

The maintainer reviewed all 72 responses. They did not claim a restart or successful
completion of unfinished work. Final-candidate questions stayed on the missing
criterion; already-known criteria and requested pauses did not get a new
preference interview. This is a qualitative reading, separate from the replay's
file checks and discovery counts. In `loop_stop-en` the opening said it would
record the gap, but the final response correctly left the proposed rule unsaved
pending confirmation. The file snapshots confirm that distinction.

- [Cases](loop-goal-cases.json)
- [Baseline replay](results/2026-10-17-loop-baseline/verification.json)
- [Rejected candidate replay](results/2026-10-17-loop-regression/verification.json)
- [Final candidate replay](results/2026-10-17-loop-final/verification.json)
- [Final Korean stopping review](results/2026-10-17-loop-final/trials/loop_stop-ko__r1.json)
- [Final Japanese preference update](results/2026-10-17-loop-final/trials/stop_preference-ja__r1.json)

## Rejected description change

The first candidate explicitly added loop setup, stopping and completion to the
catalog description. It loaded align in 7 of 15 controls, compared with 0 of 15
on 0.5.1: all three known completion violations, two usage-limit reports, and two
requested-pause reports. The answers still respected the existing criteria and
left run state unchanged, but the extra method loading was unnecessary.

The final candidate restores the original catalog description and keeps the
new workflow, instruction block and static Claude session reminder. The
rejected run is retained under `2026-10-17-loop-regression`; its directory name
reflects its initial role and does not mean it was accepted for release.

## Existing discovery regression

The final candidate also completed the original 42-case suite once. All 21
implicit requests returned the method body; none of the twelve ordinary-work
controls did. The three vague complaints loaded it, while the three one-off
tone requests did not. All retained file checks passed.

All three explicit `$align` controls received the frozen skill natively and
returned it in command output. The original successful-command metric counts
two: the Korean trial printed the method before a later Git command in the same
shell group exited 128 because the fixture has no Git repository. The existing
body-visible measure correctly counts three. Both measurements remain in the
[replay](results/2026-10-17-general-v052/verification.json); the
[native inputs](results/2026-10-17-general-v052/native-inputs.json) are retained too.

There were 114 fresh Codex executions in this follow-up, including the rejected
candidate. All completed with no timeout or runtime failure. Codex CLI was
`0.162.0-alpha.17.2`. The 72 loop/goal responses were read in full; the broader
suite received automated replay and selected response review. No claim of
independent behavioral scoring is made.

## Evidence and limits

Both successful and rejected results are retained. There were no silent retries.
A method load requires returned method content, not a mention of the skill or
its catalog entry. The replay reports the original successful-command measure
and the supplemental body-visible measure separately.

The same requests are reused during development. One run per wording, one
model and one client cannot establish general reliability or isolate the effect
of wording from model variation. The broader 42-case discovery suite checks
existing behavior on the final candidate; it is reported separately.
