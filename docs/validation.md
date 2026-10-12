# Validation

Checked on 2026-10-12. These checks distinguish package installation from
agent behavior; they do not claim that every supported client behaves identically.

## Package checks

- The Skill Creator validator accepted the skill frontmatter and structure.
- The skills CLI 1.7.2 discovered one skill named `align` from the local source.
- A project-scoped installation for Codex, Claude Code, and Cursor succeeded
  in an isolated test directory. The installed skill and license were checked
  against the source. These are installation checks, not runtime tests of all
  three client applications.
- The distributable skill contains its MIT license and optional Codex UI metadata.

## Behavioral checks

Two independent acting agents read the skill and executed seven synthetic
requests in separate filesystem fixtures. They did not receive expected answers.
Their responses and resulting files were inspected after execution. Fixture
setup created Git repositories where specified; the skill itself did not
initialize Git, stage files, commit, or publish.

| Scenario | Observed behavior |
| --- | --- |
| New workshop project | Asked three consequential questions and waited for answers; created no premature agreement. |
| Existing workshop implementation | Distinguished existing paid checkout and account signup from the new user's intentions; preserved implementation documentation. |
| Confirmed research guide without Git | Saved the confirmed agreement and agent instructions in Spanish, preserved the non-Git folder, and did not ask for approval again. |
| Existing unchanged agreement | Preserved criteria and timestamp; continued with a newsletter outline without an alignment interview. |
| One-off energetic announcement | Preserved the normal calm voice and timestamp; asked only for missing announcement facts. |
| Explicit lasting voice change | Updated the preference and its partial confirmation time; preserved the full-alignment timestamp. |
| Repeated review after a lasting change | Preserved ALIGN.md and AGENTS.md byte-for-byte, recognized the authorized uncommitted change, and continued with no additional questions. |
| Full reconfirmation | Updated only the full-confirmation timestamp in ALIGN.md; retained unrelated agent instructions. |

[Requests, responses, and resulting agreements](../tests/behavior-results.md)
provide the evidence. The newsletter baseline was accuracy before speed, a
calm voice, and a prior full-alignment timestamp. Recreate each fixture
independently when repeating the evaluation; do not show expected outcomes to
the acting agent before it runs.

## Limits and follow-up

These are single-run behavioral observations. The fixtures were isolated, but
cases within each evaluator shared an agent session. They are not statistical
benchmarks or independent cold-start trials for every model and client.
Two fixtures supplied synthetic confirmation times explicitly; their results
verify handling of user-provided times, not independent clock accuracy.

The initial run exposed two wording ambiguities. The skill now explicitly
connects AGENTS.md after an agreement is saved and keeps the `Last aligned:`
footer label stable when the document body is translated.

Future corrections should follow observed failures or user feedback. Recheck
affected behavior when changing the skill, rather than expanding instructions
for hypothetical cases.
