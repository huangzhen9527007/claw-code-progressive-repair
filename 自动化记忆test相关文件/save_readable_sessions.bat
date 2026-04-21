@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code Readable Session Save Tool
echo ============================================
echo.
echo [INFO] Convert JSONL sessions to readable Markdown format
echo [INFO] Structured conversation records with statistics and formatted content
echo [NOTE] This tool processes all files to generate readable versions
echo.
echo [FEATURES] Features:
echo           1. Structured conversation records
echo           2. Statistics tables
echo           3. Formatted message content
echo           4. Tool call display
echo           5. Token usage statistics
echo.
echo [WARNING] This will generate readable versions based on original files
echo [WARNING] File name format: original_filename_readable.md
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
if not exist "claude-readable-session-saver.py" (
    echo [ERROR] claude-readable-session-saver.py not found
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
    python claude-readable-session-saver.py --max-files 5
) else if "%option%"=="2" (
    echo [MODE] Standard mode - first 20 files
    python claude-readable-session-saver.py --max-files 20
) else if "%option%"=="3" (
    echo [MODE] Complete mode - all files
    python claude-readable-session-saver.py
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
echo [INFO] All readable session data saved to:
echo [PATH] C:\Users\Administrator\.mempalace\palace\claude_sessions\readable_sessions
echo.
echo [TIP] Check directory for:
echo       1. Readable session files (*_readable.md)
echo       2. Structured conversation records
echo       3. Statistics tables
echo.
echo [COMPARE] Compare with original version:
echo       Original: Complete JSONL data (claude-complete-session-saver.py)
echo       Readable: Structured Markdown (claude-readable-session-saver.py)
echo.
pause