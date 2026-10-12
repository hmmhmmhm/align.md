# Using align

## Install

From the target project, run:

```sh
npx skills add hmmhmmhm/align.md --skill align
```

The installer lets you choose the agent and installation scope. To explicitly
install a project-scoped copy for a particular agent:

```sh
npx skills add hmmhmmhm/align.md --skill align --agent codex
npx skills add hmmhmmhm/align.md --skill align --agent claude-code
```

Use `--list` to inspect discoverable skills without installing. Add `--global`
only if you want the skill available across your projects. The CLI requires
a supported Node.js installation and network access.

For manual installation, copy the complete `skills/align` folder, including
its license, into your agent's supported skills directory. A release archive
contains the same folder. No runtime scripts or extra services are required
by the skill itself; Git is optional.

## Start or resume alignment

Ask in ordinary language:

> Use the align skill to establish this project's ALIGN.md with me.

> Use the align skill to review what changed since our last alignment.

In clients that support `$` skill invocation, you can use `$align`.
Invocation syntax and automatic selection depend on the client.

The agent first reads existing context. It asks a few important questions,
shows a short draft, and saves the agreement after confirmation. If the user
has already made the relevant decision clear, it proceeds without asking again.

## Files and responsibility

| File | Purpose |
| --- | --- |
| `ALIGN.md` | The user's current project expectations and decision criteria. |
| `AGENTS.md` | Instructions to read, apply, and maintain the agreement. |
| Git history, when available | Previous versions and changes to the criteria. |

These are files in the target project. This repository's own ALIGN.md describes
the development of the align skill and is not a template of universal user
preferences. The skill follows the target user's language and conventions.

Installation does not add a background watcher or guarantee activation on
every task. Check whether your agent reads `AGENTS.md`. If it uses another
instruction entrypoint, preserve that file and add an appropriate reference
to the agreement and its operating rules, or invoke the skill manually.

## Changes and timestamps

An explicit lasting preference can update the agreement immediately. An
exception for one task does not change the default. An uncertain inference
is proposed to the user rather than silently stored as a preference.

`Last aligned` records confirmation of the full document, not a file edit or
automated review. A partial confirmation is attached to the affected criterion
without moving the full timestamp. Use a labeled time zone.

When Git is unavailable, the current agreement still works, but historical
comparison may be incomplete. The skill reports the limitation rather than
creating Git or a separate history log. It does not commit or publish merely
because a project uses Git.

## Compatibility

The skill uses the [Agent Skills format](https://agentskills.io/specification)
and has no mandatory product-specific tools. The
[skills CLI](https://github.com/vercel-labs/skills) supports installation into
multiple agent clients. Installation compatibility is different from verified
behavior in a particular client; see [validation](validation.md) for what was
actually checked.

## Update or remove

Use your installer's update and removal commands. With the skills CLI:

```sh
npx skills update align
npx skills remove align
```

Removing the installed skill does not remove the project's agreement or its
instruction references. Keep or revise those intentionally.
