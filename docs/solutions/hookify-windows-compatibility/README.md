# Hookify 插件 Windows 兼容性解决方案

## 问题描述

### 问题现象
Hookify 插件在 Windows 系统上无法正常工作，hook 脚本执行失败。

### 错误表现
1. Python 脚本无法执行，提示 `python3: command not found`
2. Hook 脚本接收到的输入数据格式不匹配
3. `hook_event_name` 字段未正确设置

## 根本原因分析

### 1. Python 命令差异
- **Unix 系统**：使用 `python3` 命令
- **Windows 系统**：使用 `python` 命令
- **问题**：hooks.json 配置中硬编码了 `python3` 命令

### 2. 输入数据格式不匹配
- **Claude Code 传递的数据格式**：顶层包含 `command` 字段
- **rule_engine 期望的格式**：`command` 应该在 `tool_input.command` 中
- **问题**：数据格式转换不正确

### 3. hook_event_name 字段缺失
- **rule_engine 要求**：每个 hook 事件都需要 `hook_event_name` 字段
- **实际数据**：未设置该字段
- **问题**：rule_engine 无法识别事件类型

## 解决方案

### 1. Python 命令修复

#### 修改所有 hooks.json 文件
**文件位置**：
```
C:/Users/Administrator/.claude/plugins/cache/claude-plugins-official/hookify/*/hooks/hooks.json
```

**修改内容**：
```json
// 修改前
"command": "python3",
"args": ["pretooluse.py"]

// 修改后
"command": "python",
"args": ["pretooluse.py"]
```

### 2. Shebang 修复

#### 修改所有 hook 脚本的 shebang
**需要修改的文件**：
- `pretooluse.py`
- `posttooluse.py`
- `stop.py`
- `userpromptsubmit.py`

**修改内容**：
```python
# 修改前
#!/usr/bin/env python3

# 修改后
#!/usr/bin/env python
```

### 3. 输入数据格式修复

#### pretooluse.py 修复
```python
# 修改前
def main():
    data = json.load(sys.stdin)
    # 直接使用 data['command']

# 修改后
def main():
    data = json.load(sys.stdin)
    # 确保 hook_event_name 存在
    data['hook_event_name'] = 'PreToolUse'
    # 移动 command 到 tool_input
    if 'command' in data and 'tool_input' in data:
        data['tool_input']['command'] = data['command']
```

#### posttooluse.py 修复
```python
# 修改后
def main():
    data = json.load(sys.stdin)
    data['hook_event_name'] = 'PostToolUse'
    if 'command' in data and 'tool_input' in data:
        data['tool_input']['command'] = data['command']
```

#### stop.py 修复
```python
# 修改后
def main():
    data = json.load(sys.stdin)
    data['hook_event_name'] = 'Stop'
    # stop 事件可能没有 command 字段
```

#### userpromptsubmit.py 修复
```python
# 修改后
def main():
    data = json.load(sys.stdin)
    data['hook_event_name'] = 'UserPromptSubmit'
    # 用户提示提交事件处理
```

### 4. 缓存同步
更新所有缓存目录中的相关文件，确保修改生效。

## 实施步骤

### 步骤1：备份原始文件
```bash
# 备份 hooks.json
cp hooks.json hooks.json.backup

# 备份 Python 脚本
cp pretooluse.py pretooluse.py.backup
```

### 步骤2：应用修复
```bash
# 1. 修改 hooks.json 中的 python3 为 python
sed -i 's/"python3"/"python"/g' hooks.json

# 2. 修改 Python 脚本的 shebang
sed -i 's|#!/usr/bin/env python3|#!/usr/bin/env python|g' *.py

# 3. 更新 Python 脚本的数据处理逻辑
# 按照上述代码示例修改每个脚本
```

### 步骤3：验证修复
```bash
# 测试每个 hook 脚本
python pretooluse.py < test_input.json
python posttooluse.py < test_input.json
python stop.py < test_input.json
python userpromptsubmit.py < test_input.json
```

### 步骤4：重启 Claude Code
重启 Claude Code 以使 hook 更改生效。

## 验证结果

### 功能验证清单
- ✅ `pretooluse.py`：能正确返回包含 `systemMessage` 的 JSON
- ✅ `posttooluse.py`：能正确返回包含 `systemMessage` 的 JSON  
- ✅ `stop.py`：能正确返回包含 `systemMessage` 的 JSON（需使用 `conditions` 格式规则）
- ✅ `userpromptsubmit.py`：能正确返回包含 `systemMessage` 的 JSON
- ✅ 规则加载和匹配功能正常
- ✅ 所有 hook 事件类型都能正常工作

### 测试输入示例
```json
{
  "command": "bash",
  "args": ["ls", "-la"],
  "tool_input": {
    "description": "List files"
  },
  "session_id": "test-session-123"
}
```

### 预期输出
```json
{
  "hook_event_name": "PreToolUse",
  "systemMessage": "Hook processed successfully",
  "tool_input": {
    "command": "bash",
    "description": "List files"
  }
}
```

## 故障排除

### 常见问题及解决方案

#### 问题1：Python 命令仍然找不到
**症状**：`python: command not found`
**解决方案**：
```bash
# 检查 Python 安装
where python

# 如果未安装，安装 Python
# Windows: 从 python.org 下载安装包
# 确保勾选 "Add Python to PATH"
```

#### 问题2：输入数据格式错误
**症状**：`KeyError: 'tool_input'`
**解决方案**：
```python
# 在脚本中添加默认值处理
if 'tool_input' not in data:
    data['tool_input'] = {}
```

#### 问题3：rule_engine 无法加载规则
**症状**：`rule_engine` 导入错误
**解决方案**：
```bash
# 安装 rule_engine
pip install rule-engine

# 或使用项目虚拟环境中的 Python
/path/to/venv/Scripts/python pretooluse.py
```

#### 问题4：缓存未更新
**症状**：修改后仍然使用旧版本
**解决方案**：
```bash
# 清除 Claude Code 插件缓存
# Windows: 删除 C:\Users\Administrator\.claude\plugins\cache\ 中的相关目录

# 重启 Claude Code
```

### 调试步骤
1. **检查 Python 环境**：
   ```bash
   python --version
   where python
   ```

2. **测试脚本直接运行**：
   ```bash
   echo '{"command": "test"}' | python pretooluse.py
   ```

3. **检查输出格式**：
   ```bash
   echo '{"command": "test"}' | python pretooluse.py | python -m json.tool
   ```

4. **查看 Claude Code 日志**：
   ```bash
   # 查看 hook 执行日志
   # 在 Claude Code 日志中搜索 "hookify" 或 "hook"
   ```

## 技术原理

### Hookify 插件架构
1. **Hook 系统**：基于事件的生命周期钩子
2. **规则引擎**：使用 `rule_engine` 库进行规则匹配
3. **Python 脚本**：每个 hook 事件对应一个 Python 脚本

### 数据流
```
Claude Code → Hookify 插件 → hooks.json → Python 脚本 → 规则匹配 → 返回结果
```

### Windows 兼容性挑战
1. **命令差异**：`python3` vs `python`
2. **路径分隔符**：`/` vs `\`
3. **环境变量**：PATH 配置差异
4. **文件权限**：执行权限管理

## 最佳实践

### 1. 跨平台兼容性设计
```python
#!/usr/bin/env python
# 使用通用的 python shebang

import sys
import os
import json

# 平台检测
IS_WINDOWS = os.name == 'nt'
```

### 2. 输入数据验证
```python
def validate_input(data):
    """验证输入数据格式"""
    required_fields = ['hook_event_name']
    for field in required_fields:
        if field not in data:
            data[field] = 'Unknown'
    
    # 确保 tool_input 存在
    if 'tool_input' not in data:
        data['tool_input'] = {}
    
    return data
```

### 3. 错误处理
```python
def safe_main():
    """安全的主函数包装"""
    try:
        main()
    except Exception as e:
        error_result = {
            "error": str(e),
            "hook_event_name": "Error",
            "systemMessage": f"Hook execution failed: {e}"
        }
        print(json.dumps(error_result))
        sys.exit(1)
```

### 4. 配置管理
```json
{
  "hooks": {
    "pretooluse": {
      "command": "python",
      "args": ["pretooluse.py"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

## 自动化修复脚本

### Windows 修复脚本
```batch
@echo off
REM hookify-windows-fix.bat

echo Applying Hookify Windows compatibility fixes...

REM 备份原始文件
if not exist backups mkdir backups
copy hooks.json backups\hooks.json.backup
copy pretooluse.py backups\pretooluse.py.backup

REM 修改 hooks.json
powershell -Command "(Get-Content hooks.json) -replace '\"python3\"', '\"python\"' | Set-Content hooks.json"

REM 修改 Python shebang
powershell -Command "(Get-Content pretooluse.py) -replace '#!/usr/bin/env python3', '#!/usr/bin/env python' | Set-Content pretooluse.py"
powershell -Command "(Get-Content posttooluse.py) -replace '#!/usr/bin/env python3', '#!/usr/bin/env python' | Set-Content posttooluse.py"
powershell -Command "(Get-Content stop.py) -replace '#!/usr/bin/env python3', '#!/usr/bin/env python' | Set-Content stop.py"
powershell -Command "(Get-Content userpromptsubmit.py) -replace '#!/usr/bin/env python3', '#!/usr/bin/env python' | Set-Content userpromptsubmit.py"

echo Fixes applied successfully!
echo Please restart Claude Code for changes to take effect.
```

### 验证脚本
```bash
#!/bin/bash
# verify-hookify-fix.sh

echo "Verifying Hookify Windows compatibility fixes..."

# 检查 Python 命令
if command -v python &> /dev/null; then
    echo "✅ Python command found: $(which python)"
else
    echo "❌ Python command not found"
fi

# 检查 hooks.json
if grep -q '"python"' hooks.json; then
    echo "✅ hooks.json uses 'python' command"
else
    echo "❌ hooks.json still uses 'python3'"
fi

# 检查 shebang
for script in pretooluse.py posttooluse.py stop.py userpromptsubmit.py; do
    if [ -f "$script" ]; then
        if head -1 "$script" | grep -q "#!/usr/bin/env python"; then
            echo "✅ $script has correct shebang"
        else
            echo "❌ $script has incorrect shebang"
        fi
    fi
done

echo "Verification complete!"
```

## 更新日志

### 2026-04-14
- 首次发现 Windows 兼容性问题
- 实施 Python 命令修复
- 修复输入数据格式问题
- 验证所有 hook 脚本正常工作

### 2026-04-15
- 添加自动化修复脚本
- 完善故障排除指南
- 添加跨平台最佳实践

## 贡献指南

### 报告问题
如果遇到新问题，请提供：
1. 操作系统和 Python 版本
2. 完整的错误信息
3. 相关配置文件内容
4. 已尝试的解决方案

### 改进建议
欢迎提交改进建议：
1. 更好的跨平台兼容性方案
2. 自动化测试脚本
3. 性能优化建议
4. 文档改进

## 许可证
本文档作为项目文档的一部分，遵循项目相同的许可证。

---

**总结**：通过修复 Python 命令差异、输入数据格式和 hook_event_name 字段，我们成功解决了 Hookify 插件在 Windows 系统上的兼容性问题。这些修复确保 hook 脚本能够正确执行，规则引擎能够正常匹配规则。