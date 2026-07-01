#!/usr/bin/env pwsh
# ETO Installer — 一行命令安装
# 用法（需要先配好 DEEPSEEK_API_KEY）:
#   iwr https://raw.githubusercontent.com/reoroy/evolutionary-teal-organization/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$GH_REPO = "https://github.com/reoroy/evolutionary-teal-organization"

function Step($n, $msg) { Write-Host "`n[$n/4] $msg" -ForegroundColor Cyan }
function Ok  { Write-Host "  OK" -ForegroundColor Green }
function Warn($m) { Write-Host "  WARN: $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "  FAIL: $m" -ForegroundColor Red; exit 1 }

# Step 1: Check environment
Step 1 "Checking environment..."
try { $null = Get-Command node -ErrorAction Stop; Ok() } catch { Fail("Node.js required") }
try { $null = Get-Command python3 -ErrorAction Stop; Ok() } catch { Fail("Python 3.10+ required") }
if ($env:DEEPSEEK_API_KEY) { Ok() } else { Warn("DEEPSEEK_API_KEY not set") }

# Step 2: Clone repo
Step 2 "Cloning ETO..."
$target = Join-Path $env:USERPROFILE "eto"
if (Test-Path "$target\.git") {
    Write-Host "  Already cloned at $target"
} else {
    git clone $GH_REPO $target 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail("git clone failed") }
    Ok()
}
Set-Location $target

# Step 3: Install Pi CLI + register extension
Step 3 "Installing Pi CLI and ETO extension..."
$null = Get-Command pi -ErrorAction SilentlyContinue
if ($LASTEXITCODE -ne 0) {
    npm install -g @earendil-works/pi-coding-agent 2>&1 | Out-Null
}
pi install "$target\eto\extensions\eto.ts" 2>&1 | Out-Null
Ok()

# Step 4: Python package + Bootstrap
Step 4 "Bootstrap..."
pip install -e "$target\eto" 2>&1 | Out-Null
python3 -c "import sys; sys.path.insert(0,'$target'); from eto.bootstrap import run; run()" 2>&1 | Out-Null
Ok()

Write-Host ""
Write-Host "  Done! Run: eto" -ForegroundColor Green
Write-Host "  Or:   cd $target && pi -p ""写个API""" -ForegroundColor Gray
