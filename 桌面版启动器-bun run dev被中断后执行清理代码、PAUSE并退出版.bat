@echo off
chcp 65001 >nul
echo Starting Claude Code Desktop...
echo.

REM Get the short path name (8.3 format) to avoid Chinese character issues
for %%I in (.) do set "SHORT_PATH=%%~sI"
echo Using short path: %SHORT_PATH%
echo.

REM Check if Bun is installed
where bun >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Bun is not installed or not in PATH!
    echo Please install Bun from https://bun.sh
    pause
    exit /b 1
)

REM Change to short path directory to avoid path encoding issues
cd /d "%SHORT_PATH%"

REM Check if project dependencies are installed
if not exist "node_modules\" (
    echo Installing dependencies...
    bun install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if desktop directory exists
if not exist "desktop\" (
    echo ERROR: desktop directory not found!
    echo Make sure the project is built correctly.
    pause
    exit /b 1
)

REM Check if main.cjs exists
if not exist "desktop\main.cjs" (
    echo ERROR: main.cjs not found in desktop directory!
    pause
    exit /b 1
)

REM Check if dist/cli.js exists (built version)
if not exist "dist\cli.js" (
    echo Building project...
    bun run build
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build project
        pause
        exit /b 1
    )
)

echo.
echo Launching Electron desktop app...
echo Note: First launch may take a moment to start...
echo.

REM Run desktop version
bun run desktop

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start desktop app
    echo Try running manually: bun run desktop
    echo.
    echo Alternative command to try:
    echo cd desktop ^&^& electron .
)

pause
