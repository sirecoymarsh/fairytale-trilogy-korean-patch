from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)")
TARGETS=[None,"나","(──또야)","앨리스의 방문이 또 열려 있다.^n무방비하게, 어서 들어오라는 듯 벌어진 틈.","이제는 망설이는 시늉을 할 필요조차 느끼지 못한다.^n나는 분명히 『침입할』 생각으로,^n발소리를 죽이고 문간을 넘었다.","앨리스는 탁자 앞에 있었다.","여느 때처럼 종이 뭉치와 책으로 어질러진 탁자에 엎드려,^n글을 쓰던 도중 잠의 나라로 떠난 모양이다.","나","……?","손가를 들여다보고 처음 눈에 들어온 것은,^n찢겨 나가 아무렇게나 밀쳐져 있는^n책의 일부로 보이는 종이였다.","아름다운 삽화와 기묘하고 운치 있는 문장──^n이것은 『이상한 나라의 앨리스』 마지막,^n둑에서 앨리스가 깨어나는 장면의 페이지다.","나","(왜…….^n 자기가 직접 『성서』를 찢어 버리다니)","궁극적으로 『자기 자신』인 성서가 훼손되면^n상당한 충격을 받지 않을까.","그런 걱정을 하며 앨리스를 보자,^n그녀의 뺨 아래 눌린 『성서』 본체가 보였다.","그 페이지를 뜯어낸 자리에 남은 톱니 모양 종잇조각 사이로,^n분홍색 실이 서툰 솜씨로 오가며,^n──다른 종이가 꿰매져 있다.","검은 잉크 방울을 튀기며,^n만년필 글씨가 들려주는 이야기는 이러했다.","『트럼프 병사들이 덤벼들었지만,^n 트럼프라서 바닥에 우수수 흩어지고 끝났습니다』","『그런데 앨리스는 왕자님을 만나 연정에 빠졌습니다.^n왕자님에게 자기 마음을 고백하기로 했습니다.^n고백했습니다』","『왕자님과 앨리스는 맺어졌습니다.^n오래오래 행복하게 살았습니다』","나","──이게 뭐야.","그때까지 침입자답게 숨을 죽이고 있었는데,^n있는 힘껏 어이없어하는 목소리가 새어 나오고 말았다.","나","(이건 그러니까 앨리스가 자기 줄거리를^n 자기 힘으로 바꾸려 했다는 뜻이고……)","나","(왕자님과 맺어지는 결말을 바라고 있고…….^n 그런데 이 왕자님이라는 건……)","──나겠지.","지독하게 낯부끄럽고 간지러우며,^n스스로 그렇게 생각하는 것이 뻔뻔하게 느껴지지만,^n지금까지의 여러 일을 보면 거의 틀림없다고 생각한다.","나","(게다가 아마 이 『마음을 고백한다』는 건,^n 그 깜짝 행사와 관련이 있을 듯한……)","절절히 밀려드는 『예감』을^n깊이 생각할 틈은 없었다.","앨리스","응…… 으응…….^n──후아……?","나","아…….","조금 전 내가 낸 어이없다는 목소리를 계기로,^n앨리스가 잠의 나라에서 돌아오고 말았다.","긴 속눈썹을 느릿느릿 깜빡이던 앨리스는,^n나와 내가 바라보는 일기를 번갈아 보더니^n기겁하며 눈을 크게 떴다.","의외로 재빠른 몸짓이었기에,^n적당히 얼버무리며 달아날 틈 따위는 없었다.","앨리스","──꺄악!^n다, 다, 다, 당…….","나","조, ……좋은 아침, 앨리스.","앨리스","좋은 아침이에요.^n","──가 아니라!","앨리스","나, 남의 일기를 훔쳐보다니, 예의가 아니에요.^n당신에게 보여 주려고 쓴 것도 아닌데.","나","(일기? ……아아)","확실히 성서 옆에는 일기도 펼쳐져 있다.^n아무래도 성서의 새 페이지는^n이 일기에서 찢어 붙인 모양이다.","어느 쪽이든 전에 일기도 훔쳐 읽었으니^n변명할 여지는 없다.","나","하지만 여기 봐. 리드 미라고,^n읽어 달라고 쓰여 있잖아…….","궁지에 몰려 말하자 앨리스는 뺨을 부풀린다.","앨리스","그런 건 하면 안 된다고 전하려고,^n해야 한다고 적어 둔 거예요.","앨리스","이트 미, 드링크 미, 리드 미…….^n전부 하면 안 된다는 뜻이에요.^n좋은 일이 생길 리 없어요!","나","미, 미안해.","앨리스","──뭐, 됐어요.^n이렇게 해가 높은데 졸음을 이기지 못한^n제 잘못도 있으니까요.","앨리스","그리고 중요한 계획서는 보이지 않았고…….","나","뭐라고 했어?","앨리스","아니요, 아무것도요!","앨리스는 일기 아래 깔려 있던 종잇조각을^n거칠게 구겨 옆으로 밀치며 고개를 저었다."," 노골적으로 숨기려 드는 걸 보면, 그것이^n『계획서』라는 것일까.","앨리스","그보다 당신, 중요한 이야기가 있어요.^n지금부터 세 시간 뒤에 정원의 큰 나무 아래로 와 주실래요?","나","뭐……?","가슴이 철렁했다.","며칠 전부터 앨리스가 뛰어다니며 준비한 무언가.^n아마 내게 하는 『고백』으로 이어질 무언가가,^n그 시각부터 마침내 시작되는 걸까.","나","정원의 큰 나무 아래라니.^n그곳에는 나무가 많잖아…….","앨리스","모르겠으면 누군가에게 물어보세요.^n트럼프 병사들이 잘 아니까요.","앨리스","자, 저는 바빠요.^n아아, 바빠라, 바빠.^n정말 바빠서 시계를 꺼내 볼 시간조차 아까워요.","앨리스","그러니 잠시 안녕이에요!","앨리스는 그렇게 말하며 나를 억지로 문밖에 밀어냈다.","등 뒤에서 문이 닫힌다.^n문 너머로 앨리스가 떠나가는 기척이 난다.","익숙한 문을 바라보며,^n나는 좋은지 나쁜지 알 수 없는,^n그저 간지럽기만 한 예감에 사로잡혀 있었다."]
def main():
 expected=set(range(1,88));
 if len(TARGETS)!=88:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1220.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(88,146)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1220_slots_00001_00087_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1220_slots_00001_00087_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[88,145],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
