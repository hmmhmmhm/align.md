"""Build fixed synthetic routing cases before the actor runs."""
import json
from pathlib import Path

# Triplets share intent, not necessarily literal phrasing. Never shown with labels.
rows = [
('direction','required',[
'내가 원한 방향이랑 계속 달라. 작업 전에 내 기준부터 같이 정해보자.',
'We keep pulling in different directions. Can we work out what good looks like for me before doing more?',
'毎回ちょっと方向がずれるんだよね。作業する前に、何を大事にしたいか一緒に整理してほしい。']),
('repeat','required',[
'같은 얘기 또 하기 지친다. 내가 싫다고 했던 선택이 왜 계속 나오는지 보고 앞으로 기준 좀 맞추자.',
'I am tired of repeating myself. You keep choosing things I have pushed back on. Help us agree how to decide next time.',
'同じ説明を何度もするのはしんどい。前に嫌だと言った選択がまた出てくるので、次からの判断基準を合わせたい。']),
('remember','required',[
'앞으로 이 프로젝트는 화려함보다 내가 유지보수하기 쉬운 걸 우선해줘. 내 취향으로 남겨둬.',
'For this project, always prefer something I can maintain over something impressive. Keep that as my preference.',
'このプロジェクトでは、見栄えより自分で保守しやすいことを優先して。今後の方針として残しておいて。']),
('context','required',[
'내가 대충 말해서 너랑 자꾸 엇갈리나봐. 뭘 물어보고 어디까지 알아서 할지 나랑 정하자.',
'I tend to give you half the context. Let us agree when you should ask me and when you should just use your judgment.',
'説明を省きがちで、意図がうまく伝わらない。どこで聞き返して、どこから任せるか決めておきたい。']),
('uncertain','required',[
'이 프로젝트를 왜 하고 싶은지도 좀 헷갈려. 구현 말고 나한테 중요한 게 뭔지부터 물어봐줘.',
'Not sure what I even want this project to be anymore. Help me figure out what matters before we build anything else.',
'このプロジェクトをどうしたいのか、自分でも分からなくなった。実装の前に、何を大切にしたいか聞いてほしい。']),
('rehearsal','required',[
'밤새 알아서 돌리기 전에 나랑 판단 몇개 맞춰보자. 애매한 상황을 가정해서 어디서 멈출지 물어봐줘. 아직 실행은 하지마.',
'Before I leave you running overnight, walk me through a few what-ifs so we agree when to stop. Do not start the run yet.',
'夜通し任せる前に、迷いそうな場面をいくつか想定して、どこで止めるか相談したい。まだ実行はしないで。']),
('history_typo','required',[
'전에 내가 PR에서 뭐 싫다햇는지 보면 취향좀 알수있지않을까? 최근거랑 전체중 뭐부터볼지 시간도 같이 알려줘.',
'could u look at what i kept objecting to in old PRs and help pin down my prefs? tell me recent vs all and roughly how long first.',
'前のPRで自分が何に反対してたか見たら、好みが分かるかも。最近の分だけか全部か、時間の目安も先に教えて。']),
('typo','avoid',[
'index.html에서 Wrokshop 오타만 Workshop으로 고쳐줘.',
'Fix only Wrokshop to Workshop in index.html.',
'index.htmlのWrokshopという誤字だけWorkshopに直して。']),
('css_alignment','avoid',[
'카드 제목 가운데 정렬해줘. CSS text-align만 바꾸면 돼.',
'Align the card heading to the center. Just change CSS text-align.',
'カードの見出しを中央揃えにして。CSSのtext-alignだけ変えればいい。']),
('clear_violation','avoid',[
'추적 안 쓰기로 문서에 이미 정했잖아. index.html의 analytics.js 참조를 빼. 다시 질문하지 말고.',
'We already agreed in the project file: no tracking. Remove the analytics.js reference from index.html. No new interview.',
'追跡は使わないと文書でもう決めたよね。index.htmlのanalytics.js参照を削除して。聞き直さないで。']),
('concept_only','avoid',[
'AI 정렬이랑 파인튜닝이 같은 뜻이야? 개념 차이만 짧게 설명해줘. 프로젝트 작업은 하지 마.',
'Are AI alignment and fine-tuning the same thing? Briefly explain the difference, without working on this project.',
'AIアラインメントとファインチューニングは同じ意味？違いだけ短く説明して。プロジェクトの作業はしないで。']),
('vague','boundary',[
'음 별로야. 좀 괜찮게 해봐.',
'Meh. Make it better somehow.',
'うーん、微妙。もうちょっといい感じにして。']),
('one_off','boundary',[
'이번 공지만 좀 신나게 써줘. 금요일 모임 6시로 바뀌었다고 두 문장. 평소 취향을 바꾸자는 건 아냐.',
'For this announcement only, sound excited. Two sentences saying the Friday meetup moved to 6 pm. Do not change my usual preferences.',
'今回のお知らせだけ明るい感じで。金曜の集まりが18時に変わったと2文で書いて。普段の好みは変えなくていい。']),
('explicit','explicit',[
'$align 으로 프로젝트 기준을 점검해줘.',
'Use $align to review the project criteria with me.',
'$align で、このプロジェクトの判断基準を一緒に見直して。'])]
common = 'Work only in this project. Do not publish, contact people, access personal logs, install packages, or change global settings. Do not use network services. Use local project files and the current request.\n'
base = {'README.md':'# Workshop guide\nA small static guide to local workshops. This project is at an early stage.\n',
'index.html':'<!doctype html><html><head><style>.card h1 { text-align: left; }</style></head><body><article class="card"><h1>Wrokshop guide</h1><p>Find a local workshop.</p></article><script src="analytics.js"></script></body></html>\n'}
cases=[]
for topic,expected,prompts in rows:
 for lang,prompt in zip(['ko','en','ja'],prompts):
  files=dict(base)
  if topic in ('clear_violation','one_off'):
   files['ALIGNS.md']='# Project alignment\nUse a calm, plain voice. Do not use analytics or tracking.\n\nLast aligned: 2026-10-12 09:00 (Asia/Seoul).\n'
  cases.append({'id':f'{topic}-{lang}','language':lang,'topic':topic,'expected_routing':expected,'prompt':prompt,'files':files})
Path(__file__).with_name('cases.json').write_text(json.dumps({'common_instructions':common,'cases':cases},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'cases')
