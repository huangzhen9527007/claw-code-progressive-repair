@echo off
chcp 65001 > nul
echo ========================================
echo Memory Tools - UTF-8 Mode
echo 记忆工具 - UTF-8模式
echo ========================================
echo.
echo Setting console to UTF-8 encoding...
echo 设置控制台编码为UTF-8...
echo.
echo Running memory tools with UTF-8 support...
echo 运行记忆工具（支持UTF-8）...
echo.

REM 设置Python编码环境变量
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 运行主程序
python main.py %*

REM 恢复原始代码页（如果需要）
REM chcp 936 > nul