from assets import *
import numpy as np, subprocess,sys
pack=Path('P:/AI/Codex/projects/YoruGaKuru_KR_asset_opening_20260908/tools')
sys.path.insert(0,str(pack/'stt_pkgs'))
from faster_whisper import WhisperModel
ff='F:/DOWN/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe'
src=source('Encore')/'mov/0001.mpg'; audio=np.frombuffer(subprocess.check_output([ff,'-v','error','-i',str(src),'-map','0:a:0','-ac','1','-ar','16000','-f','f32le','pipe:1']),np.float32)
modelname='models--Systran--faster-whisper-small'
modeldir=next((pack/'stt_models'/modelname/'snapshots').iterdir())
model=WhisperModel(str(modeldir),device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
segs,meta=model.transcribe(audio,language='ja',beam_size=3,condition_on_previous_text=False,vad_filter=False,without_timestamps=False)
out=[dict(start=s.start,end=s.end,text=s.text,confidence=s.avg_logprob,no_speech=s.no_speech_prob) for s in segs];save('audit/op_voice_check.json',out)
print(out)

