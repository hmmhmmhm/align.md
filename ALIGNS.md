# Project Alignment

## Purpose

Help agents make decisions that reflect the user's judgment and
continuously identify and address gaps between their work and
the user's expectations.

Alignment is an essential part of working with AI. It deserves
a dedicated document because expectations differ between users
and evolve over time.

## Role of ALIGNS.md

ALIGNS.md holds the user's current goals, priorities, preferences,
constraints, and decision criteria.

Keep these separate from harness configuration and general agent
instructions. AGENTS.md should explain when and how to use ALIGNS.md,
while ALIGNS.md remains the source of alignment criteria.

## Scope

Focus initially on alignment between an individual user and their
agents. Multi-user agreements and conflict resolution are outside
the initial scope.

Provide an easy-to-use skill that works across new and existing
projects. Make it discoverable through relevant skill directories
and distribution services, verifying support and registration
status rather than assuming universal coverage.

## Success Criteria

- Agents make decisions consistent with the user's stated criteria.
- Agents notice meaningful misalignment and propose corrections.
- Users spend less effort repeating expectations and correcting
  avoidable misunderstandings.
- The skill is easy to discover, adopt, and use.

## Operating Principles

- Ask only consequential, unresolved questions.
- Distinguish confirmed expectations from assumptions.
- Adjust autonomously within existing agreements.
- Reflect lasting changes when the user's intent is clear.
- Do not turn one-off exceptions into permanent preferences.
- Never rewrite agreements to justify an agent's own results.
- Continue independent work while a decision awaits clarification.

## State and History

Check whether the target project uses Git.

Keep only current alignment criteria in ALIGNS.md. When Git is
available, use its history to track changes instead of maintaining
a separate alignment log.

If Git is unavailable, explain the history limitation. Do not
initialize Git or create an alternative history file without
a user request.

Review available changes since the last alignment for meaningful
drift or new criteria. Do not repeat resolved questions without
new evidence.

Record the last full alignment time only after the user confirms
the document. Record partial confirmations separately without
implying a full review.

## Project name

User-confirmed naming update: 2026-10-17 (Asia/Seoul). Partial confirmation only.
Use ALIGNS.md for the project and agreement file, and hmmhmmhm/aligns.md for the
repository. Keep `$align` as the action name. The acquired aligns.md domain will
be connected separately after DNS propagation. Preserve historical benchmark
evidence and its hashes when updating current branding.

## Presentation and Licensing

- Write repository documentation in English.
- Do not use em dashes or emoji.
- Keep the README brief, with a centered title, useful badges,
  and a copyable installation request.
- Publish the project publicly under the MIT License.

## Maintained Skill and Recurring Use

User-requested scope update recorded: 2026-10-14 (Asia/Seoul).
This is a partial update, not a full reconfirmation.

Distribute the alignment method as a maintained skill. README and site copy
should guide users to install it, rather than preserving a standalone interview
prompt. Support native plugin updates where verified and a user-authorized,
targeted refresh at alignment-session start elsewhere. Keep method updates
separate from personal criteria and never promise universal background updates.

Suggest focused alignment after consequential judgment mismatches, repeated
corrections that reveal missing criteria, and when users are unsure of direction.
Before long autonomous runs, propose hypothetical scenarios for uncovered
trade-offs and stopping boundaries. Fix clear errors without an interview.
Make reflection an available habit, without imposing diaries or reminders.

Check the primary CLI at setup and whether it is the current client. Keep its
native instruction file canonical, safely linking other compatible entrypoints
when needed. Preserve distinct and nested instructions. Record the skill's
invocation and update policy in project ALIGNS.md documents.

## History-informed alignment

User-confirmed scope update: 2026-10-15 (Asia/Seoul). Partial confirmation only.

Support full paginated PR feedback collection and recent-first review. Offer
accessible project conversations, including supported Codex and Claude records,
as optional evidence. Show sources, scope and estimated retrieval/analysis time
before collection; reuse the user's choice and refine estimates as work proceeds.

Use taste invariants during self-alignment: scoped, revisable criteria supported
by the user's decisions across situations. Examine exceptions and conflicting
evidence. Do not infer immutable personality traits, treat team feedback as
personal consent, or promote repetition into an agreement. Keep the maintained
method in the skill and confirmed current criteria in ALIGNS.md.

## Revisit Alignment

Primary client: Codex. Canonical instruction file: AGENTS.md.
Use `$align`, or ask “Use the align skill to review this project's ALIGNS.md.”
This development repository discovers its local skill through
`.agents/skills/align`, linked to `skills/align`. Method changes are maintained
in this repository's Git history; do not install a second plugin copy here or
automatically pull over local development changes.
Source and user installation guide: https://github.com/hmmhmmhm/aligns.md .

Last aligned: 2026-10-12 09:24 (Asia/Seoul).
