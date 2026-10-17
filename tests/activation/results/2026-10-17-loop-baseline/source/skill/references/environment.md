# Connect the user's environment

At setup, inspect relevant existing files before proposing a layout. Ask which
CLI is primary and whether it is the current one only if context does not answer.
For equally used clients, propose AGENTS.md as the neutral canonical file. Record
the choice in ALIGNS.md; do not ask again until the user changes tools or evidence
shows the mapping is broken.

## Inspect, propose, connect, verify

- Codex normally uses AGENTS.md. Check AGENTS.override.md, parent and nested
  instructions and configured fallback names; an override can shadow AGENTS.md.
- Claude Code uses CLAUDE.md and may also load .claude/CLAUDE.md and scoped rules.
  Preserve those scopes and any tool-specific syntax.
- For other clients, confirm their actual entrypoint from local configuration
  or current official documentation. Do not assume every client reads Markdown
  filenames, supports symlinks, or understands Claude's @ imports.

Prefer the primary CLI's native file as the one source of shared instructions.
Append the short [alignment block](../assets/instruction-block.md) there. Connect
only additional clients the user actually uses. For example, with Codex primary
and no existing CLAUDE.md, `CLAUDE.md -> AGENTS.md` can share the instructions.
The inverse can work for a Claude-primary project. Use relative links inside the
project so the checkout stays portable. Link instruction files, never link
ALIGNS.md to the upstream skill or the source repository's personal agreement.

If another entrypoint already has distinct content, show what would need merging
and preserve it until that concrete replacement is authorized. Do not use force
symlink options, delete files, or flatten nested policies. For incompatible
formats or systems without usable symlinks, use a supported import or a short
pointer requiring the agent to read the canonical file. Keep tool-specific
settings where the tool expects them. Report fallback instead of claiming a
single file is automatically loaded everywhere.

## Optional deterministic helper

Requires Python 3. Run from a known project path. Default mode only reports a plan:

```sh
python3 <installed-skill>/scripts/connect_project.py --project <project> --primary codex --also claude-code
```

After the user's setup request authorizes these changes, add `--apply`. Omit
`--also` if only one client is used. The helper appends or refreshes one managed
block and creates only absent relative links. It refuses conflicting files,
symlinked canonical files, and shadowing instruction files rather than guessing
how to merge them. These need contextual review, not repeated retries.

Verify file targets and preserved content. Then check the target client's loaded
instructions, using a new session if needed. A valid filesystem link is not proof
that a client actually loaded it. Report precisely which checks were performed.
Do not modify global client configuration or install persistent hooks as a side
effect of a project-file connection. Plugin hooks belong to the chosen explicit
plugin installation and its documented lifecycle.
