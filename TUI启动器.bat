@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code TUI Launcher (Enhanced)
echo ============================================
echo.
echo [FEATURE] Keeps CMD window open after Ctrl+C
echo [USAGE] Double-click to run, Ctrl+C to stop, window stays open
echo ============================================
echo.

REM Check if Bun is installed
bun --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Bun runtime not found
    echo Please install Bun first: https://bun.sh/
    echo.
    echo [NOTE] Window will stay open - type "exit" to close
    goto :end_without_pause
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
        echo.
        echo [NOTE] Window will stay open - type "exit" to close
        goto :end_without_pause
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

REM Run in development mode
echo ============================================
echo [IMPORTANT INSTRUCTIONS]
echo 1. Claude Code is starting...
echo 2. Press Ctrl+C to STOP the program
echo 3. After Ctrl+C, CMD window will REMAIN OPEN
echo 4. You can then type commands like:
echo    - bun run dev      (to restart Claude Code)
echo    - bun run build    (to build project)
echo    - exit             (to close window)
echo ============================================
echo.

REM Run Claude Code
bun run dev

:end_without_pause
echo.
echo ============================================
echo [INFO] Claude Code has stopped or failed to start
echo [NOTE] CMD window remains open for you to type commands
echo ============================================
echo.
echo [QUICK COMMANDS YOU CAN TYPE NOW]
echo bun run dev      - Start Claude Code again
echo bun run build    - Build the project
echo bun install      - Install dependencies
echo dir              - List files in current directory
echo cls              - Clear the screen
echo exit             - Close this window
echo.
echo [AUTO MEMORY SAVER STATUS]
tasklist | findstr /i "python.exe" >nul
if errorlevel 0 (
    echo [RUNNING] Auto Memory Saver is running in background
    echo [TIP] To stop it: taskkill /F /IM python.exe
) else (
    echo [STOPPED] Auto Memory Saver is not running
)
echo.
echo [READY] Type any command above and press Enter...
