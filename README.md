# ALIGN.md

Give your agent a shared understanding of what a good outcome means. ALIGN.md captures your goals, priorities, trade-offs, and preferences, then keeps them aligned as the project evolves—so you spend less time repeating context or correcting avoidable misunderstandings.

## Copy the prompt

Paste this into your agent's chat in any new or existing project.

```text
Create ALIGN.md at the project root to align my expectations with the agent's decision-making. Capture the project's direction, success criteria, scope, priorities, constraints, preferences, things to avoid, and the boundaries between autonomous decisions and decisions that need my input. Keep detailed task lists elsewhere.

[Where to start]
- If ALIGN.md exists, review the existing agreements and changes since the last alignment.
- Otherwise, adapt to the project's stage:
  - Before work begins: clarify the purpose, intended users, desired outcomes, and constraints. Avoid committing to implementation choices prematurely.
  - Work already underway: summarize the existing documentation and implementation, then clarify what to keep or change. Do not assume the current implementation reflects my intentions or preferences.

[Initial agreement and documentation]
1. Ask 1–3 related questions at a time, starting with the most consequential unresolved matters. Use examples or options to clarify abstract expectations and trade-offs. Distinguish assumptions from open questions. Do not ask again about something I have already answered or made clear in the current request.
2. Once the essentials are clear, present a concise draft. Refine it until I confirm it is sufficient, then save it. Do not prolong the conversation just to fill every category. Distinguish requirements from default preferences, and briefly explain the reasoning behind important criteria.
3. Preserve existing files and instructions, changing only what is needed; create missing files. In AGENTS.md, instruct agents to read ALIGN.md at the start of work and apply it when defining scope, making key decisions, and reviewing results. Also record the ongoing alignment rules below in AGENTS.md.

[Ongoing alignment]
- At the start of work, review available change history and conversations for inconsistencies with ALIGN.md or potential new principles and preferences since the last alignment. Do not revisit previously reviewed matters or repeat questions without new evidence.
- Only raise meaningful inconsistencies or candidates for new guidance. Briefly explain the evidence, propose a concrete revision, and ask whether it should become a lasting criterion. If records are insufficient, state the limitation and ask only what is needed for the current decision.
- Make adjustments autonomously within existing agreements. Ask before changing goals, scope, priorities, or important constraints only when my intent is unclear. Do not seek approval again for changes I have explicitly requested. Continue work that does not depend on an unresolved decision.
- If my current explicit request conflicts with ALIGN.md, follow the applicable instruction hierarchy. Do not turn a one-off exception into a permanent preference. Update the document when my intent to make a lasting change is clear. Never rewrite agreements to justify your own choices or results.
- End ALIGN.md with "Last aligned: YYYY-MM-DD HH:mm (time zone)". This records when I confirmed and agreed to the document's expectations and criteria. Do not update it merely because the document was read, edited, or automatically reviewed. If only specific items were agreed upon, record their confirmation times separately instead of implying that the entire document was reconfirmed.

Start with a brief summary of your understanding. Ask the most important questions if any remain; otherwise, proceed without unnecessary reconfirmation.
```
