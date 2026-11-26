#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <initguid.h>
#include "research/metahost.h"
static const GUID CollectionCLRRuntimeHost={0x90f1a06e,0x7712,0x4762,{0x86,0xb5,0x7a,0x5e,0xba,0x6b,0xdb,0x02}};
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <stdexcept>
#include "native_hooks.h"
template<class T>T game(unsigned rva){return reinterpret_cast<T>(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))+rva);}
using Bytes=std::vector<uint8_t>;using Bits=std::map<uint16_t,Bytes>;
struct Error:std::runtime_error{using std::runtime_error::runtime_error;};
void require(bool b){if(!b)throw Error("invalid collection state");}
struct Buffer{uint8_t*data;uint32_t size;};struct Node{Node*left;Node*parent;Node*right;uint16_t key,pad;Buffer*record;};struct Tree{uint32_t reserved;Node*head;uint32_t flags,count;};
struct Image{Bytes prefs;std::vector<int16_t>vars;Bits read,seen;};
Tree* tree(bool seen){return *game<Tree**>(seen?0x852fc:0x852f8);}
template<class Fn>void records(bool seen,Fn fn){Tree*t=tree(seen);require(t&&t->head&&t->count<=65536);Node*n=t->head->left;for(uint32_t i=0;i<t->count;i++){require(n&&n!=t->head&&n->record&&n->record->size<=1024*1024&&n->record->data);fn(n->key,*n->record);game<void(__thiscall*)(Node**)>(0x33f00)(&n);}require(n==t->head);}
Image current(){Image x;auto p=game<uint8_t*>(0x853c0);x.prefs.assign(p,p+0x872);auto v=*game<int16_t**>(0x853b0);require(v);x.vars.assign(v+7000,v+10000);for(bool seen:{false,true})records(seen,[&](uint16_t k,Buffer b){(seen?x.seen:x.read)[k]=Bytes(b.data,b.data+b.size);});return x;}
void ensureMap(bool seen,const Bits&target){std::map<uint16_t,size_t>lengths;records(seen,[&](uint16_t k,Buffer v){lengths[k]=v.size;});for(auto&e:target){if(lengths[e.first]>=e.second.size())continue;for(size_t i=lengths[e.first];i<e.second.size();i++){for(int j=0;j<8;j++)if(e.second[i]&(1u<<j)){if(seen){require(e.first==0);game<void(__cdecl*)(int)>(0x217d0)(int(i*8+j));}else game<void(__cdecl*)(int,int)>(0x21790)(e.first,int(i*8+j));}}}}
void applyMap(bool seen,const Bits&target){records(seen,[&](uint16_t k,Buffer b){auto v=target.find(k);size_t n=v==target.end()?0:std::min<size_t>(b.size,v->second.size());if(n)memcpy(b.data,v->second.data(),n);if(n<b.size)memset(b.data+n,0,b.size-n);});}
void apply(const Image&x){require(x.prefs.size()==0x872&&x.vars.size()==3000);ensureMap(false,x.read);ensureMap(true,x.seen);memcpy(game<void*>(0x853c0),x.prefs.data(),0x872);memcpy(*game<int16_t**>(0x853b0)+7000,x.vars.data(),6000);applyMap(false,x.read);applyMap(true,x.seen);}
const char* keys[]={"R","A","S"};const char*ids[]={"FRsave","FAsave","FSsave"};const wchar_t*titles[]={L"레퀴엠",L"앙코르",L"심포니"};
static int work=0;static void*mainVm=nullptr;static std::map<void*,int> vmWork;static bool choosing=false;static Image cache[3];static bool cached[3]={};
void trace(const char*line){if(!GetEnvironmentVariableW(L"FAIRY_UNIFIED_TRACE",nullptr,0))return;FILE*f=nullptr;if(_wfopen_s(&f,L"unified-trace.log",L"ab")==0){fprintf(f,"%lu %s\n",GetCurrentProcessId(),line);fclose(f);}}
Image readImage(int which){Image x;std::wstring path=L"Save\\";path+=wchar_t(keys[which][0]);path+=L"\\";for(const char*c=ids[which];*c;c++)path+=wchar_t(*c);path+=L".dat";FILE*f=nullptr;if(_wfopen_s(&f,path.c_str(),L"rb")||!f)return x;fseek(f,0,SEEK_END);long z=ftell(f);rewind(f);if(z<0x872+6000+8||z>=32*1024*1024){fclose(f);throw Error("invalid system save size");}Bytes b(z);auto got=fread(b.data(),1,z,f);fclose(f);require(got==size_t(z));size_t pos=0;auto read=[&](void*d,size_t n){require(pos+n<=b.size());memcpy(d,b.data()+pos,n);pos+=n;};x.prefs.resize(0x872);read(x.prefs.data(),0x872);x.vars.resize(3000);read(x.vars.data(),6000);for(bool seen:{false,true}){uint32_t n;read(&n,4);require(n<=65536);auto&m=seen?x.seen:x.read;for(uint32_t i=0;i<n;i++){uint16_t k;uint32_t sz;read(&k,2);read(&sz,4);require(sz<=1024*1024&&!m.count(k));Bytes v(sz);read(v.data(),sz);m.emplace(k,std::move(v));}}require(pos==b.size());return x;}
void selectWork(int next){require(next>=0&&next<3);if(next==work)return;Image target=cached[next]?cache[next]:readImage(next);cache[work]=current();cached[work]=true;game<void(__cdecl*)()>(0x21210)();int old=work;work=next;auto cfg=*game<char**>(0xa2ba8);strcpy_s(cfg+0x39,28,ids[work]);char save[32],movie[32];sprintf_s(save,"Save\\%s",keys[work]);sprintf_s(movie,"Data\\%s\\mov",keys[work]);strcpy_s(game<char*>(0xa2bac),260,save);strcpy_s(cfg+0xea,21,movie);game<void(__cdecl*)(int)>(0x20fc0)(1);if(target.prefs.empty()){game<void(__cdecl*)()>(0x20ec0)();applyMap(false,{});applyMap(true,{});}else apply(target);char line[80];sprintf_s(line,"switch %d -> %d",old,work);trace(line);}
struct Choice{int picked=0,action=-1;};
static HWND nativeWindow=nullptr;static ICLRRuntimeHost*clr=nullptr;
BOOL CALLBACK findNative(HWND w,LPARAM){wchar_t cls[128];DWORD pid=0;GetWindowThreadProcessId(w,&pid);GetClassNameW(w,cls,128);if(pid==GetCurrentProcessId()&&wcscmp(cls,L"RosGameClass")==0){nativeWindow=w;return FALSE;}return TRUE;}
Choice choose(){
 if(!nativeWindow)EnumWindows(findNative,0);require(nativeWindow!=nullptr);
 game<void(__cdecl*)()>(0x21210)();trace("home saved");
 if(!clr){ICLRMetaHost*meta=nullptr;ICLRRuntimeInfo*info=nullptr;trace("clr begin");HMODULE shim=LoadLibraryW(L"mscoree.dll");require(shim!=nullptr);auto create=reinterpret_cast<HRESULT(STDAPICALLTYPE*)(REFCLSID,REFIID,LPVOID*)>(GetProcAddress(shim,"CLRCreateInstance"));require(create&&SUCCEEDED(create(CLSID_CLRMetaHost,IID_ICLRMetaHost,(LPVOID*)&meta)));trace("clr created");HRESULT hr=meta->GetRuntime(L"v4.0.30319",IID_ICLRRuntimeInfo,(LPVOID*)&info);meta->Release();{char line[80];sprintf_s(line,"GetRuntime hr=%08lx",hr);trace(line);}require(SUCCEEDED(hr));hr=info->GetInterface(CollectionCLRRuntimeHost,IID_ICLRRuntimeHost,(LPVOID*)&clr);info->Release();{char line[80];sprintf_s(line,"GetInterface hr=%08lx",hr);trace(line);}require(SUCCEEDED(hr));hr=clr->Start();{char line[80];sprintf_s(line,"Start hr=%08lx",hr);trace(line);}require(SUCCEEDED(hr));}
 wchar_t path[32768];require(GetModuleFileNameW(nullptr,path,32768)>0);auto slash=wcsrchr(path,L'\\');require(slash);wcscpy_s(slash+1,32768-(slash+1-path),L"FairytaleHome.dll");
 std::wstring arg=std::to_wstring((uintptr_t)nativeWindow);DWORD result=DWORD(-1);ShowWindow(nativeWindow,SW_HIDE);
 HRESULT hr=clr->ExecuteInDefaultAppDomain(path,L"FairyCollection.Home",L"Select",arg.c_str(),&result);
 {char line[100];sprintf_s(line,"Select hr=%08lx result=%ld",hr,result);trace(line);}ShowWindow(nativeWindow,SW_SHOW);SetForegroundWindow(nativeWindow);SetWindowTextW(nativeWindow,L"페어리테일 이야기 모음");require(SUCCEEDED(hr));
 Choice c;c.picked=work;if(int(result)>0){c.picked=int(result)/100-1;c.action=int(result)%100;}else PostMessageW(nativeWindow,WM_CLOSE,0,0);return c;
}
extern "C" int __fastcall ReadAsset(void*self,void*,const char*path){std::string p=path;std::replace(p.begin(),p.end(),'/','\\');while(p.rfind(".\\",0)==0)p.erase(0,2);if(p.find(':')==std::string::npos&&p.rfind("\\",0)!=0&&p.rfind("Data\\",0)!=0&&p.rfind("Integration\\",0)!=0&&p.rfind("Save\\",0)!=0){if(p=="scr\\0001.gsc"||p=="scr\\59990.gsc"||p=="scr\\59992.gsc"||p=="scr\\59993.gsc")p="Integration\\"+std::string(keys[work])+"\\"+p.substr(4);else p="Data\\"+std::string(keys[work])+"\\"+p;}int result=game<int(__thiscall*)(void*,const char*)>(OriginalReadAsset)(self,p.c_str()); if(GetEnvironmentVariableW(L"FAIRY_UNIFIED_TRACE",nullptr,0)){std::string line=std::string("asset ")+(result?"ok ":"missing ")+p;trace(line.c_str());} return result;}
extern "C" int __fastcall LoadScript(void*self,void*,unsigned short id){if(!mainVm&&id==0)mainVm=self;try{if(self==mainVm&&id==1&&!choosing){choosing=true;Choice c=choose();choosing=false;if(c.action>=0){selectWork(c.picked);if(c.action==1)id=59990;else if(c.action==5)id=59992;else if(c.action==6)id=59993;}SetWindowTextW(nativeWindow,L"페어리테일 이야기 모음");}auto it=vmWork.find(self);if(it==vmWork.end()||it->second!=work){*reinterpret_cast<uint16_t*>((char*)self+0x3c)=0xffff;vmWork[self]=work;}char line[100];sprintf_s(line,"script work=%d id=%u vm=%p main=%p",work,id,self,mainVm);trace(line);}catch(const std::exception&e){choosing=false;trace(e.what());MessageBoxW(GetActiveWindow(),L"작품을 전환할 수 없습니다. 저장 기록과 데이터 파일을 확인해 주세요.",L"이야기 모음",MB_OK|MB_ICONERROR);return 0;}return game<int(__thiscall*)(void*,unsigned short)>(OriginalLoadScript)(self,id);}
