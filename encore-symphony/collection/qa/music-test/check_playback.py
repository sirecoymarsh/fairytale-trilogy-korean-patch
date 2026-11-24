from datetime import datetime, timezone
from pathlib import Path
import json
import time

DIRECTORY = Path(__file__).resolve().parent

def select(ev, hit, name):
    selector = ".entry[aria-label='" + name + "']"
    assert ev("!!document.querySelector(" + json.dumps(selector) + ")")
    ev("document.querySelector(" + json.dumps(selector) + ").scrollIntoView({block:'center'})")
    ev("window.galleryEvents=[]")
    hit(selector)

def boot(ev, hit, wait):
    hit("#title [aria-label='감상']")
    hit(".tab:nth-of-type(2)")
    wait("section==='music' && !!document.querySelector('.entry[data-key]')")
    ev("""window.galleryEvents=[];for(const type of ['playing','waiting','ended','pause','error','seeking','seeked','stalled']){
      document.addEventListener(type,e=>{if(e.target.tagName==='AUDIO')window.galleryEvents.push([type,+e.target.currentTime.toFixed(3)]);},true);
    }""")

def sound_meter(ev):
    return ev("""(async()=>{
       if(!window.meter || meter.source.mediaElement!==audio){
        const ctx=new AudioContext();const source=ctx.createMediaElementSource(audio);
        const analyser=ctx.createAnalyser();analyser.fftSize=4096;
        const gain=ctx.createGain();gain.gain.value=0;
        source.connect(analyser);analyser.connect(gain);gain.connect(ctx.destination);
        window.meter={ctx,source,analyser};
       }
       await meter.ctx.resume();return meter.ctx.state;
    })()""")

def status(ev):
    return ev("""(()=>{
       const x=audio;if(!x)return null;
       let signal=null;if(window.meter){const f=new Float32Array(meter.analyser.fftSize);meter.analyser.getFloatTimeDomainData(f);
       signal=+Math.sqrt(f.reduce((s,v)=>s+v*v,0)/f.length).toFixed(6);}
       return {name:document.querySelector('#audioBar span')?.textContent,t:+x.currentTime.toFixed(3),duration:x.duration,
       paused:x.paused,ended:x.ended,ready:x.readyState,error:x.error?.message||null,rms:signal,events:galleryEvents.slice(-15)};
    })()""")

def before(ev,hit,wait):
    boot(ev,hit,wait)
    results={}
    for name in ['페어리테일','그레텔의 테마','게르다의 테마']:
        select(ev,hit,name)
        sound_meter(ev)
        time.sleep(2.2)
        results[name]=[status(ev)]
        if name=='게르다의 테마':
            ev("audio.currentTime=90")
            time.sleep(6)
            results[name].append(status(ev))
        print('BEFORE',name,[(s['t'],s['paused'],s['ended'],s['error'],s['rms']) for s in results[name]],flush=True)
    (DIRECTORY/'before.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    return list(results)

def decoded_tracks(ev):
    reference=json.loads((DIRECTORY/'source-comparison.json').read_text(encoding='utf8'))
    results={}
    for name,src in reference.items():
        path='media/'+src['file']
        body="""(async()=>{
          const response=await fetch(PATH,{cache:'no-store'});if(!response.ok)throw Error(response.status);
          const ctx=new OfflineAudioContext(2,1,RATE);
          const pcm=await ctx.decodeAudioData(await response.arrayBuffer());
          const ch=pcm.getChannelData(0);
          let peak=0,active=0,first=null,last=null,midPower=0;
          for(let start=0;start<ch.length;start+=pcm.sampleRate){
            let power=0,n=0;
            for(let i=start;i<Math.min(ch.length,start+pcm.sampleRate);i+=16){const x=ch[i];power+=x*x;peak=Math.max(peak,Math.abs(x));n++;}
            const rms=Math.sqrt(power/n);
            if(rms>.001){active++;if(first===null)first=start/pcm.sampleRate;last=start/pcm.sampleRate;}
            if(start===Math.floor(ch.length/(2*pcm.sampleRate))*pcm.sampleRate)midPower=rms;
          }
          return {samples:pcm.length,rate:pcm.sampleRate,channels:pcm.numberOfChannels,peak:+peak.toFixed(5),
                  activeSeconds:active,firstSignal:first,lastSignal:last,midRms:+midPower.toFixed(5)};
        })()"""
        info=ev(body.replace('PATH',json.dumps(path)).replace('RATE',str(src['sample_rate'])))
        info['source_samples']=src['expected_samples'];info['delta_samples']=info['samples']-src['expected_samples']
        assert info['rate']==src['sample_rate'] and info['channels']==2 and info['midRms']>.0001,(name,info)
        assert abs(info['delta_samples'])<=2048 and info['activeSeconds']>info['samples']/info['rate']*.7,(name,info)
        results[name]=info
        print('DECODE',name,info['samples'],info['delta_samples'],info['midRms'],flush=True)
    (DIRECTORY/'whole-tracks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    return len(results)

def installed_tracks(ev,hit,wait):
    reference=json.loads((DIRECTORY/'source-comparison.json').read_text(encoding='utf8'))
    results={}
    for name,src in reference.items():
        select(ev,hit,name)
        wait("audio && !audio.paused && audio.currentTime>.25",5)
        first=status(ev);time.sleep(1.65);after=status(ev)
        assert first['name']==name and after['t']>first['t']+1 and not after['ended'],(name,first,after)
        endtime=src['expected_samples']/src['sample_rate']
        # Check a middle segment and true EOF through the same gallery player.
        ev("audio.currentTime="+str(round(endtime/2,2)))
        wait("audio && !audio.seeking && audio.readyState>=3",5)
        time.sleep(.48);mid=status(ev)
        assert mid['t']>endtime/2+.16 and mid['rms']>.0001,(name,mid)
        ev("audio.currentTime=audio.duration-1.4")
        wait("audio && !audio.seeking && audio.currentTime>=audio.duration-1.6",5)
        at_end=status(ev)
        wait("audio.ended",5);done=status(ev)
        assert not at_end['ended'] and done['ended'] and not done['error'],(name,at_end,done)
        results[name]=dict(early=after,middle=mid,ending=done)
        print('PLAYER',name,after['t'],mid['t'],done['t'],flush=True)
    (DIRECTORY/'installed-tracks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    return len(results)

def after_natural(ev, hit, wait):
    wait("gerdaCheck.some(x=>x[1]>=98 && x[2]>.002)",90)
    ev("clearInterval(window.gerdaInterval)")
    samples=ev("gerdaCheck")
    events=ev("galleryEvents")
    assert sum(1 for s in samples if 92<=s[1]<=93.43 and s[2]>.001)>=1
    assert sum(1 for s in samples if 93.5<=s[1]<=96 and s[2]>.001)>=1
    assert not any(s[3] for s in samples) and not any(e[0] in ['ended','seeking','error'] for e in events)
    report=dict(first=samples[0],last=samples[-1],sample_period_sec=.5,around_previous_cut=[s for s in samples if 92<=s[1]<=96],events=events)
    (DIRECTORY/'gerda-continuous.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('GERDA from start',samples[-1],flush=True)
    return installed_tracks(ev,hit,wait)
