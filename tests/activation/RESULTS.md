# Natural-language discovery results

Tested on 2026-10-17 with Codex CLI `0.162.0-alpha.17.2` and `gpt-6-astra`
at medium reasoning effort. Sixty synthetic requests ran twice on align v0.5.0.
A narrow behavior correction in v0.5.1 then received 30 regression trials.
All 150 trials completed; none was silently retried.

## Discovery

The skill was installed in each project's `.agents/skills/align` directory.
The actor received the request and project files, without expected labels or
previous answers. The generic AGENTS.md set local execution boundaries; it did
not tell the actor to use align. The available catalog contained align and nine
other entries, including two browser-skill entries. The catalog was consistent
across trials. User configuration was ignored, but host authentication and
installed skills were retained. These were fresh conversations, not clean machines.

| v0.5.0 request group | Trials | Method body observed |
| --- | ---: | ---: |
| Implicit alignment requests, without the skill name | 54 | 54 |
| Misspelled or informal product names | 6 | 6 |
| Explicit `$align` controls | 6 | 6 |
| Ordinary work, homonyms, or declined review | 42 | 0 |
| Vague dissatisfaction | 6 | 6 |
| One-off tone changes | 6 | 0 |

Each language had 18 implicit trials with the method body observed in all 18,
and 14 ordinary-work/negative trials with no observed read. The requests covered
Korean, English and Japanese, including informal spelling and incomplete context.
The additional set used nine project briefs beyond the baseline workshop site:
study planning, newsletters, gardening, portfolios, research notes, recipes,
home organization, a CLI utility and essays.

Examples that found align include:

- Korean: `내 취향 좀 기억하고 작업해.`
- English: `less ping-pong pls. batch questions next time, use ur judgment on little stuff. save that for this project.`
- Japanese: `説明を省きがちで、意図がうまく伝わらない。どこで聞き返して、どこから任せるか決めておきたい。`
- Names: `얼라인즈`, `alings.md` and `ALGIN.md`.

CSS centering, sorting/sequence-alignment explanations and typo-only edits did
not load align. Requests explicitly declining another alignment discussion also
stayed on the requested edit. Vague complaints loaded the skill to clarify a
direction, without creating a lasting agreement. One-off tone changes left the
existing agreement byte-for-byte intact.

Finding the skill does not guarantee filename normalization. One Japanese
`ALGIN.md` response treated that spelling as a requested filename, while the
other assumed the canonical ALIGNS.md name. Neither created a file. This run
establishes discovery for those requests, not uniform typo correction.

## A behavior issue and its correction

Both repeats of the English short-preference request created an agreement draft
before learning any concrete preference. The draft copied operational restrictions
from AGENTS.md and marked editorial preferences as open. It did not invent a
personal preference or falsely mark full confirmation, but it created a document
too early and duplicated execution rules.

The v0.5.1 correction asks for a concrete criterion first and keeps unrequested
drafts in the conversation. Explicit lasting criteria can still be saved directly.
The skill name and discovery description were not changed.

| v0.5.1 regression group | Trials | Observed behavior |
| --- | ---: | --- |
| Learn preferences, with none supplied | 6 | Asked for a criterion; no files changed |
| Explicit lasting preferences | 12 | Saved the supplied criterion |
| Unresolved questioning preferences | 6 | Proposed or asked about the boundary; no files changed |
| Repair an already-agreed violation | 6 | Removed the tracking reference; agreement and instructions unchanged |

All 30 passed the recorded file checks. The 24 alignment requests returned method
content; the six direct repairs did not. This is a regression check on existing
cases, not an independent estimate of improvement on unseen requests. The two
v0.5.0 failures remain in the evidence and offline replay.

## Evidence and measurement

- [Protocol and amendments](PROTOCOL.md)
- [Baseline cases](cases.json) and [84-trial evidence](results/2026-10-17-baseline/verification.json)
- [Additional wording cases](holdout-cases.json) and [36-trial evidence](results/2026-10-17-additional/verification.json)
- [Regression cases](regression-cases.json) and [30-trial evidence](results/2026-10-17-regression/verification.json)
- Example failure: [v0.5.0 short-en repeat 2](results/2026-10-17-additional/trials/short-en__r2.json)
- Corresponding regression: [v0.5.1 short-en repeat 2](results/2026-10-17-regression/trials/short-en__r2.json)
- [Run and replay instructions](README.md)

Each run retains source snapshots and hashes, prompts, model context, tool events,
responses, and before/after files. Publication manifests hash public trial files.
Literal local paths are redacted; private raw evidence stays outside Git. Full
session metadata and authentication files are not published.

The original metric required a successful shell exit. It counted five of six
explicit controls: in one trial, the method was returned before a later `git status`
failed in the same command. The original count is retained as `read`. The separate
`body_visible` measurement checks actual returned method content and counts all
six. Native skill-input evidence also confirms that all six `$align` controls
received the method directly. A mention of the skill or a catalog listing alone
never counts as a method read. Input markers establish selection, not that the
model understood every instruction.

The owner authored the requests and inspected selected responses, including every
flagged mutation. File-invariant checks cover every completed trial. This is not
an independent human assessment or a comprehensive semantic quality score.
The initial runtime pilot is excluded from the fixed sets. One detached pilot
launch ended before producing model events; the foreground pilot completed.
Neither is included in the 150 completed trials.

## Limits

These results support natural-language discovery in the tested installed Codex
environment. They do not measure directory search, first-time installation,
Claude Code or Cursor execution, other models, long conversation histories, or
real user success rates. The tiny synthetic projects and related translations
are not a representative sample of users. Two repeats per case are a regression
check, not a reliability guarantee.

The additional set was frozen before running but was also maintainer-authored.
Its behavior finding informed v0.5.1. It must not later be presented as an unseen
holdout for that correction. No existing marketing benchmark numbers were changed.
