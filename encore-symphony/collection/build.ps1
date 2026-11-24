$ErrorActionPreference='Stop'
$src=$PSScriptRoot
$root='Y:\GAME\Fairytale Collection'
$pub=Join-Path $root 'Library'
$support=Join-Path $root 'Support'
$privateAssemblies='C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\PrivateAssemblies'
$net=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319'
$cache=Join-Path $src 'tmp'
$env:TEMP=$cache
$env:TMP=$cache
New-Item -ItemType Directory -Force -Path $support | Out-Null
foreach($file in 'Microsoft.Web.WebView2.Core.dll','Microsoft.Web.WebView2.Wpf.dll','WebView2Loader.dll'){
  $inputDll=Join-Path $privateAssemblies $file
  $deployedDll=Join-Path $support $file
  if(!(Test-Path -LiteralPath $deployedDll) -or (Get-FileHash -LiteralPath $inputDll).Hash -ne (Get-FileHash -LiteralPath $deployedDll).Hash){
    Copy-Item -LiteralPath $inputDll -Destination $deployedDll -Force
  }
}
foreach($file in 'index.html','castle.css','castle.js'){
  Copy-Item -LiteralPath (Join-Path $src $file) -Destination (Join-Path $pub $file) -Force
}
foreach($work in 'Requiem','Encore','Symphony'){
  $current=Join-Path $src ("qa\screens\"+$work+"-native-10.png")
  if(Test-Path -LiteralPath $current){$ref=$current}
  elseif($work -eq 'Requiem'){$ref='P:\AI\Codex\projects\fairytale-requiem-ko\evidence\runtime\final_game_qa\04_fresh_title_for_error_repro.png'}
  else{$ref=Join-Path (Split-Path $src -Parent) ("qol\evidence\"+$work+"\title.png")}
  Copy-Item -LiteralPath $ref -Destination (Join-Path $support ($work+'-title.png')) -Force
}
Add-Type -AssemblyName System.Drawing
$game=Join-Path $root 'Games\Requiem\フェアリーテイル・レクイエム.exe'
$icon=[Drawing.Icon]::ExtractAssociatedIcon($game)
$icoPath=Join-Path $src 'tmp\collection.ico'
$stream=[IO.File]::Create($icoPath)
try{$icon.Save($stream)}finally{$stream.Dispose();$icon.Dispose()}
$exe=Join-Path $root '페어리테일 통합판.exe'
$cfg='<configuration><startup><supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8"/></startup><runtime><assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1"><probing privatePath="Support"/></assemblyBinding></runtime></configuration>'
[IO.File]::WriteAllText($exe+'.config',$cfg,[Text.UTF8Encoding]::new($false))
$refs=@('System.dll','System.Core.dll','System.Drawing.dll','System.Web.Extensions.dll','System.Xaml.dll','WindowsBase.dll','PresentationCore.dll','PresentationFramework.dll')
$argsList=@('/nologo','/target:winexe','/platform:x64','/optimize+','/utf8output','/codepage:65001',('/out:'+$exe),('/win32icon:'+$icoPath))
foreach($item in $refs){
  $ref=Join-Path $net $item
  if(!(Test-Path -LiteralPath $ref)){$ref=Join-Path (Join-Path $net 'WPF') $item}
  $argsList+=('/reference:'+$ref)
}
foreach($item in 'Microsoft.Web.WebView2.Core.dll','Microsoft.Web.WebView2.Wpf.dll'){$argsList+=('/reference:'+(Join-Path $support $item))}
$argsList+=(Join-Path $src 'Castle.cs')
$argsList+=(Join-Path $src 'EntryArchive.cs')
& (Join-Path $net 'csc.exe') $argsList
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
Get-Item -LiteralPath $exe | Select-Object FullName,Length
