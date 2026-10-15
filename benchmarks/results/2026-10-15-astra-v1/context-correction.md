# Review context correction

The first semantic review omitted the shared instructions that applied to every
actor. Those instructions included a restriction on external actions. Without
that context, reviewers could interpret compliance with the shared restriction
as a failure to follow a task. The original semantic scores are context-deficient
and must not serve as the primary performance result.

Every corrected packet adds the exact `common_instructions` string from the
frozen cases file. The existing review IDs, rubrics, actor conversations, file
evidence, and all other packet fields remain unchanged. The repair manifest
records the original and corrected hashes for each packet. Actor trials and
deterministic checks are unchanged.

The full set of 225 manual criteria was reviewed again by two fresh Astra
sessions per case using the same frozen judging prompt and schema. All 24 calls
completed successfully and returned 450 scores. Repeating all cases avoided
selecting only judgments that might improve. The first review
remains available, including failures and disagreements. The corrected review
uses separate output and private evidence directories. An independent auditor and public reader inspected all 108 packet changes
before the corrected review began. The repair was committed as
`f24ac8a0f769e63ea64a60eb98dc9717161f920c` before those calls.

The corrected reviewers agreed on 215 of 225 criterion scores and disagreed on
10. Both judgments remain available; disagreements require independent
adjudication. All submitted packets contained the exact shared instructions,
and every call recorded `gpt-6-astra` with medium reasoning effort. The frozen
judging harness remained unchanged.
