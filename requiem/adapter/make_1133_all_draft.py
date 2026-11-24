from __future__ import annotations
import hashlib,json,re
from pathlib import Path
P=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
T={
1:"나",2:"후우…….",3:"병실 문을 닫고 나는 크게 한숨을 내쉬었다.",
4:"오늘 진찰에서는 여러 가지 검사를 받았다.^n형광빛이 도는 보라색 액체를 마시고, 시험관 네 개 분량의 피를 뽑히고,^n정체 모를 시험 문제 같은 것도 풀었다.",
5:"마신 것이 이상하게 작용한 건지,^n피가 부족해진 건지, 머리를 너무 많이 쓴 건지──^n아무튼 머리는 무겁고 몸은 나른하다.",6:"나",7:"(조금 낮잠이라도 잘까……)",
8:"드물게 그런 생각이 떠오른 바로 그 순간.",9:"나",10:"……어?",
11:"몇 번인가 들은 적 있는,^n이제는 완전히 불길한 인상이 박혀 버린^n뻐꾸기 울음소리가 울렸다.",
12:"하지만 방금 소리에는,^n평소와 다른 독특한 울림이 있었다.",
13:"커다란 종을 울렸을 때 귓속에 남는 여운.^n그 『위화감의 파동』 같은 것에 일그러져 변질된,^n종잡을 수 없이 음울한 울림──",
14:"그 순간 등골이 오싹하게 얼어붙었다.",
15:"이유는 모르지만, 그래서 더욱 불길했다.^n무엇보다 먼저 살갗으로 느낀 이상만큼 무서운 것은 없다.",
16:"나",17:"(……뭐지)",18:"시선이 저절로 모니터에 빨려 들어간다.",
19:"내 시선을 기다렸다는 듯,^n부우…… 하고 전원이 들어왔다.",
20:"지금까지는 전원이 들어오면 바로 선명한 영상이 비쳤다.^n하지만 내 눈앞에는 그저 흑백으로 된 노이즈만 흔들리고 있다.",
21:"나",22:"………….",23:"목소리가 나오지 않는다.",
24:"눈은 못 박힌 채,^n평평한 노이즈 속에서 의미 있는 것을 계속 찾아 헤매며,^n돌릴 수가 없다.",
25:"나",26:"…………………………………………………….",27:"나",28:"(방금 건……)",
29:"나는 허벅지 근처를 문질러,^n손바닥에 밴 차가운 땀을 닦았다.",
30:"이상이 일어난 것은 고작 십여 초였다고 생각한다.^n그런데도 내 몸은 심지까지 꽁꽁 얼어 있었다.^n온몸의 모공이 움츠러들어 소름이 돋았다.",
31:"마음도 얼버무릴 수 없을 만큼 겁에 질려 있었다.^n쿵쿵쿵쿵, 귓속에서 빠른 종소리가 들린다.^n한동안은 손가락 하나 움직이는 것조차 무서울 만큼.",
32:"지금까지 보게 된 여자아이들의 모습과는 완전히 다른 의미로,^n없던 일로 만들고 싶다, 빨리 잊고 싶다고 바랐다.",
33:"나",34:"(방금 건……)",35:"생각하고 싶지 않다. 인정하고 싶지 않다.^n하지만 흐지부지 넘기는 것도 싫다.",
36:"나",37:"(여자아이……?)",
38:"노이즈는 사라지기 직전 갑자기 형태를 이루었다.^n그것은 검은 옷을 입은 창백한 피부의 여자아이──",
39:"나",40:"──!!",41:"갑자기 울려 퍼진 비명에 온몸이 굳었다.",
42:"분명 멀리서 들린 외침이었는데,^n양쪽 귀에서 머리가 관통당한 듯했다.",
43:"나",44:"(방금 건…… 그레텔?)",
45:"하지만 이번 것은 정체를 아는 현상이다.^n그 사실이 나를 단숨에 진정시켰다.",
46:"나는 방을 뛰쳐나가 복도를 달렸다.",
47:"비명이 난 곳으로 달려가기 위해서인지,^n아니면 그 방에서──모니터에 비친 무언가로부터^n도망치기 위해서인지, 나 자신도 모른 채.",}
R=re.compile(r"\^(?:n|d\d+)")
def main():
 rows={}
 with (P/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")=="1133.gsc" and x.get("slot") in T: rows[int(x["slot"])]=x
 if set(rows)!=set(T): raise SystemExit("catalog mismatch")
 es=[]
 for i in sorted(T):
  s,t=str(rows[i]["source_text"]),T[i]
  if R.findall(s)!=R.findall(t): raise SystemExit(f"caret {i}")
  t.encode("cp949",errors="strict"); es.append({"uid":rows[i]["uid"],"source_text":s,"source_raw_sha256":rows[i]["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 전"})
 o={"schema":"fairytale-requiem-translation-map-v1","scope":"1133_slots_00001_00047_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":es}
 out=P/"packets"/"drafts"/"1133_slots_00001_00047_draft.json"; out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"PASS","output":str(out),"entries":len(es),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
