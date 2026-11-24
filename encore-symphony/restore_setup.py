from pathlib import Path
p=Path('logos.py');text=p.read_text(encoding='utf-8-sig').replace('import re','import re\nfrom restoration import restore')
a=text.index('    mask=dil(mask,13);');b=text.index('    clean=Image.fromarray(result)',a)
text=text[:a]+'''    mask=dil(mask,11)
    result=restore(a,mask,(358,65,576,576))
    # Use native paper texture to replace the fine grain lost inside the hidden ink.
    donor=q[:,np.minimum(np.arange(q.shape[1])+325,q.shape[1]-1),:].astype('float32')
    grain=donor-cv2.GaussianBlur(donor,(0,0),.9)
    result[:,:,:3][mask]=np.clip(np.rint(result[:,:,:3].astype('float32')+.34*grain),0,255).astype('uint8')[mask]
'''+text[b:]
a=text.index('    # Transport material');b=text.index('    return base,dict(',a)
text=text[:a]+'''    # The sky grain is a known native sample. Recover the contours hidden in both
    # title sources from the unprinted foreground on all sides of each mask.
    inferred=restore(base,unknown,(189,29,576,448))[:,:,:3].astype('float32')
    texture=sky.astype('float32')-cv2.GaussianBlur(sky.astype('float32'),(0,0),1.05)
    close=(np.max(np.abs(cv2.GaussianBlur(inferred,(0,0),2)-cv2.GaussianBlur(sky.astype('float32'),(0,0),2)),axis=2)<35)
    rec=np.clip(np.rint(inferred+texture*np.where(close,.63,.22)[:,:,None]),0,255).astype('uint8')
    base[:,:,:3][unknown]=rec[unknown]
'''+text[b:]
text=text.replace('local boundary colour with coherent donor grain','locally restored colour and boundaries with donor grain').replace('matched Japanese-disc end-card sky texture under jointly occluded strokes.','jointly occluded contours inferred locally with grain from the registered original sky.')
p.write_text(text,encoding='utf-8')
p=Path('plates.py');text=p.read_text(encoding='utf-8-sig').replace('def credits():','def credits(only=None):').replace('    for n,a in frames.items():\n        k=', '    for n,a in frames.items():\n        if only and n not in only:continue\n        k=');p.write_text(text,encoding='utf-8')

