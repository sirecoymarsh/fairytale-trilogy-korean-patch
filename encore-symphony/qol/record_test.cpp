// Test the same two-title record code with progress earned after a restart.
#include "content_options.cpp"
#include <cstdio>
int main(){
    for(bool encore:{false,true}){
        Catalog c{encore};Image x;x.prefs.assign(0x872,0xab);x.vars.assign(3000,0);
        auto ids=allowed(c);var(x,Mode)=1;var(x,Ready)=1;var(x,7790)=17;
        var(x,ids.front())=1;var(x,ids.back())=1;x.read[1101]={0x02,0x40};x.seen[0]=Bytes(1250,0);
        int pic=c.pictures().front();x.seen[0][pic/8]|=1u<<(pic%8);x.seen[0][1249]=0x20;
        Backup old=capture(x,c);
        auto packed=encode(old,c);
        auto bytes=packed;bytes[25]^=0x80;
        bool rejected=false;try{decode(bytes,c);}catch(...){rejected=true;}require(rejected);
        rejected=false;try{decode(packed,Catalog{!encore});}catch(...){rejected=true;}require(rejected);
        clear(x,c,old);require(!var(x,Mode)&&var(x,Pending)&&var(x,7790)==17);
        require(x.read.at(1101)==Bytes({0,0}) && x.seen[0][1249]==0x20);
        var(x,ids[1])=1;x.read[1101][0]=0x10;x.read[1201]={0x21};x.seen[0][pic/8]|=0x80;
        Backup reopened=decode(packed,c);restore(x,reopened);
        require(var(x,ids[0]) && var(x,ids[1]) && var(x,ids.back()));
        require(x.read[1101]==Bytes({0x12,0x40}) && x.read[1201]==Bytes({0x21}));
        require(var(x,Mode)==1 && var(x,Pending)==0 && x.seen[0][pic/8]&(1u<<(pic%8)));
        require(x.prefs==Bytes(0x872,0xab) && var(x,7790)==17);
        clear(x,c,reopened);var(x,Manual)=1;restore(x,reopened);require(var(x,Mode)==0);
        printf("%s: read OR merge, new scene and CG marks, recovery, corrupt and other-game undo rejected\n",encore?"Encore":"Symphony");
    }
}
