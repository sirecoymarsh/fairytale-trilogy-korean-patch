$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$collectionRoot = 'Y:\GAME\Fairytale Collection'
$exe = Join-Path $collectionRoot '페어리테일 통합판.exe'
$process = Start-Process -FilePath $exe -WorkingDirectory $collectionRoot -WindowStyle Normal -PassThru
$deadline = [DateTime]::UtcNow.AddSeconds(30)
while ([DateTime]::UtcNow -lt $deadline -and $process.MainWindowHandle -eq [IntPtr]::Zero) {
    if ($process.HasExited) { throw '설치본이 시작 중에 종료됨' }
    Start-Sleep -Milliseconds 200
    $process.Refresh()
}
$window = [System.Windows.Automation.AutomationElement]::FromHandle($process.MainWindowHandle)
function Find-Button([string]$label) {
    $name = [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::NameProperty, $label)
    $type = [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
    $condition = [System.Windows.Automation.AndCondition]::new($name, $type)
    $deadline = [DateTime]::UtcNow.AddSeconds(20)
    do {
        $matches = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
        foreach ($item in $matches) { if ($item.Current.IsEnabled -and !$item.Current.IsOffscreen) { return $item } }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "화면에서 버튼을 찾지 못함 ($label)"
}
function Click-Button([string]$label) {
    $target = Find-Button $label
    $target.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
}
try {
    Click-Button '영상'
    Click-Button '앙코르'
    Click-Button '오프닝'
    $pause = Find-Button '일시 정지'
    Start-Sleep -Seconds 5
    python -X utf8 -B (Join-Path $PSScriptRoot 'capture_cinema.py') $process.Id $process.MainWindowHandle.ToInt64()
    if ($LASTEXITCODE -ne 0) { throw '영상 화면 캡처 실패' }
    Click-Button '←  감상실'
    $null = Find-Button '오프닝'
    Write-Output '설치본의 기본 WebView2에서 메인 → 영상 → 앙코르 → 오프닝 → 감상실 확인'
}
finally { if (!$process.HasExited) { $null=$process.CloseMainWindow(); $null=$process.WaitForExit(6000) } }
