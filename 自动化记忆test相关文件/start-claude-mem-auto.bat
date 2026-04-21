@echo off
chcp 65001 >nul
title Claude Code 自动记忆保存器

echo ========================================
echo 🤖 Claude Code 自动记忆保存器
echo 📝 自动监控并保存所有会话到 MemPalace
echo 🔓 超级管理员权限 - 无限制访问
echo ========================================
echo.

REM 设置 Python 编码
set PYTHONIOENCODING=utf-8

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 检查 MemPalace
python -m mempalace --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MemPalace 可能未正确安装
    echo 尝试继续运行...
)

REM 运行自动保存器
echo 🚀 启动自动记忆保存器...
echo.

REM 参数说明：
REM --once        : 只运行一次
REM --continuous  : 持续运行模式
REM --interval 60 : 扫描间隔60秒
REM --max-files 20: 最大处理20个文件

REM 选择运行模式
echo 请选择运行模式：
echo 1. 只运行一次（处理所有未保存的会话）
echo 2. 持续运行模式（每60秒自动扫描）
echo 3. 自定义参数
echo.
set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" (
    echo 📊 模式：只运行一次
    python claude-mem-auto-save.py --once --max-files 50
) else if "%choice%"=="2" (
    echo 🔄 模式：持续运行
    python claude-mem-auto-save.py --continuous --interval 60 --max-files 10
) else if "%choice%"=="3" (
    echo ⚙️  模式：自定义参数
    set /p interval="扫描间隔（秒，默认60）: "
    set /p maxfiles="最大处理文件数（默认20）: "
    if "%interval%"=="" set interval=60
    if "%maxfiles%"=="" set maxfiles=20
    python claude-mem-auto-save.py --continuous --interval %interval% --max-files %maxfiles%
) else (
    echo ❌ 无效选择
)

echo.
echo ========================================
echo 🎉 任务完成！
echo 按任意键退出...
pause >nul