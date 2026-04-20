@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code TUI Launcher (Keep Window Open)
echo ============================================
echo.
echo [DESIGN] This launcher keeps CMD window open after Ctrl+C
echo [USAGE] Press Ctrl+C to stop Claude Code, then type commands
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
echo ============================================
echo [IMPORTANT INSTRUCTIONS]
echo 1. Press Ctrl+C to STOP Claude Code
echo 2. After Ctrl+C, CMD window will REMAIN OPEN
echo 3. You can then type commands like:
echo    - bun run dev      (restart Claude Code)
echo    - bun run build    (build project)
echo    - exit             (close window)
echo ============================================
echo.

REM The key trick: Use cmd /k to keep window open
echo [LAUNCHING] Starting Claude Code...
echo [NOTE] After Ctrl+C, you'll return to command prompt
echo.

REM Run Claude Code
bun run dev

echo.
echo ============================================
echo [INFO] Claude Code has stopped
echo [NOTE] CMD window remains open - you can type commands
echo ============================================
echo.
echo [QUICK COMMANDS]
echo bun run dev      - Restart Claude Code
echo bun run build    - Build project
echo dir              - List files
echo cls              - Clear screen
echo exit             - Close this window
echo.
echo [AUTO MEMORY SAVER STATUS]
tasklist | findstr /i "python.exe" >nul
if errorlevel 0 (
    echo [RUNNING] Auto Memory Saver is still running in background
    echo [TIP] To stop it: taskkill /F /IM python.exe
) else (
    echo [STOPPED] Auto Memory Saver is not running
)
echo.
echo [READY] Type any command and press Enter...