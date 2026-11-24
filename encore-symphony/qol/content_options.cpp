// Native configuration control for the two November 2015/2016 codeX builds.
// Linked normally by the two executables. All engine objects belong to this game instance.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <stdexcept>
#include "catalog.h"

using Bytes=std::vector<uint8_t>;
using Bits=std::map<uint16_t,Bytes>;
using Marks=std::map<uint16_t,uint16_t>;
constexpr int Mode=7988, Ready=7987, Pending=7986, Manual=7985;
struct Error:std::runtime_error { using std::runtime_error::runtime_error; };
void require(bool ok){if(!ok)throw Error("invalid game state");}
template<class T> T game(unsigned rva){return reinterpret_cast<T>(reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr))+rva);}
struct Buffer {uint8_t* data; uint32_t size;};
struct Node {Node* left;Node* parent;Node* right;uint16_t key;uint16_t pad;Buffer* record;};
struct Tree {uint32_t reserved;Node* head;uint32_t flags;uint32_t count;};
static_assert(sizeof(Node)==20 && sizeof(Tree)==16,"codeX x86 ABI");
struct Image {Bytes prefs; std::vector<int16_t> vars; Bits read, seen;};
struct Backup {Marks marks;Bits read,seen;bool overlay=false;};
using Advance=void(__thiscall*)(Node**);
Tree* tree(bool seen){return *game<Tree**>(seen?0x852fc:0x852f8);}
template<class Fn> void records(bool seen,Fn fn){
    Tree* t=tree(seen);require(t&&t->head&&t->count<=65536);
    Node* n=t->head->left;
    for(uint32_t i=0;i<t->count;++i){
        require(n&&n!=t->head&&n->record&&n->record->size<=1024*1024&&n->record->data);
        fn(n->key,*n->record);
        game<Advance>(0x33f00)(&n);
    }
    require(n==t->head);
}
Image current(){
    Image x;
    const uint8_t* p=game<uint8_t*>(0x853c0);
    x.prefs.assign(p,p+0x872);
    const int16_t* v=*game<int16_t**>(0x853b0);require(v);
    x.vars.assign(v+7000,v+10000);
    for(bool seen:{false,true})
        records(seen,[&](uint16_t k,Buffer b){(seen?x.seen:x.read)[k]=Bytes(b.data,b.data+b.size);});
    return x;
}
int16_t& var(Image& x,int id){return x.vars.at(id-7000);}
void put16(Bytes& b,uint16_t v){b.push_back(uint8_t(v));b.push_back(uint8_t(v>>8));}
void put32(Bytes& b,uint32_t v){put16(b,uint16_t(v));put16(b,uint16_t(v>>16));}
void packMap(Bytes& b,const Bits& m){
    put32(b,uint32_t(m.size()));
    for(const auto& e:m){put16(b,e.first);put32(b,uint32_t(e.second.size()));b.insert(b.end(),e.second.begin(),e.second.end());}
}
Bytes serialize(const Image& x){
    Bytes out=x.prefs;
    for(int16_t v:x.vars)put16(out,uint16_t(v));
    packMap(out,x.read);packMap(out,x.seen);return out;
}
struct Reader{
    const Bytes& b;size_t p=0;
    uint16_t u16(){require(p+2<=b.size());unsigned n=b[p]|(unsigned(b[p+1])<<8);p+=2;return uint16_t(n);}
    uint32_t u32(){uint32_t a=u16();return a|(uint32_t(u16())<<16);}
    Bits map(){
        Bits m;auto n=u32();require(n<=65536);
        for(uint32_t i=0;i<n;++i){
            auto k=u16();auto z=u32();require(z<=1024*1024 && p+z<=b.size() && !m.count(k));
            m[k]=Bytes(b.begin()+p,b.begin()+p+z);p+=z;
        }return m;
    }
};
uint32_t crc(const Bytes& b,size_t n){
    uint32_t value=~0u;for(size_t i=0;i<n;i++){value^=b[i];for(int k=0;k<8;k++)value=(value>>1)^((0u-(value&1u))&0xedb88320u);}return ~value;
}
struct Catalog{
    bool encore;
    const std::vector<int>& cgs()const{return encore?EncoreCG:SymphonyCG;}
    const std::vector<int>& pictures()const{return encore?EncorePictures:SymphonyPictures;}
    const std::vector<std::pair<int,int>>& shadow()const{return encore?EncoreShadow:SymphonyShadow;}
};
std::wstring wide(const char* s){
    int n=MultiByteToWideChar(CP_ACP,0,s,-1,nullptr,0);require(n>1&&n<=MAX_PATH);
    std::wstring w(n,0);require(MultiByteToWideChar(CP_ACP,0,s,-1,&w[0],n)==n);w.pop_back();return w;
}
struct Paths{
    Catalog cat;
    std::wstring save,backup;
    Paths(){
        const char* cfg=*game<char**>(0xa2ba8);require(cfg);
        std::wstring id=wide(cfg+0x39),dir=wide(game<char*>(0xa2bac));
        cat.encore=(_wcsicmp(id.c_str(),L"FAsave")==0);
        require(cat.encore||_wcsicmp(id.c_str(),L"FSsave")==0);
        save=dir+L"\\"+id+L".dat";backup=dir+L"\\"+id+L".content-undo";
    }
};
struct File{
    HANDLE h=INVALID_HANDLE_VALUE;
    explicit File(HANDLE v):h(v){}
    ~File(){if(h!=INVALID_HANDLE_VALUE)CloseHandle(h);}
    void close(){require(CloseHandle(h)!=0);h=INVALID_HANDLE_VALUE;}
};
Bytes readFile(const std::wstring& path){
    File f(CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr));
    require(f.h!=INVALID_HANDLE_VALUE);LARGE_INTEGER z;require(GetFileSizeEx(f.h,&z)&&z.QuadPart>0&&z.QuadPart<=32*1024*1024);
    Bytes buf(size_t(z.QuadPart));DWORD got=0;require(ReadFile(f.h,buf.data(),DWORD(buf.size()),&got,nullptr)&&got==buf.size());return buf;
}
void atomicFile(const std::wstring& path,const Bytes& b){
    const std::wstring tmp=path+L"."+std::to_wstring(GetCurrentProcessId())+L".qol-tmp";
    try{
        File f(CreateFileW(tmp.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr));
        require(f.h!=INVALID_HANDLE_VALUE);DWORD done=0;
        require(WriteFile(f.h,b.data(),DWORD(b.size()),&done,nullptr)&&done==b.size()&&FlushFileBuffers(f.h));f.close();
        require(readFile(tmp)==b);
        require(MoveFileExW(tmp.c_str(),path.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0);
    }catch(...){DeleteFileW(tmp.c_str());throw;}
}
std::vector<int> allowed(const Catalog& c){
    auto ids=c.cgs();for(auto e:c.shadow())ids.push_back(e.second);
    std::sort(ids.begin(),ids.end());require(std::adjacent_find(ids.begin(),ids.end())==ids.end());return ids;
}
Backup capture(Image& x,const Catalog& c){
    Backup b;b.overlay=var(x,Mode)!=0;b.read=x.read;
    for(int id:allowed(c))b.marks[uint16_t(id)]=uint16_t(var(x,id));
    auto it=x.seen.find(0);
    if(it!=x.seen.end()){
        Bytes selected(it->second.size(),0);
        for(int id:c.pictures())if(size_t(id/8)<selected.size())selected[id/8]|=it->second[id/8]&(1u<<(id%8));
        b.seen[0]=std::move(selected);
    }
    return b;
}
Bytes encode(const Backup& x,const Catalog& cat){
    Bytes b={'F','T','C','2'};put16(b,cat.encore?1:2);put16(b,x.overlay);put16(b,uint16_t(x.marks.size()));
    for(auto e:x.marks){put16(b,e.first);put16(b,e.second);}
    packMap(b,x.read);packMap(b,x.seen);put32(b,crc(b,b.size()));return b;
}
Backup decode(const Bytes& b,const Catalog& cat){
    require(b.size()>=22 && memcmp(b.data(),"FTC2",4)==0);
    Reader r{b,4};require(r.u16()==(cat.encore?1:2));Backup x;auto mode=r.u16();require(mode<2);x.overlay=mode!=0;
    auto ids=allowed(cat);require(r.u16()==ids.size());
    for(int id:ids){require(r.u16()==id);x.marks[uint16_t(id)]=r.u16();}
    x.read=r.map();x.seen=r.map();require(r.p+4==b.size());
    const uint32_t sum=crc(b,b.size()-4);const uint32_t stored=r.u32();require(sum==stored);return x;
}
void merge(Bits& into,const Bits& from){
    for(auto& entry:from){auto& out=into[entry.first];auto& add=entry.second;if(out.size()<add.size())out.resize(add.size());
        for(size_t i=0;i<add.size();++i)out[i]|=add[i];}
}
void clear(Image& x,const Catalog& cat,const Backup& b){
    for(int id:allowed(cat))var(x,id)=0;
    for(auto& item:x.read)std::fill(item.second.begin(),item.second.end(),0);
    for(const auto& e:b.seen)for(size_t j=0;j<e.second.size();j++)x.seen[e.first][j]&=uint8_t(~e.second[j]);
    var(x,Mode)=0;var(x,Pending)=1;var(x,Manual)=0;
}
void restore(Image& x,const Backup& b){
    for(auto e:b.marks)if(var(x,e.first)==0)var(x,e.first)=int16_t(e.second);
    merge(x.read,b.read);merge(x.seen,b.seen);
    if(!var(x,Manual))var(x,Mode)=b.overlay?1:0;
    var(x,Pending)=0;var(x,Manual)=0;
}
void ensureMap(bool seen,const Bits& target){
    std::map<uint16_t,size_t> lengths;
    records(seen,[&](uint16_t k,Buffer v){lengths[k]=v.size;});
    for(auto& e:target){
        if(lengths[e.first]>=e.second.size())continue;
        for(size_t i=lengths[e.first];i<e.second.size();++i){
            if(!e.second[i])continue;
            for(int j=0;j<8;j++)if(e.second[i]&(1u<<j)){
                int bit=int(i*8+j);
                if(seen){require(e.first==0);game<void(__cdecl*)(int)>(0x217d0)(bit);}
                else game<void(__cdecl*)(int,int)>(0x21790)(e.first,bit);
            }
        }
    }
}
void applyMap(bool seen,const Bits& target){
    records(seen,[&](uint16_t k,Buffer b){auto v=target.find(k);if(v!=target.end()){
        size_t n=std::min<size_t>(b.size,v->second.size());if(n)memcpy(b.data,v->second.data(),n);if(n<b.size)memset(b.data+n,0,b.size-n);
    }else{memset(b.data,0,b.size);}});
}
void commit(const Paths& p,const Image& before,const Image& after){
    // Existing keys are retained during a reset, including zero-filled read maps.
    // Grow missing records through the engine's own allocator when restoring an older save.
    ensureMap(false,after.read);ensureMap(true,after.seen);
    try{atomicFile(p.save,serialize(after));}
    catch(...){applyMap(false,before.read);applyMap(true,before.seen);throw;}
    auto raw=*game<int16_t**>(0x853b0);
    for(size_t i=0;i<after.vars.size();i++)if(after.vars[i]!=before.vars[i])raw[7000+i]=after.vars[i];
    applyMap(false,after.read);applyMap(true,after.seen);
}
bool confirm(HWND w,const wchar_t* text){
    return MessageBoxW(w,text,L"감상 기록",MB_YESNO|MB_DEFBUTTON2|MB_ICONQUESTION)==IDYES;
}
void info(HWND w,const wchar_t* text){MessageBoxW(w,text,L"감상 기록",MB_OK|MB_ICONINFORMATION);}
void action(HWND w,int pick){
    Paths path;Image before=current(),x=before;
    if(!var(x,Ready)){
        for(auto p:path.cat.shadow())var(x,p.second)=var(x,p.first);
        var(x,Ready)=1;
    }
    if(pick==1||pick==2){
        bool on=pick==1;
        if(bool(var(x,Mode))==on){info(w,on?L"모든 콘텐츠가 이미 열려 있습니다.":L"콘텐츠 해방이 꺼져 있습니다.");return;}
        if(!confirm(w,on?L"CG와 차분, 회상, 특전을 모두 열까요?\n직접 획득한 기록은 따로 보관됩니다.":L"모든 콘텐츠 해방을 취소하고 직접 획득한 항목만 표시할까요?"))return;
        var(x,Mode)=on?1:0;if(var(x,Pending))var(x,Manual)=1;
    }else if(pick==3){
        if(var(x,Pending)){info(w,L"이전에 초기화한 기록을 보관하고 있습니다. 다시 초기화하려면 먼저 ‘초기화 되돌리기’를 눌러 주세요.");return;}
        if(!confirm(w,L"CG·회상 감상 기록과 읽은 대사 표시를 비울까요?\n저장 슬롯과 이야기 진행은 유지됩니다. ‘초기화 되돌리기’로 복원할 수 있습니다."))return;
        auto backup=capture(x,path.cat);atomicFile(path.backup,encode(backup,path.cat));clear(x,path.cat,backup);
    }else if(pick==4){
        if(!var(x,Pending)){info(w,L"되돌릴 초기화 기록이 없습니다.");return;}
        auto backup=decode(readFile(path.backup),path.cat);
        if(!confirm(w,L"초기화 전 기록을 되돌릴까요?\n초기화 뒤에 읽은 대사와 새로 얻은 감상 기록도 함께 유지됩니다."))return;
        restore(x,backup);
    }else return;
    commit(path,before,x);
}
extern "C" int __stdcall ContentAction(void* control,void* panel){
    using Id=int(__thiscall*)(void*);
    int group=game<Id>(0x427c0)(control);
    if(group!=9)return game<int(__stdcall*)(void*,void*)>(0x102f0)(control,panel);
    auto radio=*reinterpret_cast<void**>(static_cast<uint8_t*>(panel)+0xf0+9*4);
    int pick=game<Id>(0x32b40)(radio);
    game<void(__thiscall*)(void*,int)>(0x32ac0)(radio,0);
    game<int16_t*>(0x8f576)[9]=0;
    HWND owner=GetActiveWindow();
    try{if(pick>=1&&pick<=4)action(owner,pick);}
    catch(...){MessageBoxW(owner,L"감상 기록을 적용할 수 없습니다. 저장 폴더와 복원 파일을 확인해 주세요.",L"감상 기록",MB_OK|MB_ICONERROR);}
    return 1;
}
