#!/usr/bin/env pwsh
# ETO Installer — 仅安装 ETO 插件，不碰系统配置
$ErrorActionPreference = "Stop"
$GH_REPO = "https://github.com/reoroy/evolutionary-teal-organization"

Write-Host "`n=== ETO Plugin Installer ===`n" -ForegroundColor Cyan

Write-Host "[1/3] Checking Pi CLI..." -ForegroundColor Cyan
try { Get-Command pi -ErrorAction Stop | Out-Null } catch {
    Write-Host "  FAIL: Pi CLI not found." -ForegroundColor Red
    Write-Host "  Install Pi first: npm install -g @earendil-works/pi-coding-agent" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK" -ForegroundColor Green

Write-Host "[2/3] Cloning ETO..." -ForegroundColor Cyan
$target = Join-Path $env:USERPROFILE "eto"
if (Test-Path "$target\.git") {
    Write-Host "  Already cloned at $target" -ForegroundColor Gray
} else {
    git clone $GH_REPO $target 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: git clone failed" -ForegroundColor Red; exit 1 }
    Write-Host "  OK" -ForegroundColor Green
}

Write-Host "[3/3] Registering ETO extension..." -ForegroundColor Cyan
pi install "$target\eto\extensions\eto.ts" 2>&1 | Out-Null
Write-Host "  OK" -ForegroundColor Green

Write-Host ""
Write-Host "  Done! Run: pi" -ForegroundColor Green
Write-Host "  (ETO extension auto-loads. Configure provider via pi login or --provider)" -ForegroundColor Gray
