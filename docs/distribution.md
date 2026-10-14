# Distribution

This page tracks distribution work, not changes to user alignment criteria.
Submission, acceptance, search visibility, and installation are distinct states.
Do not describe a pending or unverified listing as published.

## Source

- Repository: https://github.com/hmmhmmhm/align.md
- Skill: https://github.com/hmmhmmhm/align.md/tree/main/skills/align
- Name: `align`
- License: MIT
- Summary: Align an agent's decisions with a user's project expectations and keep the agreement current without repeated interviews.

## Service status

Directory evidence was checked on 2026-10-12. Those listings matched this
repository at that time; their current package versions have not been rechecked.
The maintained source now includes native Codex and Claude Code marketplaces.
These custom marketplaces are separate from official platform directory listings.

| Service | Route | Current evidence |
| --- | --- | --- |
| GitHub | Public source and release | Public source and the installable skill are available. Release packages include a skill ZIP and SHA-256 checksum. See the [latest release](https://github.com/hmmhmmhm/align.md/releases/latest). |
| [skills.sh](https://skills.sh/docs/faq) | Installation telemetry and directory indexing | Public [skill page](https://skills.sh/hmmhmmhm/align.md/align) verified. One real remote installation succeeded for Codex, Claude Code, and Cursor in a test project. |
| [askill](https://askill.sh/submit) | Submit GitHub URL | Submitted and indexed one skill. Public [listing](https://askill.sh/skills/704509) verified. |
| [OpenAgentSkill](https://www.openagentskill.com/submit) | Public submission queue | Submission accepted and marked public. [Listing](https://www.openagentskill.com/skills/hmmhmmhm-align-md-align) verified; static checks passed, not AI-reviewed. |
| [Agent Skill Hub](https://doc.agentskillhub.dev/guide/publishing) | GitHub import API | Imported as `hmmhmmhm/align`, version `2026.10.12`. Public [record](https://agentskillhub.dev/api/v1/u/hmmhmmhm/skills/align) and search for `ALIGN.md` verified. Source commit: `86e1ecc`. |
| [SkillsMP](https://skillsmp.com/about) | Public GitHub indexing | Public indexing documented; no self-service submission route found in the inspected site and documentation. A live search for `hmmhmmhm/align.md` returned no matches; listing is not yet verified. |
| [Skills Directory](https://skillsdir.dev/add) | GitHub issue submission | The site's linked repository and issue template both return 404. Submission currently unavailable. |
| [ClawHub](https://docs.openclaw.ai/clawhub) | Authenticated skill publication | CLI dry-run accepted `align-md` v0.1.0 with all three package files. The device authorization expired without login; a fresh owner authorization is required. Dry-run is not publication. |
| [Skillstore](https://skillstore.io/submit) | Submit GitHub URL for audit and review | Submission processed successfully and [registration PR #3749](https://github.com/aiskillstore/marketplace/pull/3749) created. The service's automated report marks the skill safe, and all three PR checks passed. The PR remains open pending final review. [Submission status](https://skillstore.io/ko/submissions/3c6ca451-04aa-435e-95c3-5c51e1094fec). Publication is not yet confirmed. |
| [Skills Directory](https://www.skillsdirectory.com/submit) | Authenticated submission | The submission route requires sign-in. The owner login request timed out with the sign-in page unchanged; no submission made. This is a different service from `skillsdir.dev`. |

## Platform directories

The [Claude directory documentation](https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory)
describes installing directory skills and publishing within an organization.
It does not establish an open, public self-service listing route for this skill.
Do not treat a personal installation or an organization-only publication as
public distribution. No official Claude directory listing is claimed.

## Native installation and updates

Use the [installation guide](usage.md) for the Codex plugin, Claude Code plugin,
or portable skills CLI. A plugin version is the alignment method version, not
the project agreement version. Directory snapshots may lag behind GitHub.

## Maintaining distribution

Publish source changes first, then refresh services that snapshot the skill.
Keep actual receipt or listing URLs and distinguish delayed indexing from
confirmed search visibility. Do not create duplicate submissions to simulate
adoption or inflate installation counts. Expand this list as relevant, active
distribution services are discovered; universal coverage is not assumed.
