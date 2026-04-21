@echo off
REM Claude Code wrapper for claude-mem plugin
REM This file makes the built cli.js executable appear as claude.cmd

setlocal

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "CLAUDE_JS=%SCRIPT_DIR%dist\cli.js"

REM Check if the built file exists
if not exist "%CLAUDE_JS%" (
    echo Error: cli.js not found at %CLAUDE_JS%
    echo Please run: bun run build
    exit /b 1
)

REM Run the built cli.js with bun
bun "%CLAUDE_JS%" %*