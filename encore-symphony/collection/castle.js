'use strict';
const $=id=>document.getElementById(id), works=['Requiem','Encore','Symphony'], names={Requiem:'레퀴엠',Encore:'앙코르',Symphony:'심포니'};
const menus={story:'작품 선택',continue:'불러올 작품',settings:'설정할 작품'},tabs={cg:'CG',music:'음악',movies:'영상',scene:'회상'};
const host=window.chrome?.webview;const post=(cmd,work='',id='')=>host?.postMessage({cmd,work,id:String(id)});
let catalog={},progress={},screen='title',intent='story',section='cg',filter='All',page=0,pan=null,shown=null,timerNotice,nowSong='',audio=null,busy=false,returnFocus=null;
let volume=Number(localStorage.getItem('galleryVolume')??'.65');if(!Number.isFinite(volume))volume=.65;
function node(type,cls,txt){const el=document.createElement(type);if(cls)el.className=cls;if(txt!==undefined)el.textContent=txt;return el;}
function button(t,cls,fn,label){const b=node('button',cls,t);b.type='button';if(label)b.setAttribute('aria-label',label);b.onclick=fn;return b;}
function notify(t){$('notice').textContent=t;$('notice').hidden=false;clearTimeout(timerNotice);timerNotice=setTimeout(()=>$('notice').hidden=true,3800);}
function current(s){screen=s;for(const name of ['title','doors','book'])$(name).hidden=s!==name;$('viewer').hidden=!shown;}
function stopAudio(){if(audio){audio.pause();audio.removeAttribute('src');audio.load();audio=null;}nowSong='';}
function home(){stopAudio();busy=false;current('title');focusPrev();}
function focusPrev(){if(returnFocus&&!returnFocus.closest('[hidden]'))returnFocus.focus({preventScroll:true});}
function doors(mode){stopAudio();intent=mode;current('doors');const note=$('modeNote');note.textContent=menus[mode]??'';note.hidden=mode==='story';}
function installed(w){return progress[w]?.installed===true;}
function updateAvailability(){
 for(const w of works){const b=$('doors').querySelector('[data-work="'+w+'"]');if(!b)continue;
  const ready=!!progress[w],on=installed(w);b.disabled=!on;b.classList.toggle('unavailable',ready&&!on);
  b.setAttribute('aria-label',names[w]+(!ready?' · 확인 중':on?'':' · 미설치'));
  b.querySelector('span').textContent=!ready?'확인 중':on?names[w]:'미설치';
 }
}
function hotspot(parent,label,area,fn,door=false){
 const b=button('','hit'+(door?' door':''),()=>{returnFocus=b;fn();},label);const [x,y,w,h]=area;
 Object.assign(b.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});b.append(node('span','',label));parent.append(b);return b;
}
function buildMain(){
 const t=$('title'),areas=[['시작',[62.8,14.4,6.4,12],()=>doors('story')],['계속',[72,25.7,7.1,14],()=>doors('continue')],['감상',[55.3,33.1,6.8,13],()=>gallery('cg')],['설정',[69.5,40.6,6.9,13.4],settings],['영상',[78.3,41,6.25,12.4],()=>gallery('movies')],['조작',[48.3,48.6,6.6,13],help],['종료',[41.5,65.2,6.5,12.5],()=>post('close')]];
 for(const [label,area,fn] of areas)hotspot(t,label,area,fn);
 const d=$('doors');for(const [i,w] of works.entries()){const b=hotspot(d,names[w],[[18.8,40,22.7,40.7],[42.1,39,21.8,42.5],[65.6,39.8,20.6,41]][i],()=>launch(w,intent),true);b.dataset.work=w;}
 updateAvailability();
 hotspot(d,'뒤로',[42.5,83.1,15.8,7.2],()=>intent==='settings'?settings():home());
 const note=node('div','doorcaption');note.id='modeNote';note.hidden=true;d.append(note);
}
function launch(w,mode){
 if(busy)return;if(!host){notify('통합판 실행 파일에서 열어 주세요.');return;}
 if(!installed(w)){notify('이 작품은 미설치 상태예요.');return;}
 stopAudio();busy=true;post('play',w,mode);
}
function albumOpen(w,g){const state=progress[w]??{flags:[]};return state.overlay||!g||state.flags.includes(g);}
function anyGate(w,ids){return ids.length===0||ids.some(g=>albumOpen(w,g));}
function folio(title,back){current('book');$('heading').textContent=title;$('back').onclick=back;$('body').replaceChildren();}
function selected(){return (filter==='All'?works:[filter]).filter(w=>installed(w)&&catalog[w]);}
function gallery(which,keep=false){
 if(!keep){stopAudio();section=which;filter='All';page=0;}
 folio('감상실',home);
 const body=$('body'),ts=node('nav','tabs');ts.setAttribute('aria-label','감상 종류');
 for(const [val,t] of Object.entries(tabs)){const b=button(t,'tab'+(section===val?' selected':''),()=>{if(section!==val){stopAudio();section=val;page=0;gallery(section,true);}});b.setAttribute('aria-pressed',String(section===val));ts.append(b);}body.append(ts);
 const fs=node('div','filters');fs.setAttribute('aria-label','작품별 보기');
 for(const val of ['All',...works]){const b=button(names[val]??'전체','filter'+(filter===val?' selected':''),()=>{filter=val;page=0;gallery(section,true);});b.setAttribute('aria-pressed',String(filter===val));if(val!=='All'&&!installed(val)){b.disabled=true;b.textContent=names[val]+' · 미설치';}fs.append(b);}
 const count=node('span','count');count.id='count';fs.append(count);body.append(fs);
 if(!works.every(w=>progress[w])){body.append(node('p','sectionnote','감상 목록을 읽고 있어요.'));return;}
 if(!selected().length){count.textContent='설치된 작품 없음';body.append(node('p','sectionnote','설치된 작품이 없어요. 작품을 설치한 뒤 통합판을 다시 열어 주세요.'));return;}
 if(section==='cg')cgList(body,count);else if(section==='music')songList(body,count);else if(section==='movies')filmList(body,count);else replayList(body,count);
}
function groups(){return selected().flatMap(w=>catalog[w].cg.map((g,i)=>({w,i,variants:albumOpen(w,g.flag)?g.variants.filter(v=>albumOpen(w,v.flag)):[]})));}
function cgList(body,count){
 const all=groups(),pages=Math.ceil(all.length/8);page=Math.max(0,Math.min(page,pages-1));count.textContent='열린 CG '+all.filter(g=>g.variants.length).length+' / '+all.length+'묶음';
 const grid=node('div','grid');for(const g of all.slice(page*8,page*8+8)){
  const open=g.variants.length>0,title=names[g.w]+' · '+String(g.i+1).padStart(2,'0');
  const b=button('','card',()=>openCG(g),open?title+' 크게 보기':names[g.w]+' 미해금');b.disabled=!open;
  if(open){const pic=node('img','thumb');pic.alt='';pic.src='media/'+g.variants[0].image+'-s.jpg';b.append(pic);}else{const lock=node('span','veil','미해금');b.append(lock);}
  const label=node('span','tag',title);label.append(node('small','',open?g.variants.length+'장':''));b.append(label);grid.append(b);
 }body.append(grid);
 const nav=node('div','pagenav');const prev=button('‹ 이전','',()=>{page--;gallery(section,true);}),next=button('다음 ›','',()=>{page++;gallery(section,true);});prev.disabled=page===0;next.disabled=page+1>=pages;nav.append(prev,node('span','',(page+1)+' / '+pages),next);body.append(nav);
}
function openCG(group){shown={group,i:0};$('viewer').hidden=false;renderCG();$('imagebox').focus();}
function renderCG(){
 const {group:g,i}=shown;$('caption').textContent=names[g.w]+' · CG '+String(g.i+1).padStart(2,'0')+'　'+(i+1)+' / '+g.variants.length;
 $('prev').disabled=i===0;$('next').disabled=i===g.variants.length-1;
 const pic=$('picture');pan=null;pic.onload=fit;pic.src='media/'+g.variants[i].image+'.png';
}
function fit(){const im=$('picture'),box=$('imagebox');if(!shown||!im.naturalWidth||!box.clientWidth)return;
 const s=Math.min(box.clientWidth/im.naturalWidth,box.clientHeight/im.naturalHeight);
 pan={s,min:s,x:(box.clientWidth-im.naturalWidth*s)/2,y:(box.clientHeight-im.naturalHeight*s)/2};paint();}
function paint(){if(pan)$('picture').style.transform='translate('+pan.x+'px,'+pan.y+'px) scale('+pan.s+')';}
function switchCG(dir){if(!shown)return;let n=shown.i+dir;if(n>=0&&n<shown.group.variants.length){shown.i=n;renderCG();}}
function closeCG(){shown=null;pan=null;$('viewer').hidden=true;$('picture').removeAttribute('src');$('body').querySelector('.card:enabled')?.focus();}
$('prev').onclick=()=>switchCG(-1);$('next').onclick=()=>switchCG(1);$('vClose').onclick=closeCG;$('fit').onclick=fit;
const box=$('imagebox');box.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey||!pan)return;e.preventDefault();const r=box.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
 const n=Math.max(pan.min*.5,Math.min(pan.min*8,pan.s*Math.exp(-e.deltaY*.0017)));pan.x=x-(x-pan.x)*n/pan.s;pan.y=y-(y-pan.y)*n/pan.s;pan.s=n;paint();},{passive:false});
let drag;box.onpointerdown=e=>{if(!pan||e.button!==0)return;drag={x:e.clientX,y:e.clientY};box.setPointerCapture(e.pointerId);};box.onpointermove=e=>{if(!drag||!pan)return;pan.x+=e.clientX-drag.x;pan.y+=e.clientY-drag.y;drag={x:e.clientX,y:e.clientY};paint();};box.onpointerup=box.onpointercancel=()=>drag=null;box.ondblclick=fit;window.addEventListener('resize',()=>{if(shown)fit();});
function listEntry(title,reason,cb,enabled=true){const b=button('','entry',cb,title);b.disabled=!enabled;b.append(node('span','',title),node('small','',reason));return b;}
function songList(body,count){
 const by=new Map();for(const w of selected())for(const s of catalog[w].music){if(!by.has(s.audio))by.set(s.audio,{...s,works:[],active:false});const item=by.get(s.audio);item.works.push(w);item.active||=albumOpen(w,s.gate);}
 const rows=[...by.values()];count.textContent='재생 가능 '+rows.filter(r=>r.active).length+' / '+rows.length+'곡';const list=node('div','list');
 for(const song of rows){
  const on=song.active;const b=listEntry(on?song.name:'미해금',song.works.map(w=>names[w]).join(' · '),()=>playSong(song),on);b.dataset.key=song.audio;if(song.audio===nowSong)b.classList.add('active');list.append(b);
 }body.append(list);const bar=node('div','player');bar.id='audioBar';body.append(bar);
 if(audio){const old=catalog[works.find(w=>catalog[w].music.some(s=>s.audio===nowSong))]?.music.find(s=>s.audio===nowSong);bar.append(node('span','',old?.name??''),audio);}
}
function playSong(song){if(!audio){audio=document.createElement('audio');audio.controls=true;audio.onerror=()=>notify('음악을 열 수 없어요.');}const bar=$('audioBar');bar.replaceChildren(node('span','',song.name),audio);
 if(nowSong!==song.audio){nowSong=song.audio;audio.src='media/'+song.audio;}audio.volume=volume;audio.play().catch(e=>notify(e.message));document.querySelectorAll('.entry[data-key]').forEach(b=>b.classList.toggle('active',b.dataset.key===nowSong));}
function filmList(body,count){
 const list=node('div','list');let total=0,open=0;
 for(const w of selected())for(const f of catalog[w].movies){
  total++;const on=anyGate(w,f.gates);if(on)open++;
  list.append(listEntry(on?f.name:'미해금',names[w],()=>{if(f.kind==='native'){launch(w,'credits');}else{post('film',w,f.id);}},on));
 }count.textContent='재생 가능 '+open+' / '+total+'편';body.append(list);
}
function closeFilm(){const v=$('movie');v.pause();v.removeAttribute('src');v.load();$('cinema').hidden=true;$('filmBack').blur();$('body').querySelector('.entry:enabled')?.focus();}
function openFilm(m){stopAudio();const v=$('movie');$('filmCaption').textContent=m.name;$('cinema').hidden=false;v.volume=volume;v.src=m.url;v.play().catch(()=>{closeFilm();notify('영상을 재생하지 못했어요. Windows 미디어 기능과 WebView2를 확인해 주세요.');});$('filmBack').focus();}
$('filmBack').onclick=closeFilm;$('movie').onended=closeFilm;$('movie').onerror=()=>{if(!$('cinema').hidden){closeFilm();notify('영상 파일을 재생하지 못했어요.');}};
function replayList(body,count){
 const list=node('div','list');count.textContent='작품별 회상';for(const w of selected()){
  list.append(listEntry(names[w]+' 회상','열린 장면 다시 보기',()=>launch(w,'replay')));
  if(w==='Encore')list.append(listEntry('앙코르 에피소드 선택','원작 에피소드 목록',()=>launch(w,'episodes')));
 }body.append(list);
}
function settingRow(title,text,other){const row=node('div','settingsrow'),labels=node('div');labels.append(node('strong','',title));if(text)labels.append(node('p','',text));row.append(labels,other);return row;}
function settings(){
 stopAudio();folio('환경 설정',home);const data=node('div','settingsbody'),slider=node('input');slider.type='range';slider.min='0';slider.max='100';slider.value=Math.round(volume*100);slider.setAttribute('aria-label','감상실 음량');
 slider.oninput=()=>{volume=Number(slider.value)/100;localStorage.setItem('galleryVolume',String(volume));post('volume','',volume);if(audio)audio.volume=volume;};
 data.append(settingRow('감상실 음량','음악과 영상에 적용해요.',slider),settingRow('화면 모드','F11로 전환할 수 있어요.',button('전체 화면 전환','action',()=>post('fullscreen'))),settingRow('작품별 환경 설정','대사·음성·화면과 작품별 편의 기능을 설정해요.',button('작품 선택','action',()=>doors('settings'))));$('body').append(data);}
function help(){
 stopAudio();folio('조작 안내',home);const list=node('div','settingsbody');const info=[
 ['작품 시작','시작에서 문을 고르면 그 작품의 첫 장면으로 들어가요. 앙코르의 다른 에피소드는 감상실의 회상에서 고를 수 있어요.'],
 ['계속하기','계속에서 작품을 고르면 해당 작품의 저장 목록을 열어요.'],
 ['감상실','상단에서 CG·음악·영상·회상을 고르고 작품별로 볼 수 있어요. CG는 휠로 확대하고 드래그로 옮겨요. 더블클릭하면 화면에 맞춰요.'],
 ['키보드','Tab이나 방향키로 버튼을 고르고 Enter로 열어요. Esc는 뒤로, F11은 화면 모드 전환이에요.'],
 ['통합 화면으로 돌아오기','플레이를 마치고 게임 창을 닫거나 게임에서 타이틀로 돌아오면 통합 화면으로 복귀해요.']
 ];for(const [a,b] of info){const r=node('div','help');r.append(node('b','',a),node('div','',b));list.append(r);}$('body').append(list);
}
function visibleButtons(){const parent=shown?$('viewer'):$(screen);return [...parent.querySelectorAll('button:not(:disabled)')].filter(b=>b.offsetWidth&&b.offsetHeight);}
document.addEventListener('keydown',e=>{
 if(e.key==='F11'){e.preventDefault();post('fullscreen');return;}
 if(!$('cinema').hidden){if(e.key==='Escape'){e.preventDefault();closeFilm();}return;}
 if(e.key==='Escape'){e.preventDefault();if(shown)closeCG();else if(screen==='book')home();else if(screen==='doors'){if(intent==='settings')settings();else home();}return;}
 if(e.target.tagName==='INPUT'||e.target.tagName==='AUDIO')return;
 if(shown&&(e.key==='ArrowLeft'||e.key==='ArrowRight')){e.preventDefault();switchCG(e.key==='ArrowLeft'?-1:1);return;}
 if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){const items=visibleButtons();if(!items.length)return;e.preventDefault();const ix=items.indexOf(document.activeElement),forward=e.key==='ArrowRight'||e.key==='ArrowDown';items[ix<0?(forward?0:items.length-1):(ix+(forward?1:-1)+items.length)%items.length].focus();}
});
host?.addEventListener('message',e=>{const m=e.data;
 if(m.type==='filmOpen')openFilm(m);
 if(m.type==='state'){progress=m.works;updateAvailability();if(filter!=='All'&&!installed(filter))filter='All';if(shown&&!installed(shown.group.w))closeCG();if(screen==='book'&&$('heading').textContent==='감상실'&&!shown)gallery(section,true);}
 if(m.type==='returned'){busy=false;if(m.action==='story'||m.action==='continue')home();else if(m.action==='settings')settings();else gallery(section,true);}
 if(m.type==='error'){busy=false;notify(m.message);}
});
buildMain();fetch('catalog.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('감상 목록을 읽을 수 없어요.');return r.json();}).then(r=>{catalog=r;if(host){post('ready');post('volume','',volume);}else notify('통합판 실행 파일에서 열어 주세요.');}).catch(e=>notify(e.message));

