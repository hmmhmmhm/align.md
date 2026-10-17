# Validation

Initial checks: 2026-10-12. Maintained-skill checks: 2026-10-14.
These checks distinguish package installation from
agent behavior; they do not claim that every supported client behaves identically.

The [public benchmark](../BENCHMARK.md) compares the same criteria in AGENTS.md,
a referenced ALIGNS.md, and the complete maintained skill setup. Its protocol,
actor evidence, model judgments, context correction, and offline verification
are separate from the earlier development checks below.

## Package checks

- The Skill Creator validator accepted the skill frontmatter and structure.
- The skills CLI 1.7.2 discovered one skill named `align` from the local source and public GitHub source.
- A project-scoped installation for Codex, Claude Code, and Cursor succeeded
  from both sources in isolated test directories. The installed skill and license were checked
  against the source. These are installation checks, not runtime tests of all
  three client applications.
- The distributable skill contains its MIT license and optional Codex UI metadata.

## Behavioral checks

Two acting model agents read the skill and executed seven initial synthetic
requests, followed by one repeated-review request, in separate filesystem
fixtures. These were separate model contexts, not external human evaluators.
They did not receive expected answers.
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
| Repeated review after a lasting change | Preserved ALIGNS.md and AGENTS.md byte-for-byte, recognized the authorized uncommitted change, and continued with no additional questions. |
| Full reconfirmation | Updated only the full-confirmation timestamp in ALIGNS.md; retained unrelated agent instructions. |

[Requests, responses, and resulting agreements](../tests/behavior-results.md)
provide the evidence. The newsletter baseline was accuracy before speed, a
calm voice, and a prior full-alignment timestamp. Recreate each fixture
independently when repeating the evaluation; do not show expected outcomes to
the acting agent before it runs.

## Limits and follow-up

Three additional requests ran in separate fresh Codex CLI sessions using the
installed skill: saving explicitly confirmed criteria, questioning an inherited
prototype, and implementing a page in a later session without an alignment
request. The last session read the resulting agreement, kept accounts and
payments out of scope, marked unconfirmed access information, and preserved
both agreement files byte-for-byte. See the [requests and evidence](../tests/cold-cli-results.md).

These are single-run behavioral observations. In the original evaluator runs,
the fixtures were isolated but cases within each evaluator shared an agent
session. The additional CLI runs used fresh sessions with the existing local
configuration. Neither set is a statistical benchmark or evidence for every
model and client.
Two fixtures supplied synthetic confirmation times explicitly; their results
verify handling of user-provided times, not independent clock accuracy.

The initial run exposed two wording ambiguities. The skill now explicitly
connects AGENTS.md after an agreement is saved and keeps the `Last aligned:`
footer label stable when the document body is translated.

Future corrections should follow observed failures or user feedback. Recheck
affected behavior when changing the skill, rather than expanding instructions
for hypothetical cases.

## Maintained-skill checks (0.2.0)

- Skill Creator validation passed.
- Eleven Python checks passed for conflict refusal, byte-preserving instruction
  edits, relative links, idempotency, version consistency, and static hook output.
- The skills CLI 1.7.2 installed the complete revised skill from local source into
  an isolated Codex project. Its command help confirms named, scope-specific
  updates. Installation alone does not demonstrate automatic invocation.
- A project-scoped copy of the earlier GitHub installation was upgraded with
  `npx skills update align -p`. All revised skill files matched the published
  source; a separate personal ALIGNS.md remained byte-for-byte unchanged.
- Codex plugin command syntax was checked against the installed CLI. Native
  plugin manifests and declared paths were checked locally. Native installation,
  Claude SessionStart delivery, and automatic refresh were not exercised in real
  client sessions for this release.

Two acting model agents in separate contexts completed six additional isolated scenarios.
They preserved distinct client instructions, kept rehearsals hypothetical,
clarified an uncertain direction, fixed a known violation without an interview,
kept a one-off exception temporary, and saved an explicit lasting change without
reconfirming the full agreement. These are single-run observations, not a
reliability benchmark. See [requests and results](../tests/recurring-results.md).

One ambiguity was corrected: a narrow criterion update must not expand into
installation questions just because the document lacks a revisit section.


## History review, 0.3.0

The history collectors have 19 synthetic unit/integration checks covering full
selection beyond 1,000 PRs, endpoint pagination, exact bot exclusions, short
feedback, quota stops, interruption/resumption, scoped transcript parsing,
unsupported formats, duplicate records and private output locations. These run
with the existing package checks through `python3 -m unittest discover -s tests`.

An independent Astra code review found stale project-context inheritance and
silent unsupported-message omissions. The parser now resets uncertain context,
reports partial coverage and has regression fixtures for those cases, including
falsy malformed payloads. A read-only metadata plan was also checked against
this repository's GitHub API; it had zero PRs at validation time. Full collection
and conversation parsing were tested with fixtures, not personal logs.

These checks establish collector behavior. They do not measure preference
inference accuracy, real-world time savings, or compatibility with every client
transcript version. Analysis speed defaults remain disclosed assumptions.

## Natural-language discovery, 0.5.0 and 0.5.1

[The discovery report](../tests/activation/RESULTS.md) covers short and informal
requests in English, Korean and Japanese, including misspelled product names
and requests that should not start alignment. It separates observed method
loading from file behavior and retains both original and corrected measurements.

The report includes a premature agreement-draft case and the narrow 0.5.1
correction. Frozen fixtures, actor traces, source hashes and an offline replay
are in [tests/activation](../tests/activation/). These are synthetic Codex runs
on one model, not evidence from real users or every supported client.
