"""Recompose only the marked surfaces on the previously verified clean backgrounds."""
from logos import *
from lettering import master,export
def render():
    export()
    ix=read('audit/index.json')
    for game,name in [('Encore','앙코르'),('Symphony','심포니')]:
        layer=logo_layer((1280,720),(249,127,720,344),name)
        manifest=read('audit/logos.json')
        for i in range(8):
            k=next(k for k in ix[game] if k.startswith(f'grpe/9101.lwg/{i}:'))
            clean=Image.open(ART/artkey(game,k)/'clean.png').convert('RGBA');out=clean.copy();out.alpha_composite(layer)
            emit(game,k,Image.fromarray(original_title(game,i)),clean,out,manifest[game][k]['source_ja'],'페어리테일 '+name,'Original-aligned two-line hand-drawn Hangul outlines, hooked terminals, optical white keyline and individual sparkle. Verified clean background reused.')
    animation()
    manifest=read('audit/logos.json')
    for game,rs in INFO.items():manifest[game].update(rs)
    save('audit/logos.json',manifest);INFO.clear()
    k='grpe/4001.wcg';game='Symphony';c=Image.open(ART/artkey(game,k)/'clean.png').convert('RGBA');out=c.copy()
    a=raw(game,k);out.alpha_composite(logo_layer(a.size,(392,195,888,442),'심포니'))
    emit(game,k,a,c,out,'フェアリーテイル・シンフォニー','페어리테일 심포니','Same hand-drawn master as the main screen and opening animation.')
    p=read('audit/plates.json');p[game].update(INFO[game]);save('audit/plates.json',p)
if __name__=='__main__':render()

