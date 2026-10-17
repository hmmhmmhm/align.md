# Use align over time

The skill contains the evolving alignment method. Your project's ALIGNS.md
contains your criteria. Install the skill once through one route, connect your
project instructions, and use it again when there is something worth aligning.

## Ask your agent to install it

Copy the [installation request](install-request.txt), or say:

> Set up the maintained align skill from https://github.com/hmmhmmhm/aligns.md for
> my primary CLI. Connect it to this project and enable supported method updates.

The agent checks what is already installed, which client you mainly use and
whether that is the current one. It asks only if context leaves the choice open.
It selects one installation route and verifies discovery. An installation request
cannot bypass the client's permissions or install into another person's account.

## Codex plugin

With a Codex CLI that supports custom plugin marketplaces:

```sh
codex plugin marketplace add hmmhmmhm/aligns.md --ref main
codex plugin add aligns-md@aligns-md
```

Open a new session if the skill is not yet visible. Select **align** or use
`$align`. The repository includes a Codex marketplace and plugin manifest;
it is not a claim of inclusion in OpenAI's official directory.

To refresh the marketplace snapshot and installed package:

```sh
codex plugin marketplace upgrade aligns-md
codex plugin add aligns-md@aligns-md
```

The official documentation does not promise an automatic refresh interval for
all custom marketplace installations. Use the client's native update setting
where supported, or agree to a targeted refresh when an alignment session starts.
This Codex package is hook-free; recurring triggers live in project instructions.

## Claude Code plugin

Inside Claude Code:

```text
/plugin marketplace add hmmhmmhm/aligns.md
/plugin install align@aligns-md
```

Invoke `/align:align`. The plugin includes a static SessionStart reminder for
startup, resume, clear and compact. It performs no networking, file changes or
project-data collection. It does not start an alignment interview on every task.

For native automatic updates, open `/plugin`, select **Marketplaces**, choose
**aligns-md**, and enable auto-update. Third-party marketplaces do not enable it
by default. Manual refresh is `/plugin update align@aligns-md`. Use
`/reload-plugins` or a new session to load changed files when required.

## Portable skill installation

From the target project:

```sh
npx skills add hmmhmmhm/aligns.md --skill align
```

The skills CLI lets you select the client and scope. For example, add
`--agent codex` or `--agent claude-code`; add `-g` only for a user-wide installation.
Use `--list` to inspect the repository first. Node.js and network access are
required for this installer, not for reading the skill itself.

Update only this skill, preserving its installed scope:

```sh
npx skills update align -p
# User-wide installation instead:
npx skills update align -g
```

This command is a refresh, not a persistent background updater. A manual copy of
the entire `skills/align` folder is also possible, but requires manual replacement
for updates. Avoid duplicate plugin and folder installs for the same client.

## Make updates part of alignment

At setup, choose a supported native auto-update setting, **update when alignment
starts**, or manual updates. The copied installation request authorizes the first
two as supported by the client. Record the actual mode and installation scope in
ALIGNS.md. For update-when-alignment-starts, the project instruction tells the agent
to perform one targeted refresh before an alignment session, not every task.

Offline failures fall back to the installed version. Local edits, pinned versions,
permission changes and migrations need separate handling. If a client requires a
restart, report that the new method is not active yet. None of these updates
change your criteria, confirmation timestamps, or project files automatically.

## Connect project instructions

Keep the primary CLI's instruction file as the canonical source. For Codex this
is normally AGENTS.md; for Claude Code, CLAUDE.md. Confirm actual loading rules,
including overrides and nested instructions. Use safe relative symlinks for
additional clients with compatible instruction formats, such as
`CLAUDE.md -> AGENTS.md`, only when the secondary path is absent or replacement
has been explicitly agreed after reviewing its content.

Do not overwrite a distinct instruction file. Preserve tool-specific rules and
use a supported import or pointer when sharing the whole file is inappropriate.
The optional Python 3 helper plans changes before applying them:

```sh
python3 <installed-skill>/scripts/connect_project.py --project <project> --primary codex --also claude-code
```

Add `--apply` to carry out a conflict-free, authorized plan. It refuses conflicts
and shadowing files. The agent must still verify which instructions its client
actually loads. Installation and a valid symlink alone do not prove activation.

Generated ALIGNS.md documents include the working skill invocation, trusted
source, update policy, primary CLI and canonical instruction file. They do not
copy the entire method. This repository's own ALIGNS.md is not a universal set
of preferences for users to inherit.

## Use it at meaningful moments

- “Use align. That decision was different from what I meant.”
- “Before the afternoon automation, let's rehearse a few choices with align.”
- “I don't know what to work on next. Help me clarify it with align.”
- “Use align to review what changed since our last agreement.”

Existing clear criteria are applied without another interview. Obvious errors
are fixed directly. Important unresolved choices get focused questions. A
hypothetical rehearsal does not execute actions or authorize the real loop.
The skill installs no daily reminders, schedule or diary. Reflection stays local
unless you separately choose to share it.

## Decide when the agent should ask

A short request can leave room for judgment. The agent first checks the project
and earlier decisions. It asks when missing context would materially change
the result or scope, and proceeds with minor reversible choices within its
authority. Related questions are grouped; answered questions stay answered.

If misunderstandings keep causing rework, use align to agree on when you want
questions. For example: "For open-ended design requests, show me a brief outline
before implementation. Handle small fixes using the existing conventions."
The skill records a lasting preference only when you request or confirm it.
An answer about one task stays with that task unless you say otherwise.

## Confirmation and removal

Explicit lasting preferences can update the relevant criteria. One-off exceptions
leave defaults intact. `Last aligned` changes only when you confirm the full
agreement; partial confirmations are attached to the affected criteria. Git,
when present, records history. The skill does not initialize or publish Git.

Remove the package with the client or installer's removal operation, such as
`npx skills remove align`. Review alignment pointers or symlinks separately;
uninstalling should not remove your agreement or unrelated instructions.

## Verified sources

- [Codex local skills and symlinks](https://learn.chatgpt.com/docs/build-skills)
- [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins)
- [Claude plugin updates](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated)
- [Claude plugin versions](https://code.claude.com/docs/en/plugins-reference#version)
- [skills CLI](https://github.com/vercel-labs/skills)


## Learn from earlier feedback

Ask: "Use align to find recurring criteria in my recent PR feedback and this
project's available conversations. Show the scope and estimated time first."
You can also choose the full PR history, a date range, selected transcripts or
no history. The agent offers sources it can actually access and asks once for
the scope. Codex and Claude logs are optional; availability and formats vary.

The skill looks for taste invariants: criteria that remain consistent across
observed situations. It checks the context and exceptions before proposing a
lasting rule. Team requirements, assistant suggestions and one-off corrections
are not automatically personal preferences. Confirmed criteria guide later work;
new evidence can change them.

Python helpers provide metadata-only planning, paginated PR collection, resumable
PR scans and project-scoped JSONL parsing. They make no model calls. The agent
reviews the evidence and proposes changes for confirmation. Time estimates show
their assumptions and are refined from actual volume and processing speed.
Raw evidence stays in a chosen private working file outside Git. It is not added
to ALIGNS.md or published with the skill.

See [history review and collector commands](../skills/align/references/history.md).

## Upgrading from ALIGN.md

The project and agreement file are now named ALIGNS.md. The skill command is still
`$align`. Read the existing `ALIGN.md` before migrating it. Once the rename is
authorized, move it to `ALIGNS.md` and update references in the project instruction
files. Preserve its criteria and confirmation date. If both files exist, resolve
the differences before changing either.

The repository is now `hmmhmmhm/aligns.md`; the Codex plugin and marketplace are
`aligns-md`. Replace old marketplace registrations with the installation entries
above when upgrading, and remove the old registration after the new one works.
Do not keep duplicate plugin installations.
