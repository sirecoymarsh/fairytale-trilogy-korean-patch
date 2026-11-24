$ErrorActionPreference='Stop'
$control=$PSScriptRoot
$target='C:\GameDrop\Fairytale'
$env:TEMP=$env:TMP=(Join-Path $control 'tmp')
[void][IO.Directory]::CreateDirectory($env:TEMP)
try {
  $ver=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
  $wv=@()
  foreach($base in 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients','HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients','HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients') {
    if(Test-Path $base){$wv+=@(Get-ChildItem $base | ForEach-Object { Get-ItemProperty -LiteralPath $_.PSPath } | Where-Object {$_.name -like '*WebView2*'} | ForEach-Object {$_.pv})}
  }
  $info=[ordered]@{computer=$env:COMPUTERNAME;user=$env:USERNAME;build=$ver.CurrentBuildNumber;edition=$ver.EditionID;locale=(Get-WinSystemLocale).Name;release=(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full').Release;webview=$wv;korean_font=Test-Path (Join-Path $env:WINDIR 'Fonts\malgun.ttf');guest_target=$target;has_y=Test-Path 'Y:\';has_p=Test-Path 'P:\'}
  [IO.File]::WriteAllText((Join-Path $control 'boot.json'),($info|ConvertTo-Json -Depth 4))
  $until=[DateTime]::UtcNow.AddMinutes(4)
  while (!(Test-Path (Join-Path $control 'run-guest.ps1')) -and [DateTime]::UtcNow -lt $until){Start-Sleep -Milliseconds 300}
  & (Join-Path $control 'run-guest.ps1') -Root $target -LogDir $control
} catch {
  [IO.File]::WriteAllText((Join-Path $control 'failure.txt'),($_ | Out-String))
} finally {
  [IO.File]::WriteAllText((Join-Path $control 'finished.txt'),[DateTime]::UtcNow.ToString('o'))
  if ($env:USERNAME -eq 'WDAGUtilityAccount') { & "$env:SystemRoot\System32\shutdown.exe" /s /t 0 }
}