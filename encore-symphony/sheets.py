from assets import *
from PIL import Image,ImageDraw,ImageFont
from collections import defaultdict
from subprocess import run
import math
def bankcat(key):
    bank,entry,*sub=key.split('/')
    if bank=='grps':
        if sub:return 'system-'+entry.split('.')[0]
        if entry.startswith('dt'):return 'save'
        if entry.startswith('es'):return 'system-es'
        return 'system-other'
    if bank=='grpo_ex':
        return 'gallery-'+str(int(entry[:4])//1000)
    if bank=='grpe' and sub:return 'cg-layers'
    if bank=='grpo_bu0' or bank=='grpo_bu1':return 'portrait'
    return bank
def jobs(index):
    imgdir=ROOT/'audit/thumbs';imgdir.mkdir(parents=True,exist_ok=True)
    lines=[];seen=set(); layers={}
    for g,records in index.items():
        for key,row in records.items():
            if 'size' not in row or row['sha'] in seen: continue
            seen.add(row['sha']); bank,entry,*layer=key.split('/')
            src=source(g)/(bank+'.xfl');e=entry_map(src)[entry]
            pos=e.absolute_offset; size=e.size
            if layer:
                pair=(src,entry)
                if pair not in layers: layers[pair]=lwg(read_entry(src,entry))
                info=layers[pair][int(layer[0].split(':')[0])];pos+=info[2];size=info[3]
            dest=imgdir/(row['sha']+'.png')
            lines.append('\t'.join(map(str,[src,pos,size,dest,320])))
    path=ROOT/'audit/thumb-jobs.tsv';path.write_text('\n'.join(lines),encoding='utf-8-sig')
    run([str(ROOT/'tools/RasterBatch.exe'),str(path)],check=True)
def sheets(index):
    groups=defaultdict(list); seen=set()
    for g,records in index.items():
        for key,row in records.items():
            sha=row['sha']
            if 'size' not in row:continue
            cat=bankcat(key)
            ident=(cat,sha)
            if ident in seen:continue
            seen.add(ident)
            groups[cat].append((g,key,row))
    out=ROOT/'audit/sheets';out.mkdir(exist_ok=True)
    sheetdata={}
    for cat,group in groups.items():
        cellw,cellh,cols,rows=176,121,6,7
        if cat.startswith(('system-','gallery-','save','grpo','cg-layers')) and cat not in ('grpo_pp','grpo_cu','grpo_bg'):
            cellw,cellh=210,112
        pagesize=cols*rows
        for page,st in enumerate(range(0,len(group),pagesize),1):
            section=group[st:st+pagesize]
            im=Image.new('RGB',(cols*cellw,math.ceil(len(section)/cols)*cellh),'#434546');draw=ImageDraw.Draw(im); sheetname=cat+'-'+str(page).zfill(2);sheetdata[sheetname]=[]
            for i,(g,key,row) in enumerate(section):
                x=i%cols*cellw;y=i//cols*cellh
                p=Image.open(ROOT/'audit/thumbs'/(row['sha']+'.png')).convert('RGBA')
                p.thumbnail((cellw-3,cellh-19));im.paste(p,(x+(cellw-p.width)//2,y+(cellh-19-p.height)//2),p)
                label=g[0]+' '+key.split('/')[1].split('.')[0]+(' '+key.split('/')[-1] if key.count('/')==2 else '')+(' [KO]' if 'donor' in row else '')
                draw.text((x+2,y+cellh-14),label,fill='white');sheetdata[sheetname].append([g,key,row['sha']])
            im.save(out/(sheetname+'.jpg'),quality=90)
    save('audit/sheets.json',sheetdata)
    print('sheets:',{k:len(v) for k,v in groups.items()})
if __name__=='__main__':
    idx=read('audit/index.json');jobs(idx);sheets(idx)
