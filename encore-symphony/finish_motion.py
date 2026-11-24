from pathlib import Path
f=Path('movie_design.py');s=f.read_text(encoding='utf-8-sig').replace('pivot,rad=robust_fit()','pivot,rad=robust_fit()\n# Register the resting print to its measured original pixel window.\npivot=np.array([L,T])+center-rad');f.write_text(s,encoding='utf-8')
f=Path('movie_render.py');s=f.read_text(encoding='utf-8-sig')
s=s.replace("    count=1 if shutter<=.015 or f<2209 else 7","""    if shutter<=.015 or f<2209:count=1
    else:
        probe=np.array([[0,0,1],[W,0,1],[0,H,1],[W,H,1]])
        travel=np.linalg.norm(probe@(pose(f+.5*shutter)-pose(f-.5*shutter)).T,axis=1).max()
        count=max(3,min(65,2*int(np.ceil(travel/2.3))+1))""")
f.write_text(s,encoding='utf-8')

