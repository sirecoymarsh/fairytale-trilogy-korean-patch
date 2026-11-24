"""Build the common gallery from retail CG, sound-room tables and original local movies."""
from assemble import *
from menu_scripts import pages
from wording import TRACKS,ROUTES
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import subprocess, tempfile, struct
PUB=OUT/'Library';ART=PUB/'media';TMP=HERE/'tmp';TOOL=BASE/'tools'/'UiAssetTool.exe'
WORKS={'Requiem':'레퀴엠','Encore':'앙코르','Symphony':'심포니'}
def binary(root,bank,name):
 loose=root/bank/name
 return loose.read_bytes() if loose.is_file() else read_entry(root/(bank+'.xfl'),name)
def cg_image(job):
 key,data=job;full=ART/(key+'.png');thumb=ART/(key+'-s.jpg')
 if not full.exists():
  source=TMP/(key+'.wcg');stage=TMP/(key+'.png');source.write_bytes(data)
  try:
   subprocess.run([str(TOOL),'wcg2png',str(source),str(stage)],check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
   os.replace(stage,full)
  finally:source.unlink(missing_ok=True)
 if not thumb.exists():
  with Image.open(full) as src:
   im=src.convert('RGB');im.thumbnail((360,210),Image.Resampling.LANCZOS);im.save(thumb,'JPEG',quality=89)
 return key
def ogg(wav):
 assert wav[:4]==b'RIFF' and wav[8:12]==b'WAVE'
 i=12
 while i+8<=len(wav):
  chunk=wav[i:i+4];length=int.from_bytes(wav[i+4:i+8],'little');body=wav[i+8:i+8+length]
  if chunk==b'data':
   if wav[20:22]==bytes((1,0)):return wav
   assert body.startswith(b'OggS') and b'vorbis' in body[:110];return body
  i+=8+length+(length%2)
 raise ValueError('missing Ogg stream')
def remove_empty_vorbis_stream(data):
 """Keep the game's Vorbis pages intact and drop its separate, empty ACM padding stream."""
 audio_serial = None
 pages = []
 offset = 0
 next_page = 0
 ended = False
 while offset < len(data):
  if data[offset:offset + 5] != b'OggS\0' or offset + 27 > len(data):
   raise ValueError('Invalid Ogg page header')
  segments = data[offset + 26]
  payload = offset + 27 + segments
  length = sum(data[offset + 27:payload])
  end = payload + length
  if end > len(data):
   raise ValueError('Truncated Ogg page')
  serial, sequence = struct.unpack_from('<II', data, offset + 14)
  flags = data[offset + 5]
  if audio_serial is None and flags & 2 and data[payload:payload + 7] == b'\x01vorbis':
   audio_serial = serial
  if serial == audio_serial:
   if sequence != next_page or ended:
    raise ValueError('Non-contiguous Vorbis stream')
   pages.append(data[offset:end])
   next_page += 1
   ended = bool(flags & 4)
  elif serial != 0xffffffff or length:
   raise ValueError('Unexpected secondary stream in game audio')
  offset = end
 if not ended:
  raise ValueError('Missing end-of-stream page for game audio')
 return b''.join(pages)

def publish_music(wav):
 source = ogg(wav)
 # Filenames identify the original track. Existing catalogs and open players keep valid links.
 key = hashlib.sha256(source).hexdigest()[:28]
 pcm = source.startswith(b'RIFF')
 filename = key + ('.wav' if pcm else '.ogg')
 playable = source if pcm else remove_empty_vorbis_stream(source)
 dest = ART / filename
 if not dest.exists() or dest.read_bytes() != playable:
  temp = tempfile.NamedTemporaryFile(dir=ART, prefix=key+'-', suffix='.part', delete=False)
  try:
   with temp:
    temp.write(playable)
   os.replace(temp.name, dest)
  finally:
   Path(temp.name).unlink(missing_ok=True)
 return filename

def movies(work,root):
 # The completed scene marks below are assigned by the corresponding story or ending dispatcher.
 gates={'Requiem':{11:[7072],12:[7319],13:[7333]},'Encore':{11:[7057,7110,7158],12:[7020]},'Symphony':{}}
 out=[]
 for p in sorted((root/'mov').glob('*.mpg')):
  n=int(p.stem)
  if n==2:continue
  out.append(dict(id=p.stem,name='오프닝' if n==1 else '엔딩 영상 '+str(n-10),gates=gates[work].get(n,[]),kind='film'))
 if work=='Symphony':out.append(dict(id='credits',name='엔딩 크레딧',gates=[7700,7024],kind='native'))
 return out
def main():
 ART.mkdir(exist_ok=True,parents=True);TMP.mkdir(exist_ok=True)
 tracks={n:k[1] for n,k in zip([6,1,11,12,13,14,15,16,2,3,7],TRACKS)}
 result={};seen=set();futures=[]
 with ThreadPoolExecutor(max_workers=5) as pool:
  for w,root in GAMES.items():
   bank=root/'scr.xfl';parse=lambda n:parse_gsc(read_entry(bank,f'{n:04}.gsc'))
   album=[];music=[]
   for _,row in pages(parse(201),63):
    variants=[]
    for image,override in zip(row[3:33],row[33:63]):
     if image<0:continue
     data=binary(root,'grpe',f'{image:04}.wcg');key=hashlib.sha256(data).hexdigest()[:28]
     if key not in seen:
      seen.add(key);futures.append(pool.submit(cg_image,(key,data)))
      if len(futures)>10:futures.pop(0).result()
     variants.append(dict(flag=override if override>=0 else image+(9000 if image<1000 else 7000),image=key))
    album.append(dict(flag=row[0],variants=variants))
   cmds=parse_commands(parse(401).command,FMT)
   for line in [c for c in cmds if c.opcode==0x3c]:
    track=line.args[0];filename=publish_music(binary(root,'bgm',f'Track{track:02}.wav'))
    index=len(music)+1
    music.append(dict(name=tracks[track],audio=filename,track=track,gate=7700 if w=='Requiem' and index>=8 else 0))
   result[w]=dict(name=WORKS[w],cg=album,music=music,movies=movies(w,root),episodes=[k for j,k in ROUTES] if w=='Encore' else [])
   print(w,len(album),'CG groups;',len(music),'tracks',flush=True)
  for fut in futures:fut.result()
 jsonout(PUB/'catalog.json',result)
 print('unique CG',len(seen),'unique Ogg',len(list(ART.glob('*.ogg'))),flush=True)
if __name__=='__main__':main()

