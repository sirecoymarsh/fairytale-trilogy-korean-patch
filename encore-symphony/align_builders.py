from pathlib import Path
p=Path('logos.py');s=p.read_text(encoding='utf-8-sig');a=s.index('def animation():');b=s.index("if __name__=='__main__':",a)
s=s[:a]+"""def animation():
    from symphony_motion import track
    track()
"""+s[b:]
s=s.replace('(247,110,719,351)','(249,127,720,344)');p.write_text(s,encoding='utf-8')
p=Path('plates.py');s=p.read_text(encoding='utf-8-sig').replace('box=(397,180,885,460)','box=(392,195,888,442)');p.write_text(s,encoding='utf-8')

