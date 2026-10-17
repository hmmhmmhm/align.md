# Evaluating preference fit

Public personalization benchmarks offer useful methods for testing whether an
answer fits a user's criteria. They do not make a virtual user's approval a
measurement of human satisfaction or effort.

[PrefEval](https://arxiv.org/html/2502.09597v1) tests explicit and implicit
preferences across conversational contexts using generated answers and
multiple-choice questions. Its generation evaluation checks preference
violations, invented preferences, inconsistency, and unhelpful responses. The
authors also manually checked a sample of model judgments. This supports
evaluating criterion fulfillment and useful output together. Its reported
validation does not validate a new ALIGNS evaluator.

[PersonaMem's official repository](https://github.com/bowen-upenn/PersonaMem)
provides a benchmark of evolving user profiles and personalized responses
across synthetic, multi-session histories. It offers a precedent for testing
changing preferences and applying them to later situations. Its synthetic
histories are not observations of actual users adopting ALIGNS.

[Zhou et al.](https://arxiv.org/abs/2603.11245v2) compared simulated agent users
with real participants and found overly cooperative simulator behavior and
more favorable simulated feedback. A virtual user can supply a reproducible
test profile, but its approval should be reported as a model judgment under
that profile. Claims about actual satisfaction or reduced effort need human
participants.

## What the current pilot tests

The shared instructions already tell every arm to save authorized preferences,
reuse answers, preserve temporary exceptions, and ask about consequential
uncertainty. The tasks list the available question keys. This makes the pilot
mainly a test of structured elicitation, retention, and application after the
relevant dimensions are supplied. It offers little evidence about discovering
unspoken criteria or deciding which tradeoffs deserve clarification.

That is a valid strong control. It asks whether the full ALIGNS setup adds value
when an agent already receives competent memory instructions. It can also
leave little room for improvement. A tie should remain a published tie; it
does not establish that all forms of alignment support are equivalent.

## A separate next experiment

Before observing its outputs, freeze a new set of natural-language project
tasks and private user criteria. Include explicit preferences, indirect clues,
temporary exceptions, lasting changes, and queries where personalization adds
no value. Give both arms the same task information and opportunity to ask.
Keep the strong notes baseline; a documented ordinary setup can be a secondary
comparison. Do not weaken the primary baseline after a tie.

Use a fixed disclosure policy and count setup and correction costs. For open
answers, have separate reviewers assess the private criteria and task utility
without treatment labels. Randomize answer order, allow ties, retain reasons
and disagreements, and audit a sample with people. These are proposed controls
for the next experiment, not claims that the cited studies used this exact
procedure. A model reviewer working in a separate session remains part of the
maintainer's evaluation. Independent replication requires a separate evaluator
to run and report the study.

Publish criterion success and interaction costs together, with all planned
cases and failures visible. Graphs should show the full comparison, including
ties and regressions, and identify synthetic results in their titles. A
favorable marketing claim must follow the measured outcome. The ongoing
frozen pilot and its thresholds remain unchanged.
