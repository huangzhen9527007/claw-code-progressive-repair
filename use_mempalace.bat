@echo off
chcp 65001 >nul
REM 使用 mempalace 的 Windows 脚本

set MEMPA_DIR=mempalace\mempalace

REM 激活虚拟环境
call "%MEMPA_DIR%\venv\Scripts\activate.bat"

REM 执行 mempalace 命令
python -m mempalace %*