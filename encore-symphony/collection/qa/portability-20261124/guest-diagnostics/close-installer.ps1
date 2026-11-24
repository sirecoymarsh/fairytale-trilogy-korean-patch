if($env:USERNAME -ne 'WDAGUtilityAccount'){return}
Get-Process MicrosoftEdgeUpdate -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like '*WebView2*' -and $_.MainWindowHandle -ne [intptr]::Zero} | ForEach-Object { [void]$_.CloseMainWindow() }
