# Project Alignment

## Purpose

Help agents make decisions that reflect the user's judgment and
continuously identify and address gaps between their work and
the user's expectations.

Alignment is an essential part of working with AI. It deserves
a dedicated document because expectations differ between users
and evolve over time.

## Role of ALIGN.md

ALIGN.md holds the user's current goals, priorities, preferences,
constraints, and decision criteria.

Keep these separate from harness configuration and general agent
instructions. AGENTS.md should explain when and how to use ALIGN.md,
while ALIGN.md remains the source of alignment criteria.

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

Keep only current alignment criteria in ALIGN.md. When Git is
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

## Presentation and Licensing

- Write repository documentation in English.
- Do not use em dashes or emoji.
- Keep the README brief, with a centered title, useful badges,
  and a copyable prompt.
- Publish the project publicly under the MIT License.

Last aligned: 2026-10-12 09:24 (Asia/Seoul).
