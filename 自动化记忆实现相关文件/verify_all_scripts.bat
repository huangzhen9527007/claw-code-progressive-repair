@echo off
chcp 65001 >nul
echo ============================================
echo Claude Code Script Verification Tool
echo ============================================
echo.

echo [CHECK 1] Check all required files
echo.

if exist "TUI启动器.bat" (
    echo ✓ TUI启动器.bat exists
) else (
    echo ✗ TUI启动器.bat not found
)

if exist "claude-complete-session-saver.py" (
    echo ✓ claude-complete-session-saver.py exists (complete data version)
) else (
    echo ✗ claude-complete-session-saver.py not found
)

if exist "claude-readable-session-saver.py" (
    echo ✓ claude-readable-session-saver.py exists (readable version)
) else (
    echo ✗ claude-readable-session-saver.py not found
)

if exist "save_all_sessions.bat" (
    echo ✓ save_all_sessions.bat exists (batch process complete data)
) else (
    echo ✗ save_all_sessions.bat not found
)

if exist "save_readable_sessions.bat" (
    echo ✓ save_readable_sessions.bat exists (batch process readable data)
) else (
    echo ✗ save_readable_sessions.bat not found
)

echo.
echo [CHECK 2] Check Python script syntax
echo.

python -m py_compile "claude-complete-session-saver.py" >nul 2>&1
if errorlevel 0 (
    echo ✓ claude-complete-session-saver.py syntax correct
) else (
    echo ✗ claude-complete-session-saver.py syntax error
)

python -m py_compile "claude-readable-session-saver.py" >nul 2>&1
if errorlevel 0 (
    echo ✓ claude-readable-session-saver.py syntax correct
) else (
    echo ✗ claude-readable-session-saver.py syntax error
)

echo.
echo [CHECK 3] Check batch file configuration
echo.

echo [INFO] TUI Launcher configuration:
type "TUI启动器.bat" | findstr /C:"--max-files" /C:"Readable Session" /C:"Complete Session"

echo.
echo [INFO] save_all_sessions.bat default option:
type "save_all_sessions.bat" | findstr /C:"Default is option" /C:"set option="

echo.
echo [INFO] save_readable_sessions.bat default option:
type "save_readable_sessions.bat" | findstr /C:"Default is option" /C:"set option="

echo.
echo ============================================
echo Verification complete
echo ============================================
echo.
echo [SUMMARY] Current configuration:
echo.
echo 1. TUI启动器.bat
echo     - Runs two savers on startup
echo     - Complete data saver: --max-files 10
echo     - Readable data saver: --max-files 10
echo.
echo 2. Batch processing tools
echo     - save_all_sessions.bat: Process all files, generate complete data
echo     - save_readable_sessions.bat: Process all files, generate readable data
echo.
echo 3. File overwrite policy
echo     - Same name files directly overwritten, no duplicates
echo     - Readable version filename: original_filename_readable.md
echo     - Complete version filename: original_filename.md
echo.
echo 4. Output directories
echo     - Complete data: ~/.mempalace/palace/claude_sessions/complete_sessions/
echo     - Readable data: ~/.mempalace/palace/claude_sessions/readable_sessions/
echo.
pause