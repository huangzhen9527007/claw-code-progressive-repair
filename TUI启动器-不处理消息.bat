@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code TUI Launcher
echo ============================================
echo.

REM Check if Bun is installed
where bun >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Bun runtime not found
    echo Please install Bun first: https://bun.sh/
    pause
    exit /b 1
)

echo Checking Bun version...
bun --version
echo.

REM Check if dependencies are installed
if not exist "node_modules" (
    echo WARNING: node_modules directory not found
    echo Installing dependencies...
    bun install
    if %errorlevel% neq 0 (
        echo ERROR: Dependency installation failed
        pause
        exit /b 1
    )
    echo.
)

echo Checking environment configuration...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating .env file from .env.example...
    copy ".env.example" ".env" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Cannot create .env file
        echo Please manually copy .env.example to .env
    )
    echo.
)

echo Starting Claude Code TUI...
echo Note: If you see API errors, check API configuration in .env file
echo ============================================
echo.

REM Run in development mode
bun run dev

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Claude Code startup failed
    echo Possible reasons:
    echo 1. API key not configured - edit .env file
    echo 2. Network issue - check your connection
    echo 3. Dependency problem - try running bun install
    echo ============================================
)

pause
