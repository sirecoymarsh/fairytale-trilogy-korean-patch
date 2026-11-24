using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

class GuestGameCheck {
    [StructLayout(LayoutKind.Sequential)] struct Rect { public int L,T,R,B; }
    [StructLayout(LayoutKind.Sequential)] struct Point { public int X,Y; }
    delegate bool Visit(IntPtr w,IntPtr param);
    [DllImport("user32")] static extern bool EnumWindows(Visit cb,IntPtr l);
    [DllImport("user32")] static extern bool EnumChildWindows(IntPtr w,Visit cb,IntPtr l);
    [DllImport("user32")] static extern int GetWindowThreadProcessId(IntPtr w,out int id);
    [DllImport("user32",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr w,StringBuilder s,int max);
    [DllImport("user32",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr w,StringBuilder s,int max);
    [DllImport("user32")] static extern bool IsWindowVisible(IntPtr w);
    [DllImport("user32")] static extern bool GetClientRect(IntPtr w,out Rect r);
    [DllImport("user32")] static extern bool ClientToScreen(IntPtr w,ref Point p);
    [DllImport("user32")] static extern bool PrintWindow(IntPtr w,IntPtr dc,uint flags);
    [DllImport("user32")] static extern bool SetForegroundWindow(IntPtr w);
    [DllImport("user32")] static extern bool ShowWindow(IntPtr w,int s);
    [DllImport("user32")] static extern bool SetCursorPos(int x,int y);
    [DllImport("user32")] static extern void mouse_event(uint flags,int dx,int dy,uint data,UIntPtr extra);
    [DllImport("user32")] static extern bool PostMessage(IntPtr w,int msg,IntPtr a,IntPtr b);
    [DllImport("user32")] static extern IntPtr GetDlgItem(IntPtr w,int id);
    [DllImport("user32")] static extern bool SetProcessDPIAware();
    static string Caption(IntPtr w) {var s=new StringBuilder(700);GetWindowText(w,s,s.Capacity);return s.ToString();}
    static string Class(IntPtr w){var s=new StringBuilder(150);GetClassName(w,s,s.Capacity);return s.ToString();}
    static List<IntPtr> Owned(Process p){
        var result=new List<IntPtr>();
        EnumWindows((w,l)=>{int id;GetWindowThreadProcessId(w,out id);if(id==p.Id&&IsWindowVisible(w))result.Add(w);return true;},IntPtr.Zero);
        return result;
    }
    static string Describe(Process p){
        if(p==null)return "No process";
        if(p.HasExited)return "Process exit "+p.ExitCode;
        var lines=new List<string>();
        foreach(var h in Owned(p)){
            lines.Add(Class(h)+" "+Caption(h));
            if(Class(h)=="#32770")EnumChildWindows(h,(x,l)=>{lines.Add(Class(x)+" "+Caption(x));return true;},IntPtr.Zero);
        }
        return String.Join(" | ",lines);
    }
    static string root,log;
    static Dictionary<string,object> report=new Dictionary<string,object>();
    static void Save(){File.WriteAllText(Path.Combine(log,"visual-result.json"),new JavaScriptSerializer().Serialize(report));}
    static void Capture(IntPtr h,string name,bool game){
        Rect r;if(!GetClientRect(h,out r)||r.R<10||r.B<10)throw new Exception("No client rectangle");
        using(var b=new Bitmap(r.R,r.B)){
            using(var g=Graphics.FromImage(b)){
                if(game){var dc=g.GetHdc();try{PrintWindow(h,dc,1);}finally{g.ReleaseHdc(dc);}}
                else{var pt=new Point();ClientToScreen(h,ref pt);g.CopyFromScreen(pt.X,pt.Y,0,0,b.Size);}
            }
            b.Save(Path.Combine(log,name+".png"),ImageFormat.Png);
        }
    }
    static IntPtr Window(Process process, string prefix){
        return Owned(process).FirstOrDefault(w=>Class(w).StartsWith(prefix,StringComparison.Ordinal));
    }
    static void Click(IntPtr h,double x,double y){
        ShowWindow(h,9);SetForegroundWindow(h);Thread.Sleep(300);Rect r;GetClientRect(h,out r);
        double width=Math.Min(r.R,r.B*16.0/9),height=width*9/16;
        var loc=new Point{X=(int)((r.R-width)/2+x*width),Y=(int)((r.B-height)/2+y*height)};
        ClientToScreen(h,ref loc);SetCursorPos(loc.X,loc.Y);Thread.Sleep(120);
        mouse_event(2,0,0,0,UIntPtr.Zero);Thread.Sleep(70);mouse_event(4,0,0,0,UIntPtr.Zero);
    }
    static Process Child(string folder){
        string path=Directory.GetFiles(folder,"*.exe").Single();
        foreach(var p in Process.GetProcessesByName(Path.GetFileNameWithoutExtension(path))){
            try{if(String.Equals(p.MainModule.FileName,path,StringComparison.OrdinalIgnoreCase))return p;}catch{}
            p.Dispose();
        }
        return null;
    }
    static void CloseGame(Process p,IntPtr w){
        if(p==null||p.HasExited)return;
        PostMessage(w,16,IntPtr.Zero,IntPtr.Zero);
        for(int i=0;i<30&&!p.HasExited;i++){
            var dlg=Window(p,"#32770");
            if(dlg!=IntPtr.Zero){var yes=GetDlgItem(dlg,6);if(yes!=IntPtr.Zero)PostMessage(yes,0xf5,IntPtr.Zero,IntPtr.Zero);}
            Thread.Sleep(200);
        }
    }
    [STAThread] static void Main(string[] args){
        if(Environment.UserName!="WDAGUtilityAccount"||args.Length!=2)return;
        try{
            root=args[0];log=args[1];Directory.CreateDirectory(log);
            SetProcessDPIAware();report["root"]=root;Save();
            // Only our previous guest test may still have an open collection window.
            var path=Path.Combine(root,"페어리테일 통합판.exe");
            foreach(var p in Process.GetProcessesByName("페어리테일 통합판")){
                if(String.Equals(p.MainModule.FileName,path,StringComparison.OrdinalIgnoreCase)){
                    foreach(var w in Owned(p))PostMessage(w,16,IntPtr.Zero,IntPtr.Zero);
                    p.WaitForExit(3500);
                }
            }
            var hub=Process.Start(new ProcessStartInfo(path){WorkingDirectory=root,UseShellExecute=false});
            try{
                Thread.Sleep(5500);var h=Window(hub,"HwndWrapper");
                report["hubWindows"]=Describe(hub);Save();
                if(h==IntPtr.Zero)throw new Exception("Hub window missing");
                ShowWindow(h,9);SetForegroundWindow(h);Thread.Sleep(500);
                Capture(h,"main",false);
                string[] names={"Requiem","Encore","Symphony"};
                double[] xs={.301,.530,.759};
                for(int n=0;n<names.Length;n++){
                    Click(h,.66,.204);Thread.Sleep(600);
                    if(n==0)Capture(h,"doors",false);
                    Click(h,xs[n],.60);
                    Process p=null;IntPtr g=IntPtr.Zero;
                    for(int i=0;i<45;i++){p=Child(Path.Combine(root,"Games",names[n]));if(p!=null){g=Window(p,"RosGameClass");if(g!=IntPtr.Zero)break;}Thread.Sleep(250);}
                    if(g==IntPtr.Zero){
                        report["lastHub"]=Describe(hub);report["lastGame"]=Describe(p);
                        Capture(h,"after-click",false);throw new Exception("No game window for "+names[n]);
                    }
                    Thread.Sleep(8000);Capture(g,names[n],true);
                    report[names[n]]=Describe(p);CloseGame(p,g);Thread.Sleep(800);
                    if(!p.HasExited)throw new Exception("Game did not return "+names[n]);
                    Save();
                }
                report["allReturned"]=true;
            }finally{if(!hub.HasExited){foreach(var w in Owned(hub))PostMessage(w,16,IntPtr.Zero,IntPtr.Zero);}}
        }catch(Exception e){report["error"]=e.ToString();}finally{if(log!=null)Save();}
    }
}