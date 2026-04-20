@echo off
REM 测试中文编码的简单脚本

echo ============================================
echo 测试1: 默认编码
echo ============================================
echo 中文测试 - 默认编码
echo 当前代码页:
chcp
echo.

echo ============================================
echo 测试2: UTF-8编码 (chcp 65001)
echo ============================================
chcp 65001 >nul
echo 中文测试 - UTF-8编码
echo 当前代码页:
chcp
echo.

echo ============================================
echo 测试3: 检查系统区域设置
echo ============================================
echo 系统区域设置:
wmic os get locale
echo.

echo ============================================
echo 测试4: 注册表中的代码页设置
echo ============================================
echo 注册表中的代码页:
reg query "HKCU\Console" /v CodePage 2>nul || echo 未设置
echo.

echo ============================================
echo 测试5: 字体设置
echo ============================================
echo 控制台字体:
reg query "HKCU\Console" /v FaceName 2>nul || echo 未设置
echo.

echo ============================================
echo [建议解决方案]
echo ============================================
echo 1. 使用 chcp 65001 设置UTF-8编码
echo 2. 修改注册表永久设置:
echo    reg add "HKCU\Console" /v CodePage /t REG_DWORD /d 65001 /f
echo 3. 设置支持UTF-8的字体:
echo    reg add "HKCU\Console" /v FaceName /t REG_SZ /d "MS Gothic" /f
echo 4. 使用PowerShell启动CMD
echo.

pause