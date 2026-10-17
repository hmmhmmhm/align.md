# Natural-language skill discovery

This is a synthetic development evaluation of installed-skill discovery in Codex,
not a directory search, human user study, or comparison with other clients.

Freeze cases, expected routing, runner and skill before executing. Each trial gets
a fresh project and conversation. Only the request and project fixtures go to the
actor. Do not pass expected labels, rubrics, prior responses or evaluator conclusions.
Use the existing authenticated host with user configuration and execpolicy ignored;
retain its available skill catalog and document it. Do not modify HOME or CODEX_HOME.
No network actions, personal log review, publication or package installation is allowed
inside the actor fixtures. These limits do not block reading installed skills.

Run 42 cases twice on gpt-6-astra at medium effort: 21 implicit positive cases,
12 negative controls, 6 ambiguous or one-off cases, and 3 explicit controls.
Each group covers Korean, English and Japanese. Use three workers, a fixed shuffled
order, and a 180-second timeout per trial. Preserve failures; do not silently retry.

The primary observable is a successful tool command whose output includes the
actual align method body. A skill mention or catalog entry does not count.
Report the read rate for each category and language with raw counts. A missing
read is an observation, not proof the agent never applied the method. Keep
infrastructure failures out of completed-trial rates and show their count separately.

Review the response and file changes separately. In particular, check that
ambiguous requests do not become invented lasting criteria, one-off preferences
leave the agreement intact, confirmed narrow updates preserve the full timestamp,
known errors are fixed without another interview, and hypothetical rehearsal
never starts an autonomous loop. Do not equate loading the skill with good behavior.

The owner-side evaluator reviews all outputs. This is not an independent or blinded
behavioral score. Public records retain prompts, outputs, commands, changes and
source hashes with literal local paths redacted. Raw evidence stays outside Git.
Do not publish host account identifiers or credentials. A pre-run pilot establishes
that the runtime works but is excluded from the fixed case results.

If observed failures justify a description change, preserve the baseline and
freeze a separate candidate before retesting the entire suite. Report both;
reusing these cases is a regression test, not held-out validation. Any new held-out
cases must be fixed before candidate results are inspected.

Sources: [OpenAI skill evaluation guidance](https://developers.openai.com/blog/eval-skills)
and [skill activation](https://developers.openai.com/plugins/concepts/skills).

## Additional wording set

Freeze 18 additional cases in `holdout-cases.json` before changing any description
or running those cases. They cover very short preference requests, misspelled
product names, casual phrasing, alignment homonyms, declined review, and answers
already present in project context. Run each twice. Six cases require implicit
selection, three are explicit misspelled-name requests, and nine should avoid
selection. This is additional synthetic coverage, not an independently authored
holdout. Do not count it as unseen validation if it is later used for tuning.

Raw command-output hashes in `read_evidence` are computed before path redaction.
The replay recomputes actual method reads from published event text and compares
commands and event positions; it does not equate raw and redacted output hashes.
A publication manifest hashes the final public trial files separately.

## Measurement correction during the baseline run

The first `explicit-ko` repeat 2 returned the complete method, then `git status`
in the same shell command exited 128 because the fixture has no Git repository.
The preregistered successful-command metric undercounts this real read. Preserve
that original metric and all records. Add a separately named `body_visible`
metric that checks returned method content regardless of the shell group's final
exit code. A failed read with no method content still does not count. Explicit
`$align` requests can also inject the method natively; record that separately
from shell reads. This correction changes measurement, not the actor or case labels.

Before the additional run, its nine positive/name-typo fixtures were broadened
beyond the baseline workshop site: study planning, a newsletter, gardening,
a portfolio, research notes, recipes, home organization, a CLI utility and essays.
These are synthetic project briefs, not observations of actual user populations.

## Behavior correction and regression scope

The additional run's `short-en` repeat 2 loaded the skill, then created an
unrequested agreement draft before learning a concrete preference. It copied
operational restrictions into the agreement, marked editorial choices open, and
kept `Last aligned: Not yet confirmed.` No personal preference was fabricated.
This is premature scaffolding, not a discovery failure.

Version 0.5.1 adds one narrow instruction: ask for a concrete criterion before
creating this agreement, keep unrequested drafts in the conversation, and do not
use copied tool restrictions as substitute preferences. Explicit lasting criteria
can still be saved immediately. The name and description remain unchanged.

Freeze `regression-cases.json` with 15 existing cases before running v0.5.1 twice
per case: vague requests to learn preferences, explicit questioning preferences,
explicit maintainability preferences, unresolved questioning preferences, and
known errors to repair directly. This is targeted regression on observed cases,
not a fresh held-out improvement estimate. Retain the v0.5.0 evidence unchanged.
