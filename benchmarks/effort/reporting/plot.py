#!/usr/bin/env python3
"""Plot published scripted outcomes; this utility adds no scoring rules."""
import argparse
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
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, default=Path('assets/benchmarks/effort-comparison'))
    args = parser.parse_args()
    data = json.loads(args.report.read_text())
    if not data.get('verified') or data.get('non_scored_smoke'):
        raise SystemExit('A verified scored-run report is required.')
    rows = []
    for arm in ('A', 'B', 'C'):
        trajectories = [r for r in data['trajectories'] if r['arm'] == arm]
        tasks = [e for r in trajectories for e in r['episodes'] if e['id'] != 'setup']
        planned = data['arms'][arm]['planned_trajectories'] * 5
        total = data['arms'][arm]['totals']
        rows.append({'arm': arm, 'planned_tasks': planned,
                     'first_submission_passes': sum(e['_derived']['first_submission_passed'] is True for e in tasks),
                     'setup_replies': total['setup_intervention_turns'],
                     'task_replies': total['task_intervention_turns'],
                     'preference_units': total['preference_units']})
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'axes.spines.top': False,
                         'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.6))
    labels = ['A\nOrdinary instructions', 'B\nPersistent notes', 'C\nALIGN setup']
    x = range(3)
    colors = ['#788594', '#315F87', '#147B78']
    rates = [100 * r['first_submission_passes'] / r['planned_tasks'] for r in rows]
    axes[0].bar(x, rates, color=colors, width=.58)
    axes[0].set_ylim(0, 100)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel('Task outputs passing on first submission (%)')
    axes[0].set_title('Scripted preference criteria', loc='left', weight='bold', pad=16)
    for i, (r, value) in enumerate(zip(rows, rates)):
        axes[0].text(i, value - 7 if value >= 20 else value + 4,
                     f"{r['first_submission_passes']}/{r['planned_tasks']}",
                     ha='center', va='center', color='white' if value >= 20 else '#182531', weight='bold')
    setup = [r['setup_replies'] for r in rows]
    task = [r['task_replies'] for r in rows]
    totals = [s+t for s, t in zip(setup, task)]
    axes[1].bar(x, setup, color='#ADBCD0', label='Setup', width=.58)
    axes[1].bar(x, task, bottom=setup, color='#315F87', label='Tasks', width=.58)
    axes[1].set_ylim(0, max(1, max(totals)) * 1.35)
    axes[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axes[1].set_ylabel('Additional scripted user replies (count)')
    axes[1].set_title('User replies, including setup', loc='left', weight='bold', pad=16)
    axes[1].legend(frameon=False, loc='upper right', ncol=2, fontsize=10)
    for i, total in enumerate(totals):
        axes[1].text(i, total + max(totals)*.035, str(total), ha='center', weight='bold')
    for ax in axes:
        ax.set_xticks(list(x), labels, fontsize=10)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#E0E5EB', linewidth=.7)
        ax.tick_params(axis='x', length=0, pad=10)
    fig.suptitle('ALIGN scripted intervention pilot', x=.06, ha='left', fontsize=18, weight='bold')
    fig.text(.06, .91, 'Two authored profiles, two repetitions per condition. B is the primary comparator.', fontsize=11)
    fig.text(.06, .045, 'Fixed user scripts and exact artifact checks. No human satisfaction or time was measured.', fontsize=10, color='#475565')
    fig.subplots_adjust(left=.075, right=.98, top=.79, bottom=.20, wspace=.32)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ('svg', 'png'):
        fig.savefig(args.output.with_suffix('.'+ext), dpi=180, facecolor='white', metadata={'Creator': 'ALIGN effort reporting plot.py'} if ext == 'svg' else {'Software': 'ALIGN effort reporting plot.py'})
    args.output.with_suffix('.json').write_text(json.dumps({
        'report_sha256': hashlib.sha256(args.report.read_bytes()).hexdigest(),
        'python': sys.version.split()[0], 'matplotlib': matplotlib.__version__, 'data': rows,
        'scope': 'Scripted criteria and user replies; not measured human satisfaction or effort.'}, indent=2)+'\n')


if __name__ == '__main__':
    main()
