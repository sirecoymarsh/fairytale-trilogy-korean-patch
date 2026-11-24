"""Restore the limited regions shared by the title marks using adjacent native artwork."""
import importlib
import sys
import types
from pathlib import Path
from functools import lru_cache
import numpy as np
import cv2
BASE=Path('F:/DOWN/Ballon-translator-portable-main (1)/Ballon-translator-portable-main')
@lru_cache(maxsize=1)
def getnet():
    import torch
    pkg=types.ModuleType('bt_lama_native')
    pkg.__path__=[str(BASE/'modules/inpaint')]
    sys.modules[pkg.__name__]=pkg
    module=importlib.import_module(pkg.__name__+'.lama')
    weights=BASE/'data/models/lama_large_512px.ckpt'
    net=module.LamaFourier(build_discriminator=False,use_mpe=False,large_arch=True)
    data=torch.load(weights,map_location='cpu',weights_only=True)
    net.generator.load_state_dict(data['gen_state_dict'])
    net.eval().to('cuda' if torch.cuda.is_available() else 'cpu')
    return net
def restore(rgb,mask,region):
    import torch
    net=getnet()
    device=next(net.generator.parameters()).device
    x,y,w,h=region
    part=rgb[y:y+h,x:x+w,:3]
    ma=mask[y:y+h,x:x+w]
    assert ma.sum()==mask.sum() and h%8==0 and w%8==0
    image=torch.from_numpy(np.ascontiguousarray(part.transpose(2,0,1))).float()[None].to(device)/255
    m=torch.from_numpy(ma.astype('float32'))[None,None].to(device)
    with torch.inference_mode():
        result=net(image,m)[0].permute(1,2,0).cpu().numpy()
    restored=rgb.copy()
    target=restored[y:y+h,x:x+w,:3]
    target[ma]=np.clip(np.rint(result[ma]*255),0,255).astype('uint8')
    return restored


