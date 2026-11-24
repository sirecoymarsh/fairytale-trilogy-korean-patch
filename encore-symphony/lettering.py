"""Bespoke Hangul outlines for the two Liar-soft Fairytale title marks.
All coordinates describe the silhouette of a jamo or its counter. No installed
font is used for the logo. The same drawing is used by the game and the film.
"""
from functools import lru_cache
from pathlib import Path
import html
import numpy as np
import cv2
from PIL import Image
from fontTools.svgLib.path import parse_path
from fontTools.pens.basePen import BasePen
from assets import ROOT

# Each closed outline is drawn in a 100 by 100 local em. Counters use even/odd fill.
BONES={
 'bar':'M0 32 Q2 22 13 26 C35 31 68 22 80 23 Q90 26 96 12 Q103 17 99 69 Q97 78 88 73 C68 69 38 76 17 72 Q4 79 1 65 Z',
 'stem':'M12 1 Q40 -1 79 1 Q96 -1 93 5 L80 11 L77 43 L91 49 L78 54 L75 88 Q75 94 98 94 Q94 100 70 98 L42 99 Q17 102 12 96 L16 57 L3 53 L16 46 Q19 21 17 11 Q18 6 8 5 Z',
 'narrow':'M15 0 Q52 1 83 0 Q102 -1 98 5 L81 10 C80 43 75 78 80 92 C86 96 94 95 99 94 Q96 100 79 99 L31 100 Q12 100 13 97 C18 66 19 22 16 9 Q13 5 1 5 Q1 1 15 0 Z',
 'hook':'M67 1 Q75 2 91 1 Q98 1 94 7 L89 13 C87 32 93 55 86 73 Q74 98 43 100 C23 102 3 94 4 81 C4 71 12 65 22 65 C33 65 38 71 37 77 Q36 85 27 86 Q20 86 18 80 Q17 75 22 74 Q27 73 28 77 Q32 71 26 70 Q17 66 12 76 Q7 87 20 91 C39 98 63 85 68 66 Q71 55 69 44 L65 39 L69 34 L69 12 Q69 7 64 7 Q62 1 67 1 Z',
 'ring':'M56 4 C78 -1 96 12 99 36 C107 65 85 94 57 98 C31 104 8 94 2 69 C-4 45 10 15 32 8 Q40 3 45 0 Q50 0 50 5 Z M52 17 C35 16 22 29 18 47 C13 68 24 84 41 86 C61 89 76 76 81 57 C87 37 79 16 60 15 Z',
 'rieul':'M4 5 Q12 2 21 5 C43 7 65 4 78 4 Q88 5 96 0 Q99 -1 98 7 L95 43 Q96 49 90 51 C67 49 42 52 25 52 L23 82 C46 85 67 81 82 80 Q92 82 97 75 Q102 76 98 94 Q96 100 88 98 C62 94 27 99 10 98 L0 96 C4 79 5 59 6 44 L7 36 Q39 37 73 36 L76 19 Q44 18 17 20 Q4 21 3 15 Z',
 'rieul_low':'M2 4 Q12 0 20 3 C39 6 69 2 83 3 Q91 3 98 0 L96 46 Q95 50 88 49 L25 52 L24 79 C43 84 67 80 85 77 C91 77 94 73 96 66 Q103 67 99 87 Q99 98 88 99 C62 96 29 102 5 98 L6 37 Q39 40 74 35 L75 20 Q34 17 9 22 L3 18 Z',
 'tigeut':'M4 5 Q13 2 24 5 C48 8 69 4 80 4 Q92 5 99 1 L96 19 C76 18 49 21 28 21 L24 76 C45 82 71 78 87 74 Q93 72 97 65 Q103 64 99 78 L96 95 Q94 100 87 98 C65 95 38 100 6 96 L4 93 Q10 47 10 20 Q9 14 3 13 Z',
 'mieum':'M4 2 Q15 5 32 5 L71 4 Q87 4 96 0 Q101 -1 99 8 L94 93 Q95 99 89 98 C64 95 34 99 11 97 L1 94 Q7 40 6 17 Q7 9 0 8 Z M25 22 L22 77 C40 80 61 77 74 76 L78 21 Q52 20 25 22 Z',
 'kiyeok':'M2 5 Q9 2 17 5 C40 9 68 5 80 5 Q90 4 96 1 Q102 -2 100 8 L96 52 Q94 81 80 94 Q72 101 65 99 Q65 97 71 90 C77 81 79 57 79 21 C54 19 27 23 9 21 Q3 23 2 16 Z',
 'nieun':'M10 1 Q21 -1 32 1 L27 11 L24 56 C24 64 21 74 23 79 C40 84 60 78 73 76 C86 73 91 65 85 62 Q81 61 81 66 Q82 68 85 68 Q78 74 72 67 Q67 59 76 54 C90 47 104 60 96 77 C87 94 57 98 30 99 L5 96 C7 76 8 54 7 38 L2 33 L7 30 L8 10 L3 7 Z',
 'siot':'M48 0 C55 1 68 0 74 5 Q72 12 68 18 C65 32 64 40 68 49 C76 66 84 73 96 80 Q102 84 98 90 L87 99 Q63 85 54 56 C43 75 24 92 5 98 Q0 100 0 93 Q21 74 33 51 C44 29 48 13 45 7 L40 5 Q40 0 48 0 Z',
 'wave':'M0 45 Q10 19 21 30 C29 35 37 34 45 18 L52 7 L62 21 Q69 35 78 29 L89 16 Q95 12 99 25 L100 54 Q88 81 77 66 Q66 56 61 64 L50 90 L40 69 Q36 60 29 63 C16 78 7 77 1 69 Z',
 'teeth':'M1 15 Q19 12 38 14 C59 16 78 10 98 14 L95 33 L88 64 L78 43 L69 79 L60 47 L51 78 L42 46 L32 80 L23 49 L14 72 L7 43 Z',
 'flourish':'M0 68 C18 76 35 74 50 64 C69 51 73 31 63 20 C57 12 44 13 40 21 C35 29 39 41 47 41 C52 42 56 36 51 34 Q46 36 46 31 C42 23 54 18 59 27 C66 38 57 52 43 52 C29 51 23 36 28 22 C33 4 52 -4 68 3 C88 12 91 35 83 56 C70 91 34 108 0 96 Z',
 'finial':'M7 100 C24 87 33 69 41 52 C28 57 15 49 14 34 C11 13 33 -1 51 3 C75 6 88 24 84 45 C81 60 72 70 61 76 Q60 91 69 99 Z M60 33 C60 22 51 16 41 18 C32 19 27 26 29 33 Q32 40 39 38 Q46 36 41 31 Q37 29 35 31 Q35 24 45 24 C53 24 58 30 55 39 Q59 37 60 33 Z',
 'wall':'M8 0 L28 1 L25 12 L21 58 C20 69 17 77 21 81 Q53 87 86 78 Q95 77 97 69 Q102 68 98 87 L95 97 Q91 99 82 97 C56 95 27 101 5 96 Q10 47 10 19 L7 11 Z',
 'spark':'M50 0 C53 30 59 42 99 49 C66 52 55 63 50 100 C47 69 41 56 0 50 C35 46 46 36 50 0 Z',
}
def prim(kind,x,y,w,h):return (kind,x,y,w,h)
def bars(x,y,w,h):
    return [prim('bar',x,y,w,h*.24),prim('narrow',x+w*.18,y+h*.1,w*.21,h*.77),
            prim('narrow',x+w*.62,y+h*.09,w*.21,h*.78),prim('bar',x-1,y+h*.79,w+2,h*.27)]
def e_vowel(x,y,w,h,curled=False):
    return [prim('stem',x+w*.29,y+h*.08,w*.28,h*.82),prim('bar',x,y+h*.39,w*.42,h*.12),
            prim('hook',x+w*.18,y,w*.88,h) if curled else prim('narrow',x+w*.72,y,w*.26,h)]
def o_vowel(x,y,w,h):
    return [prim('stem',x+w*.46,y,w*.14,h*.84),prim('bar',x,y+h*.72,w,h*.39)]
# Individual blocks are sized to keep Hangul counters open at native game size.
GLYPHS={
 '페':bars(4,21,51,53)+e_vowel(55,3,44,94,True)+[prim('finial',87,-3,13,14)],
 '어':[prim('ring',4,23,52,52),prim('bar',57,42,25,13),prim('hook',43,7,59,94)],
 '리':[prim('rieul',4,21,52,58),prim('hook',46,3,54,96)],
 '테':[prim('wall',4,28,52,51),prim('teeth',7,18,51,24),prim('bar',17,45,34,12)]+e_vowel(59,5,40,89),
 '일':[prim('ring',9,12,46,45),prim('stem',68,2,15,53),prim('rieul_low',15,60,73,37)],
 '앙':[prim('ring',3,10,45,45),prim('stem',57,1,15,55),prim('bar',65,22,27,12),prim('ring',28,59,47,41),prim('finial',57,-4,14,12)],
 '코':[prim('kiyeok',9,8,69,44),prim('wave',19,28,52,15)]+o_vowel(4,59,93,37),
 '르':[prim('rieul',10,8,72,57),prim('bar',0,81,78,15),prim('flourish',65,56,34,39)],
 '심':[prim('siot',3,5,55,49),prim('stem',70,0,15,52),prim('mieum',15,60,68,36)],
 '포':bars(9,9,74,51)+o_vowel(2,65,96,30),
 '니':[prim('nieun',1,15,57,64),prim('hook',45,0,55,98)],
}
# The upper line spans both versions. The Encore star marks the turn between
# lines. Symphony's paired star cluster leads into its wider lower line.
def layout(name):
    top=[('페',13,6,100,105),('어',109,7,95,102),('리',204,5,91,104),
         ('테',294,8,102,99),('일',398,9,94,101)]
    if name=='앙코르':
        lower=[('앙',71,112,99,91),('코',177,109,112,94),('르',295,106,118,101)]
        stars=[(409,111,25,32)]
    elif name=='심포니':
        lower=[('심',71,108,107,95),('포',190,111,106,95),('니',305,110,114,98)]
        stars=[(30,126,25,33),(51,151,14,19)]
    else:raise ValueError(name)
    return top+lower,stars

class Contours(BasePen):
    def __init__(self):super().__init__(None);self.polys=[];self.line=[]
    def _moveTo(self,p):self.line=[np.array(p,dtype=float)]
    def _lineTo(self,p):self.line.append(np.array(p,dtype=float))
    def _curveToOne(self,a,b,c):
        p=self.line[-1];a,b,c=map(np.asarray,(a,b,c))
        length=np.linalg.norm(p-a)+np.linalg.norm(a-b)+np.linalg.norm(b-c)
        for u in np.linspace(0,1,max(4,int(length/2)+1))[1:]:
            v=1-u;self.line.append(v*v*v*p+3*v*v*u*a+3*v*u*u*b+u*u*u*c)
    def _qCurveToOne(self,a,b):
        p=self.line[-1];a,b=map(np.asarray,(a,b))
        for u in np.linspace(0,1,max(4,int((np.linalg.norm(p-a)+np.linalg.norm(a-b))/2)+1))[1:]:
            self.line.append((1-u)**2*p+2*(1-u)*u*a+u*u*b)
    def _closePath(self):self.polys.append(np.asarray(self.line));self.line=[]
    def _endPath(self):self._closePath()
@lru_cache(None)
def outline(n):
    pen=Contours();parse_path(BONES[n],pen);return pen.polys
def pieces(name):
    glyphs,stars=layout(name)
    for ch,x,y,w,h in glyphs:
        for shape,a,b,sw,sh in GLYPHS[ch]:
            yield shape,x+a*w/100,y+b*h/100,sw*w/100,sh*h/100,'ink'
    for x,y,w,h in stars:
        yield 'spark',x,y,w,h,'ink'
        yield 'spark',x+w*.17,y+h*.17,w*.66,h*.66,'gold'
@lru_cache(maxsize=8)
def master(name,scale=3):
    shape=(222*scale,505*scale)
    ink=np.zeros(shape,np.uint8);gold=np.zeros(shape,np.uint8)
    for n,x,y,w,h,kind in pieces(name):
        polys=[np.rint((p*[w/100,h/100]+[x,y])*scale).astype('int32') for p in outline(n)]
        # Each outline is composited individually: a ring's counter never erases
        # a separate overlapping stroke.
        tgt=gold if kind=='gold' else ink
        cv2.fillPoly(tgt,polys,255,lineType=cv2.LINE_AA)
    sigma=scale*3.9
    edge=cv2.dilate(ink,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(scale*1.7)*2+1,)*2))
    shadow=cv2.GaussianBlur(edge,(0,0),sigma)
    out=Image.new('RGBA',(shape[1],shape[0]))
    for ch,alpha in [((10,8,13),np.rint(shadow*.77).astype('uint8')),((255,255,251),edge),((17,15,19),ink),((250,222,101),gold)]:
        pt=Image.new('RGBA',out.size,(*ch,0));pt.putalpha(Image.fromarray(alpha));out.alpha_composite(pt)
    return out
def logo_layer(size,box,name,english=False):
    im=Image.new('RGBA',size);x,y,r,b=box
    m=master(name,4)
    # The original lettering changes scale with each native canvas.
    fitted=m.resize((r-x,b-y),Image.Resampling.LANCZOS)
    im.alpha_composite(fitted,(x,y))
    return im
def export():
    dest=ROOT/'design';dest.mkdir(exist_ok=True)
    for n in ('앙코르','심포니'):
        master(n,4).save(dest/(n+'.png'))
if __name__=='__main__':export()

