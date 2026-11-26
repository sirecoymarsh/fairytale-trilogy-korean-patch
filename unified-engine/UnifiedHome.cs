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
 public static class Home {
  static Castle window;static ManualResetEvent created=new ManualResetEvent(false),picked=new ManualResetEvent(false);static int result;static Exception fault;static Thread ui;
  [DllImport("user32.dll")] static extern IntPtr GetThreadDesktop(uint id);
  [DllImport("user32.dll")] static extern bool SetThreadDesktop(IntPtr desktop);
  [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode)] static extern bool SetDllDirectory(string p);
  public static int Select(string value){
   try{
    long hwnd=Int64.Parse(value);picked.Reset();
    if(ui==null){IntPtr desktop=GetThreadDesktop(GetCurrentThreadId());ui=new Thread(()=>{try{if(!SetThreadDesktop(desktop))throw new InvalidOperationException("통합 화면 데스크톱을 열 수 없어요.");string root=AppDomain.CurrentDomain.BaseDirectory;SetDllDirectory(Path.Combine(root,"Support"));window=new Castle(root,new IntPtr(hwnd));window.Chosen=(v)=>{result=v;picked.Set();};created.Set();new Application{ShutdownMode=ShutdownMode.OnExplicitShutdown}.Run(window);}catch(Exception e){fault=e;created.Set();picked.Set();}});ui.IsBackground=true;ui.SetApartmentState(ApartmentState.STA);ui.Start();created.WaitOne();}
    else window.Dispatcher.BeginInvoke(new Action(()=>window.ResumeHome()));
    if(fault!=null)throw fault;picked.WaitOne();if(fault!=null)throw fault;return result;
   }catch(Exception e){MessageBox.Show(e.GetBaseException().Message,"페어리테일 이야기 모음");return -1;}
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
  string work,action; bool clicked,ready,video,paused,seekDrag,updateSeek;
  DateTime opened; double volume=.65;
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
  public Action<int> Chosen; readonly IntPtr native; int pendingAction;
  public Castle(string dir,IntPtr nativeWindow) {
   native=nativeWindow;new System.Windows.Interop.WindowInteropHelper(this).Owner=native;
   root=dir;Title="페어리테일 이야기 모음";Width=1296;Height=759;
   Width=Math.Min(Width,SystemParameters.WorkArea.Width);Height=Math.Min(Height,SystemParameters.WorkArea.Height);
   MinWidth=640;MinHeight=382;WindowStartupLocation=WindowStartupLocation.CenterScreen;Background=Brushes.Black;
   Content=stage;stage.Children.Add(web);stage.Children.Add(theater);
   BuildTheater();timer.Tick+=Tick;Loaded+=async (s,e)=>await Init();
   Closing+=(s,e)=>{e.Cancel=true;timer.Stop();film.Close();Hide();if(Chosen!=null)Chosen(-1);};
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
  string WorkKey(string w){return w=="Requiem"?"R":w=="Encore"?"A":"S";}
  string Folder(string w){return Path.Combine(root,"Data",WorkKey(w));}
  string SaveFolder(string w){return Path.Combine(root,"Save",WorkKey(w));}
  bool Installed(string w){return File.Exists(Path.Combine(Folder(w),"scr.xfl"));}
  string SysSave(string w){return Path.Combine(SaveFolder(w),saves[w]+".dat");}
  HashSet<int> Marks(string w){
   var marks=new HashSet<int>();var p=SysSave(w);if(!File.Exists(p))return marks;
   using(var f=new FileStream(p,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete))
   using(var br=new BinaryReader(f)){
    if(f.Length<0x872+6000)throw new InvalidDataException("저장 파일의 진행 정보를 읽을 수 없어요.");
    f.Position=0x872;
    for(int i=7000;i<10000;++i)if(br.ReadInt16()!=0)marks.Add(i);
   } return marks;
  }
  void State(){
   var result=new Dictionary<string,object>();
   foreach(var w in exes.Keys){
    bool installed=Installed(w);var marks=new HashSet<int>();int slots=0;string error="";
    if(installed)try{
     marks=Marks(w);string saveFolder=SaveFolder(w);
     if(Directory.Exists(saveFolder))slots=Directory.EnumerateFiles(saveFolder,saves[w]+"*.dat").Count(p=>!String.Equals(Path.GetFileName(p),saves[w]+".dat",StringComparison.OrdinalIgnoreCase));
    }catch(InvalidDataException e){error=e.Message;}catch(IOException e){error=e.Message;}catch(UnauthorizedAccessException e){error=e.Message;}
    result[w]=new {installed=installed,flags=marks.ToArray(),overlay=w!="Requiem"&&marks.Contains(7988),slots=slots,error=error};
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
   var marks=Marks(w);return (w!="Requiem"&&marks.Contains(7988))||gates.Any(marks.Contains);
  }
  Task Launch(string w,string id){
   if(!Installed(w))throw new FileNotFoundException("작품 데이터가 없어요. 세 작품으로 통합판을 다시 만들어 주세요.");
   int code=id=="story"?1:id=="continue"?2:id=="settings"?3:id=="episodes"?4:id=="replay"?5:id=="credits"?6:0;
   if(code==0||(id=="episodes"&&w!="Encore")||(id=="credits"&&!CanFilm(w,id)))return Task.FromResult(0);
   work=w;action=id;pendingAction=(code>=2&&code<=4)?code:0;opened=DateTime.UtcNow;clicked=false;
   if(titleRef!=null){titleRef.Dispose();titleRef=null;}if(pendingAction!=0)titleRef=new Gdi.Bitmap(Path.Combine(root,"Support",w+"-title.png"));
   Send(new {type="launched",work=w,action=id});Hide();timer.Start();
   int n=w=="Requiem"?1:w=="Encore"?2:3;Chosen(n*100+code);return Task.FromResult(0);
  }
  public void ResumeHome(){pendingAction=0;timer.Stop();Show();Activate();web.Focus();Send(new {type="returned",work=work,action=action});State();}
  IntPtr GameWindow(){return native;}
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
  void Tick(object s,EventArgs e){
   if(video){if(!seekDrag&&film.NaturalDuration.HasTimeSpan){updateSeek=true;seek.Maximum=film.NaturalDuration.TimeSpan.TotalSeconds;seek.Value=film.Position.TotalSeconds;updateSeek=false;}return;}
   if(pendingAction==0||clicked)return;
   if((DateTime.UtcNow-opened).TotalSeconds>30){pendingAction=0;timer.Stop();return;}
   if(!AtTitle(native,titleRef))return;
   clicked=true;int x=pendingAction==2?963:pendingAction==3?924:838;int y=pendingAction==2?236:pendingAction==3?340:143;
   PointClick(native,x,y);pendingAction=0;timer.Stop();
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
