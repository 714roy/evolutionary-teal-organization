@echo off
chcp 65001 >nul

echo === ETO Plugin Installer ===
echo.

echo [1/3] Checking Pi CLI...
where pi >nul 2>&1
if errorlevel 1 (
    echo FAIL: Pi CLI not found.
    echo Install Pi first: npm install -g @earendil-works/pi-coding-agent
    pause & exit /b 1
)
echo OK

echo [2/3] Cloning ETO...
set "ETO_DIR=%USERPROFILE%\eto"
if exist "%ETO_DIR%\.git" (
    echo Already cloned at %ETO_DIR%
) else (
    git clone https://github.com/reoroy/evolutionary-teal-organization "%ETO_DIR%" >nul 2>&1
    if errorlevel 1 (echo FAIL: git clone failed; pause & exit /b 1)
    echo OK
)

echo [3/3] Registering ETO extension...
pi install "%ETO_DIR%\eto\extensions\eto.ts" >nul 2>&1
if errorlevel 1 (echo FAIL: pi install failed; pause & exit /b 1)
echo OK

echo.
echo Done! Run: pi
