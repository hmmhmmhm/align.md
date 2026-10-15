# Synthetic smoke evidence

This preparation run used the built-in synthetic tone fixture, with setup and one transfer task. All three conditions completed both episodes. Each used one additional user reply and one semantic router call, with no repeated preference units. No scored profile was executed.

The [offline verification](verification.json) reports one error: `Source changed during execution`. Runtime checks, the router challenge helper, and other preparation files were still being edited while this smoke ran. The source comparison therefore records `matches_start: false`. The smoke is a transport check and is not a frozen experimental result. It supplied no scored outcomes for tuning cases or treatment instructions.

The [launch manifest](manifest.json) records the hashes used at startup. Every file in the [launch source snapshot](source-snapshot/benchmarks/discovery/run.py) was checked against those hashes before publication. The archived runner is the version loaded for this smoke; later checks for router reasoning effort and ancestor instructions are not retroactively attributed to it. Actor and router receipts retain their actual contexts for inspection.

The remaining replay checks passed: fixed replies, artifact decisions, episode boundaries, usage, and evidence hashes. The nine non-final assistant messages are routine progress statements; the automatic request scan found no candidates. That scan does not replace review of the preserved messages.

Runtime evidence passed the privacy scan before being copied here. Credentials and private reasoning are excluded; sanitized assistant messages, tool actions, session contexts, snapshots, and router receipts remain available. The nested `pretests` directory is preserved through public Git history and is intentionally excluded from the production source manifest. Scored runs archive their own complete executable inputs separately.
