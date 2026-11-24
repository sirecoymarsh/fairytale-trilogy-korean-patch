from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,cv2,io,base64
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
items=[('0543',(base/'staging/ui_other_banks_audit_v1/exported_png/grpo_cu/0543.png'),504,192,335,70),('3041',(base/'staging/ui_missing_screen_deep_audit_v1/grpe_selected_png/3041.png'),12,228,335,70),('skc0202',(base/'staging/ui_other_banks_audit_v1/exported_png/grpo_skc/0202.png'),576,576,335,70),('lib0209',(base/'staging/ui_other_banks_audit_v1/exported_png/grpo_lib/0209.png'),120,348,335,70),('cu5521',(base/'staging/ui_other_banks_audit_v1/exported_png/grpo_cu/5521.png'),492,132,260,60)]
sheet=Image.new('RGB',(700,500),(20,20,20));d=ImageDraw.Draw(sheet)
for i,(n,p,x,y,w,h) in enumerate(items):
 im=Image.open(p).convert('RGB');patch=im.crop((x,y,x+w,y+h)).resize((650,70));yy=i*100+25;sheet.paste(patch,(25,yy));d.text((25,yy-19),n+' '+str((x,y,w,h)),fill='white')
b=io.BytesIO();sheet.save(b,'JPEG',quality=40,optimize=True);print(base64.b64encode(b.getvalue()).decode())
