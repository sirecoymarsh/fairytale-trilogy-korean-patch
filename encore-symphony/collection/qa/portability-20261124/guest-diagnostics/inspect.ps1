param([string]$OutDir='C:\FairyQA')
$ErrorActionPreference='Continue'
if($env:USERNAME -ne 'WDAGUtilityAccount') {throw 'Guest account required'}
$runtimeKey='{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'
$wv=@()
foreach($prefix in 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients','HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients','HKCU:\Software\Microsoft\EdgeUpdate\Clients'){
 $key=Join-Path $prefix $runtimeKey
 if(Test-Path -LiteralPath $key){$wv+=@((Get-ItemProperty -LiteralPath $key).pv)}
}
$client=[Net.WebClient]::new();$client.Proxy=$null
try{$endpoint=$client.DownloadString('http://127.0.0.1:39117/json/list')}catch{$endpoint=$_.Exception.GetBaseException().Message}
$windows=@();$procs=@(Get-Process -ErrorAction SilentlyContinue|Where-Object {$_.ProcessName -in @('페어리테일 통합판','msedgewebview2','MicrosoftEdgeWebView2RuntimeInstallerX64','setup','MicrosoftEdgeUpdate') -or $_.MainWindowTitle})
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
foreach($proc in $procs){
 $entry=[ordered]@{id=$proc.Id;name=$proc.ProcessName;path=$proc.Path;title=$proc.MainWindowTitle}
 if($proc.MainWindowHandle -ne [IntPtr]::Zero -and $proc.ProcessName -in @('페어리테일 통합판','MicrosoftEdgeWebView2RuntimeInstallerX64','setup','MicrosoftEdgeUpdate','MicrosoftEdgeUpdateCore')){
  try{$root=[System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
  $entry['elements']=@($root.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)|ForEach-Object {$_.Current.Name}|Where-Object {$_}|Select-Object -First 30)
  }catch{}
 }
 $windows+=$entry
}
$data=[ordered]@{time=[DateTime]::UtcNow.ToString('o');runtime=$wv;endpoint=$endpoint;processes=$windows}
[IO.File]::WriteAllText((Join-Path $OutDir 'diagnostic-state.json'),($data|ConvertTo-Json -Depth 5))
