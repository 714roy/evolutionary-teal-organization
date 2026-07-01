#!/usr/bin/env pwsh
# ETO Uninstaller — iex 兼容版
$target = Join-Path $env:USERPROFILE "eto"
$npmDir = Join-Path $env:APPDATA "npm"

Write-Host "`n=== ETO Uninstaller ===`n" -ForegroundColor Cyan

Write-Host "[1/3] Unregistering ETO extension..." -ForegroundColor Cyan
try { Get-Command pi -ErrorAction Stop | Out-Null; pi remove eto/extensions/eto.ts 2>&1 | Out-Null; Write-Host "  Extension removed" -ForegroundColor Green } catch { Write-Host "  Skipped" -ForegroundColor Gray }

Write-Host "[2/3] Removing ETO data..." -ForegroundColor Cyan
foreach ($p in @((Join-Path $env:USERPROFILE ".eto"), (Join-Path $env:USERPROFILE ".pi\etoprofiles"), (Join-Path $env:USERPROFILE ".pi\eto-config.json"))) {
    if (Test-Path $p) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue }
}
foreach ($f in @("eto.ps1", "eto.cmd")) { $p = Join-Path $npmDir $f; if (Test-Path $p) { Remove-Item $p -Force } }
Write-Host "  OK" -ForegroundColor Green

Write-Host "[3/3] Removing cloned repo..." -ForegroundColor Cyan
if (Test-Path $target) { Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "  Removed $target" -ForegroundColor Gray }
Write-Host "  OK" -ForegroundColor Green

Write-Host "`n  Uninstall complete." -ForegroundColor Green
Write-Host "  Pi CLI was not removed. Run: npm uninstall -g @earendil-works/pi-coding-agent" -ForegroundColor Gray
