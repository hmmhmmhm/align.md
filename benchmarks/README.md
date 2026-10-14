# ALIGN behavioral benchmark

This is a maintainer-authored synthetic benchmark of small project decisions. It tests whether an agent follows existing criteria, handles changes carefully, and avoids unnecessary clarification. It does not establish benefits for real users, independent replication, or general agent capability.

The first protocol plans 12 scenarios, three conditions, and three repetitions: 108 scenario runs. Four scenarios contain a second cold session, for 144 CLI sessions in a complete run. A partial run must report its actual coverage and leave unexecuted cells empty.

## Comparison

Every condition receives the exact same `common_instructions`, case criteria, task files, and user messages from [cases.json](cases.json). The common instructions give all conditions a strong baseline: reuse answers, preserve agreements, keep temporary exceptions temporary, ask about consequential uncertainty, continue independent work, and avoid invented facts.

| Condition | Project context |
| --- | --- |
| A | Common instructions and current criteria in AGENTS.md. No align skill. |
| B | Common instructions in AGENTS.md, with a neutral instruction to read ALIGN.md; identical current criteria in ALIGN.md. No align skill. |
| C | B plus the frozen current align skill, its normal discovery metadata, and the repository's recommended managed instruction block. |

B minus A estimates the effect of separating the criteria into a referenced file. C minus B estimates the complete recommended align setup under this harness, including its recurring-use instructions. C minus A is the combined comparison. Added context length, skill discovery, and the managed instruction block are part of the treatment; this design cannot isolate their individual effects. The harness must record any extra discovery text used in C. It must not add exclusive user preferences to C or explicitly invoke the skill in only one condition's task prompt.

No points depend on creating ALIGN.md, using a heading, reading a skill, or naming an output in the skill's preferred style. User-requested task outputs have ordinary filenames so their contents can be inspected. Current criteria may remain in the condition's existing instruction file; graders evaluate their meaning.

## Cases and scoring

Each case has three one-point checks. Its category and checks are declared in cases.json before evaluation. Cases cover clear error correction, a temporary exception, a lasting change, unresolved access policy, independent work during uncertainty, autonomy rehearsal, routine work, inherited implementation, repeated feedback, a declined review, an agreed tradeoff, and uncertainty about project direction.

The file checks verify narrow observable facts. A substring match cannot establish that an entire answer is correct. Semantic checks use the accompanying description and require inspection of the response and relevant file snapshots. Publish objective check results separately from model-judged semantic results. A semantic check remains pending until graded; missing grades never count as passes.

A model judge should receive the case, its rubric, responses, and before/after files under anonymous run labels. Conceal treatment labels and skill-use traces where possible. File names and prose may still reveal the treatment, so describe this as partially blinded judging. Use a fresh judge session without the acting agent's conversation. Record the judge model, prompt, evidence, and rationale for every decision. A separate model session is not an independent external evaluator. Disclose maintainer authorship and any shared model family.

Each check is pass (1), fail (0), or pending. Report completed checks over all planned checks, objective and semantic rates, and fully passed scenarios only when every check was graded. Report per-case and per-repetition results before an overall average. Compare paired case/repetition cells and retain all wins, ties, and losses. With three repetitions, differences of a few checks are descriptive observations; do not claim statistical significance or general population effects.

Also report wall time, available token usage, tool calls, clarification requests, and execution failures. Do not convert unavailable usage into zero or infer dollar costs without a recorded price source. Count actual requests for user input, including permission questions; punctuation alone is insufficient. Report whether clarification was useful separately from its count.

## Sessions and scripted users

Every turn in this version starts a fresh conversation. The second turn retains only the workspace left by the first; it receives no previous transcript or summary. Cases 02 and 03 test whether a temporary exception and an explicit lasting change carry correctly into later work. Case 09 tests a fixed followup that confirms a previously undecided preference. Case 12 supplies fixed evidence after an uncertain-direction request and asks for a concrete next step.

All scripted messages are sent verbatim and in order, regardless of the agent's response. There is no adaptive simulated user. First-turn checks use the first-turn snapshot, even when later work repairs a mistake. For a one-turn case that asks a useful question, the run ends at that question and is judged against the declared rubric. The benchmark measures the quality of that stopping point, not a completed dialogue.

Each case/condition/repetition starts from clean fixtures. Use the same model, reasoning effort, tool permissions, time limit, and client version throughout. Use a fresh HOME and CODEX_HOME for each scenario, with only an authentication link from the host. The client automatically supplies four bundled skills in every condition: imagegen, openai-docs, skill-creator, and skill-installer. C adds align. The runner audits this exact list and rejects ancestor AGENTS.md files; host personal instructions and installed skills are excluded. The sandbox restricts writes to the fixture and disables network access, but permits reads outside the fixture. The rubric is never supplied to the acting agent; trace review must check for unintended outside reads. Record whether the skill was discovered, but do not award points for discovery. An unavailable model or unsupported isolation flag is an execution limitation, not a reason to silently substitute another model or weaker isolation.

## Freeze and run

Before the first scored run, commit the protocol, cases, runner, grader, and tested skill. Record that Git commit plus SHA-256 hashes of these files and the complete skill tree in the run manifest. The commit cannot contain its own hash; the later manifest records it. A hash without a dated run record proves content identity, not when preregistration occurred.

The runner must refuse dirty or changed benchmark inputs after the freeze, or explicitly record the run as exploratory. Use a smoke fixture outside the 12 scored cases to validate client connectivity and result capture. Smoke outputs cannot be included in the score. Freeze the schedule before observing scored outputs, using a recorded seed or a balanced rotation of A/B/C within case/repetition blocks.

Keep raw responses, event traces, prompts, fixture snapshots, exit codes, timing, and grading evidence. Authentication material must never enter the evidence bundle. Publish the run manifest and the complete result matrix, including failed runs. If a process fails or times out, record the failure and leave unobservable checks pending. Do not replace it with a better attempt. Any diagnostic rerun receives a new ID and stays separate from the planned matrix.

Do not change the skill, cases, or rubric in response to scored results and retain the same benchmark version. Corrections require a new version with the old outputs retained. These scenarios use fresh fixtures rather than copying earlier development exercises, but their behavior categories informed skill development. They are held out from case-specific tuning only after the freeze, not a previously unseen independent test set.

## What this can establish

The benchmark can expose concrete regressions, unnecessary questions, lost preferences across cold sessions, and differences on the declared tasks. Many tasks may be easy enough for all three conditions to pass. A tie is useful evidence of no observed additional benefit on those tasks.

This small local behavioral pilot does not test installation on a clean machine, long autonomous execution, live external actions, multi-user agreement, or long-term user effort. The rehearsal case tests a discussion about autonomy, not an autonomous afternoon. The benchmark uses one selected model and client unless a later run explicitly expands that scope. Public source examples that informed this protocol are listed in [references.md](references.md).
