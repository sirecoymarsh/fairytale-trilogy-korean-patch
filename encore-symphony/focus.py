from assets import *
from subprocess import run
from PIL import Image, ImageDraw
def selected(k):
    b,n,*layer=k.split('/'); s=n.split('.')[0]; idn=int(s) if s.isdigit() else -1
    if b=='grpo':return True
    if b=='grpo_ex':return (2000<=idn<4000 or idn>=9500)
    if b=='grps':return n.startswith(('dt','dat_new'))
    if b=='grpe':return idn in (3022,9001,9002,9003,9101,9201,9905) or 4001<=idn<=4010
    if b=='grpo_ef':return 1<=idn<=96
    if b=='grpo_cu':return 5800<=idn<=6000
    return False
def fullpath(g,k):
    b,n,*sub=k.split('/')
    name=n.split('.')[0]+('-'+sub[0].split(':')[0] if sub else '')
    return ROOT/'audit/full'/g/b/(name+'.png')
def export():
    data=read('audit/index.json'); lines=[];ll={}
    for g,rec in data.items():
        for k,row in rec.items():
            if 'size' not in row or not selected(k): continue
            b,n,*layer=k.split('/')
            f=source(g)/(b+'.xfl');e=entry_map(f)[n];pos=e.absolute_offset;size=e.size
            if layer:
                if (f,n) not in ll: ll[f,n]=lwg(read_entry(f,n))
                recL=ll[f,n][int(layer[0].split(':')[0])];pos+=recL[2];size=recL[3]
            dst=fullpath(g,k);dst.parent.mkdir(parents=True,exist_ok=True)
            lines.append('\t'.join(map(str,[f,pos,size,dst,0])))
    jobs=ROOT/'audit/full-jobs.tsv';jobs.write_text('\n'.join(lines),encoding='utf-8-sig')
    run([str(ROOT/'tools/RasterBatch.exe'),str(jobs)],check=True)
    print('Native size candidates',len(lines))
if __name__=='__main__':export()
