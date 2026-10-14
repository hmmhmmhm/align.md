# Maintaining the method

Improve align from observed mismatches and user feedback. Keep the shared skill
small, and put guidance used only during setup or recurring review in the linked
references. Personal agreements belong to users, not to a release migration.

## Release a method update

1. Update the skill and the affected reference. Record the behavior change in
   CHANGELOG.md. Check realistic scenarios when a change affects judgment.
2. Keep VERSION, both plugin manifests, the Claude marketplace entry, and skill
   metadata on the same version. Claude uses the version to notice updates.
3. Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`.
   Validate the skill with Skill Creator when available. Test affected install
   paths in an isolated project; never use personal agreements as fixtures.
4. Publish the tested source, tag that exact commit, and attach a ZIP of the
   complete `skills/align` folder plus its SHA-256 checksum to the GitHub release.
   Native plugin installations use the repository manifests.
5. Refresh directories that snapshot releases, and record actual listing evidence
   in docs/distribution.md. Do not describe a submission as acceptance.

## Updating installed copies

Follow the client's supported update route in docs/usage.md. Native auto-update
settings, or an agreed refresh when alignment starts, bring users the revised
method. An update must not alter project ALIGN.md files, confirmation times,
client permissions, or unrelated packages. Keep a usable installed version if
refresh fails. Report reload requirements instead of claiming immediate activation.

The source repository itself uses the local skill through `.agents/skills/align`.
Keep AGENTS.md canonical for Codex here; do not auto-update this development
checkout over uncommitted changes or install a duplicate plugin.

## Design reference

[Superpowers](https://github.com/obra/superpowers) demonstrates native plugin
distribution and a session bootstrap. ALIGN uses that separation between discovery
and method, with a static Claude reminder and project instructions for recurring
triggers. It does not start an interview on every session or update through a
networked hook.
