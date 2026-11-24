from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"게르다","대체 어떻게 된 거예요!",
"진찰실 앞을 지나가다가^n안에서 게르다의 고함이 들려왔다.",
"세게 내리치듯 닫은 반동으로 튕겨 나왔는지,^n입구 문은 조금 열린 채였다.",
"나","(무슨 일이지……?)",
"나는 그녀의 상태가 마음에 걸려 안을 들여다봤다.",
"게르다","왜 적절한 기관에 연락하지 않는 거예요!?^n새까맣게 탄 시체 때도 그랬잖아요!",
"게르다는 무서운 기세로 의사에게 따져 들고 있었다.",
"의사","그렇게 말해도 말이지…….",
"게르다의 필사적인 호소와 대조적으로,^n의사는 느긋한 말투였다.",
"의사","그건 제대로 조사해서^n문제가 없다는 결론이 나왔어.",
"그때 의사의 시선과 말투가 조금 날카로워졌다.^n게르다의 심장을 향해 깊이 파고들 듯이.",
"의사","그건 자네가 가장 잘 알고 있지 않나?",
"게르다","으…… 그, 그건…….",
"의사가 그렇게 받아치자,^n게르다는 노골적으로 말문이 막혔다.",
"나","(무슨 뜻이지?^n 저 사건에 관해 게르다가 뭔가 알고 있는 걸까?)",
"나","(설마 그 아이가 범인일 리는 없다고 생각하지만──)",
"하지만 『문제없다』는 말의 뜻을 모르겠다.^n사람이 한 명 죽었는데 왜 『문제없다』는 걸까?",
"게르다는 더 이상 사건에 관해 물고 늘어지지 않았다.",
"포기한 게 아니라,^n사건 이야기는 게르다에게도 아픈 부분이었기 때문일 것이다.",
"문틈으로 게르다가 손을 세게 움켜쥐는 모습이 보였다.^n손의 떨림을 억누르듯 몇 번이나,^n주먹 전체에서 핏기가 가실 정도로.",
"둔한 나도 어렴풋이 알겠다.^n이건 내놓고 싶지 않은 패를 꺼낼 때의 비장한 결의다.",
"게르다","그, 그럼 제…… 제 일은요?",
"의사","자네 일이라니, 무슨 말인가?",
"시치미를 떼는 건지 정말 모르는 건지,^n어느 쪽으로도 들리는 여유로운 말투로 의사가 되물었다.",
"게르다","아까부터 말하고 있잖아요!^n","제 방에 남자들이 와서…… 저를…….",
"말을 잇지 못한 게르다의 얼굴이 귀까지 새빨개졌다.^n반대로 입술은 하얗게 될 만큼 이를 악물고 있었다.",
"의사","자네를 어떻게 했다는 건가?^n아, 성적인 장난을 당했다고 했던가.",
"말하기 어려운 일을 의사가 단도직입적으로 입에 올리자,^n게르다는 치욕에 얼굴을 일그러뜨리며 분하다는 듯 고개를 끄덕였다.",
"게르다","어제 낮과 한밤중에……",
"정말이에요!",
"끝내 참지 못하고 게르다의 보석 같은 눈에서 굵은 눈물이 흘러내렸다.",
"나는 머리를 얻어맞은 듯한 기분이 들었다.",
"나","(게르다가 남자들에게…… 장난을 당했다니……?)",
"의사","거짓말을 하는 건지 환각이라도 본 건지.^n어른을 놀리면 안 돼.^n나는 다 알고 있으니까",
"의사는 그럴 리가 없다는 태도였다.^n타이르듯 두 손을 모으고 게르다를 빤히 바라본다.",
"게르다","거짓말이 아니야……!^n그, 그건…… 그런 짓은…….",
"흐트러진 게르다가^n끔찍한 기억을 떨쳐 내려는 듯 고개를 저었다.",
"──그러자 그녀의 눈이^n문틈에서 들여다보던 내 눈과 우연히 마주치고 말았다.",
"나","(아……)",
"죄책감에 꿰뚫려 순간 말이 나오지 않는다.^n그러는 사이 게르다의 얼굴에서 순식간에 핏기가 가셨다.",
"엿보인 놀라움과 당혹감 같은 것을 걷어차듯^n정체를 알 수 없는 감정이 그녀의 지적인 얼굴을 크게 일그러뜨린다──",
"──나중에 생각했다.^n그것은 아마 절망이었으리라고.",
"게르다","아…… 아아…… 싫어…….^n","시…… 싫어어어어어!!",
"나","게, 게르다……!",
"게르다는 말을 걸 틈도 없이^n진찰실을 뛰쳐나가 달아났다.",
"나","기다려, 게르다!!",
"나는 그녀를 뒤쫓으려 했지만,^n의사에게 붙잡혀 그 뒤 한동안 엿본 일을 두고 야단을 맞았다."]
def main():
 expected=set(range(1,71))
 if len(TARGETS)!=71:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1306.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(71,129)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1306_slots_00001_00070_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1306_slots_00001_00070_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[71,128],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
