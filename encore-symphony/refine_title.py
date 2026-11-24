from pathlib import Path
p=Path('logos.py');t=p.read_text(encoding='utf-8-sig');a=t.index('    rec=np.clip(np.rint(inferred');b=t.index('    base[:,:,:3][unknown]',a)
t=t[:a]+'''    yy,xx=np.indices(unknown.shape)
    foreground=np.zeros_like(unknown,dtype='float32')
    # Three balloons and the castle turret cross the native sky. Keep the actual
    # registered sky elsewhere, including its paper edges, seams and cloud ink.
    for x,y,rx,ry in [(393,333,30,32),(477,312,29,29),(551,235,23,32)]:
        radius=((xx-x)/rx)**2+((yy-y)/ry)**2
        foreground=np.maximum(foreground,np.clip((1.30-radius)*3.3,0,1))
    roof=np.asarray([[532,306],[549,281],[563,276],[571,245],[591,256],[599,225],[629,210],[684,211],[718,323],[590,350],[545,333]],'int32')
    castle=np.zeros_like(unknown,dtype='uint8');cv2.fillPoly(castle,[roof],255)
    foreground=np.maximum(foreground,cv2.GaussianBlur(castle.astype('float32')/255,(0,0),1.4))
    inferred=np.clip(inferred+texture*np.where(close,.63,.22)[:,:,None],0,255)
    rec=np.rint(sky*(1-foreground[:,:,None])+inferred*foreground[:,:,None]).astype('uint8')
    # The parchment ends above the hanging blue and red balloons. Its independently
    # unobstructed lower contours are native pixels and take priority over prediction.
    native=req[i][:,:,:3];hsv=cv2.cvtColor(native,cv2.COLOR_RGB2HSV)
    exposed=(yy>=325)&(yy<371)&(xx>=369)&(xx<=524)&(hsv[:,:,1]>180)&(hsv[:,:,2]>101)
    native_close=np.abs(native.astype('int16')-rec.astype('int16')).max(2)<55
    rec[exposed&native_close]=native[exposed&native_close]
'''+t[b:];p.write_text(t,encoding='utf-8')

