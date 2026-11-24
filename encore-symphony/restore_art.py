from logos import *
from restoration import restore
import argparse
def do(mode):
    art_manifest=read('audit/logos.json')
    plate_manifest=read('audit/plates.json')
    if mode=='all':
        credits({4001});plate_manifest['Symphony'].update(INFO['Symphony']);save('audit/plates.json',plate_manifest)
        INFO.clear()
    credit=encore_credit()
    if mode=='sample':
        fr={g:[original_title(g,i) for i in range(8)] for g in GAMES}
        masks={g:registered_ink(g) for g in GAMES}
        req=[arr(Image.open(REF/f'{i:02d}/source.png')) for i in range(8)]
        base,stats=recover_title('Encore',0,fr,masks,req,credit)
        sample=ROOT/'audit'/'restoration-sample.png'
        Image.fromarray(base).crop((200,102,742,394)).save(sample)
        print(stats)
        return
    titles(credit)
    for g,r in INFO.items():art_manifest.setdefault(g,{}).update(r)
    save('audit/logos.json',art_manifest)
if __name__=='__main__':
    do(sys.argv[1])

