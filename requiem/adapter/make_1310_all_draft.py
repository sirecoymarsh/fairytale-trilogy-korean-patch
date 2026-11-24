from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"게르다","문을, 자물쇠를 잠가야 해…….",
"게르다는 반쯤 미친 상태로 잠꼬대처럼 중얼거렸다.",
"하지만 그녀들의 방 문은^n밖에서만 자물쇠를 잠글 수 있는 구조다.",
"어쩔 수 없이 시설을 돌아다닐 때 몰래 모은 도구를 사용해^n이것저것 시행착오를 거쳤다.",
"게르다","아…… 아아.",
"진찰실에서 훔쳐 온 머리핀으로 열쇠 구멍 안쪽을 더듬었지만,^n도중에 뚝 부러져 열쇠 구멍을 막는 꼴이 되어^n오히려 역효과가 났다.",
"이래서는 진짜 열쇠가 있어도 잠글 수 없다.",
"조금만 더 냉정하게 생각할 힘이 남아 있었다면^n어쩌면 가능했을지도 모르지만,^n안타깝게도 지금 그녀는 몹시 지쳐 심신 미약 상태였다.",
"게르다","마, 막아야 해…… 아무도 들어오지 못하게…….",
"다음으로 그녀는 문 앞에 가구를 쌓아 올려^n바리케이드를 만들려고 했다.",
"──하지만.^n가구는 하나같이 바닥에 단단히 고정되어^n꿈쩍도 하지 않았다.",
"유일하게 움직일 수 있는 것은 벽난로 앞 흔들의자뿐이지만,^n그것 하나로는 도저히 바리케이드가 되지 않는다.",
"게르다","막대…… 무슨 막대라도 빗장으로…….",
"초조해질수록 그녀의 생각은 헛돌았다.",
"그런 적당한 물건은 방에 없다는 사실을 깨닫기까지^n상당한 시간을 허비했다.",
"게르다","마, 맞아…… 도망치면 돼…….",
"서둘러야 한다.^n그것이 오기 전에.",
"게르다","빨리, 빨리 여기서 도망쳐야 해……!",
"어쨌든 이 방에 있으면 안 된다.^n빨리 달아나야 해──하지만 어디로?^n어디든 좋아, 일단 방에서 뛰쳐나가자.",
"문을 열자 그녀는^n『누군가』의 몸에 세게 부딪혀 튕겨 나왔다.",
"시야가 어두워진다.^n검푸르고 불길하게 뻗어 손쉽게 게르다를 뒤덮는 사람의 그림자 때문에──",
"──아무래도 판단이 아주 조금 늦었던 모양이다.",
"게르다","아…… 아아아…….",
"뱀 앞의 개구리처럼 얼어붙어 게르다는 떨었다.^n팔다리에서 힘이 빠져나간다.",
"어제까지 그녀의 안을 차지하던 분노는 모두 타 버렸다.^n남은 불씨 속에 있는 것은 체념뿐이었다.",
"???","안녕, 게르다. 좋은 저녁이야.",
"남자의 그림자가 그녀를 덮칠 듯 다가와 히죽 웃었다.",
"아프다거나 괴롭다거나 굴욕적이라거나 역겹다거나,^n그런 것들도 함께 타 버렸으면 좋았을 텐데.",
"머릿속까지 인형이 되어 버린다면,^n몸이 인형처럼 다뤄져도 신경 쓰이지 않을 텐데.",
"아직 게르다에게는 감정 한 조각이 남아 있다.",
"게르다에게 남은 게르다다운 부분이^n그녀 자신을 상처 입히고 몰아붙인다.",
"게르다","시, 싫어…… 그만…… 이제…… 그만, 해…….",
"비단실보다도 가느다란 목소리로 게르다는 흐느꼈다.^n그 목소리가 약탈자의 정복욕을 더욱 부추길 뿐인 줄도 모른 채."]
def main():
 expected=set(range(1,43))
 if len(TARGETS)!=43:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1310.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(43,101)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1310_slots_00001_00042_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1310_slots_00001_00042_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[43,100],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
