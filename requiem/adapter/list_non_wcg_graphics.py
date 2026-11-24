from pathlib import Path
import sys
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");sys.path.insert(0,str(base/'adapter'))
from xfl_tool import parse_archive
for n in ['grpe.xfl','grpo_cu.xfl','grpo_ef.xfl']:
 a=parse_archive(base/'runtime/trial_ko'/n); print(n)
 for e in a.entries:
  if Path(e.name).suffix.lower() not in {'.wcg','.lwg','.fsc'}: print(' ',e.name,e.size,e.absolute_offset)
