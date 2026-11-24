from opening_line_match import *
import opening_line_match as am
am.entries=inventory()
import re,math
from PIL import ImageFont
from functools import lru_cache
from pathlib import Path

OD=ROOT/'opening/자막'
M=Path('P:/AI/Codex/projects/migrated-from-c/onedrive-chatgpt/페이러 테일 및 도화이담 시리즈')
T={
11605: ('이게 제가 ‘사랑에 빠진’ 무게예요!',[1]),
11607: ('이번에야말로 당신에게 줄게요.|‘고양이 없는 웃음’을!',[.55,.45]),
40201: ('장미가 밤이슬에 젖어|여기까지 향기가 전해져 와요.|향기뿐인 귀한 꿀에 잠기는 듯한 밤이에요.',[.34,.24,.42]),
10912: ('가엾게도, 몹쓸 짓을 했네요.|제가 고집을 부리는 바람에…….',[.48,.52]),
51503: ('자, 서로 사랑해요, 카이.',[1]),
20706: ('빨리, 빨리 여기서 도망쳐야 해……!',[1]),
51610: ('계속 함께 있어요.|언제까지나, 영원히.',[.48,.52]),
10905: ('저 말이에요.|깨달았다기보다 떠올렸어요.|모든 일에는 끝이 있다는 걸.',[.22,.36,.42]),
20708: ('시, 싫어…… 그만…….|이제…… 그만, 해…….',[.52,.48]),
40716: ('그러지 않으면 그 아이가…….|아아…… 어떻게 되는 거야…….',[.45,.55]),
21613: ('오빠 같은 건…… 없었어…….',[1]),
40220: ('저는…… 분명|라푼젤로서는 낙제인가 봐요.',[.38,.62]),
21121: ('추워. 얼어붙을 것 같아.|왜 여긴 이렇게 추운 거야…….|보고 싶어…… 당신이…….',[.29,.39,.32]),
21922: ('싫어…… 싫어어…….|그만해, 그만하라고…….',[.50,.50]),
40609: ('아기 울음소리가 둘.|배냇저고리도 둘.',[.52,.48]),
30939: ('아하, 아하하, 하하……!',[1]),
31106: ('이게 나의 ‘저주’.|결코 풀리지 않는 ‘저주’…….',[.41,.59]),
31321: ('오딜, 부탁이야. 용서해 줘.|제발, 이 사람만은……|빼앗지 마!',[.42,.40,.18]),
30951: ('돌려줘! 그건 네 게 아니야!|돌려달라고!!',[.56,.44]),
11010: ('등 뒤에서 마물의 발소리가 느껴져요.|마물의 커다란 그림자가 저를 통째로 삼키고 있어요.|저도 곧 잡아먹히겠죠.',[.30,.44,.26]),
31378: ('장난하지 마!|이럴 때만큼은 내 말을……!',[.36,.64]),
31118: ('안녕히, 지크프리트 님.',[1]),
31380: ('싫어어어! 오딜──!!',[1]),
31350: ('난 살인자야.|언니는 내 범죄의 유일한 목격자고.',[.35,.65]),
22002: ('나는…… 그레텔 같은 게…… 아니야…….|그냥 필요 없는 아이…….',[.62,.38]),
41205: ('꼭 구해 줄 테니까!!',[1]),
22014: ('으으…… 으아아아!!|싫어어! 오빠! 오빠!!',[.47,.53]),
31377: ('어쩔까.|……난 이제 왠지, 말이야…….',[.36,.64]),
}
SPEAK={'アリス':'앨리스','ラプンツェル':'라푼젤','雪の女王':'눈의 여왕','ゲルダ':'게르다','グレーテル':'그레텔','オデット':'오데트','オディール':'오딜'}
# Each Japanese line is the in-game 9501 lyric sheet. The four vocalized English lines have no printed words.
JP=['ことりが また 鳴いてるね','この おはなし 続きは なあに？','','','','','さかさまのまさかが この場所で','きっと 起こる','見ていてね','ときどきのどきどき つながって','あなたも いま わらってる','ちいさなカプセル','うそのバラ','星のかけら ほおばると','心とける','だいすきな この庭で 踊りましょう','さあ この手を取って','なんども 見ていた こわい夢なら ね','きっとすぐに 忘れられるから ね']
# Keep the melody-timed lines of the prior release and correct only verified card/recording mismatches.
PATCH={9:'때때로 느끼는 두근거림이 이어져',11:'작은 캡슐',12:'거짓의 장미',13:'별 조각을 볼 가득 머금으면'}
def envbounds(y, weights):
    step=441;n=len(y)//step;env=np.sqrt(np.mean(y[:n*step].reshape(n,step)**2,axis=1))
    active=np.flatnonzero(env>max(.0018,np.quantile(env,.92)*.038))
    assert len(active)
    first=max(0,(active[0]-5)/100);end=min(len(y)/44100,(active[-1]+11)/100)
    cum=np.cumsum(weights)[:-1]/sum(weights)
    limits=[first]
    smooth=np.convolve(env,np.ones(9)/9,'same')
    for ix,t in enumerate(cum):
        desired=first+(end-first)*t
        lower=max(limits[-1]+.56,desired-min(.72,(end-first)*.14));upper=min(end-.58*(len(weights)-ix-1),desired+min(.72,(end-first)*.14))
        indices=np.arange(int(np.ceil(lower*100)),int(upper*100)+1)
        if not len(indices):limits.append(desired);continue
        score=(smooth[indices]/max(.001,np.quantile(env,.85)))+np.abs(indices/100-desired)*.18
        limits.append(indices[np.argmin(score)]/100)
    return [*limits,end]
def prepare():
    full=read('audit/encore_spoken_verified.json');extra=read('audit/encore_opening_residual_matches.json')
    sources={r['voice']:r for r in full if r['voice'] in T}
    sources[31377]=next(r for r in extra if r['voice']==31377 and 51.1<r['offset']<51.2)
    assert set(T)==set(sources)
    takes=[]
    for voice,(translated,weights) in T.items():
        r=sources[voice];g=r['game'];assert g=='R'
        ko=translated.split('|');assert len(ko)==len(weights)
        wave=am.voice((g,voice));bounds=envbounds(wave,weights);offset=r['offset'];f,slot,sp,ja=r['text']
        takes.append(dict(voice=voice,source_file=f,slot=slot,source_ja=ja,speaker=SPEAK[sp],
                          start=max(0,round(offset+bounds[0],2)),end=round(offset+bounds[-1],2),
                          cues=[{'start':max(0,round(offset+a,2)),'end':round(offset+b,2),'ko':v} for a,b,v in zip(bounds,bounds[1:],ko)]))
    takes.sort(key=lambda r:r['start'])
    ends=[];lastslot={}
    for r in takes:
        free=[i for i,a in enumerate(ends) if a<=r['start']+.001]
        if free:
            previous=lastslot.get(r['speaker'])
            lane=previous if previous in free else min(free)
        else:lane=len(ends);ends.append(0)
        r['lane']=lane;ends[lane]=r['end'];lastslot[r['speaker']]=lane
    req=read(M/'opening_motion_v6_1/deliverables/manifest.json')['lyrics']['segments']
    assert len(req)==len(JP)
    req=[dict(start=v['start'],end=v['end'],ko=PATCH.get(i,v['ko']),source=JP[i],prior_ko=v['ko']) for i,v in enumerate(req)]
    out={'translator_model':'Codex internal','Encore':takes,'Requiem':req,'layout_lanes':len(ends),
         'sources':{'jp_lyrics':'grpo_ex.xfl::9501.wcg', 'English_refrain':'unprinted, existing 4 Korean listening-draft cues', 'voice':'Requiem original recordings independently matched against Encore opening'}}
    save('audit/opening_caption_timeline.json',out);return out
if __name__=='__main__':
    o=prepare()
    print('timeline',len(o['Encore']),sum(len(x['cues']) for x in o['Encore']),len(o['Requiem']),o['layout_lanes'],max(r['end'] for r in o['Encore']))
