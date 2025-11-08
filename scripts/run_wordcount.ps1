param (
    [string]$Url = "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    [int]$Top = 10,
    [int]$Threads = 4,
    [string]$StopWords = "",
    [string]$Figure = "data\output\top_words.png",
    [switch]$NoPlot
)

chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🔄 Запуск MapReduce аналізу тексту..." -ForegroundColor Cyan
$cmd = "python -m src.wordcount_mapreduce.cli --url `"$Url`" --top $Top --threads $Threads --figure `"$Figure`""
if ($StopWords) { $cmd += " --stop-words `"$StopWords`"" }
if ($NoPlot) { $cmd += " --no-plot" }

Write-Host "▶ $cmd" -ForegroundColor Gray
Invoke-Expression $cmd
