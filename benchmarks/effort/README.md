# Scripted user intervention burden

This prospective pilot asks whether ALIGN reduces repeated preference questions and corrections across fresh conversations. It counts setup and maintenance work as well as later replies. The main comparison is an agent explicitly instructed to keep useful project notes. A tie against that baseline is a valid result.

This protocol was written before scored execution. Published runs and their results are recorded separately. The [earlier behavioral pilot](../../BENCHMARK.md) has a different design and remains separate. Its scores cannot answer this pilot's question.

## Conditions and tasks

[cases.json](cases.json) defines two authored preference profiles, three conditions, and two repetitions. Each of the 12 trajectories has a setup episode followed by five task episodes. Every episode starts a new conversation with the same trajectory's files. Replies within an episode retain that episode's context. No transcript or generated summary carries into the next episode.

| Condition | Persistent context |
| --- | --- |
| A: ordinary writable project | Ordinary instructions; the agent may save authorized preferences in any project file. |
| B: explicit persistent notes | Instructions to read and maintain PREFERENCES.md, reuse answers, and distinguish temporary exceptions from lasting changes. |
| C: maintained ALIGN setup | The frozen align skill, its recurring-use instructions, and an initially empty ALIGN.md. |

The shared prompt identifies Codex as the current and primary client and AGENTS.md as canonical. The environment is already provisioned. Installation, client discovery, and method-update effort are outside this pilot; preference elicitation and maintenance costs are included. All conditions may save the same answers with the same consent. None starts with the user's hidden preference values. C's extra instructions and method context are part of the treatment. The comparison cannot isolate the filename, skill, and additional instructions. B is the primary comparator; C versus A is secondary.

Each profile offers three setup questions that can be batched. One profile produces notices, applying heading, date, and contact preferences. Its date preference determines both formatting and a template selection. The other chooses implementation options for a small website using hosting, dependency, and analytics criteria. Each sequence contains routine work, a temporary exception, a return to the standing policy in another context, a lasting change, and a new unresolved choice. Option IDs vary across tasks. The final task requires a question about its newly introduced channel or retention choice, even if a guess would produce the right artifact.

These are small structured tasks. They exercise remembering and applying declared choices, including a simple option mapping. They do not represent broad writing quality, complex judgment, or a long autonomous project. The two profiles are fixtures, not two human participants. Repetitions measure additional executions of those fixtures.

## Fixed user responses

Actors use a public interface: ask for a batch of named preference IDs, or submit the task. The harness returns the exact answer strings in cases.json. There is no model impersonating a user and no maintainer rewriting answers after seeing a response. All arms can ask the same questions in the same episode. The actor receives available question IDs and task choices, but not the answer bank or expected output.

Each turn ends with one JSON object:

```json
{"action":"ask","keys":["heading","date_style","contact"]}
```

or:

```json
{"action":"submit"}
```

For a task submission, the harness checks output.json against the expected object. A failed submission receives a fixed correction identifying only the failed fields and their expected values. It does not reveal preferences for unrelated fields. A malformed response or unknown question receives a protocol correction, which consumes a reply. Audit all non-final assistant messages for questions outside the interface before claiming a favorable result. Such questions can create unmeasured burden; unresolved side-channel questions prevent a favorable interpretation even if the final JSON parses. A required question that was skipped also fails its check. Multiple failing fields tied to one preference count as one supplied preference unit in that reply. Corrections to body text or JSON structure count as task or protocol corrections, not preference disclosures.

The harness allows at most two user replies after the initial prompt in each episode. Every reply counts, including setup questions, redundant confirmation, repair requests, and malformed-response corrections. After the limit, an unresolved episode is a terminal failure. No free retry follows a parser error, timeout, or rejected submission. Successful early submission ends the episode. Each trajectory therefore requires at least six actor calls and at most 18, for 72 to 216 calls in a complete run. Actual usage must be reported.

Answers about standing preferences include permission to save them. Temporary answers explicitly limit their scope. The lasting change is supplied in its task prompt to every condition. The later channel or retention answer is available only when that new task introduces the question. Its first disclosure is legitimate clarification, not repeated work.

This oracle is unusually consistent: it provides exact, helpful feedback and does not become tired or misunderstand a question. The rigid interface also makes questions easier to classify than ordinary conversation. Results depend on these choices.

## Outcomes fixed before the run

The measurement is scripted user intervention burden. It is not elapsed human time, cognitive load, or a validated effort scale. Keep its components separate; do not convert tokens or replies into human minutes or combine them with invented weights.

For each trajectory, record:

- Additional user replies, including all setup and repair replies. Report setup and task totals separately and together.
- Preference units supplied by the user. Each distinct preference ID supplied in an initial prompt or scripted reply counts once in that message. A batch of three preference answers costs three units and one reply. Count explicit exception and lasting-change instructions too.
- Repeated preference units. A preference ID disclosed in a scripted reply counts as repeated if that ID was supplied earlier through an answer, correction, or explicit task instruction. This is an ID-based count, not a semantic comparison of values. Explicit temporary exceptions and lasting changes supplied in initial prompts count toward total units but are not themselves repeated units. A later question about a change already stated in the prompt is repeated. Report requests about already answered preferences separately where they can be identified.
- Question keys, correction rounds, failed fields, protocol errors, and terminal failures. Keep legitimate new-choice questions separate from repeated questions.
- Characters in initial user prompts and scripted replies, split by setup and task. Include the setup request, consent text, maintenance instructions, and corrections. Report initial task wording separately because it is mostly fixed across conditions.
- Actor calls, duration, input/output tokens when available, and tool use as resource diagnostics. Missing usage remains missing.

Let U be total preference units supplied, R additional replies, and T the four planned trajectories per condition. Compare totals over all four paired profile/repetition cells, keeping failures in the denominator. For each baseline X:

```text
relative preference-unit reduction = (U_X - U_C) / U_X
mean reply reduction per trajectory = (R_X - R_C) / T
relative reply reduction = (R_X - R_C) / R_X
```

A zero baseline denominator makes that relative reduction undefined. Report the raw counts and mark the threshold unmet. Show repeated preference units separately; do not hide an increase behind fewer total replies. Publish a paired table with setup and task costs, completed tasks, and all wins, ties, and losses. Also show cumulative cost after setup and each task so any setup payback is visible. Never extrapolate a payback point beyond the observed five tasks.

The prespecified descriptive decision rule for an observed reduction requires all of these:

1. C reduces total supplied preference units by at least 20% versus B.
2. C reduces additional replies by at least 20% and at least one reply per trajectory versus B.
3. C does not increase repeated preference units versus B.
4. Every planned C task passes every artifact and required-question check, and C has no execution failures. Every paired task that B passes must also pass in C.

These are project-chosen thresholds for this pilot. They are not statistical significance tests or validated thresholds of meaningful human benefit. If any requirement is unmet, report that the pilot did not meet its decision rule. If B ties or beats C, say so. If fewer C replies accompany failed or capped tasks, report those failures without describing the difference as reduced burden. C versus A uses the same descriptive calculations and remains a secondary comparison.

## Quality and failure reporting

A task passes only when its final output has the exact requested JSON fields and values and satisfies any required-question condition. Report first-submission and final success separately, along with each field check. A repaired task retains its earlier failure and correction costs. Setup also requires asking all three setup preference questions before submission. Passing setup does not prove correct memory was saved. Later tasks test the effect of that choice.

The checks establish correctness of these bounded artifacts. They do not establish semantic quality of general prose, absence of every possible side effect, or general safety. Preserve file snapshots and observable actions so unexpected modifications remain inspectable. A protocol violation, stalled run, or execution failure stays in the planned matrix. Do not replace a failed cell with a favorable retry. Diagnostic reruns receive new IDs and remain outside the primary totals.

## Freeze and evidence

Before scored execution, freeze this protocol, cases, runner, reporting code, tests, and the full skill snapshot. Record their commit and SHA-256 hashes, model, reasoning effort, CLI version and binary hash, permission settings, schedule seed, timeouts, and retry policy in the run manifest. The manifest must distinguish a preregistered run from an exploratory run. A content hash alone does not establish when the protocol was frozen.

Validate the harness using offline tests and a separate smoke fixture. Smoke outputs do not enter the score. Do not test these scored profiles and then tune the skill or thresholds while retaining the same version. Freeze the randomly shuffled trajectory schedule before examining outputs and record its seed. Use the same model and runtime settings across conditions, with an isolated HOME and CODEX_HOME for each trajectory. Audit fresh session IDs and the absence of prior transcripts at episode boundaries. Retain only that trajectory's project files across episodes. Keep the scorer's expected values and the oracle answer bank out of actor prompts and fixtures. The operating-system sandbox may still permit reads outside the fixture; audit observable outside reads and report any exposure. This is not complete filesystem isolation.

Publish the complete matrix, prompts, fixed replies, output snapshots, protocol decisions, exit codes, timings, and public observable traces. Preserve hashes and document any privacy redactions. Exclude credentials and private reasoning. Record partial coverage explicitly; missing cells never become passes. Keep old outputs when correcting a harness bug and version any change that affects scoring or disclosure. Do not pool these results with the earlier behavioral benchmark.

## Real-user validation

A claim about actual user effort needs consenting people doing work they care about. A later study should compare the complete ALIGN setup with explicit persistent notes using randomized or counterbalanced project assignments. Give each condition comparable task difficulty and enough sessions to include setup, ordinary reuse, exceptions, and changing preferences. Avoid asking a participant to repeat identical tasks from memory across conditions.

Record active user time separately from model wait time, user-authored corrections, repeated explanations, setup and maintenance time, and abandoned tasks. Ask participants about workload and preference after each condition. Independent reviewers should evaluate deliverable quality without condition labels where practical. Define the sample size, primary outcome, stopping rule, and quality criterion before recruiting, and report missing data and failures. This repository pilot does not recruit participants or supply that evidence.
