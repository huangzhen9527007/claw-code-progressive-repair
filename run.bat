@echo off
chcp 65001 >nul

echo Checking environment...
where bun >nul
if errorlevel 1 (
    echo Bun not installed. Get it from: https://bun.sh/
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo Installing dependencies...
    bun install
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file. Please configure API settings.
    )
)

echo Starting Claude Code...
bun run dev

pause