# Method review

This pilot can measure scripted user interventions across repeated project
tasks. It cannot establish how much time, attention, or frustration a person
saves. A large reduction in its counts would justify a human study. A tie or
increase is also a valid result.

This review was prepared before scored execution by a separate agent session
within the maintainer's evaluation. It is not external validation. The proposed
design has two authored user profiles, three conditions, two repetitions, a
setup episode, and five later episodes. The frozen protocol and source manifest
must identify the implementation actually run.

The final design review accepts the notice and website-option profiles for a
small diagnostic pilot. The implementation still needs its recorded offline
checks and smoke run before freeze. Acceptance of the design does not certify
the harness or its future outputs.

## Comparison and counting

The main comparison is the complete ALIGN setup against a strong baseline
explicitly allowed and instructed to maintain persistent notes. Both need the
same user information, consent to save it, tools, model, and opportunity to ask.
An ordinary instruction baseline is useful context, but a win over it alone
does not establish benefit over competent memory use. Extra ALIGN instructions
and their context cost belong to the treatment.

The tasks expose preference keys and require small structured outputs. They
primarily test elicitation, memory reuse, and applying known preferences.
Changing option IDs between episodes tests a limited form of transfer;
explicit mappings still make the decision simple. Two authored profiles
cannot establish performance across project domains or open-ended collaboration. The interface
itself teaches agents what they can ask and constrains how they can ask it.

Each later episode starts a new conversation with the project's saved files.
The trajectory must include initial elicitation and confirmation costs. Report
setup separately, then cumulative totals after every episode so readers can see
whether later savings repay the initial cost. Automatically installing the
fixture does not measure human installation effort; that cost remains outside
the pilot.

Count actual oracle reply events, requested preference keys, repeated fact
disclosures, confirmations, and corrective feedback separately. A question
containing six decisions may consume one reply round while still asking for six
decisions. User-message length and visible agent output length provide additional
diagnostics, but neither converts to human reading or thinking time. Do not
assign invented seconds or combine unlike counts through unvalidated weights.
The protocol defines repeated units by previously disclosed preference ID,
including IDs supplied in task instructions. It does not compare the meaning
of successive values. Total units must include the initial temporary-exception
and lasting-change disclosures as well as answers and corrections.

The protocol's joint rule requires at least 20% fewer supplied preference units,
at least 20% fewer replies and one fewer reply per trajectory, no increase in
repeated units, and the success guardrail. These are project-selected
descriptive thresholds. They have not been validated as meaningful human
benefits. State each denominator and treatment of a zero baseline. Report raw
paired counts even when the joint rule fails.

## Oracle and successful output

Freeze the oracle before scoring. It should answer the keys actually asked,
using the same private values and disclosure rules in every condition. A new
preference becomes available at the same episode in every arm. Temporary
exceptions must expire at the same point. The oracle must not infer treatment
labels or give ALIGN more cooperative answers.

Deterministic output checks make failures inspectable. The task schema, valid
keys, correction order, turn budget, and malformed-response policy need to be
explicit. Retain out-of-schema requests and exhausted turns as failures or
unresolved protocol events; do not silently repair them or give free retries.
Inspect visible assistant messages as well as the structured action response.
Questions in prose outside that interface still request user attention. If the harness cannot
reliably count them, mark their burden unmeasured and fail the protocol gate.
A missing or malformed file must never become a valid zero-intervention win.
Report protocol noncompliance separately from a correctly formatted but
unsuccessful task, and apply the quality gate across all planned tasks.
Fixed correction feedback that supplies every failed value is an unusually
helpful user model. It may reduce differences between methods and does not
represent how reliably people notice or explain errors.

Fewer replies support a favorable result only with the frozen success guardrail
satisfied. Show every planned episode's accepted output and failure status.
Include abandoned, timed-out, and malformed runs in the planned denominators.
A run that stops without producing the required output cannot win by avoiding
questions. Analyze successful matched pairs only as a secondary view because
that subset can hide condition-dependent failures. JSON acceptance supports
claims about the tested fields; broader task quality or safe actions require
their own checks.

Two profiles and two repetitions provide descriptive evidence for these
fixtures. Later episodes share memory, so individual turns are not independent
samples. Do not treat repeated model runs as additional human participants,
claim statistical noninferiority from this small matrix, or extend a favorable
result to unseen users and projects.

## Human study needed for an effort claim

Recruit people who routinely use coding agents and let them work on repeated
tasks over several sessions. A feasible crossover template has two comparable
projects per participant, one per condition. Randomize and balance ALIGN-first
and baseline-first order, and separately balance which project receives which
condition. Start each project with clean agent memory and record its full setup
cost. Use the same strong memory baseline and keep all scheduled followups
inside the assigned project's condition.

Participants may carry learned habits from the first project into the second;
resetting agent memory does not remove this. Prespecify period and order checks
and report first-period results separately. If the feasibility study shows
substantial carryover, use a between-participant confirmatory study. Record
prior agent experience and disclose recruitment and exclusions. The number of
participants remains undecided until a sample-size justification is available.

Include onboarding, preference elicitation, reading, answering, review, and
repair in observed active user time. Record agent wait time separately, using
consented interaction logging and a prespecified rule for inactivity. Keep
time spent before abandonment and report completion and abandonment alongside
effort. Have reviewers who do not know the condition assess required outputs
against the same acceptance criteria. Ask participants about workload after
each session, without prompting them to expect improvement.

NASA-TLX offers a subjective workload measure across mental, physical, and
temporal demand, performance, effort, and frustration. Use its administration
and scoring instructions consistently, and report its scores separately from
active time and output success. A simulator cannot supply these participant
ratings. [NASA's official TLX materials](https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/)
describe the instrument and its manual.

Run a human feasibility study first to estimate variability and logging quality.
Before a confirmatory study, preregister the primary cumulative-time endpoint,
success margin, practically meaningful benefit, sample-size justification,
missing-data rules, and analysis at the participant/project level. Include
confidence intervals and the full workload and success results. Do not select a
sample size or endpoint after seeing which favors ALIGN.

## Research behind these limits

[Yao et al., tau-bench (2024)](https://arxiv.org/abs/2406.12045v1) evaluates
simulated conversations using final database states and reports consistency
across repeated trials. It supports checking task outcomes alongside
interaction counts; it does not validate a human-effort measure for this pilot.

[Zhu, Huang, and Sang (2024)](https://arxiv.org/abs/2403.16416v1) found leakage
and prompt-control problems in conversational recommendation user simulators.
That domain differs from project alignment, but the findings support auditing
what private information the oracle reveals.

[Zhou et al. (2026)](https://arxiv.org/abs/2603.11245v2) compared agentic user
simulation with real participants and reported overly cooperative simulated
behavior and more favorable feedback. Their results give a direct reason to
require human validation before translating scripted interaction savings into
claims about actual user effort. None of these sources evaluates ALIGN.
