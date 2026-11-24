import json,sys,re,collections
sys.stdout.reconfigure(encoding='utf-8')
W=r"Y:\AI\claude-work\fairytale-review"
src=open(rf"{W}\register2.py",encoding='utf-8').read().split("LABELS=set()")[0]
ns={}; exec(src,ns); ja_reg=ns['ja_reg']; ko_reg=ns['ko_reg']
def clean_ja(s): return re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',s).replace('^n','')
def ruby_read(s):  # use reading for 私 etc.
    return re.sub(r'\|([^\[]+)\[([^\]]*)\]',r'\2',s).replace('^n','')
JFP=[('わたくし',r'わたくし|私\[わたくし\]'),('あたし',r'あたし'),('わたし',r'わたし|(?<![\[|])私(?![\]])'),('僕',r'僕|ぼく|ボク'),('俺',r'俺|おれ|オレ'),('うち',r'(?<![ぁ-ん])うち(?=[はがのも、])'),('わし',r'わし(?=[はがのも])'),('自分',r'自分(?=[はがも])'),('我',r'我(?=[はがの])|われわれ|我々')]
JSP=[('あなた',r'あなた|貴方|アナタ'),('あんた',r'あんた|アンタ'),('きみ',r'きみ|(?<![ぁ-んァ-ン一-龥])君(?![ぁ-ん]*達)'),('おまえ',r'お前|おまえ|オマエ'),('てめえ',r'てめえ|テメエ|てめぇ'),('貴様',r'貴様'),('そなた',r'そなた|おぬし')]
KFP=[('저',r'(?<![가-힣])(저는|저도|저를|저한테|저에게|저의|제가|전(?= )|저(?=[\s,.…!?]))|(?<![가-힣])제(?= [가-힣])'),('나',r'(?<![가-힣])(나는|나도|나를|나한테|나에게|나의|내가|난(?= )|나(?=[\s,.…!?])|내(?= [가-힣]))'),('우리',r'(?<![가-힣])우리')]
KSP=[('당신',r'당신'),('너',r'(?<![가-힣])(너는|너도|너를|너한테|너에게|너의|네가|넌(?= )|너(?=[\s,.…!?])|네(?= [가-힣]))'),('그쪽',r'그쪽'),('자네',r'자네'),('그대',r'그대'),('댁',r'(?<![가-힣])댁(?=[은이도])')]
def feats(pats,t):
    return [k for k,p in pats if re.search(p,t)]
def ja_tail(t):
    s=[x for x in re.split(r'[。！？!?…]+|　|\n',re.sub(r'[「」『』（）\(\)]','',t)) if x.strip()]
    if not s: return ''
    x=re.sub(r'[、，,ー〜～♪っッ・─\s]+$','',s[-1])
    return x[-3:]
def ko_end(t):
    t=re.sub(r'\|([^\[]+)\[[^\]]*\]',r'\1',t).replace('^n','\n')
    s=[x for x in re.split(r'[\.。！？!?…\n]+',re.sub(r'[「」『』（）\(\)]','',t)) if len(x.strip())>1]
    if not s: return ''
    x=re.sub(r'[,，、~〜♪ー―─\s]+$','',s[-1].strip())
    if re.search(r'(습니다|습니까|십시오|[갑답랍럽릅입합봅옵줍씁깁십읍]니다|[갑답랍럽릅입합봅옵줍씁깁십읍]니까)$',x): return '합쇼'
    if re.search(r'요$',x): return '해요'
    if re.search(r'(오|소)$',x) and re.search(r'(하오|이오|구려|시오|소)$',x): return '하오'
    if re.search(r'(는다|ㄴ다|다|냐|니|라|자|련|마)$',x): return '해라'
    return '해'
out={}
for g in ['Requiem','Encore','Symphony']:
    rows=[json.loads(l) for l in open(rf'{W}\{g}.jsonl',encoding='utf-8')]
    labels={r['ja'] for r in rows if r['changed'] and len(r['ja'])<=10 and not re.search(r'[。、？！…「」『』\^ 　（）()─]',r['ja'])}-{'はい','いいえ'}
    names=[l for l in labels if len(l)>=3 and re.fullmatch(r'[ァ-ヴー]+',l)]
    lines=[]; prev=None
    for r in rows:
        if not r['changed']: prev=None; continue
        if r['ja'] in labels: prev=(r['ja'],r['ko']); continue
        if prev:
            ja=clean_ja(r['ja']); jr=ruby_read(r['ja'])
            thought=ja.lstrip('　 ').startswith('（')
            voc=[n for n in names if re.search(n+r'(?:[、。！？…]|ちゃん|さん|$)',ja) and n!=prev[0]]
            lines.append(dict(spk=prev[0],spk_ko=prev[1],scene=r['scene'][:4],slot=r['slot'],blk=r['scene'][:2],thought=thought,
              jreg=ja_reg(ja),kreg=ko_reg(r['ko']),jfp=feats(JFP,jr),jsp=feats(JSP,jr),kfp=feats(KFP,r['ko'].replace('^n',' ')),ksp=feats(KSP,r['ko'].replace('^n',' ')),
              jtail=ja_tail(ja),kend=ko_end(r['ko']),voc=voc,ja=r['ja'],ko=r['ko']))
        prev=None
    out[g]=lines
json.dump(out,open(rf'{W}\voice_lines.json','w',encoding='utf-8'),ensure_ascii=False)
print({g:len(v) for g,v in out.items()})
