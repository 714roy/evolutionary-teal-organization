#!/usr/bin/env pwsh
# ETO Installer — iex 兼容版
$ErrorActionPreference = "Stop"
$GH_REPO = "https://github.com/reoroy/evolutionary-teal-organization"

Write-Host "`n=== ETO Installer ===`n" -ForegroundColor Cyan

# 1. Check environment
Write-Host "[1/4] Checking environment..." -ForegroundColor Cyan
$ok = $true
try { Get-Command node -ErrorAction Stop | Out-Null } catch { Write-Host "  FAIL: Node.js required" -ForegroundColor Red; $ok = $false }
try { Get-Command python3 -ErrorAction Stop | Out-Null } catch { Write-Host "  FAIL: Python 3.10+ required" -ForegroundColor Red; $ok = $false }
if (-not $env:DEEPSEEK_API_KEY) { Write-Host "  WARN: DEEPSEEK_API_KEY not set" -ForegroundColor Yellow }
if (-not $ok) { exit 1 }
Write-Host "  OK" -ForegroundColor Green

# 2. Clone
Write-Host "[2/4] Cloning ETO..." -ForegroundColor Cyan
$target = Join-Path $env:USERPROFILE "eto"
if (Test-Path "$target\.git") {
    Write-Host "  Already cloned at $target" -ForegroundColor Gray
} else {
    git clone $GH_REPO $target 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: git clone failed" -ForegroundColor Red; exit 1 }
    Write-Host "  OK" -ForegroundColor Green
}
Set-Location $target

# 3. Pi CLI + extension
Write-Host "[3/4] Installing Pi CLI and extension..." -ForegroundColor Cyan
try { Get-Command pi -ErrorAction Stop | Out-Null } catch { npm install -g @earendil-works/pi-coding-agent 2>&1 | Out-Null }
pi install "$target\eto\extensions\eto.ts" 2>&1 | Out-Null
Write-Host "  OK" -ForegroundColor Green

# 4. Bootstrap
Write-Host "[4/4] Bootstrap..." -ForegroundColor Cyan
pip install -e "$target\eto" 2>&1 | Out-Null
python3 -c "import sys; sys.path.insert(0,'$target'); from eto.bootstrap import run; run()" 2>&1 | Out-Null
Write-Host "  OK" -ForegroundColor Green

Write-Host ""
Write-Host "  Done! Run: eto" -ForegroundColor Green
