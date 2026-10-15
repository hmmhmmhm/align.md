# Infrastructure correction before v2

The v1 run at commit `df5752f4155480ef11f4b03932e47d7474ca2ac7` recorded all 12 planned trajectories as harness failures before any actor call. Its private log destination had an ancestor instruction file. Because actor workspaces were created inside that destination, the isolation guard refused to start them. The 72 planned episodes remain failed or missing in the v1 report.

Publication also stopped when the privacy scanner found its own temporary-path detection literal inside the frozen source archive. That finding contained no actor output or credential. The original failed audit receipt is preserved as `privacy-audit-original.json` in the v1 failure publication. A separate runtime-evidence audit and source-hash receipt document the corrected publication scope.

V2 creates actor workspaces under the system temporary directory and retains private logs at the requested private destination. The ancestor-instruction guard remains active. Runtime evidence is scanned before publication; the already public committed source archive is attached afterward, with every archived file checked against the frozen manifest before and after copying. No source file may be added, removed, substituted, or symlinked through this exception.

Regression tests cover temporary-workspace placement, private-directory permissions, the source-literal false positive, and rejection of a changed source archive. The task cases, scripted answers, comparison thresholds, and tested alignment skill are unchanged. V2 uses new output locations and a new public freeze. V1 is retained as a failed run and is not pooled with v2.
