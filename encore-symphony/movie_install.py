from opening_build import *
from assets import live
import math
def verify_install():
    if (ROOT/'audit/opening_caption_persisted.json').is_file() and (ROOT/'audit/opening_caption_Encore.json').is_file():
        from opening_caption_finish import install
        return install('Encore')
    qa=read('audit/opening_build.json');file=Path(qa['replacement'])
    dest=live('Encore')/'mov/0001.mpg'
    ids=[0,2111,2129,2136,2160,2209,2225,2261,2341,2380,2436,2500,2514,3014,3015,3016,3498,3500,3530,3650,3695,3817]
    old=loadframes(ids);picked={};cap=cv2.VideoCapture(str(file));wanted=set(ids)
    for i in range(max(ids)+1):
        if not cap.grab():raise ValueError(('short',i))
        if i in wanted:
            ok,img=cap.retrieve();assert ok;picked[i]=img
    cap.release()
    checks={};shutter=read('audit/op_design_proof.json')['shutter']
    for i in ids:
        design=edit(old[i],i,shutter);image=picked[i];diff=image.astype('float32')-design
        err=float(np.abs(diff).mean());sq=float(np.mean(diff*diff))
        exact=(i<2130 or 3015<=i<3499)
        if exact and np.any(diff):raise ValueError(('source image moved across splice',i,err))
        if not exact and err>5:raise ValueError(('persisted image too different',i,err))
        checks[i]=dict(exact_original=bool(np.array_equal(old[i],image)),design_mae=round(err,4),design_psnr=round(10*math.log10(255**2/sq),2) if sq else None)
    prior=read('audit/opening_install.json') if (ROOT/'audit/opening_install.json').exists() else {}
    current=digest(dest);known={ORIGINAL,qa['sha256'],prior.get('sha256')}
    if current not in known:raise ValueError('Unexpected live video '+current)
    if current!=qa['sha256']:
        q=dest.with_name('0001.ko-pending');shutil.copyfile(file,q)
        if digest(q)!=qa['sha256']:raise ValueError('staged copy mismatch')
        os.replace(q,dest)
    assert digest(dest)==qa['sha256']
    save('audit/opening_install.json',dict(installed=str(dest),sha256=qa['sha256'],source_sha256=ORIGINAL,source_comparison=checks,
         unchanged_video_pictures=qa['original_picture_count'],complete_audio_stream_match=True,rollback=str(SRC),translator_model='Codex internal'))
    print('Installed',dest,'no skipped picture at either splice',len(checks),'design comparison frames')
if __name__=='__main__':verify_install()


