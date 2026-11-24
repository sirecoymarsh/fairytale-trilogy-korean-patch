from assets import *
import json,subprocess,time,tempfile,urllib.request
from pathlib import Path
import websocket
def main():
    profile=Path(tempfile.mkdtemp(prefix='logo-review-',dir=ROOT/'tmp'))
    chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';doc=ROOT/'로고 비교.html'
    process=subprocess.Popen([chrome,'--headless=new','--disable-extensions','--disable-background-networking','--no-first-run','--no-default-browser-check','--disable-component-update','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1200,800','--user-data-dir='+str(profile),doc.as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    ws=None;n=0
    try:
        port=profile/'DevToolsActivePort'
        for _ in range(120):
            if port.exists() and port.stat().st_size:break
            time.sleep(.1)
        pp=port.read_text().splitlines()[0]
        http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        page=next(v for v in json.load(http.open(f'http://127.0.0.1:{pp}/json/list')) if v['type']=='page')
        ws=websocket.create_connection(page['webSocketDebuggerUrl'],timeout=12,suppress_origin=True,http_proxy_host=None)
        def call(method,args):
            nonlocal n;n+=1;idx=n;ws.send(json.dumps(dict(id=idx,method=method,params=args)))
            while True:
                v=json.loads(ws.recv())
                if v.get('id')==idx:
                    if v.get('error'):raise RuntimeError(v['error'])
                    return v.get('result',{})
        def ev(code):
            r=call('Runtime.evaluate',dict(expression=code,returnByValue=True,awaitPromise=True))
            if r.get('exceptionDetails'):raise RuntimeError(str(r['exceptionDetails'])[:650])
            return r['result'].get('value')
        def wait(code):
            for _ in range(120):
                if ev(code):return
                time.sleep(.08)
            raise RuntimeError('Browser did not reach '+code+': '+str(ev('document.querySelector("#status").textContent')))
        wait('typeof media!=="undefined" && media.length===2')
        data=ev('(()=>{const c=canvases[1],r=c.getBoundingClientRect(),x=r.left+r.width*.67,y=r.top+r.height*.4;return [x,y,sourcePoint(c,x,y),scale]})()')
        x,y,anchor,old=data
        call('Input.dispatchMouseEvent',dict(type='mouseWheel',x=x,y=y,deltaX=0,deltaY=-215,modifiers=0))
        wait('scale>1.1')
        now=ev(f'[scale,sourcePoint(canvases[1],{x},{y}),canvases.map(c=>geometry(c).w/c.getBoundingClientRect().width)]')
        assert max(abs(a-b) for a,b in zip(anchor,now[1]))<.001 and abs(now[2][0]-now[2][1])<.002
        call('Input.dispatchMouseEvent',dict(type='mouseWheel',x=x,y=y,deltaX=0,deltaY=125,modifiers=0))
        wait(f'scale<{now[0]-.02}')
        ev('document.querySelector("#fit").click()');assert ev('scale===1 && cx===.5 && cy===.5')
        ev("document.querySelector('[data-mode=sym]').click()");wait("scene==='sym' && media.length===2")
        clips={}
        for name in ['movie','pieces']:
            ev(f"document.querySelector('[data-mode={name}]').click()")
            wait(f"scene==='{name}' && video && video.currentTime>0.12 && !video.paused")
            ev('document.querySelector("#play").click()');assert ev('video.paused')
            ev("seek.value=550;seek.dispatchEvent(new Event('input'))")
            wait('!video.seeking && video.currentTime/video.duration>.53')
            clips[name]=ev('[video.videoWidth,video.videoHeight,video.duration,video.currentTime]')
        save('audit/logo_viewer_test.json',dict(pointer_wheel_magnification=now[0],source_anchor_before=anchor,source_anchor_after=now[1],both_panes_synchronized=True,fit_reset=True,play_pause_and_scrub=clips))
        print('Wheel',round(now[0],3),'pointer retained; two videos played and sought',clips)
    finally:
        if ws:
            try:ws.send(json.dumps(dict(id=n+1,method='Browser.close',params={})))
            except OSError:pass
            ws.close()
        try:process.wait(timeout=6)
        except subprocess.TimeoutExpired:process.terminate()
if __name__=='__main__':main()

