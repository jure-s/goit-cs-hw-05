param (
    [string]$Src = "data\sample_input",
    [string]$Dst = "data\output",
    [int]$Workers = 50,
    [switch]$DryRun,
    [string]$LogLevel = "INFO"
)

chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🔄 Запуск асинхронного сортування..." -ForegroundColor Cyan
$cmd = "python -m src.sorter_async.cli --src `"$Src`" --dst `"$Dst`" --workers $Workers --log-level $LogLevel"
if ($DryRun) { $cmd += " --dry-run" }

Write-Host "▶ $cmd" -ForegroundColor Gray
Invoke-Expression $cmd
