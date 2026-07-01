@echo off
chcp 65001 >nul
echo === ETO Uninstaller ===
echo.

echo [1/3] Unregistering ETO extension...
where pi >nul 2>&1
if not errorlevel 1 (
    pi remove eto/extensions/eto.ts >nul 2>&1
    echo   OK
) else (
    echo   Pi CLI not found, skipping
)

echo [2/3] Removing ETO data...
if exist "%USERPROFILE%\.eto" (
    rmdir /s /q "%USERPROFILE%\.eto" >nul 2>&1
)
if exist "%USERPROFILE%\.pi\etoprofiles" (
    rmdir /s /q "%USERPROFILE%\.pi\etoprofiles" >nul 2>&1
)
if exist "%USERPROFILE%\.pi\eto-config.json" (
    del "%USERPROFILE%\.pi\eto-config.json" >nul 2>&1
)
echo   OK

echo [3/3] Removing cloned repo...
if exist "%~dp0.git" (
    echo   Remove the folder manually: rmdir /s /q "%~dp0"
) else (
    echo   Skipped
)

echo.
echo Done. Pi CLI was kept. Run: npm uninstall -g @earendil-works/pi-coding-agent
pause
