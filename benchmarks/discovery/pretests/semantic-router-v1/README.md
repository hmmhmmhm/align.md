# Semantic router development validation

The replacement classifier selected the intended routes in all 26 authored
challenge cases. Each question received one Astra call with medium reasoning;
no classifier used a tool. The public receipts retain the exact prompts,
selections, model contexts, timings, and redaction counts. No actor trajectory
was scored in this check.

The fixture had already exposed failures in the lexical router, so this is
development validation. It is not a held-out test, a general accuracy estimate,
or external validation. Scored-run questions still require blind semantic
review.

The report retains `source_unchanged: false`. During these calls, the production
runner acquired explicit reasoning-effort and ancestor-instruction checks.
Those checks were absent from this process's already loaded code. The archived
`run.py` exactly matches the pretest's recorded source hash. Its classifier
prompt and answer-selection logic match the subsequent production version.
All retained pretest turn contexts independently show `gpt-6-astra` with
`medium` effort. The pretest is not being replaced to obtain a clean flag.
