from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)")
TARGETS=[None,"──이렇게 앨리스와 왕자님은 맺어졌습니다.","앨리스는 손으로 쓴 그 『성서』에 그렇게 덧붙인 모양이다.","실제로 『맺어진』 것은 아니지만.^n앨리스는 그 표현이 무척 마음에 든 듯,^n어떻게든 써 보고 싶었던 모양이다.","나도 앨리스도^n라푼젤이 말한 것 같은 『사랑』은 아직 모른다."," 알몸으로 껴안고 부끄러운 곳을 맞비비는 듯한^n 의식 따위──서로 굳이 하지 않아도 상관없다고 생각하지만,^n『성서』에 어떻게 적어야 할지는 모른다.","어쨌든 앨리스가 자기 손으로 쓰기로 한^n새로운 『성서』의 일화는 그런 한 문장으로 막을 내렸다.","하지만 경사 났네 경사 났어로 끝날 리 없다.","앨리스","자, 어서 일어나요. 출발이에요!","나","앨리스…… 잠깐만.^n어제 일로 다리가 퉁퉁 부었어.^n오늘은 좀 봐줘…….","앨리스","안 돼요! 한시가 급하니까요.","약한 소리를 하며 엎어진 내 위로 앨리스가 올라탔다.","나","윽! ──무거워, 앨리스…….","앨리스","일어나지 않는 당신이 잘못했어요.^n이건 제 분노의 무게예요.","나","지금이 아니어도 되잖아…….^n다음 기회로 미루자, 다음에.","앨리스","정말, 지금이 『다음』이에요!","앨리스는 가슴을 펴고 『성서』를 펼쳤다.^n어제 일이 끝나자마자 벌써 새 페이지를 써 온 모양이다.","앨리스","신데렐라의 못된 의붓언니가 뒤꿈치를 잘라 내고^n유리 구두를 억지로 신었어요.^n그대로 강제로 신데렐라가 될 생각이에요.","앨리스","진실을 아는 건 우리뿐이에요!^n자, 작은 새가 되어 왕자님에게 알리러 가야 해요!","나","뒤꿈치를 잘라 냈다니, 그런 무모한…….^n일부러 알려 주지 않아도 언젠가는 알아차릴 거야.","앨리스","들키지 않을 승산이 있으니 그렇게 했겠죠?^n실제로 왕자님은 알아차리지 못하고 데리러 가고 있어요.^n이대로라면 전혀 닮지도 않은 꽝을 뽑고 말 거예요!","나","………….","얼굴도 기억하지 못하는 왕자에게는 좋은 약이겠다는 말을^n나는 간신히 삼켰다.","싫다고 버텨도 결국 앨리스 뜻대로 된다.^n나는 그것을 싫을 만큼 이해하고 있었다.","앨리스가 고집스럽고 제멋대로인 것 이상으로,^n나는──나만이 아니라 이 『낙원』의 모든 주민이,^n앨리스에게 약하다.","필사적으로 무언가를 호소하는 모습을 듣고 있으면,^n무엇이든 이루어 주고 싶어지고 만다.","실제로 이 하얀 방도 완전히 달라졌다.^n앨리스가 가져온 여러 보물로 꾸며져 있다.","석궁이나 보물 지도, 어떤 동물의 모피 같은 것.^n페인트를 마구 칠해 더없이 붉어진 흰 장미 같은 것.","지금까지의 『모험』에서 얻은 전리품도 많다.^n구해 준 엄지 공주가 두고 간 작은 신발과 드레스,^n도와준 개구리 왕자에게 받은 공 같은 것.","나","──알았어.^n알았으니까 이제 그만 내려와…….","앨리스","안 돼요. 당신이 일어나 준비하는 게 먼저예요!","나","억지 부리지 마.^n올라탄 채로는 준비할 수 없잖아.","앨리스","어머! ──그것도 그렇네요, 실례했어요.^n그럼 목소리가 조금 더 또렷해지면^n당신이 일어날 거라고 믿기로 할게요.","나","으…….","졸린 것을 들킨 내가 신음하자,^n앨리스는 화사한 웃음소리를 울렸다.","나는 단념하고 무거운 눈꺼풀을 억지로 열었다.","──세상이 하얗다.^n새하얗고 갓 태어난 빛으로 가득하다.","한때 앨리스와 나를 붙잡을 뻔한 『옅은 그림자 같은 기억』은,^n너무나 눈부신 이 빛에 비쳐^n얼룩처럼 비참하게 사라지려 한다."," 앨리스가 바랐던,^n『즐거운 나날』이 『결코 끝나지 않는 것』은^n 앞으로도 이런 빛 속에서 이어질 것이다.","상상력만 있다면,^n즐거운 일과 멋진 일은 끝이 없다.","『성서』가 한 구간을 맞이하더라도,^n 페이지 뒤에 새로운 장을 써 넣으면 된다.","끝나지 않는 즐거운 이야기를 산다.^n우리는 그러기 위해 태어났다.","이케노","어이, 앨리스, 나나시.^n서두르지 않으면 왕자님의 마차가 와 버려!","창밖에서 이케노 씨가 부르고 있다.","앨리스","네에!^n자, 어서 일어나요! 네? 부탁이에요.","──당해 낼 수가 없다.^n정말 정말 지쳐 움직이고 싶지 않지만,^n아무래도 움직여야만 한다.","우리가 가지 않으면^n보는 눈 없는 왕자는 못된 의붓언니에게 속고 말 테니까──","앨리스","부탁이에요, 서둘러야 해요.^n불쌍한 신데렐라가 이제 다시는 왕자님을^n만나지 못할지도 몰라요.","앨리스","있죠, 당신도 싫잖아요?^n누군가의 계략으로 사랑하는 사람과 헤어지고,^n상대가 남의 것이 되어 다시는 만나지 못한다니…….","나","………….","치익, 하고.^n어째서인지 가슴 깊은 곳이 그을리는 느낌에 단번에 잠이 깼다.","나도 모르게 몸을 일으키는 바람에^n튕겨 나갈 뻔한 앨리스는^n황급히 사나운 말을 다루듯 자세를 바로잡았다.","앨리스","꺄악!^n──아아, 일어났네요. 다행이에요!","앨리스","자, 어서 가요.^n지금이라면 분명 늦지 않을 거예요!","앨리스에게 팔을 끌리는 대로,^n나는 침대에서 내려와 문간을 나섰다.","앨리스에게 이끌려 오늘의 모험을 향해 달리는 내 발밑으로^n치익치익 그을리는 『무언가』가 뚝뚝 떨어지는 것을 느낀다.^n마치 헨젤과 그레텔이 표식으로 떨어뜨린 빵 부스러기처럼.","나","(──이상하네. 아무것도 생각할 필요가 없는데)","가슴 깊은 곳에 한순간 나타난 『그림자』를──^n두려운 듯 물어 오는 불안한 누군가의 목소리를,^n나는 못 본 척했다.","──그런데 이 『낙원』은 대체,^n누구를 위한 어떤 곳이었더라?","나","………….","──생각하지 않아도 돼.^n──생각하는 데 의미는 없어.","하얀 빛만 바라보며 달려가자.^n그 아름답고 눈부신 빛이,^n쓸데없는 것을 모두 지워 줄 테니까.","앨리스의 손바닥에서 전해지는 다정한 온기를 느끼며,^n이대로 어디까지든 달려가자──"]
def main():
 expected=set(range(1,89));
 if len(TARGETS)!=89:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1222.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(89,147)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1222_slots_00001_00088_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1222_slots_00001_00088_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[89,146],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
