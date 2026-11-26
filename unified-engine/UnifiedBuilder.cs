using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;

namespace FairyBuilder {
 internal static class Program {
  [STAThread] static void Main() {
   Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false);
   Application.Run(new Builder());
  }
 }
 internal sealed class Builder : Form {
  readonly string root=AppDomain.CurrentDomain.BaseDirectory;
  readonly string[] works={"Requiem","Encore","Symphony"}, names={"레퀴엠","앙코르","심포니"};
  readonly TextBox[] paths=new TextBox[3]; readonly CheckBox[] saves=new CheckBox[3];
  readonly TextBox output=new TextBox(), log=new TextBox();
  readonly Button build=new Button(), open=new Button(); readonly Panel choices=new Panel();
  readonly Label status=new Label(); bool building;
  public Builder() {
   Text="페어리테일 이야기 모음 만들기"; ClientSize=new Size(880,690); MinimumSize=new Size(896,729);
   Font=new Font("맑은 고딕",10); StartPosition=FormStartPosition.CenterScreen;
   BackColor=Color.FromArgb(248,245,248);
   var title=new Label {Text="세 작품으로 하나의 이야기 모음 만들기",Font=new Font(Font.FontFamily,19,FontStyle.Bold),AutoSize=true,Location=new Point(24,21)};
   Controls.Add(title);
   Controls.Add(new Label {Text="레퀴엠·앙코르·심포니 세 작품의 원본 또는 지원하는 한국어판 설치 폴더를 선택하세요.",AutoSize=true,Location=new Point(26,64)});
   choices.SetBounds(20,100,840,330);choices.Anchor=AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right;Controls.Add(choices);
   for(int i=0;i<3;i++) {
    int row=i, y=i*84; var label=new Label {Text=names[i],AutoSize=true,Location=new Point(6,y+6)}; choices.Controls.Add(label);
    paths[i]=new TextBox {Location=new Point(100,y),Width=580,Anchor=AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right,AccessibleName=names[i]+" 설치 폴더"}; choices.Controls.Add(paths[i]);
    var browse=new Button {Text="폴더 선택",Location=new Point(690,y-1),Size=new Size(90,30),Anchor=AnchorStyles.Top|AnchorStyles.Right};
    browse.Click+=(s,e)=>Pick(paths[row],false); choices.Controls.Add(browse);
    var clear=new Button {Text="해제",Location=new Point(784,y-1),Size=new Size(52,30),Anchor=AnchorStyles.Top|AnchorStyles.Right};clear.Click+=(s,e)=>{paths[row].Clear();saves[row].Checked=false;};choices.Controls.Add(clear);
    saves[i]=new CheckBox {Text="이 작품의 세이브 가져오기",AutoSize=true,Location=new Point(100,y+37),AccessibleName=names[i]+" 세이브 가져오기"}; choices.Controls.Add(saves[i]);
   }
   choices.Controls.Add(new Label {Text="만들 위치",AutoSize=true,Location=new Point(6,263)});
   output.SetBounds(100,257,580,28);output.Anchor=AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right;output.AccessibleName="통합판 출력 폴더";choices.Controls.Add(output);
   var destination=new Button {Text="폴더 선택",Location=new Point(690,256),Size=new Size(146,30),Anchor=AnchorStyles.Top|AnchorStyles.Right};destination.Click+=(s,e)=>Pick(output,true);choices.Controls.Add(destination);
   choices.Controls.Add(new Label {Text="새 폴더에 독립된 통합판을 만듭니다. 원본 게임과 원본 세이브는 그대로 보존돼요.",AutoSize=true,Location=new Point(100,298)});
   log.SetBounds(26,440,828,163);log.Multiline=true;log.ReadOnly=true;log.ScrollBars=ScrollBars.Vertical;log.Anchor=AnchorStyles.Top|AnchorStyles.Bottom|AnchorStyles.Left|AnchorStyles.Right;log.BackColor=Color.White;log.AccessibleName="제작 진행 상황";Controls.Add(log);
   status.SetBounds(26,619,490,40);status.Anchor=AnchorStyles.Bottom|AnchorStyles.Left|AnchorStyles.Right;status.Text="세 작품을 한 엔진에서 실행합니다. 세이브는 작품별로 구분됩니다.";Controls.Add(status);
   build.Text="통합판 만들기";build.SetBounds(692,620,162,42);build.Anchor=AnchorStyles.Bottom|AnchorStyles.Right;build.Click+=async(s,e)=>await Make();Controls.Add(build);
   open.Text="완성 폴더 열기";open.SetBounds(524,620,157,42);open.Anchor=AnchorStyles.Bottom|AnchorStyles.Right;open.Enabled=false;open.Click+=(s,e)=>Process.Start("explorer.exe",Quote(Path.GetFullPath(output.Text.Trim())));Controls.Add(open);
   FormClosing+=(s,e)=>{if(building){e.Cancel=true;status.Text="제작이 끝난 뒤 창을 닫아 주세요.";}};
  }
  static string Quote(string value){return "\""+value.Replace("\"","")+"\"";}
  void Pick(TextBox field,bool target){using(var dialog=new FolderBrowserDialog {Description=target?"빈 출력 폴더를 선택하거나 새 폴더를 만들어 주세요.":"해당 작품의 실행 파일이 들어 있는 폴더를 선택해 주세요.",ShowNewFolderButton=target}){if(Directory.Exists(field.Text))dialog.SelectedPath=field.Text;if(dialog.ShowDialog(this)==DialogResult.OK)field.Text=dialog.SelectedPath;}}
  void Line(string message){if(IsDisposed)return;if(InvokeRequired){BeginInvoke(new Action<string>(Line),message);return;}log.AppendText(message+Environment.NewLine);status.Text=message;}
  async Task Make(){
   if(building)return;
   var games=new Dictionary<string,object>();
   for(int i=0;i<works.Length;i++)if(!String.IsNullOrWhiteSpace(paths[i].Text))games[works[i]]=new {path=paths[i].Text.Trim(),import_save=saves[i].Checked};
   if(games.Count!=3||String.IsNullOrWhiteSpace(output.Text)){status.Text="세 작품을 모두 선택하고 만들 위치를 지정해 주세요.";return;}
   string control=null;
   try{
    string target=Path.GetFullPath(output.Text.Trim());string parent=Path.GetDirectoryName(target);
    if(String.IsNullOrEmpty(parent))throw new InvalidOperationException("새 출력 폴더를 선택해 주세요.");
    if(Directory.Exists(target)&&Directory.GetFileSystemEntries(target).Length!=0)throw new InvalidOperationException("출력 폴더가 비어 있지 않아요. 새 폴더를 선택해 주세요.");
    Directory.CreateDirectory(parent);control=Path.Combine(parent,".fairytale-builder-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(control);
    string config=Path.Combine(control,"selection.json");File.WriteAllText(config,new JavaScriptSerializer().Serialize(new {output=target,games=games}),new UTF8Encoding(false));
    string python=Path.Combine(root,"Runtime","python.exe"),script=Path.Combine(root,"Scripts","build_unified.py");
    if(!File.Exists(python)||!File.Exists(script))throw new FileNotFoundException("패키지의 Runtime 또는 Scripts 폴더가 없어요. 압축을 모두 풀어 주세요.");
    building=true;choices.Enabled=false;build.Enabled=false;open.Enabled=false;log.Clear();Line("설치 파일을 확인하고 있어요.");
    int result=await Task.Run(()=>{
     var info=new ProcessStartInfo(python,"-B -u "+Quote(script)+" --package "+Quote(root.TrimEnd(Path.DirectorySeparatorChar))+" --config "+Quote(config)){UseShellExecute=false,CreateNoWindow=true,WorkingDirectory=root,RedirectStandardOutput=true,RedirectStandardError=true,StandardOutputEncoding=Encoding.UTF8,StandardErrorEncoding=Encoding.UTF8};
     info.EnvironmentVariables["TEMP"]=control;info.EnvironmentVariables["TMP"]=control;info.EnvironmentVariables["PYTHONIOENCODING"]="utf-8";
     using(var p=new Process{StartInfo=info}){p.OutputDataReceived+=(s,e)=>{if(e.Data!=null)Line(e.Data);};p.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)Line(e.Data);};p.Start();p.BeginOutputReadLine();p.BeginErrorReadLine();p.WaitForExit();return p.ExitCode;}
    });
    if(result==0){status.Text="완료했어요. 완성 폴더의 통합판 실행 파일을 열어 주세요.";open.Enabled=true;}
    else status.Text="만들지 못했어요. 위의 오류 내용을 확인해 주세요. 원본은 보존되어 있어요.";
   }catch(Exception e){Line("실패: "+e.GetBaseException().Message);}
   finally{building=false;choices.Enabled=true;build.Enabled=true;if(control!=null&&Directory.Exists(control)){try{Directory.Delete(control,true);}catch(IOException){}}}
  }
 }
}
