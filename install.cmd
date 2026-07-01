@echo off
chcp 65001 >nul
title ETO Installer v0.1.0

:: 用法:
::   1. git clone https://github.com/reoroy/evolutionary-teal-organization
::   2. cd evolutionary-teal-organization
::   3. set DEEPSEEK_API_KEY=sk-xxx
::   4. install.cmd
::   5. eto
::
:: 一行版（需先在环境变量设好 DEEPSEEK_API_KEY）：
::   iwr https://raw.githubusercontent.com/reoroy/evolutionary-teal-organization/main/install.ps1 | iex

echo === ETO Installer ===
echo.

:: Step 1: Check Node.js
echo [1/4] Checking environment...
where node >nul 2>&1
if errorlevel 1 (
    echo FAIL: Node.js required: https://nodejs.org/
    pause & exit /b 1
)
where python3 >nul 2>&1
if errorlevel 1 (
    echo FAIL: Python 3.10+ required: https://python.org/
    pause & exit /b 1
)
if "%DEEPSEEK_API_KEY%"=="" (
    echo WARN: DEEPSEEK_API_KEY not set. Routing will use keyword fallback.
) else (
    echo OK: DEEPSEEK_API_KEY set
)

:: Step 2: Install Pi CLI
echo.
echo [2/4] Installing Pi CLI...
where pi >nul 2>&1
if errorlevel 1 (
    npm install -g @earendil-works/pi-coding-agent
    if errorlevel 1 ( echo FAIL & pause & exit /b 1 )
)
echo OK

:: Step 3: Register ETO extension
echo.
echo [3/4] Registering ETO extension...
set EXT_PATH=%~dp0eto\extensions\eto.ts
if not exist "%EXT_PATH%" ( echo FAIL: %EXT_PATH% not found & pause & exit /b 1 )
pi install "%EXT_PATH%" >nul 2>&1
if errorlevel 1 ( echo FAIL & pause & exit /b 1 )
echo OK

:: Step 4: Bootstrap
echo.
echo [4/4] Bootstrap...
pip install -e "%~dp0eto" >nul 2>&1
python3 -c "import sys; sys.path.insert(0,'%~dp0'); from eto.bootstrap import run; run()"
echo OK

echo.
echo === Install complete! Run: eto ===
pause
