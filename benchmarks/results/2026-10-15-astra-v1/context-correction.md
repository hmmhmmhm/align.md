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

The full set of 225 manual criteria will be reviewed again by two fresh Astra
sessions per case using the same frozen judging prompt and schema. Repeating
all cases avoids selecting only judgments that might improve. The first review
remains available, including failures and disagreements. The corrected review
uses separate output and private evidence directories. Independent inspection
of all packet changes must precede the corrected review.
