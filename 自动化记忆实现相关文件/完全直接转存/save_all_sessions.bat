@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code Session Save Tool (Complete)
echo ============================================
echo.
echo [INFO] Saving Claude Code sessions with 100% complete data
echo [INFO] No information loss - 100%% complete raw data
echo [NOTE] This tool processes ALL files by default
echo [TIP] Use --max-files parameter to limit processing
echo.
echo [WARNING] This will create large files
echo [WARNING] Each session ~0.5-1MB, total may be 50-100MB
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo [TIP] Please install Python or add it to PATH
    pause
    exit /b 1
)

REM Check script
if not exist "claude-complete-session-saver.py" (
    echo [ERROR] claude-complete-session-saver.py not found
    pause
    exit /b 1
)

echo [QUESTION] Processing options:
echo.
echo 1. Quick test (first 5 files)
echo 2. Standard (first 20 files)
echo 3. All files (may take time) [RECOMMENDED]
echo.
echo Default is option 3 (ALL files)
echo Starting in 5 seconds...
timeout /t 5 /nobreak >nul

REM Default to option 3 (ALL files)
set option=3

echo.
echo ============================================
echo [START] Starting session processing...
echo ============================================
echo.

if "%option%"=="1" (
    echo [MODE] Quick test mode - first 5 files
    python claude-complete-session-saver.py --max-files 5
) else if "%option%"=="2" (
    echo [MODE] Standard mode - first 20 files
    python claude-complete-session-saver.py --max-files 20
) else if "%option%"=="3" (
    echo [MODE] Complete mode - all files
    python claude-complete-session-saver.py
) else (
    echo [ERROR] Invalid option
    pause
    exit /b 1
)

echo.
echo ============================================
echo [COMPLETE] Processing complete!
echo ============================================
echo.
echo [INFO] All 100% complete session data saved to:
echo [PATH] C:\Users\Administrator\.mempalace\palace\claude_sessions\complete_sessions
echo.
echo [TIP] Check the directory for:
echo       1. Complete session files (*.md)
echo       2. Session summary file
echo.
pause