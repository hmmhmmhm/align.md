#!/usr/bin/env python3
"""Plot verified synthetic results without changing the frozen scoring rules."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('verification', type=Path)
    parser.add_argument('--output', type=Path, default=Path('assets/benchmarks/discovery-comparison'))
    args = parser.parse_args()
    data = json.loads(args.verification.read_text())
    if data.get('verified') is not True or data.get('non_scored_smoke'):
        raise SystemExit('A verified scored-run report is required.')
    cases_path = args.verification.parent / 'source-snapshot/benchmarks/discovery/cases.json'
    cases = json.loads(cases_path.read_text())
    planned = sum(len(c['episodes']) for c in cases['cases']) * cases['protocol']['repetitions']
    planned_setup = sum(sum(e['kind'] == 'setup' for e in c['episodes']) for c in cases['cases']) * cases['protocol']['repetitions']
    snapshot = args.verification.parent / 'source-snapshot'
    runtime_source = (snapshot / 'benchmarks/discovery/run.py').read_text()
    protocol = next(ast.literal_eval(node.value) for node in ast.parse(runtime_source).body
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PROTOCOL' for t in node.targets))
    instruction_block = (snapshot / 'skills/align/assets/instruction-block.md').read_text()
    repetitions = cases['protocol']['repetitions']
    planned_trajectories = len(cases['cases']) * repetitions
    source_characters = sum(sum(len(v) for v in c.get('files', {}).values()) for c in cases['cases']) * repetitions
    text_counts = {}
    for arm in ('A', 'B', 'C'):
        instruction = cases['conditions'][arm]['instructions']
        agents = cases['common_instructions'] + '\n' + instruction + protocol
        if arm == 'C':
            agents += '\n' + instruction_block
        total = data['arms'][arm]['totals']
        text_counts[arm] = {
            'planned_trajectories': planned_trajectories,
            'source_file_characters_once_per_trajectory': source_characters,
            'common_instruction_characters_once_per_trajectory': len(cases['common_instructions']) * planned_trajectories,
            'condition_instruction_characters_once_per_trajectory': len(instruction) * planned_trajectories,
            'align_instruction_block_characters_once_per_trajectory': len(instruction_block) * planned_trajectories if arm == 'C' else 0,
            'initial_agents_file_characters_once_per_trajectory': len(agents) * planned_trajectories,
            **{key: total.get(key, 0) for key in ('setup_initial_user_characters', 'task_initial_user_characters', 'setup_reply_user_characters', 'task_reply_user_characters', 'harness_protocol_characters')},
        }
    rows = []
    for arm in ('A', 'B', 'C'):
        trajectories = [r for r in data['trajectories'] if r['arm'] == arm]
        episodes = [e for r in trajectories for e in r['episodes']]
        total = data['arms'][arm]['totals']
        rows.append({'arm': arm, 'planned_episodes': planned,
                     'planned_setup_episodes': planned_setup,
                     'planned_later_episodes': planned - planned_setup,
                     'first_submission_passes': sum(e['_derived']['first_submission_passed'] is True for e in episodes),
                     'final_passes': sum(e['passed'] is True for e in episodes),
                     'setup_replies': total.get('setup_intervention_turns', 0),
                     'later_replies': total.get('task_intervention_turns', 0),
                     'execution_failures': data['arms'][arm]['execution_failures']})
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'axes.spines.top': False,
                         'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.0))
    x = [0, 1, 2]
    labels = ['A\nAGENTS memory', 'B\nSeparate notes', 'C\nALIGN method']
    for offset, key, color, label in [(-.17, 'first_submission_passes', '#315F87', 'First submission'),
                                     (.17, 'final_passes', '#99B6C9', 'Final submission')]:
        axes[0].bar([v + offset for v in x], [r[key] for r in rows], width=.3, color=color, label=label)
        for i, row in enumerate(rows):
            axes[0].text(i + offset, row[key] + .35, str(row[key]), ha='center', fontsize=11)
    axes[0].set_ylim(0, planned * 1.22)
    axes[0].set_yticks(range(0, planned + 1, max(1, planned // 4)))
    axes[0].axhline(planned, color='#596A79', linestyle=':', linewidth=.8)
    axes[0].set_ylabel(f'Passed episodes (out of {planned} planned per condition)')
    axes[0].set_title('Exact decision-format checks, including setup', loc='left', fontsize=12, pad=12)
    axes[0].legend(frameon=False, ncol=2, loc='upper center', fontsize=9)
    setup = [r['setup_replies'] for r in rows]
    later = [r['later_replies'] for r in rows]
    totals = [a + b for a, b in zip(setup, later)]
    axes[1].bar(x, setup, color='#99B6C9', label='Setup', width=.58)
    axes[1].bar(x, later, bottom=setup, color='#315F87', label='Later episodes', width=.58)
    top = max(1, max(totals))
    axes[1].set_ylim(0, top * 1.32)
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].set_ylabel('Additional scripted user replies (count)')
    axes[1].set_title('Replies, including clarification and correction', loc='left', fontsize=12, pad=12)
    axes[1].legend(frameon=False, loc='upper right', ncol=2, fontsize=9)
    for i, value in enumerate(totals):
        axes[1].text(i, value + top * .025, str(value), ha='center')
    for ax in axes:
        ax.set_xticks(x, labels, fontsize=10)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#E0E5EB', linewidth=.7)
        ax.tick_params(axis='x', length=0, pad=10)
    fig.suptitle('Synthetic preference evidence and transfer benchmark', x=.065, ha='left', fontsize=18, weight='bold')
    fig.text(.065, .91, 'Two authored profiles, two repetitions per condition. B is the primary comparator.', fontsize=11)
    fig.text(.065, .065, f'{planned} episodes per condition include {planned_setup} setup and {planned - planned_setup} later episodes. Missing episodes stay in the denominator.', fontsize=10, color='#475565')
    fig.text(.065, .03, 'Format failures can include unstated literal or type requirements, not preference mistakes. No human time or satisfaction measured.', fontsize=10, color='#475565')
    fig.subplots_adjust(left=.075, right=.98, top=.79, bottom=.24, wspace=.35)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ('svg', 'png'):
        metadata = {'Creator': 'ALIGN discovery reporting plot.py'} if ext == 'svg' else {'Software': 'ALIGN discovery reporting plot.py'}
        fig.savefig(args.output.with_suffix('.'+ext), dpi=180, facecolor='white', metadata=metadata)
    args.output.with_suffix('.json').write_text(json.dumps({
        'verification_sha256': hashlib.sha256(args.verification.read_bytes()).hexdigest(),
        'frozen_cases_sha256': hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        'python': sys.version.split()[0], 'matplotlib': matplotlib.__version__, 'data': rows,
        'text_counts': text_counts,
        'text_count_convention': 'Unicode characters, not bytes or tokens. Source files and initial instruction files count once per planned trajectory; this does not measure model rereads. User-message and harness-protocol counts come from verified delivered turns. Initial AGENTS totals include separators and protocol text; component rows are not all disjoint from that total.',
        'scope': 'Synthetic bounded artifact checks and scripted replies; semantic review is separate; no human effort measurement.'}, indent=2)+'\n')


if __name__ == '__main__':
    main()
