param([string]$Root,[string]$LogDir)
$ErrorActionPreference='Stop'
$gameApp=Join-Path $Root '페어리테일 통합판.exe'
$qa=[ordered]@{package=$gameApp;hub=$false;works=@{}}
$record=Join-Path $LogDir 'result.json'
function Save-Result { [IO.File]::WriteAllText($record,($qa | ConvertTo-Json -Depth 7)) }
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class FTWindow {
 [StructLayout(LayoutKind.Sequential)] public struct R { public int left,top,right,bottom; }
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [DllImport("user32")] public static extern bool EnumWindows(EnumProc cb,IntPtr l);
 [DllImport("user32")] static extern int GetWindowThreadProcessId(IntPtr h,out int p);
 [DllImport("user32",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h,StringBuilder b,int max);
 [DllImport("user32",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h,StringBuilder b,int max);
 [DllImport("user32")] public static extern IntPtr GetDlgItem(IntPtr h,int id);
 [DllImport("user32")] public static extern bool PostMessage(IntPtr h,int m,IntPtr w,IntPtr l);
 [DllImport("user32")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flag);
 [DllImport("user32")] public static extern bool GetClientRect(IntPtr h,out R r);
 public static IntPtr Find(int processId,string kind) {IntPtr result=IntPtr.Zero;EnumWindows((h,l)=>{int proc;GetWindowThreadProcessId(h,out proc);var s=new StringBuilder(256);GetClassName(h,s,256);if(proc==processId&&s.ToString()==kind){result=h;return false;}return true;},IntPtr.Zero);return result;}
 public static string Dialog(int pid){var dlg=Find(pid,"#32770");if(dlg==IntPtr.Zero)return "";var t=new StringBuilder(1024);GetWindowText(GetDlgItem(dlg,65535),t,1024);return t.ToString();}
 public static void Quit(int pid){var h=Find(pid,"RosGameClass");if(h!=IntPtr.Zero)PostMessage(h,0x10,IntPtr.Zero,IntPtr.Zero);}
 public static void Confirm(int pid){var h=Find(pid,"#32770");if(h==IntPtr.Zero)return;var yes=GetDlgItem(h,6);if(yes!=IntPtr.Zero)PostMessage(yes,0xf5,IntPtr.Zero,IntPtr.Zero);}
}
'@
function Capture-Game($window,$filename) {
 $rect=New-Object FTWindow+R
 if(![FTWindow]::GetClientRect($window,[ref]$rect)-or $rect.right -lt 32){throw 'Missing game client rectangle'}
 $bmp=New-Object Drawing.Bitmap($rect.right,$rect.bottom)
 $graphics=[Drawing.Graphics]::FromImage($bmp)
 $dc=$graphics.GetHdc()
 try { [void][FTWindow]::PrintWindow($window,$dc,1) } finally { $graphics.ReleaseHdc($dc);$graphics.Dispose() }
 try { $bmp.Save($filename,[Drawing.Imaging.ImageFormat]::Png) } finally { $bmp.Dispose() }
}
$port=39117
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS="--remote-debugging-port=$port --remote-debugging-address=127.0.0.1 --disable-background-networking --mute-audio"
$env:WEBVIEW2_USER_DATA_FOLDER=Join-Path $Root 'User\WebView'
$counter=0
function Invoke-Page([string]$expr){
 $script:counter++
 $active=$script:counter
 $request=@{id=$active;method='Runtime.evaluate';params=@{expression=$expr;returnByValue=$true;awaitPromise=$true}} | ConvertTo-Json -Compress -Depth 6
 $wire=[Text.Encoding]::UTF8.GetBytes($request)
 $cts=New-Object Threading.CancellationTokenSource(8000)
 try{
  [void]$ws.SendAsync([ArraySegment[byte]]::new($wire),[Net.WebSockets.WebSocketMessageType]::Text,$true,$cts.Token).GetAwaiter().GetResult()
  do {
   $buffer=New-Object byte[] 65536
   $stream=New-Object IO.MemoryStream
   do{$packet=$ws.ReceiveAsync([ArraySegment[byte]]::new($buffer),$cts.Token).GetAwaiter().GetResult();$stream.Write($buffer,0,$packet.Count)}while(!$packet.EndOfMessage)
   $message=[Text.Encoding]::UTF8.GetString($stream.ToArray())|ConvertFrom-Json;$stream.Dispose()
  }while($message.id -ne $active)
  if($message.result.exceptionDetails){throw $message.result.exceptionDetails.text}
  return $message.result.result.value
 }finally{$cts.Dispose()}
}
$hub=$null
$ws=$null
try{
 Save-Result
 $hub=Start-Process -FilePath $gameApp -WorkingDirectory $Root -PassThru
 $tabs=@();$limit=[DateTime]::UtcNow.AddSeconds(25)
 while([DateTime]::UtcNow -lt $limit -and !$hub.HasExited){
  try{
   $tabs=@(Invoke-RestMethod "http://127.0.0.1:$port/json/list" -TimeoutSec 2 -UseBasicParsing | ForEach-Object {$_} | Where-Object {$_.url -like 'https://fairytale.example/index*'})
   if($tabs.Count -gt 0){break}
  }catch{}
  Start-Sleep -Milliseconds 350
 }
 if(!$tabs.Count){$qa['hubDialog']=[FTWindow]::Dialog($hub.Id);throw 'Game hub did not initialize its WebView in this Windows image'}
 $ws=[Net.WebSockets.ClientWebSocket]::new()
 $ws.ConnectAsync([Uri]$tabs[0].webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
 $limit=[DateTime]::UtcNow.AddSeconds(14)
 do{$loaded=Invoke-Page "typeof progress!=='undefined' && !!progress.Symphony && !!catalog.Encore";if(!$loaded){Start-Sleep -Milliseconds 200}}while(!$loaded -and [DateTime]::UtcNow -lt $limit)
 if(!$loaded){throw 'Title did not load its local catalogs'}
 $qa.hub=$true;$qa['menu']=Invoke-Page "Array.from(document.querySelectorAll('#title button'),b=>b.getAttribute('aria-label')).join(' / ')";Save-Result
 foreach($pair in @(@('Requiem','레퀴엠'),@('Encore','앙코르'),@('Symphony','심포니'))){
  $work,$label=$pair;$directory=Join-Path $Root ('Games\'+$work)
  $target=(Get-ChildItem -LiteralPath $directory -Filter '*.exe' -File).FullName
  $data=[ordered]@{window=$false;screenshot=$false};$qa.works[$work]=$data
  [void](Invoke-Page "document.querySelector('#title button[aria-label=시작]').click();document.querySelector('#doors button[aria-label=$label]').click();true")
  $limit=[DateTime]::UtcNow.AddSeconds(18);$proc=$null;$h=[IntPtr]::Zero
  do{
   $proc=Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($target)) -ErrorAction SilentlyContinue|Where-Object {$_.Path -ieq $target}|Select-Object -First 1
   if($proc){$h=[FTWindow]::Find($proc.Id,'RosGameClass')}
   if($h -eq [IntPtr]::Zero){Start-Sleep -Milliseconds 220}
  }while([DateTime]::UtcNow -lt $limit -and $h -eq [IntPtr]::Zero)
  if($h -eq [IntPtr]::Zero){$data['notice']=Invoke-Page "document.getElementById('notice').textContent";Save-Result;throw "No native game window for $work"}
  Start-Sleep -Seconds 8
  $data.window=$true;$data['nativePath']=$proc.Path
  Capture-Game $h (Join-Path $LogDir ($work+'.png'));$data.screenshot=$true;Save-Result
  [FTWindow]::Quit($proc.Id)
  for($k=0;$k -lt 35 -and !$proc.HasExited;$k++){[FTWindow]::Confirm($proc.Id);Start-Sleep -Milliseconds 200}
  if(!$proc.HasExited){throw "Native game did not return for $work"}
  $limit=[DateTime]::UtcNow.AddSeconds(7)
  do{$returned=Invoke-Page "screen==='title' && !busy";if(!$returned){Start-Sleep -Milliseconds 160}}while(!$returned -and [DateTime]::UtcNow -lt $limit)
  if(!$returned){throw "No hub return for $work"};$data['returned']=$true;Save-Result
 }
}catch{
 $qa['detail']=$_ | Out-String
}finally{
 Save-Result
 if($ws){$ws.Dispose()}
 if($hub -and !$hub.HasExited){[void]$hub.CloseMainWindow()}
}
