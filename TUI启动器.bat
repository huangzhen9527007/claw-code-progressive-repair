@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code TUI Launcher
echo ============================================
echo.

REM Check if Bun is installed
bun --version >nul 2>&1
if errorlevel 1 (
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
    if errorlevel 1 (
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
    if errorlevel 1 (
        echo ERROR: Cannot create .env file
        echo Please manually copy .env.example to .env
    )
    echo.
)

echo Starting Claude Code TUI...
echo Note: If you see API errors, check API configuration in .env file
echo ============================================
echo.

REM Start Auto Memory Saver in background
echo [INFO] Starting Auto Memory Saver (background)...
echo [NOTE] This service saves your conversations to MemPalace every 5 minutes
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found. Auto Memory Saver will not start.
    echo [TIP] Install Python or add it to PATH to enable automatic memory saving.
    goto :skip_python_check
)

	REM Start Readable Session Saver if script exists
	if exist "claude-readable-session-saver.py" (
	    start /B python claude-readable-session-saver.py --max-files 10
	    echo [OK] Readable Session Saver started (structured readable mode)
	    echo [INFO] Latest 10 sessions readable data will be saved to MemPalace
	)

:skip_python_check
echo.

REM Run in development mode with interactive prompt
echo.
echo [TIP] Type your query and press Enter to start, or press Ctrl+C to exit
echo.
bun run dev

if errorlevel 1 (
    echo.
    echo ============================================
    echo Claude Code startup failed
    echo Possible reasons:
    echo 1. API key not configured - edit .env file
    echo 2. Network issue - check your connection
    echo 3. Dependency problem - try running bun install
    echo ============================================
)

echo.
echo ============================================
echo [INFO] Claude Code closed. Cleaning up...

REM Stop Auto Memory Saver if it was started
tasklist | findstr /i "python.exe" >nul
if errorlevel 0 (
    echo [INFO] Stopping Auto Memory Saver...
    taskkill /F /IM python.exe /T >nul 2>&1
    echo [OK] Auto Memory Saver stopped
) else (
    echo [INFO] No Auto Memory Saver process found
)

echo ============================================
echo [SUMMARY]
echo 1. Claude Code session ended
echo 2. Auto Memory Saver stopped (if running)
echo 3. Your conversations are saved in MemPalace
echo ============================================
pause
