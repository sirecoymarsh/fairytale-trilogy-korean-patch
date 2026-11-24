$ErrorActionPreference='Stop'
$fixture=Split-Path $PSScriptRoot -Parent
$support=Join-Path $fixture 'Support'
$env:PATH=$support+';'+$env:PATH
Add-Type -AssemblyName PresentationFramework
[void][Reflection.Assembly]::LoadFrom((Join-Path $support 'Microsoft.Web.WebView2.Core.dll'))
[void][Reflection.Assembly]::LoadFrom((Join-Path $support 'Microsoft.Web.WebView2.Wpf.dll'))
$release=[Reflection.Assembly]::LoadFrom('Y:\GAME\Fairytale Collection\페어리테일 통합판.exe')
$ctor=$release.GetType('FairyCollection.Castle',$true).GetConstructor([type[]]@([string]))
$window=$ctor.Invoke([object[]]@([string]$fixture))
$app=[Windows.Application]::new()
$app.ShutdownMode=[Windows.ShutdownMode]::OnMainWindowClose
[void]$app.Run($window)
