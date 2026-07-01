#!/usr/bin/env pwsh
# ETO Uninstaller — 一键卸载
$GH_REPO = "https://github.com/reoroy/evolutionary-teal-organization"
$target = Join-Path $env:USERPROFILE "eto"

Write-Host "`n=== ETO Uninstaller ===`n" -ForegroundColor Cyan

# Step 1: Unregister extension
Write-Host "[1/3] Unregistering ETO extension..." -ForegroundColor Cyan
try {
    $null = Get-Command pi -ErrorAction Stop
    $list = pi list 2>&1
    if ($list -match "eto.ts") {
        pi remove eto/extensions/eto.ts 2>&1 | Out-Null
        Write-Host "  Extension removed" -ForegroundColor Green
    } else {
        Write-Host "  Not registered" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Pi CLI not found, skipping" -ForegroundColor Gray
}

# Step 2: Remove bootstrap data
Write-Host "[2/3] Removing ETO data..." -ForegroundColor Cyan
$paths = @(
    Join-Path $env:USERPROFILE ".eto"
    Join-Path $env:USERPROFILE ".pi\etoprofiles"
    Join-Path $env:USERPROFILE ".pi\eto-config.json"
)
foreach ($p in $paths) {
    if (Test-Path $p) {
        Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed $p" -ForegroundColor Gray
    }
}
Write-Host "  Done" -ForegroundColor Green

# Step 3: Remove cloned repo
Write-Host "[3/3] Removing cloned repo..." -ForegroundColor Cyan
if (Test-Path $target) {
    Remove-Item -Path $target -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Removed $target" -ForegroundColor Gray
}
Write-Host "  Done" -ForegroundColor Green

Write-Host ""
Write-Host "  Uninstall complete." -ForegroundColor Green
Write-Host "  Note: Pi CLI was not removed. Run: npm uninstall -g @earendil-works/pi-coding-agent" -ForegroundColor Gray
