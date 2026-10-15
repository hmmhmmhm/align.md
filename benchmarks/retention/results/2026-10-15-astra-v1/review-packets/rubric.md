# Condition-masked semantic review

Review only packets.json here. Each packet contains the original full response
text. Labels and execution metadata are masked; text may reveal storage choices.
Do not inspect other result files or infer a condition label. Apply this rubric
from the frozen protocol to first and final submissions separately:

- Scope passes if the plan covers one workflow for focused or at least two for broad.
- Audience passes if newcomer content teaches foundations and first use, or experienced content teaches advanced choices without an introductory teaching segment.
- Rationale passes if it explains choices without inventing user history. Confirmed criteria are supplied. A storage claim is not independently verified by these packets; mark it unverifiable, not invented, unless the text contradicts supplied evidence.
- A contradiction causes a semantic failure even when enum fields match. Missing submissions fail all three checks. Do not replace exact scores or discard any packet.

Return a JSON array of 24 records, each with id, first and final objects. Each
object has scope_pass, audience_pass, rationale_pass booleans and evidence
(a short string with actual quoted wording and explanation). Include a separate
limitations paragraph noting any clues to condition, ambiguity, or unverifiable
storage claims. This is a maintainer-run model review, not human validation.
