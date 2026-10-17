<p align="center">
  <img src="assets/aligns-header.png" alt="ALIGNS.md on a yellow and cyan background with a connected node diagram" width="100%">
</p>

<h1 align="center">ALIGNS.md</h1>

<p align="center">
  <strong lang="en">English</strong> · <a href="docs/translated-readme/ko.md" lang="ko">한국어</a> · <a href="docs/translated-readme/ja.md" lang="ja">日本語</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/hmmhmmhm/aligns.md/stargazers"><img src="https://img.shields.io/github/stars/hmmhmmhm/aligns.md?style=flat&amp;logo=github" alt="GitHub stars"></a>
  <a href="#install-align"><img src="https://img.shields.io/badge/Format-Markdown-222222.svg?logo=markdown" alt="Format: Markdown"></a>
  <a href="https://skills.sh/hmmhmmhm/aligns.md/align"><img src="https://skills.sh/b/hmmhmmhm/aligns.md" alt="Available on skills.sh"></a>
</p>

## Define what good means

ALIGNS.md records the goals and trade-offs you want your agent to use. The **align** skill helps you agree on those criteria and revisit them as the work changes.

<p align="center">
  <img src="assets/define-what-good-means.png" alt="Several paths converge on a shared reference point" width="100%">
</p>

## Keep expectations separate

Keep personal criteria in ALIGNS.md and the reusable alignment method in the skill. Connect the agreement through your primary agent instruction file, such as AGENTS.md or CLAUDE.md. Use Git history when available. Updating the skill never rewrites your agreement.

<p align="center">
  <img src="assets/keep-expectations-separate.png" alt="Three distinct connected panels represent execution, instructions, and expectations" width="100%">
</p>

## Fewer follow-up questions

Across 12 synthetic tasks, an agent starting with generic instructions needed nine clarification replies. With confirmed preferences already in ALIGNS.md and the align skill available, it needed none. Both conditions met the final criteria on all 12 tasks. The chart also includes four assumed setup replies for the ALIGNS condition. [Results and method](RETENTION_BENCHMARK.md).

<p align="center">
  <a href="RETENTION_BENCHMARK.md"><img src="assets/benchmarks/retention-comparison.svg" alt="Synthetic benchmark: nine task replies with generic instructions versus zero with saved preferences and align; four assumed setup replies included separately; final fit 12 of 12 in both conditions" width="100%"></a>
</p>

## Continuous self-alignment

Return to alignment when an important decision misses your intent, repeated corrections reveal a missing criterion, or you are unsure what to do next. You can also review selected PR feedback and accessible project conversations to find recurring criteria, called taste invariants, with their scope and exceptions. Choose recent or full history after seeing the estimated time. Before a long autonomous run, rehearse a few hypothetical choices. Clear errors get fixed directly; settled questions stay settled.

Brief requests work too. The agent checks existing context, then asks only about gaps that would materially change the result. You can agree on when it should ask and when it should proceed. Only confirmed lasting preferences go into ALIGNS.md.

<p align="center">
  <img src="assets/continuous-self-alignment.png" alt="A path gradually corrects its deviations from a steady reference line" width="100%">
</p>

## Install align

Paste this request into your agent. It sets up the maintained skill and an update
policy, then connects it to your project.

```text
Set up the maintained align skill from https://github.com/hmmhmmhm/aligns.md for this project. Read its current installation guide, check the existing installation and agent instructions, and use the supported installation route for my primary CLI. Ask which CLI I mainly use, and whether it is this one, only if that is unclear.

Enable supported automatic method updates. If the client has no native auto-update option, use a targeted update at the start of each alignment session, preserving the installation scope. Keep a working installed version when offline. Explain which update mode is active; do not add a scheduler or update unrelated packages.

Use the skill to establish or review ALIGNS.md and connect the primary instruction file to it. Preserve existing rules and distinct files; propose safe links for any other clients I use. Record the invocation and update policy in ALIGNS.md. Reuse clear answers, and suggest a focused alignment check after important judgment mismatches, before untested long autonomous work, or when I am unsure of the next direction. Method updates must never rewrite my personal criteria or count as agreement.
```

Or install the portable skill directly:

```sh
npx skills add hmmhmmhm/aligns.md --skill align
```

Then ask: **Use the align skill to set up ongoing alignment for this project.**

Native plugin installation is available for Codex and Claude Code. Claude Code
can update this marketplace automatically when enabled. Other routes can use a
user-authorized update at the start of an alignment session. No background
updater or universal automatic activation is assumed.

[Installation and updates](docs/usage.md) · [Behavioral benchmark](BENCHMARK.md) · [Intervention pilot](EFFORT_BENCHMARK.md) · [Preference transfer](DISCOVERY_BENCHMARK.md) · [Preference retention](RETENTION_BENCHMARK.md) · [Validation](docs/validation.md) · [Distribution](docs/distribution.md)

## License

[MIT](LICENSE). Copyright (c) 2026 hmmhmmhm.

<p align="center">
  <img src="assets/aligns-footer.png" alt="ALIGNS.md on a green background with overlapping coordinate grids" width="100%">
</p>
