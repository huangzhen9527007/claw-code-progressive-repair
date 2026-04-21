@echo off
chcp 65001 > nul
title Memory Tools Interactive Menu - 记忆工具交互式菜单

:menu
cls
echo ========================================
echo        MEMORY TOOLS INTERACTIVE MENU
echo        记忆工具交互式菜单
echo ========================================
echo.
echo Please select an option:
echo 请选择选项：
echo.
echo 1. Basic memory system check - 基本记忆系统检查
echo 2. Full diagnostic report - 完整诊断报告
echo 3. Classification issues report - 分类问题报告
echo 4. Preview fix plan (dry run) - 预览修复计划（试运行）
echo 5. Execute fixes (with confirmation) - 执行修复（需确认）
echo 6. Check for unindexed files - 检查未索引文件
echo 7. Check for extra indexes - 检查多余索引
echo 8. Check for duplicate indexes - 检查重复索引
echo 9. Run custom command - 运行自定义命令
echo 0. Exit - 退出
echo.
set /p choice="Enter your choice (0-9): 输入您的选择 (0-9): "

if "%choice%"=="1" goto check
if "%choice%"=="2" goto report
if "%choice%"=="3" goto classify
if "%choice%"=="4" goto fix_dry
if "%choice%"=="5" goto fix_execute
if "%choice%"=="6" goto unindexed
if "%choice%"=="7" goto extra
if "%choice%"=="8" goto duplicate
if "%choice%"=="9" goto custom
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
echo 无效选择，请重试。
pause
goto menu

:check
echo.
echo Running basic memory system check...
echo 运行基本记忆系统检查...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py check
pause
goto menu

:report
echo.
echo Running full diagnostic report...
echo 运行完整诊断报告...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py report
pause
goto menu

:classify
echo.
echo Running classification issues report...
echo 运行分类问题报告...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py classify
pause
goto menu

:fix_dry
echo.
echo Previewing fix plan (dry run)...
echo 预览修复计划（试运行）...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py fix --dry-run
pause
goto menu

:fix_execute
echo.
echo WARNING: This will modify your memory system!
echo 警告：这将修改您的记忆系统！
echo.
set /p confirm="Are you sure? Type 'yes' to continue: 确定吗？输入'yes'继续: "
if not "%confirm%"=="yes" (
    echo Operation cancelled. - 操作已取消
    pause
    goto menu
)
echo.
echo Executing fixes...
echo 执行修复...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py fix --execute
pause
goto menu

:unindexed
echo.
echo Checking for unindexed files...
echo 检查未索引文件...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python -c "
import sys
sys.path.insert(0, '.')
from src.memory_tools import MemoryTools
tools = MemoryTools()
unindexed = tools.find_unindexed_files()
if unindexed:
    print(f'Found {len(unindexed)} unindexed files - 发现 {len(unindexed)} 个未索引文件:')
    for i, f in enumerate(unindexed[:10], 1):
        print(f'  {i}. {f}')
    if len(unindexed) > 10:
        print(f'  ... and {len(unindexed) - 10} more - 还有 {len(unindexed) - 10} 个')
else:
    print('No unindexed files found - 未发现未索引文件')
"
pause
goto menu

:extra
echo.
echo Checking for extra indexes...
echo 检查多余索引...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python -c "
import sys
sys.path.insert(0, '.')
from src.memory_tools import MemoryTools
tools = MemoryTools()
extra = tools.find_extra_indexes()
if extra:
    print(f'Found {len(extra)} extra indexes - 发现 {len(extra)} 个多余索引:')
    for i, f in enumerate(extra[:10], 1):
        print(f'  {i}. {f}')
    if len(extra) > 10:
        print(f'  ... and {len(extra) - 10} more - 还有 {len(extra) - 10} 个')
else:
    print('No extra indexes found - 未发现多余索引')
"
pause
goto menu

:duplicate
echo.
echo Checking for duplicate indexes...
echo 检查重复索引...
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python -c "
import sys
sys.path.insert(0, '.')
from src.memory_tools import MemoryTools
tools = MemoryTools()
duplicates = tools.find_duplicate_indexes()
if duplicates:
    print(f'Found {len(duplicates)} duplicate indexes - 发现 {len(duplicates)} 个重复索引:')
    for i, (f, count) in enumerate(list(duplicates.items())[:10], 1):
        print(f'  {i}. {f} (appears {count} times) - (出现 {count} 次)')
    if len(duplicates) > 10:
        print(f'  ... and {len(duplicates) - 10} more - 还有 {len(duplicates) - 10} 个')
else:
    print('No duplicate indexes found - 未发现重复索引')
"
pause
goto menu

:custom
echo.
echo Enter custom command (e.g., "check --json"):
echo 输入自定义命令（例如："check --json"）:
echo.
set /p custom_cmd="Command: 命令: "
echo.
echo Running: python main.py %custom_cmd%
echo 运行: python main.py %custom_cmd%
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python main.py %custom_cmd%
pause
goto menu

:exit
echo.
echo Thank you for using Memory Tools!
echo 感谢使用记忆工具！
echo.
pause
exit