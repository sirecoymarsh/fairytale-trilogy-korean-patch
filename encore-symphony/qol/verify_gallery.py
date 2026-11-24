from pathlib import Path
import json
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
def img(p):return np.array(Image.open(p).convert('RGB'),dtype='int16')
def read_album(a):
    return sum((a[y+5:y+145,x+5:x+260].max(axis=2)<4).mean()<.90 for y in (132,302,472) for x in (78,364,650,936))
def read_replay(a,locked):
    count=0
    for col in range(3):
        for row in range(9):
            x=41+col*401;y=140+row*54
            patch=a[y+5:y+35,x+160:x+230]
            # Only classify the native blank card, independent of the ink and background colour of real titles.
            match=np.abs(patch-locked).mean()
            if match>6:count+=1
    return count
def main():
    result={}
    for g in ('Encore','Symphony'):
        d=HERE/'evidence'/g
        before=img(d/'gallery-201-0.png');after=img(d/'gallery-201-1.png')
        locked=img(d/'gallery-301-0.png')
        # The second row of the first column is locked in the mixed source save of both titles.
        ref=locked[199:229,201:271]
        one,two=read_album(before),read_album(after)
        x,y=read_replay(locked,ref),read_replay(img(d/'gallery-301-1.png'),ref)
        cap=27 if g=='Encore' else 24
        # Symphony has three unused rows on its only page; exclude slots without a painted card.
        if g=='Symphony':
            def real(a):
                count=0
                for i in range(cap):
                    co,ro=divmod(i,9);xx=41+401*co;yy=140+54*ro
                    count+=np.abs(a[yy+5:yy+35,xx+160:xx+230]-ref).mean()>6
                return count
            x,y=real(locked),real(img(d/'gallery-301-1.png'))
        print(g,int(one),int(two),int(x),int(y))
        assert one<two==12 and x<y==cap
        result[g]={'first_page_cg_before_after':[int(one),int(two)],'first_page_replay_before_after':[int(x),int(y)],'verification':'Retail renderer with identical mixed progress; only the trial title entry jumped directly into the unmodified release gallery routines.'}
    (HERE/'evidence/gallery-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
