using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;
using Gdi = System.Drawing;

namespace FairyCollection {
 internal static class Program {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] internal static extern bool SetDllDirectory(string path);
  [STAThread] public static void Main() {
   string root=AppDomain.CurrentDomain.BaseDirectory;
   bool first;
   using(var mutex=new Mutex(true,@"Local\FairytaleCollection.Korean.Hub",out first)) {
    if(!first){MessageBox.Show("페어리테일 통합판이 이미 열려 있어요.","페어리테일");return;}
    SetDllDirectory(Path.Combine(root,"Support"));
    try {new Application {ShutdownMode=ShutdownMode.OnMainWindowClose}.Run(new Castle(root));}
    catch(Exception ex){MessageBox.Show(ex.GetBaseException().Message,"페어리테일 통합판");}
   }
  }
 }
 internal sealed class Castle:Window {
  readonly string root;
  readonly WebView2 web=new WebView2(); readonly Grid stage=new Grid();
  readonly JavaScriptSerializer json=new JavaScriptSerializer();
  readonly Dictionary<string,string> exes=new Dictionary<string,string>{
   {"Requiem","フェアリーテイル・レクイエム.exe"},{"Encore","フェアリーテイル・アンコール.exe"},{"Symphony","フェアリーテイル・シンフォニー.exe"}};
  readonly Dictionary<string,string> saves=new Dictionary<string,string>{{"Requiem","FRsave"},{"Encore","FAsave"},{"Symphony","FSsave"}};
  readonly DispatcherTimer timer=new DispatcherTimer {Interval=TimeSpan.FromMilliseconds(650)};
  readonly MediaElement film=new MediaElement {LoadedBehavior=MediaState.Manual,UnloadedBehavior=MediaState.Manual,Stretch=Stretch.Uniform};
  readonly DockPanel theater=new DockPanel{Background=Brushes.Black,Visibility=Visibility.Collapsed};
  readonly Slider seek=new Slider{Minimum=0,Width=330,Margin=new Thickness(12,8,12,8)};
  readonly TextBlock filmName=new TextBlock{Foreground=Brushes.White,VerticalAlignment=VerticalAlignment.Center,Margin=new Thickness(14,0,12,0)};
  readonly Button pause=new Button{Content="일시 정지",Padding=new Thickness(15,4,15,4)};
  Process playing; string work,action; bool hasLeft,clicked,closingNative,ready,video,starting,paused,seekDrag,updateSeek;
  DateTime settle,opened; double volume=.65;
  [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h,int m,IntPtr w,IntPtr l);
  [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h,out RECT rect);
  [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
  [DllImport("user32.dll")] static extern IntPtr GetDlgItem(IntPtr h,int id);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
  delegate bool EnumProc(IntPtr h,IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb,IntPtr l);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h,System.Text.StringBuilder b,int max);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h,System.Text.StringBuilder b,int max);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr h,EnumProc cb,IntPtr l);
  struct RECT {public int left,top,right,bottom;}
  Gdi.Bitmap titleRef;
  public Castle(string dir) {
   root=dir;Title="페어리테일 통합판";Width=1296;Height=759;
   Width=Math.Min(Width,SystemParameters.WorkArea.Width);Height=Math.Min(Height,SystemParameters.WorkArea.Height);
   MinWidth=640;MinHeight=382;WindowStartupLocation=WindowStartupLocation.CenterScreen;Background=Brushes.Black;
   Content=stage;stage.Children.Add(web);stage.Children.Add(theater);
   BuildTheater();timer.Tick+=Tick;Loaded+=async (s,e)=>await Init();
   Closing+=(s,e)=>{if(playing!=null&&!playing.HasExited){e.Cancel=true;SetForegroundWindow(GameWindow());}else{timer.Stop();film.Close();}};
   PreviewKeyDown+=(s,e)=>{if(video&&e.Key==Key.Escape){StopFilm();e.Handled=true;}else if(e.Key==Key.F11){Fullscreen();e.Handled=true;}};
  }
  async Task Init(){
   try {
    string profile=Path.Combine(root,"User","WebView");
    var env=await CoreWebView2Environment.CreateAsync(null,profile);
    await web.EnsureCoreWebView2Async(env);
    var core=web.CoreWebView2;
    core.SetVirtualHostNameToFolderMapping("fairytale.example",Path.Combine(root,"Library"),CoreWebView2HostResourceAccessKind.DenyCors);
    core.Settings.AreDefaultContextMenusEnabled=false;core.Settings.IsStatusBarEnabled=false;core.Settings.AreBrowserAcceleratorKeysEnabled=false;
    core.Settings.IsZoomControlEnabled=true;core.Settings.AreDevToolsEnabled=false;
    core.NewWindowRequested+=(s,e)=>e.Handled=true;
    core.NavigationStarting+=(s,e)=>{Uri u;if(!Uri.TryCreate(e.Uri,UriKind.Absolute,out u)||u.Scheme!="https"||u.Host!="fairytale.example")e.Cancel=true;};
    core.WebMessageReceived+=Message;core.Navigate("https://fairytale.example/index.html");
   } catch(WebView2RuntimeNotFoundException){MessageBox.Show("Microsoft Edge WebView2 Runtime이 필요해요.\n통합판의 Support 폴더에서 WebView2_설치.exe를 실행한 뒤 다시 열어 주세요.\nWindows 10/11 64비트와 .NET Framework 4.8 이상을 지원합니다.",Title);Close();}
   catch(Exception e){MessageBox.Show("통합 화면을 열 수 없어요.\n"+e.GetBaseException().Message,Title);Close();}
  }
  void Fullscreen(){if(WindowStyle==WindowStyle.None){WindowStyle=WindowStyle.SingleBorderWindow;WindowState=WindowState.Normal;}else{WindowStyle=WindowStyle.None;WindowState=WindowState.Maximized;}}
  void Send(object msg){if(ready&&web.CoreWebView2!=null)web.CoreWebView2.PostWebMessageAsJson(json.Serialize(msg));}
  void Error(string message){Send(new {type="error",message=message});}
  string Folder(string w){return Path.Combine(root,"Games",w);}
  bool Installed(string w){return File.Exists(Path.Combine(Folder(w),exes[w]))&&File.Exists(Path.Combine(Folder(w),"scr.xfl"));}
  string SysSave(string w){return Path.Combine(Folder(w),"save",saves[w]+".dat");}
  HashSet<int> Marks(string w){
   var marks=new HashSet<int>();var p=SysSave(w);if(!File.Exists(p))return marks;
   using(var f=new FileStream(p,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete))
   using(var br=new BinaryReader(f)){
    if(f.Length<0x872+6000)throw new InvalidDataException("저장 파일의 진행 정보를 읽을 수 없어요.");
    f.Position=0x872;
    for(int i=7000;i<10000;++i)if(br.ReadInt16()!=0)marks.Add(i);
   }
   if(w=="Requiem"&&marks.Contains(7987)){
    int[] originals=new[]{7001,7002,7003,7004,7005,7006,7007,7008,7009,7010,7011,7012,7013,7014,7015,7016,7017,7018,7019,7020,7021,7022,7023,7024,7025,7026,7027,7028,7029,7030,7031,7032,7033,7034,7035,7036,7037,7038,7039,7040,7041,7042,7043,7044,7051,7052,7053,7055,7056,7057,7058,7059,7060,7061,7062,7063,7064,7065,7066,7067,7068,7069,7070,7071,7072,7101,7102,7103,7104,7105,7106,7107,7108,7109,7110,7111,7112,7113,7114,7115,7116,7117,7118,7119,7120,7121,7122,7123,7124,7125,7126,7127,7128,7151,7152,7153,7154,7155,7156,7157,7158,7159,7160,7161,7162,7163,7164,7165,7166,7167,7168,7169,7170,7171,7172,7201,7202,7203,7204,7205,7206,7207,7208,7209,7210,7211,7212,7213,7214,7215,7216,7217,7218,7219,7220,7221,7222,7223,7224,7251,7252,7253,7254,7255,7256,7257,7258,7259,7260,7261,7262,7263,7264,7265,7266,7267,7268,7269,7270,7271,7272,7273,7274,7301,7302,7303,7304,7305,7306,7307,7308,7309,7310,7311,7312,7313,7314,7315,7316,7317,7318,7319,7320,7321,7322,7323,7324,7325,7326,7327,7328,7329,7330,7331,7332,7333,7334,7351,7352,7353,7354,7355,7356,7357,7358,7359,7360,7361,7362,7363,7364,7365,7366,7367,7401,7402,7403,7404,7405,7406,7407,7408,7409,7410,7411,7412,7413,7414,7415,7700,7713};
    for(int i=0;i<originals.Length;i++){marks.Remove(originals[i]);if(marks.Contains(8300+i))marks.Add(originals[i]);}
   }
   return marks;
  }
  void State(){
   var result=new Dictionary<string,object>();
   foreach(var w in exes.Keys){
    bool installed=Installed(w);var marks=new HashSet<int>();int slots=0;string error="";
    if(installed)try{
     marks=Marks(w);string saveFolder=Path.Combine(Folder(w),"save");
     if(Directory.Exists(saveFolder))slots=Directory.EnumerateFiles(saveFolder,saves[w]+"*.dat").Count(p=>!String.Equals(Path.GetFileName(p),saves[w]+".dat",StringComparison.OrdinalIgnoreCase));
    }catch(InvalidDataException e){error=e.Message;}catch(IOException e){error=e.Message;}catch(UnauthorizedAccessException e){error=e.Message;}
    result[w]=new {installed=installed,flags=marks.ToArray(),overlay=marks.Contains(7988),slots=slots,error=error};
   }
   Send(new {type="state",works=result});
  }
  async void Message(object sender,CoreWebView2WebMessageReceivedEventArgs e){
   if(e.Source!="https://fairytale.example/index.html")return;
   try{
    var args=json.Deserialize<Dictionary<string,string>>(e.WebMessageAsJson);
    string cmd=args["cmd"];string w=args.ContainsKey("work")?args["work"]:"";string id=args.ContainsKey("id")?args["id"]:"";
    if(cmd=="ready"){ready=true;State();return;}
    if(cmd=="refresh"){State();return;}
    if(cmd=="fullscreen"){Fullscreen();return;}
    if(cmd=="close"){Close();return;}
    if(cmd=="volume"){double value;if(double.TryParse(id,System.Globalization.NumberStyles.Float,System.Globalization.CultureInfo.InvariantCulture,out value))volume=Math.Max(0,Math.Min(1,value));film.Volume=volume;return;}
    if(!exes.ContainsKey(w))return;
    if(cmd=="film"){PlayFilm(w,id);return;}
    if(cmd=="play")await Launch(w,id);
   }catch(Exception ex){Error(ex.GetBaseException().Message);}
  }
  bool CanFilm(string w,string id){
   if(!Installed(w))return false;
   if(id=="0001")return w!="Symphony";
   int[] gates;
   if(w=="Requiem"&&id=="0011")gates=new[]{7072};
   else if(w=="Requiem"&&id=="0012")gates=new[]{7319};
   else if(w=="Requiem"&&id=="0013")gates=new[]{7333};
   else if(w=="Encore"&&id=="0011")gates=new[]{7057,7110,7158};
   else if(w=="Encore"&&id=="0012")gates=new[]{7020};
   else if(w=="Symphony"&&id=="credits")gates=new[]{7700,7024};
   else return false;
   var marks=Marks(w);return (marks.Contains(7988))||gates.Any(marks.Contains);
  }
  async Task Launch(string w,string id){
   if(playing!=null||starting)return;
   if(!Installed(w)){State();throw new FileNotFoundException("이 작품이 설치되어 있지 않아요. 게임 폴더를 확인해 주세요.");}
   string mode=id;
   if(id=="continue"||id=="settings"||id=="episodes")mode="native";
   if(!(mode=="native"||mode=="story"||mode=="replay"||(mode=="credits"&&w=="Symphony")))return;
   if(id=="episodes"&&w!="Encore")return;
   if(id=="credits"&&!CanFilm(w,id)){Error("이 영상은 아직 열리지 않았어요.");return;}
   if(id=="native")return;
   starting=true;
   try{
    foreach(string name in exes.Values){
     var others=Process.GetProcessesByName(Path.GetFileNameWithoutExtension(name));
     try{if(others.Length>0)throw new InvalidOperationException("이미 실행 중인 페어리테일 작품을 종료한 뒤 선택해 주세요.");}
     finally{foreach(var other in others)other.Dispose();}
    }
    string folder=Folder(w),source=Path.Combine(root,"Entries",w,mode+".gsc"),target=Path.Combine(folder,"scr.xfl");
    await Task.Run(()=>EntryArchive.Select(target,source));
    string refFile=Path.Combine(root,"Support",w+"-title.png");if(titleRef!=null)titleRef.Dispose();
    titleRef=new Gdi.Bitmap(refFile);
    work=w; action=id;hasLeft=false;clicked=false;closingNative=false;opened=DateTime.UtcNow;
    settle=opened.AddSeconds(2);
    var child=new Process{StartInfo=new ProcessStartInfo(Path.Combine(folder,exes[w])){WorkingDirectory=folder,UseShellExecute=false}};
    child.EnableRaisingEvents=true;child.Exited+=(s,e)=>Dispatcher.BeginInvoke(new Action(()=>Finished(child)));
    playing=child;
    try{if(!child.Start())throw new InvalidOperationException("작품을 시작하지 못했어요.");}
    catch{playing=null;child.Dispose();throw;}
    timer.Start();Send(new {type="launched",work=w,action=id});Hide();
   }finally{starting=false;}
  }
  void Finished(Process child){
   if(playing!=child)return;
   timer.Stop();int code=child.ExitCode;child.Dispose();playing=null;
   if(titleRef!=null){titleRef.Dispose();titleRef=null;}
   Show();Activate();web.Focus();Send(new {type="returned",work=work,action=action});State();
   if(code!=0)Error("작품이 종료되었어요. 종료 코드 "+code.ToString());
  }
  IntPtr GameWindow(){
   IntPtr result=IntPtr.Zero;if(playing==null)return result;
   int pid=playing.Id;
   EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);
    if((int)p==pid&&Class(h)=="RosGameClass"&&IsWindowVisible(h)){result=h;return false;}return true;},IntPtr.Zero);
   return result;
  }
  static string Class(IntPtr h){var b=new System.Text.StringBuilder(128);GetClassName(h,b,128);return b.ToString();}
  static bool AtTitle(IntPtr h,Gdi.Bitmap reference){
   RECT r;if(!GetClientRect(h,out r)||r.right<320||r.bottom<180||IsIconic(h))return false;
   using(var b=new Gdi.Bitmap(r.right,r.bottom)){
    using(var g=Gdi.Graphics.FromImage(b)){IntPtr dc=g.GetHdc();try{if(!PrintWindow(h,dc,1))return false;}finally{g.ReleaseHdc(dc);}}
    int match=0,n=0;int menu=0,m=0;
    for(int y=135;y<305;y+=23)for(int x=260;x<702;x+=27){var a=b.GetPixel(x*r.right/1280,y*r.bottom/720);var c=reference.GetPixel(x*reference.Width/1280,y*reference.Height/720);if(Diff(a,c)<44)match++;n++;}
    for(int y=118;y<178;y+=9)for(int x=819;x<856;x+=8){var a=b.GetPixel(x*r.right/1280,y*r.bottom/720);var c=reference.GetPixel(x*reference.Width/1280,y*reference.Height/720);if(Diff(a,c)<52)menu++;m++;}
    return match*100>n*77&&menu*100>m*68;
   }
  }
  static int Diff(Gdi.Color a,Gdi.Color b){return Math.Max(Math.Abs(a.R-b.R),Math.Max(Math.Abs(a.G-b.G),Math.Abs(a.B-b.B)));}
  static async void PointClick(IntPtr h,int x,int y){
   RECT r;if(!GetClientRect(h,out r))return;
   var lp=(IntPtr)(((y*r.bottom/720)<<16)|(x*r.right/1280));
   SetForegroundWindow(h);PostMessage(h,0x200,IntPtr.Zero,lp);await Task.Delay(120);PostMessage(h,0x201,(IntPtr)1,lp);await Task.Delay(85);PostMessage(h,0x202,IntPtr.Zero,lp);
  }
  void ConfirmTitleExit(){
   if(playing==null)return;int pid=playing.Id;
   EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if((int)p!=pid||Class(h)!="#32770")return true;
    string message="";EnumChildWindows(h,(c,j)=>{if(Class(c)=="Static"){var s=new System.Text.StringBuilder(400);GetWindowText(c,s,400);message+=s.ToString();}return true;},IntPtr.Zero);
    if(message.Contains("종료")||message.Contains("終了")||message.IndexOf("exit",StringComparison.OrdinalIgnoreCase)>=0){
     var yes=GetDlgItem(h,6);if(yes==IntPtr.Zero)yes=GetDlgItem(h,1);if(yes!=IntPtr.Zero)PostMessage(yes,0xf5,IntPtr.Zero,IntPtr.Zero);
    }return true;},IntPtr.Zero);
  }
  void Tick(object s,EventArgs e){
   if(video){if(!seekDrag&&film.NaturalDuration.HasTimeSpan){updateSeek=true;seek.Maximum=film.NaturalDuration.TimeSpan.TotalSeconds;seek.Value=film.Position.TotalSeconds;updateSeek=false;}return;}
   if(playing==null||playing.HasExited||DateTime.UtcNow<settle)return;
   if(closingNative){ConfirmTitleExit();return;}
   var h=GameWindow();if(h==IntPtr.Zero)return;
   bool needMenu=action=="continue"||action=="settings"||action=="episodes";
   bool title=AtTitle(h,titleRef);
   if(needMenu&&!clicked){
    if(!title)return;
    clicked=true;int x=action=="continue"?963:action=="settings"?924:838;int y=action=="continue"?236:action=="settings"?340:143;
    PointClick(h,x,y);settle=DateTime.UtcNow.AddMilliseconds(1200);return;
   }
   if(!title){if((DateTime.UtcNow-opened).TotalSeconds>3)hasLeft=true;return;}
   if(!hasLeft&&!(needMenu&&clicked&&(DateTime.UtcNow-opened).TotalSeconds>8))return;
   closingNative=true;PostMessage(h,0x10,IntPtr.Zero,IntPtr.Zero);
  }
  void BuildTheater(){
   var bar=new StackPanel{Orientation=Orientation.Horizontal,Height=42,Background=new SolidColorBrush(Color.FromRgb(42,24,43))};
   var back=new Button{Content="←  감상실",Padding=new Thickness(13,4,13,4)};back.Click+=(s,e)=>StopFilm();bar.Children.Add(back);bar.Children.Add(filmName);
   pause.Click+=(s,e)=>{paused=!paused;if(paused)film.Pause();else film.Play();pause.Content=paused?"재생":"일시 정지";};bar.Children.Add(pause);bar.Children.Add(seek);
   seek.PreviewMouseLeftButtonDown+=(s,e)=>seekDrag=true;seek.PreviewMouseLeftButtonUp+=(s,e)=>{seekDrag=false;film.Position=TimeSpan.FromSeconds(seek.Value);};
   seek.ValueChanged+=(s,e)=>{if(video&&!updateSeek&&!seekDrag)film.Position=TimeSpan.FromSeconds(seek.Value);};
   DockPanel.SetDock(bar,Dock.Bottom);theater.Children.Add(bar);theater.Children.Add(film);
   film.MediaEnded+=(s,e)=>StopFilm();film.MediaFailed+=(s,e)=>{if(video){StopFilm();Error("영상을 재생하지 못했어요. "+e.ErrorException.Message);}};
  }
  void PlayFilm(string w,string id){
   if(!CanFilm(w,id)){Error("이 영상은 아직 열리지 않았어요.");return;}
   if(id=="credits"){return;}
   var browserMovie=Path.Combine(root,"Library","cinema",w,id+".mp4");
   if(File.Exists(browserMovie)){
    Send(new {type="filmOpen",url="cinema/"+w+"/"+id+".mp4",name=id=="0001"?"오프닝":"엔딩 영상 "+(Int32.Parse(id)-10)});return;
   }
   var p=Path.Combine(root,"Cinema",w,id+".mpg");if(!File.Exists(p))throw new FileNotFoundException("영상을 찾을 수 없어요.",p);
   video=true;paused=false;pause.Content="일시 정지";filmName.Text=id=="0001"?"오프닝":"엔딩 영상 "+(Int32.Parse(id)-10);
   web.Visibility=Visibility.Collapsed;theater.Visibility=Visibility.Visible;film.Volume=volume;film.Source=new Uri(p);film.Play();timer.Start();
  }
  void StopFilm(){if(!video)return;video=false;timer.Stop();film.Stop();film.Close();theater.Visibility=Visibility.Collapsed;web.Visibility=Visibility.Visible;web.Focus();Send(new {type="filmClosed"});}
 }
}

