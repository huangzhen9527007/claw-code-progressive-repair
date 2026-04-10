@echo off
chcp 65001 >nul
echo Starting Claude Code...

REM Simple check for bun
where bun >nul 2>&1
if %errorlevel% neq 0 (
    echo Bun not found. Please install Bun from https://bun.sh/
    pause
    exit /b 1
)

REM Create .env if missing
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo Created .env file from .env.example
        echo Please edit .env to configure API settings
        echo.
    )
)

REM Run the app
bun run dev

if %errorlevel% neq 0 (
    echo.
    echo Startup failed. Common issues:
    echo 1. Run "bun install" to install dependencies
    echo 2. Check API configuration in .env file
    echo 3. Make sure your API service is running
)

pause