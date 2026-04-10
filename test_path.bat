@echo off
chcp 65001 >nul
echo Testing path resolution...
echo.

echo Current directory: %CD%
echo.

REM Get short path
for %%I in (.) do set "SHORT_PATH=%%~sI"
echo Short path: %SHORT_PATH%
echo.

REM Test if desktop directory exists
if exist "desktop\" (
    echo ✓ desktop directory exists
) else (
    echo ✗ desktop directory not found
)

echo.
echo Testing Electron path...
echo.

REM Try to run electron with explicit path
if exist "desktop\main.cjs" (
    echo ✓ desktop/main.cjs exists
    echo.
    echo Trying to run: electron desktop/main.cjs
    electron desktop/main.cjs
) else (
    echo ✗ desktop/main.cjs not found
)

echo.
pause