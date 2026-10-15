# Installation and method updates

Trusted source: https://github.com/hmmhmmhm/align.md . Use its current installation
instructions and inspect the selected package. Prefer the user's existing skill
manager. Do not install multiple copies of `align` for the same client.

## Choose a route

- **Codex plugin:** add the repository's `align-md` marketplace and install
  `align-md@align-md`. Invoke `$align` or select the installed skill. The package
  has no Codex lifecycle hook. Project instructions supply recurring triggers.
- **Claude Code plugin:** add `hmmhmmhm/align.md` as a marketplace, install
  `align@align-md`, and invoke `/align:align`. This installation includes a
  static SessionStart reminder. It reads no project data, makes no network
  requests, and changes no files. A third-party marketplace's native auto-update
  is off by default; enable it only within the user's installation/update request.
- **Portable skills CLI:** `npx skills add hmmhmmhm/align.md --skill align`.
  Select only the intended agent and project/user scope. Use `--agent codex`
  or `--agent claude-code` when known; use `-g` for user scope, not by default.
  Other clients must be supported by the current installer and verified locally.

For exact client commands and current limitations, consult
https://github.com/hmmhmmhm/align.md/blob/main/docs/usage.md . If no installer,
network access, or compatible client is available, state the gap and give the
next step; never report installation as complete without checking discovery.
Manual folder copies are a fallback and have no automatic upstream update.

## Set update policy once

Distinguish the installed method from the user's agreement. Record the chosen
route, scope, invocation and update policy in ALIGN.md's Revisit alignment section.
Offer the supported native auto-update option. For clients without a verified
native option, offer **update when alignment starts**: the agent performs one
targeted refresh before the next alignment session, using the recorded route.
Enable this only when the user requests or accepts ongoing updates. Do not ask
again each session after that authorization. Manual updates remain available.

With update-when-alignment-starts enabled:

1. Once per alignment session, before doing the alignment work, inspect the
   recorded route and supported commands. Refresh only this package from the
   trusted source. Do not update unrelated skills or migrate package managers.
2. Respect pinned versions, local modifications, client permissions and network
   boundaries. If an update needs broader access, leave it pending and continue
   with the installed method; do not silently install a scheduler or background
   process. On offline or transient failure, use the installed version and
   mention the limitation once. Do not retry in a loop.
3. Verify the installed version and reload the skill if the client supports it.
   If a restart is required, tell the user and use the current loaded version
   consistently for this session. Never claim the update is already active.
4. Never change project criteria, timestamps, or tool settings just because the
   method changed. Review setup migrations separately if a new version needs one.

Current targeted refresh commands (check support in the installed client):

```sh
# Codex plugin route, our one-plugin marketplace
codex plugin marketplace upgrade align-md
codex plugin add align-md@align-md

# skills CLI, preserve the actual installation scope
npx skills update align -p
# OR, for a user-scoped installation
npx skills update align -g
```

Claude Code uses its marketplace auto-update setting or `/plugin update
align@align-md`, followed by `/reload-plugins` or a new session when required.
This is conditional delivery through the host, not a guarantee that every
installed copy updates while idle. Never upload ALIGN.md, conversations, or
reflection answers to improve the shared method. A user can separately choose
to submit feedback with only the information they authorize.
