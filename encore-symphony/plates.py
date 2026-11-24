from labels import *
import math
WHITE=(255,255,255,255)
# Left / middle / right columns of the original paper, stanzas separated by empty rows.
LYRICS=[
 ['작은 새가','또 지저귀네','이 이야기','그다음은 뭘까?','','거꾸로 뒤집힌 ‘설마’가 이곳에서','틀림없이 일어날 거야','지켜봐 줘','','두근거림과 두근거림이 이어져','너도 지금','웃고 있어','','조그만 캡슐','거짓의 장미','별의 조각','볼 가득 머금으면 마음이 녹아','','내가 사랑하는','이 정원에서','춤추자','자, 이 손을 잡아'],
 ['가짜와 진짜가 뒤바뀌어','아마 너는','모를 거야','','고마워, 안녕, 중얼거려도','여기서는','나갈 수 없어','','있잖아','행복과','불행','누가 정하는 걸까','이 이야기의 끝을','','내가 사랑하는','이 정원에서','춤추자','자, 너도 함께'],
 ['슬퍼지면','전부 잊어버리고','즐거운 꿈을 꾸며','그저 노래해','','지금','네 눈에는','보이니?','돌고 돌아','시작의 실이 풀린 그 끝','','내가 사랑하는','이 정원에서','춤추자','영원히 끝나지 않을 왈츠를','','몇 번이고 꾸었던','무서운 꿈이라면','틀림없이 금방','잊을 수 있을 테니까, 응']]
def lyrics():
    for g in GAMES:
        k='grpo_ex/9501.wcg';s=raw(g,k);a=arr(s);c=a.copy()
        for l,t,r,b in [(14,12,947,81),(21,91,946,518)]:
            crop=c[t:b,l:r];mask=(crop[:,:,:3]<255).any(2)&(crop[:,:,3]==255);crop[mask]=WHITE
        cl=Image.fromarray(c);out=cl.copy()
        fittext(out,(27,12,400,31),'오프닝 테마',19,'black',SERIF,'left');fittext(out,(23,34,422,77),'『페어리테일』',46,'black',SERIF,'left')
        fittext(out,(450,53,941,78),'작사·노래  Rita     작곡·편곡  Blueberry & Yogurt',20,'black',SERIF,'right')
        for col,(left,right) in enumerate([(28,365),(377,714),(726,947)]):
            for i,l in enumerate(LYRICS[col]):
                if l:fittext(out,(left,94+i*19,right,113+i*19),l,18,'black',SERIF,'left')
        emit(g,k,s,cl,out,'オープニングテーマ『フェアリーテイル』歌詞カード','페어리테일 가사 카드\n'+'\n\n'.join('\n'.join(v) for v in LYRICS),'Uniform white paper inside the original page, separator and paper edges preserved.')
CREDITS={
 4002:[('기획·원안·시나리오',25),('우미하라 노조무',32),('',18),('캐릭터 디자인·원화',25),('오이시 류코',32)],
 4003:[('타이틀 로고 디자인',24),('시마사라 유메키',30),('',10),('타이틀 화면 디자인',24),('오이시 류코',30),('',10),('CG 작업',24),('시마사라 유메키',28),('오키 이누타로',27),('aina',27)],
 4004:[('낙원 지도 러프',25),('타카시',30),('',12),('낙원 지도 제작',25),('Lem',30),('',12),('프로그램·스크립트 작업',25),('노기 후나사토 (codeX)',30)],
 4005:[('BGM',24),('삿포로 모모코',29),('내시 스튜디오 FREE USE MUSIC',27),('차이콥스키 『백조의 호수』',27),('',13),('메인 테마 『페어리테일』',27),('작사  Rita',25),('작곡·편곡  Blueberry & Yogurt',25),('노래  Rita',25)],
 4006:[('출연',25),('',9),('앨리스 · 과거의 앨리스',24),('모카 초코',31),('',9),('그레텔 · 과거의 그레텔',24),('쿠사야나기 준코',31),('',9),('오데트 · 과거의 오데트 · 오딜',24),('카와시마 리노',31)],
 4007:[('라푼젤',24),('미스미 나나호',32),('',13),('게르다 · 과거의 게르다',24),('아카시 유키',32),('',13),('검은 소녀',24),('사쿠라기 치카',32)],
 4008:[('음성 제작',25),('주식회사 아르카디아 프로젝트',28),('',8),('음성 연출·녹음',23),('Ben',28),('음성 편집',23),('OKY',28),('음성 제작 담당',23),('M.KOMIYA',28),('녹음 스튜디오',23),('아르카디아 프로젝트 스튜디오',26)],
 4009:[('진행 관리',25),('Kobi',33),('',40),('판매',25),('주식회사 비즈니스 파트너',32)],
 4010:[('제작·저작',28)]}
def credit_bg():
    frames={n:arr(raw('Symphony',f'grpe/{n}.wcg')) for n in range(4001,4011)}
    # These authored cards use one bit-identical background. White type and black shadows occupy different rows on each card.
    stack=np.stack([v[85:600,300:980] for v in frames.values()])
    med=np.median(stack,axis=0)
    dist=np.abs(stack.astype(float)-med).sum(3);ii=dist.argmin(0)
    yy,xx=np.indices(ii.shape); bg=frames[4009].copy();bg[85:600,300:980]=stack[ii,yy,xx]
    return frames,bg
from lettering import logo_layer
def credits(only=None):
    frames,bg=credit_bg()
    for n,a in frames.items():
        if only and n not in only:continue
        k=f'grpe/{n}.wcg';s=Image.fromarray(a)
        clean=a.copy();l,t,r,b=300,85,980,600
        if n==4010:
            # Card 4009 has bare paper here. The source role spans y=314..335,
            # and the independent Latin brand mark begins at y=346.
            l,t,r,b=512,307,768,343
            donor=frames[4009]
        else:
            donor=bg
        clean[t:b,l:r]=donor[t:b,l:r];c=Image.fromarray(clean);out=c.copy()
        if n==4001:
            box=(392,195,888,442);out.alpha_composite(logo_layer(s.size,box,'심포니',False));words='페어리테일 심포니'
        else:
            vals=CREDITS[n];words='\n'.join(t for t,p in vals if t)
            total=sum(p+7 for t,p in vals); y=(720-total)//2 if n!=4010 else (t+b-vals[0][1]-5)//2
            for phrase,points in vals:
                if phrase:fittext(out,(330,y,950,y+points+5),phrase,points,WHITE,FONT,'center',1,'#24151a')
                y+=points+7
        emit('Symphony',k,s,c,out,'スタッフクレジット '+str(n),words,'Same pixel coordinates recovered from the shared blank portions of the other nine original credit cards.')
def movie_button():
    import build_fairytale_grpo_ui_master as ref
    g,k='Encore','grpo/0006.wcg';s=raw(g,k);a=arr(s);m=ref.neutral_bright_mask(a);y,x=np.where(m)
    center=((x.max()+x.min())/2,(y.max()+y.min())/2);ang=ref.principal_angle(m)
    clean,mask,_=ref.restore_small_plate(a,m);mask &= a[:,:,3]>0;clean[~mask]=a[~mask];clean[:,:,3]=a[:,:,3]
    c=Image.fromarray(clean);hi=Image.new('RGBA',(s.width*4,s.height*4));f=ImageFont.truetype(str(MENU),48)
    try:f.set_variation_by_name('Black')
    except OSError:pass
    bx=f.getbbox('영상');ImageDraw.Draw(hi).text((center[0]*4-(bx[0]+bx[2])/2,center[1]*4-(bx[1]+bx[3])/2),'영상',font=f,fill='white')
    hi=hi.rotate(-ang,resample=Image.Resampling.BICUBIC,center=(center[0]*4,center[1]*4));out=c.copy();out.alpha_composite(hi.resize(s.size,Image.Resampling.LANCZOS))
    emit(g,k,s,c,out,'Movie','영상','Source glyph baseline measured in image coordinates and supersampled with the corrected Pillow rotation sign.')
if __name__=='__main__':
    lyrics();credits();movie_button();save('audit/plates.json',INFO)

