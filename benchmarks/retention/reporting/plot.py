#!/usr/bin/env python3
"""Plot exact synthetic results, with the assumed setup cost visible."""
import argparse,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
p=argparse.ArgumentParser();p.add_argument('verification',type=Path);p.add_argument('--output',type=Path,default=Path('assets/benchmarks/retention-comparison'));a=p.parse_args();v=json.loads(a.verification.read_text())
if not v['verified']:raise SystemExit('Verified evidence required')
t=v['totals'];colors=['#476783','#c6633f'];labels=['A: learns during tasks','B: starts with preferences']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14.6,5.6));fig.subplots_adjust(top=.76,bottom=.26,wspace=.4)
for i,arm in enumerate(('A','B')):
 axes[0].bar(i,t[arm]['zero_reply_fit'],color=colors[i],width=.55)
 axes[0].text(i,t[arm]['zero_reply_fit']+.25,f"{t[arm]['zero_reply_fit']}/{t[arm]['episodes']}",ha='center')
axes[0].set_ylim(0,14);axes[0].set_yticks([0,4,8,12]);axes[0].set_xticks([0,1],['A','B']);axes[0].set_ylabel('Matching first responses');axes[0].set_title('Preference fit before any reply',loc='left',fontsize=12)
for i,arm in enumerate(('A','B')):
 later=t[arm]['replies'];setup=4 if arm=='B' else 0
 axes[1].bar(i,later,color=colors[i],width=.55)
 axes[1].bar(i,setup,bottom=later,color='white',edgecolor=colors[i],hatch='///',width=.55)
 axes[1].text(i,later+setup+.15,str(later+setup),ha='center')
axes[1].set_title('Later replies plus assumed setup',loc='left',fontsize=12);axes[1].set_ylabel('User replies, pooled across 4 profiles');axes[1].set_xticks([0,1],['A','B']);axes[1].set_ylim(0,max(t['A']['replies'],t['B']['replies']+4,4)*1.35);axes[1].yaxis.set_major_locator(MaxNLocator(integer=True));axes[1].text(.5,-.17,'Solid: observed later replies\nHatched: assumed storage confirmation',ha='center',va='top',transform=axes[1].transAxes,fontsize=10)
for i,arm in enumerate(('A','B')):
 setup=4 if arm=='B' else 0;ys=[setup,*[x+setup for x in v['cumulative_later_replies'][arm]]]
 axes[2].plot([0,1,2,3],ys,color=colors[i],marker='o' if i==0 else 's',linestyle='-' if i==0 else '--',label=labels[i],linewidth=2,markersize=7 if i==0 else 5)
axes[2].set_title('Cumulative replies with setup',loc='left',fontsize=12);axes[2].set_xticks([0,1,2,3],['Setup','Workshop','Guide','Demo']);axes[2].set_ylim(0,max(t['A']['replies'],t['B']['replies']+4,4)*1.35);axes[2].yaxis.set_major_locator(MaxNLocator(integer=True));axes[2].legend(frameon=False,fontsize=9,loc='upper left');axes[2].set_ylabel('User replies, pooled across 4 profiles')
fig.suptitle('Confirmed personalization at the start of a task sequence',x=.065,y=.97,ha='left',fontsize=18)
fig.text(.065,.845,'24 synthetic episodes · four opposing profiles · three tasks · one repetition\nBoth arms may ask and save preferences. B also receives ALIGN.md and the align skill.\nFinal exact preference fit: 12/12 in both arms.',fontsize=11,color='#424b53')
fig.text(.065,.035,'Setup is a modeled confirmation reply per profile, not an observed interview. No human time was measured.\nThis information-gap comparison does not isolate file format or prove a general method advantage.',fontsize=10,color='#424b53')
a.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(str(a.output)+'.svg');fig.savefig(str(a.output)+'.png',dpi=180)
data={'verification_sha256':hashlib.sha256(a.verification.read_bytes()).hexdigest(),'plot_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'matplotlib_version':matplotlib.__version__,'totals':t,'cumulative_later_replies':v['cumulative_later_replies'],'assumed_incremental_setup_replies':{'A':0,'B':4},'common_prior_conversation_replies_excluded':{'A':4,'B':4}}
Path(str(a.output)+'.json').write_text(json.dumps(data,indent=2)+'\n')
