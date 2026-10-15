# Public evaluation examples

These repositories informed the reporting choices below. They evaluate different skills and tasks, so their scores are not comparable with ALIGN results. Links were checked on 2026-10-15; the linked branch contents may change.

| Source | What it reports | Lesson for this benchmark |
| --- | --- | --- |
| [NVIDIA nvidia-kaggle benchmark](https://github.com/NVIDIA/nvidia-kaggle/blob/main/BENCHMARK.md) | With-skill and without-skill evaluation across two agents, with 18 tasks: 12 positive and six negative activation cases. It separates execution, efficiency, accuracy, and goal accuracy. | Include routine cases where extra process can hurt, and distinguish procedure use from task outcomes. |
| [Planning with files evaluations](https://github.com/soucod/planning-with-files-skill/blob/master/docs/evals.md) | The initial evaluation explicitly measures adherence to its three-file workflow rather than general planning ability. Later sections discuss recovery tests and limitations. | Name the measured construct. Creating the expected files alone cannot demonstrate improved user decisions. |
| [Codebase onboarding skill](https://github.com/eabait/codebase-onboarding-skill#evaluation) | Public example outputs and a comparison across Claude, Codex, and Gemini, with structural and content checks. Its displayed baseline is a Claude run, not a no-skill condition. | Publish inspectable outputs, and say exactly what a baseline contains. Cross-model comparisons do not isolate skill effects. |
| [Odoo workflow benchmark](https://github.com/unclecatvn/agent-skills/blob/main/tests/evals/odoo-workflow/benchmark.md) | Per-case outcomes, grader preferences including losses and ties, tool counts, output tokens, and limits from one-model, one-run coverage. | Show cost and unfavorable outcomes beside gains, and keep conclusions within the sample. |

These are examples of public project evaluations, not independent validation of ALIGN. None establishes that ALIGN improves collaboration or reduces user effort.
