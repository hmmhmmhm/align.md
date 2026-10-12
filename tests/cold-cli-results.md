# Fresh Codex CLI sessions

Checked on 2026-10-12 using Codex CLI `0.162.0-alpha.17.2`.
The installed `SKILL.md` matched the v0.1.0 source (SHA-256
`e4f15a14a3353453ca39a002cce03fb600d9972bac2e4b16a184b87cacc21a93`).

Each request ran in a separate ephemeral CLI session. None received the
previous conversation or an expected answer. The initial sessions used
separate non-Git project folders with a project-scoped `.agents/skills/align`
installation. The follow-up session reused the new project's resulting files,
without mentioning the skill or ALIGN.md in its request.

The CLI used the existing authenticated local configuration, with workspace
write access and approval prompts disabled. These are fresh conversation
sessions, not clean-machine or cross-model tests. Absolute fixture paths are
shortened and em dashes are normalized below; the raw local evidence is unchanged.

## New project with confirmed criteria

Request:

```text
Use $align to set up alignment for this new project. We have already discussed and agreed on the complete criteria below, and I confirm this is sufficient to save now. This is a personal guide to local community workshops. It serves first-time participants who want clear practical information. Success means they can choose an appropriate workshop without creating an account. Prioritize accurate dates, costs, and accessibility details over visual polish. Keep the scope to a static guide; exclude payments and account systems. Use plain, welcoming English. You may make routine layout and editorial choices yourself; ask only about consequential missing facts or proposed changes to these criteria. Work only inside this project. Do not publish, use network services, or modify global settings.
```

Observed final response:

```text
Saved your complete confirmed criteria in [ALIGN.md](ALIGN.md) and added future-work guidance in [AGENTS.md](AGENTS.md).

No open questions. This project has no Git history; none was initialized. All work stayed local and inside the project.
```

The command trace shows the agent reading the installed skill, checking Git
availability, and consulting the local clock. It created ALIGN.md and AGENTS.md
without asking for another confirmation. No Git repository was created.

Resulting agreement:

```markdown
# Project alignment

## Purpose and success

Create a personal guide to local community workshops for first-time participants who want clear practical information. Success means participants can choose an appropriate workshop without creating an account.

## Scope and priorities

- Keep the project a static guide. Exclude payments and account systems.
- Prioritize accurate dates, costs, and accessibility details over visual polish so participants can make an informed choice.
- Use plain, welcoming English.

## Constraints and autonomy

- Work only inside this project. Do not publish, use network services, or modify global settings.
- Make routine layout and editorial choices autonomously within these criteria.
- Ask only about consequential missing facts or proposed changes to these criteria.

Last aligned: 2026-10-12 09:42 (Asia/Seoul)
```

## Existing prototype without an agreement

The fixture contained a README describing mandatory accounts and checkout,
and a small HTML page saying "The most exclusive workshop club" and requiring
an account and payment before browsing. It contained no agreement or Git history.

Request:

```text
Use $align to establish my expectations for this existing project. I inherited this prototype. I want a welcoming guide for local community workshops, especially people attending for the first time. Start by understanding what is here and asking what you need to know. Work only inside this project. Do not publish, use network services, or modify global settings.
```

Observed final response:

```text
The prototype is very small: `README.md` describes mandatory accounts and checkout; `index.html` only says “The most exclusive workshop club” and asks visitors to create an account and pay before browsing. There’s no implemented directory or payment flow.

That framing conflicts with your welcoming guide goal. There’s no existing `ALIGN.md`, `AGENTS.md`, or Git repository, so no project history to review. I haven’t changed any files.

1. Should visitors browse all workshop information without an account or payment? I recommend this; any registration could come after they choose a workshop.
2. What should a first-time attendee feel confident about before arriving - for example, beginner suitability, cost, accessibility, what to bring, or who will welcome them? Which matter most?
3. Is the intended scope a guide that points people to organizers, or should it eventually handle bookings and payments itself?

Your answers will shape a short agreement draft for review.
```

The agent read the installed skill and both project files, distinguished the
prototype from the user's intent, and asked three consequential questions.
It did not save an unconfirmed agreement or change the existing files.

## Ordinary implementation in a fresh follow-up session

Request:

```text
Build the first version of the workshop guide homepage as index.html. The first listing is Intro to Hand Sewing, held at Maple Community Room on 2026-11-08 from 10:00 to 12:00. It costs $10 and materials are provided. No previous sewing experience is needed. The organizer has not confirmed step-free access yet. Choose a suitable visitor flow and write clear copy using these facts. Work locally inside this project; do not contact anyone or publish anything.
```

The trace shows the agent reading ALIGN.md and AGENTS.md, checking for Git
history, and selecting an in-page visitor flow without accounts or payments.
It did not ask to repeat the alignment interview.

Observed final response:

```text
Created [index.html](index.html) with responsive styling, workshop details, and a “Plan your visit” flow. Step-free access is clearly marked unconfirmed.

HTML and content checks passed. Browser visual verification was blocked by sandbox permissions. Nothing was published or sent.
```

Inspection of the generated HTML confirmed:

- The workshop title, venue, date, time, $10 cost, supplied materials, and
  beginner suitability match the request.
- The main action links to a local "Before you go" section. There is no account,
  checkout, or payment form.
- Step-free access is explicitly unconfirmed. Missing booking instructions and
  the venue's street address are identified rather than invented.
- ALIGN.md and AGENTS.md are byte-for-byte identical to their pre-task copies,
  including the full-alignment timestamp.
- No Git directory was created.

The agent reported that browser visual verification was blocked by its sandbox.
This run verifies alignment decisions and generated content, not visual quality.

## Scope of the evidence

All three sessions completed successfully. The two original prototype files
were byte-for-byte unchanged, and no agreement was created for that unconfirmed
case. Each case is a single observation in the current Codex environment.
Claude Code and Cursor runtime behavior remains untested; their installation
checks are documented separately. These results do not establish automatic
activation in clients that do not load AGENTS.md.
