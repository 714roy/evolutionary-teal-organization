#!/usr/bin/env pwsh
# ETO Uninstaller — 仅移除 ETO 插件
Write-Host "`n=== ETO Plugin Uninstaller ===`n" -ForegroundColor Cyan

Write-Host "[1/2] Unregistering ETO extension..." -ForegroundColor Cyan
try { Get-Command pi -ErrorAction Stop | Out-Null } catch { Write-Host "  Pi CLI not found, skipping" -ForegroundColor Gray; exit 0 }
pi remove eto/extensions/eto.ts 2>&1 | Out-Null
Write-Host "  OK" -ForegroundColor Green

Write-Host "[2/2] Removing cloned repo and wrapper..." -ForegroundColor Cyan
$target = Join-Path $env:USERPROFILE "eto"
if (Test-Path $target) { Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "  Removed $target" -ForegroundColor Gray }
$npmDir = Join-Path $env:APPDATA "npm"
foreach ($f in @("eto.ps1", "eto.cmd")) {
    $p = Join-Path $npmDir $f
    if (Test-Path $p) { Remove-Item $p -Force; Write-Host "  Removed npm\$f" -ForegroundColor Gray }
}
Write-Host "  OK" -ForegroundColor Green

Write-Host "`n  Done." -ForegroundColor Green
