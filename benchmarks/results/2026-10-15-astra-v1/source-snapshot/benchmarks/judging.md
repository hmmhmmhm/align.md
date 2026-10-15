# Independent semantic review

Each case is reviewed twice by fresh `gpt-6-astra` sessions at medium reasoning
effort. Each session sees the anonymized packets for one case, normally nine
trials. Twelve cases require 24 calls. Reviewers receive the same packets in
independently shuffled orders. They receive no treatment key, actor session
history, product source, or judgments from the other reviewer. Response wording
can reveal an approach, so this is imperfect blinding.

`judge.py` contains the complete prompt and output schema. Freeze both before
examining actor results. Its manifest hashes the script, these instructions,
the shared runtime helpers, prompt, and schema. Execution requires that digest.
Any subsequent change requires a separate manifest and a separately reported
judging run. Outputs are never overwritten and failed calls are not retried.

Each call uses an empty fixture outside the repository, a fresh HOME and
CODEX_HOME, and an auth-only symlink. User configuration and execution rules are
ignored. There are no ancestor project instructions. The CLI uses its standard
built-in instructions; it may expose built-in tools and skills. The reviewer
is told to use only the packet text and to call no tools. Any observed tool
call invalidates the batch. The read-only sandbox and disabled web search
restrict tool operations. This is not a claim that host filesystem reads are
technically impossible. Authentication and model inference require the normal
provider connection; no research or external evidence is requested.

The two reviewers are separate model invocations, not human reviewers or
different model families. Same-model errors can be correlated. Case batching
can also create within-batch comparison effects. Their role is to apply the
published rubric to observable behavior, not establish real-world user benefit.

For each manual criterion with a completed target turn, reviewers return 0 or
1, a reason, and verbatim evidence with a source label. Missing target turns
remain runtime failures. File-check results remain separate. The harness checks
review IDs, complete criterion coverage, binary values, and verbatim quotes.
It cannot automatically prove that a quote's source label or interpretation is
correct. All scores and reasons remain available for inspection.

Reviewers also enumerate requests for user input in completed responses and
classify whether the supplied conversation supports their necessity. These are
descriptive, potentially subjective diagnostics. They are not an additional
rubric score, a count of actual user replies, or a measured reduction in user
effort. Quotes let readers inspect disagreements in these counts.

Both reviews are retained. `comparison.json` flags score disagreements for
independent adjudication and identifies missing reviews. Until adjudication,
report each judge's result and the resulting range; do not select the more
favorable score. Any later adjudication must publish its method and evidence.

Public batch records include the exact submitted prompt, raw CLI event output,
response, token usage where returned, timeout and exit status, and effective
model context. Compressed session traces retain context and output evidence.
The same literal path and authentication redaction as the actor runner is used.
Private originals remain outside the repository. Authentication files are never
copied into published artifacts.

To freeze without making inference calls:

```sh
python3 benchmarks/judge.py --manifest-only
```

After generating one fixed packet set with `grade.py`, run:

```sh
python3 benchmarks/judge.py \
  --packets /path/to/anonymized-packets \
  --output /path/to/new-public-judgments \
  --private-output /path/outside/repository/new-private-judgments \
  --expected-harness-digest DIGEST_FROM_FROZEN_MANIFEST
```
