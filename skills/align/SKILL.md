---
name: align
description: Establish and maintain personal project alignment in ALIGNS.md, including selected PR or conversation history review for scoped taste invariants. Use when goals or priorities are unclear, important decisions diverge from the user's expectations, repeated corrections expose a missing criterion, or a long autonomous run needs judgment calibration. Apply existing agreements without reopening routine decisions.
license: MIT
metadata:
  version: "0.4.0"
---

# Align

Help a user and their agent agree on what good work means and keep decisions
consistent with that agreement. The maintained skill supplies the method;
project-root `ALIGNS.md` holds the user's current criteria. Updating the skill
must never replace, reconfirm, or migrate those criteria automatically.
Use the user's language and project conventions. Do not import preferences
from the skill's source repository.

## Existing installations

The agreement filename is now `ALIGNS.md`. If a project still has `ALIGN.md`,
read it as the existing agreement. When migration is authorized, rename the file
and update its instruction references without changing its criteria or confirmation
date. If both files exist, compare them with the user before choosing or merging;
never silently overwrite either. `$align` remains the invocation.

## Read before asking

Identify the target project, applicable instructions, existing `ALIGNS.md`,
relevant conversation, and changes that could affect the current decision.
Check whether Git is available and this is a work tree. Use available history
and uncommitted work; a timestamp does not prove all later work was reviewed.
If history is unavailable, explain only material gaps. Do not initialize Git
or create an alternative alignment log without a request.

At initial setup, or after the user changes tools, read
[environment setup](references/environment.md). Establish which CLI is primary
and whether it is the current client. Reuse explicit context; ask once if it
is unclear. Do not infer the main client just from a filename or installed binary.
Inspect the actual instruction entrypoints before proposing any changes.

## Choose the smallest useful alignment

| Situation | Action |
| --- | --- |
| New project | Clarify intended outcome and consequential trade-offs before choosing implementation details. |
| Existing work without ALIGNS.md | Describe what exists, then ask what should stay or change. Existing code is not evidence of consent. |
| Routine task within the agreement | Apply the criteria and proceed. No interview or gratuitous report. |
| Important disagreement or repeated correction | Compare expectation and result, repair what is already clear, then use the focused drift review below. |
| User does not know what to do next | Offer a brief alignment conversation with concrete options. Do not invent a roadmap or start work without a direction. |
| Long autonomous or repeated run | Check agreed boundaries and offer a short hypothetical rehearsal if consequential judgments are untested. |

For drift, uncertainty, or autonomous work, read
[recurring alignment](references/recurring.md). A suggestion is not a new
scheduled task or permission to run unattended.

## Learn from selected history

When earlier feedback could reduce the user's effort, offer the optional
[history review](references/history.md). Let the user choose recent or full PR
history, accessible project conversations, or neither, with estimated retrieval
and analysis times. Reuse a clear choice; never scan all personal logs by default.

Use **taste invariants** as candidates for criteria that hold across observed
situations within a stated scope. Find supporting decisions and counterexamples;
keep personal preferences separate from team requirements and one-off exceptions.
Repeated feedback is evidence to discuss, not permission to save a permanent rule.
Apply confirmed criteria during self-alignment and revisit them when new user
evidence changes the agreement. Do not claim a personality trait is immutable.

## Agree through conversation

Ask 1-3 related questions about consequential unresolved matters. Reuse clear
answers and accepted decisions. Cover only relevant gaps: outcome, success,
scope, priorities, constraints, things to avoid, and autonomy boundaries.
Use a concrete choice to clarify a vague preference. Label inferences and
hypotheticals; neither is an agreement.

Once the essentials are clear, show a short draft. Do not keep interviewing
to fill categories. Save after confirmation or explicit authorization for the
specific lasting change. Honor delegated drafting scope, marking unconfirmed
parts as draft. A correction to one result is not automatically a lasting rule.

## Keep the agreement current

Preserve unrelated content. Record requirements separately from defaults, with
a reason where it changes decisions. Keep detailed tasks and the skill's full
method out of ALIGNS.md. At initial setup or a requested full review, include a
short **Revisit alignment** section with the items below. A narrow criterion
update must not expand into environment setup merely because this section is
missing; mention a material discovery problem only when it affects the work.

- A working invocation for this client, plus the portable request
  “Use the align skill to review this project's ALIGNS.md with me.”
- The trusted source `https://github.com/hmmhmmhm/aligns.md`, installed route and
  supported update method. Never claim an unverified installation or auto-update.
- The chosen primary CLI and canonical instruction file, and any unresolved
  setup issue. Keep this current instead of accumulating setup history.
- User-agreed review occasions or autonomy boundaries when relevant. Do not
  invent a daily schedule, reminders, telemetry, or an alignment diary.

Keep current criteria only and use Git history when available. Git availability
does not authorize staging, committing, or publishing. Never revise agreements
to justify the agent's mistake or its preferred outcome. Follow the applicable
instruction hierarchy and distinguish a one-off exception from a lasting change.

End with `Last aligned: YYYY-MM-DD HH:mm (time zone)` only at actual full user
confirmation. Use a known zone, or explicitly labeled UTC. Reading, editing,
updating the skill, and automatic review are not confirmation. For partial
confirmation, annotate only affected criteria with their latest confirmation
times and preserve the full timestamp. Replace superseded annotations instead
of logging them. An unconfirmed draft ends `Last aligned: Not yet confirmed.`
Do not invent a date for an undated agreement.

## Connect future sessions

Use the environment reference to connect the canonical instruction file to
ALIGNS.md and to the installed skill. Prefer a short maintained trigger block
from [the instruction template](assets/instruction-block.md), not a copy of
this workflow. Add it once and preserve other instructions. For additional
clients, use safe relative symlinks when their format and loading rules allow;
never replace distinct files or nested policies with links without reconciling
and obtaining authorization for the concrete replacement.

Method updates use the installer's supported route. Read
[installation and updates](references/installation.md) when installing,
repairing discovery, or updating. During ordinary work use the installed version;
do not fetch or change it every turn. An update does not authorize publishing
project data or changing the user's criteria.

Finish an alignment session with the agreed changes, consequential open issues,
and saved paths. In routine work, return to the task without a closing approval
question. If the user declines a suggestion, continue within existing agreements
and do not repeat it without new evidence.
