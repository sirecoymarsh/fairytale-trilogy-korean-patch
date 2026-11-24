from pathlib import Path
p=Path('lettering.py');t=p.read_text(encoding='utf-8')
t=t.replace(" 'spark':'M50", """ 'finial':'M7 100 C24 87 33 69 41 52 C28 57 15 49 14 34 C11 13 33 -1 51 3 C75 6 88 24 84 45 C81 60 72 70 61 76 Q60 91 69 99 Z M60 33 C60 22 51 16 41 18 C32 19 27 26 29 33 Q32 40 39 38 Q46 36 41 31 Q37 29 35 31 Q35 24 45 24 C53 24 58 30 55 39 Q59 37 60 33 Z',
 'wall':'M8 0 L28 1 L25 12 L21 58 C20 69 17 77 21 81 Q53 87 86 78 Q95 77 97 69 Q102 68 98 87 L95 97 Q91 99 82 97 C56 95 27 101 5 96 Q10 47 10 19 L7 11 Z',
 'spark':'M50""")
t=t.replace("'페':bars(4,21,51,53)+e_vowel(55,3,44,94,True)","'페':bars(4,21,51,53)+e_vowel(55,3,44,94,True)+[prim('finial',87,-3,13,14)]")
t=t.replace("prim('bar',49,42,33,13)","prim('bar',57,42,25,13)")
t=t.replace("prim('tigeut',4,23,52,56),prim('teeth',7,18,51,19)","prim('wall',4,28,52,51),prim('teeth',7,18,51,24)")
t=t.replace("prim('kiyeok',9,10,69,49)","prim('kiyeok',9,8,69,44)")
t=t.replace("prim('ring',28,59,47,41)","prim('ring',28,59,47,41),prim('finial',57,-4,14,12)")
p.write_text(t,encoding='utf-8')
p=Path('plates.py');t=p.read_text(encoding='utf-8-sig')
a=t.index('def logo_layer(');b=t.index('def credits(',a)
p.write_text(t[:a]+'from lettering import logo_layer\n'+t[b:],encoding='utf-8')

