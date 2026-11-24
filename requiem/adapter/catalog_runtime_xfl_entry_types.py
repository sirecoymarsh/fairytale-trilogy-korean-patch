from pathlib import Path
from collections import Counter
import sys
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko"); sys.path.insert(0,str(base/'adapter'))
from xfl_tool import parse_archive
for p in sorted((base/'runtime/trial_ko').glob('*.xfl')):
 try:a=parse_archive(p)
 except Exception as e: print(p.name,'ERROR',e); continue
 c=Counter(Path(e.name).suffix.lower() for e in a.entries)
 print(p.name,len(a.entries),dict(c))
 for e in a.entries:
  if Path(e.name).suffix.lower() in {'.lwg','.dzi','.dz','.fsc','.svg'}: print(' ',e.name,e.size)
