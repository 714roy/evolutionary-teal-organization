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
if exist "%USERPROFILE%\.git" (
    echo Already cloned
) else (
    git clone https://github.com/reoroy/evolutionary-teal-organization "%USERPROFILE%\eto"
)
echo OK

echo [3/3] Registering ETO extension...
pi install "%USERPROFILE%\eto\eto\extensions\eto.ts"
echo OK

echo.
echo Done! Run: pi
pause
