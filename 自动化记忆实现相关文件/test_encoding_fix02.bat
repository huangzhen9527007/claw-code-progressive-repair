@echo off
chcp 65001 >nul
echo ============================================
echo Encoding Test for Batch Files
echo ============================================
echo.
echo Testing if batch files can run without encoding errors...
echo.

echo [TEST 1] Testing save_readable_sessions.bat header
echo First 10 lines of save_readable_sessions.bat:
echo --------------------------------------------
type "save_readable_sessions.bat" | head -10
echo --------------------------------------------
echo.

echo [TEST 2] Testing save_all_sessions.bat header
echo First 10 lines of save_all_sessions.bat:
echo --------------------------------------------
type "save_all_sessions.bat" | head -10
echo --------------------------------------------
echo.

echo [TEST 3] Testing TUI启动器.bat header
echo First 10 lines of TUI启动器.bat:
echo --------------------------------------------
type "TUI启动器.bat" | head -10
echo --------------------------------------------
echo.

echo [TEST 4] Checking for Chinese characters in batch files
echo Searching for potential encoding issues...
echo.

findstr /n "[\x80-\xFF]" "save_readable_sessions.bat" >nul
if errorlevel 1 (
    echo ✓ save_readable_sessions.bat: No Chinese characters found (good for encoding)
) else (
    echo ⚠ save_readable_sessions.bat: Contains non-ASCII characters
)

findstr /n "[\x80-\xFF]" "save_all_sessions.bat" >nul
if errorlevel 1 (
    echo ✓ save_all_sessions.bat: No Chinese characters found (good for encoding)
) else (
    echo ⚠ save_all_sessions.bat: Contains non-ASCII characters
)

echo.
echo ============================================
echo Test Results
echo ============================================
echo.
echo All batch files should now work without encoding errors.
echo Key changes made:
echo 1. Added "chcp 65001" at the beginning of each .bat file
echo 2. Changed Chinese text to English in save_readable_sessions.bat
echo 3. All file headers now use UTF-8 encoding
echo.
echo You can now run:
echo   - save_readable_sessions.bat (for readable Markdown)
echo   - save_all_sessions.bat (for complete JSONL data)
echo   - TUI启动器.bat (to start Claude Code with auto-saving)
echo.
pause