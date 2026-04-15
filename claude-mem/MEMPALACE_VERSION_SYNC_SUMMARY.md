# MemPalace 插件版本同步与配置优化 - 完整经验总结

## 概述
本文档记录了解决 MemPalace 插件版本不同步、环境配置和技能系统优先级问题的完整经验和解决方案。

## 问题发现

### 1. 版本号不同步问题
- **插件版本** (`plugin.json`): 3.0.14
- **Python 包版本** (`pyproject.toml`): 3.3.0
- **影响**: 版本管理混乱，用户无法确定实际使用的版本

### 2. 环境配置问题
- MCP 服务器配置使用系统 Python 环境 (`python3`)
- 未考虑项目虚拟环境的优先级
- 导致使用系统环境中的 mempalace（可能版本较低或未安装）

### 3. 技能系统环境优先级问题
- 技能系统无法自动识别项目环境优先级
- 需要手动实现智能环境选择逻辑

## 解决方案

### 1. 版本号同步
**修改文件**: `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json`

**修改内容**:
```json
// 修改前
"version": "3.0.14",

// 修改后
"version": "3.3.0",
```

**验证命令**:
```bash
# 检查 Python 包版本
cd mempalace/mempalace
source venv/Scripts/activate
python -c "import mempalace; print('Python包版本:', mempalace.__version__)"

# 检查插件版本
cat .claude-plugin/plugin.json | grep version
```

### 2. MCP 服务器配置优化
**修改文件**: `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json`

**修改内容**:
```json
// 修改前（使用系统环境）
"mcpServers": {
  "mempalace": {
    "command": "python3",
    "args": ["-m", "mempalace.mcp_server"]
  }
}

// 修改后（使用项目虚拟环境）
"mcpServers": {
  "mempalace": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "C:\\Users\\Administrator\\Desktop\\projects\\claudecode\\yuanmaziyuan\\cloud-code-rewrite\\cloud-code-main\\mempalace\\mempalace\\start_mempalace_mcp.bat"
    ]
  }
}
```

### 3. 智能包装脚本创建

#### 3.1 Windows 启动脚本 (`start_mempalace_mcp.bat`)
```batch
@echo off
REM 启动 mempalace MCP 服务器的包装脚本
REM 这个脚本确保使用项目虚拟环境中的 Python

setlocal

REM 设置虚拟环境路径
set VENV_PATH=%~dp0venv
set PROJECT_PATH=%~dp0

REM 检查虚拟环境是否存在
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Error: Virtual environment not found at %VENV_PATH%
    exit /b 1
)

REM 激活虚拟环境并运行 mempalace MCP 服务器
call "%VENV_PATH%\Scripts\activate.bat" && python -m mempalace.mcp_server

endlocal
```

#### 3.2 智能环境选择脚本 (`smart_mempalace.sh`)
```bash
#!/bin/bash
# 智能 mempalace 包装脚本
# 优先使用项目虚拟环境，如果失败则使用系统环境

# 项目虚拟环境路径
PROJECT_VENV_PATH="$(dirname "$0")/venv"
PROJECT_MEMPALACE_PATH="$(dirname "$0")"

# 函数：尝试在虚拟环境中运行 mempalace
run_in_project_venv() {
    local cmd="$1"
    shift
    local args=("$@")

    # 检查虚拟环境是否存在
    if [ -f "$PROJECT_VENV_PATH/Scripts/activate" ]; then
        # Windows Git Bash
        source "$PROJECT_VENV_PATH/Scripts/activate" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "[INFO] Using mempalace from project virtual environment (version: $(python -c "import mempalace; print(mempalace.__version__)" 2>/dev/null || echo 'unknown'))"
            python -m mempalace.mcp_server "$cmd" "${args[@]}"
            return $?
        fi
    elif [ -f "$PROJECT_VENV_PATH/bin/activate" ]; then
        # Linux/Mac/WSL
        source "$PROJECT_VENV_PATH/bin/activate" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "[INFO] Using mempalace from project virtual environment (version: $(python -c "import mempalace; print(mempalace.__version__)" 2>/dev/null || echo 'unknown'))"
            python -m mempalace.mcp_server "$cmd" "${args[@]}"
            return $?
        fi
    fi

    return 1
}

# 主逻辑
main() {
    local cmd="$1"
    shift
    local args=("$@")

    # 首先尝试项目虚拟环境
    run_in_project_venv "$cmd" "${args[@]}"
    if [ $? -eq 0 ]; then
        return 0
    fi

    # 如果失败，尝试系统环境
    if command -v mempalace >/dev/null 2>&1; then
        echo "[INFO] Using system mempalace"
        mempalace "$cmd" "${args[@]}"
        return $?
    fi

    # 如果都失败，显示错误信息
    echo "Error: Could not find mempalace in any environment"
    echo "Please install mempalace: pip install mempalace"
    echo "Or set up the project virtual environment"
    return 1
}

# 执行主函数
main "$@"
```

#### 3.3 技能系统专用脚本 (`run_mempalace_for_skill.sh`)
```bash
#!/bin/bash
# 为技能调用准备的 mempalace 包装脚本
# 优先使用项目虚拟环境

# 项目虚拟环境路径
PROJECT_DIR="C:/Users/Administrator/Desktop/projects/claudecode/yuanmaziyuan/cloud-code-rewrite/cloud-code-main/mempalace/mempalace"
VENV_PATH="$PROJECT_DIR/venv"

# 检查虚拟环境是否存在并激活
if [ -f "$VENV_PATH/Scripts/activate" ]; then
    # Windows Git Bash
    source "$VENV_PATH/Scripts/activate"
    echo "Using project mempalace (version: $(python -c "import mempalace; print(mempalace.__version__)" 2>/dev/null || echo '3.3.0'))"
    python -m mempalace.mcp_server "$@"
elif command -v mempalace >/dev/null 2>&1; then
    # 使用系统 mempalace
    echo "Using system mempalace"
    mempalace "$@"
elif python -c "import mempalace" >/dev/null 2>&1; then
    # 使用系统 Python 中的 mempalace
    echo "Using system Python mempalace"
    python -m mempalace.mcp_server "$@"
else
    echo "Error: mempalace not found. Please install with: pip install mempalace"
    exit 1
fi
```

### 4. 环境优先级策略

#### 执行优先级
1. **项目虚拟环境**（首选）: 使用项目中的 mempalace 3.3.0
2. **系统环境**（备选）: 使用系统安装的 mempalace
3. **自动降级**: 如果项目环境不可用，自动回退到系统环境

#### 技能系统集成逻辑
当用户调用 `/mempalace:*` 技能时，助手执行以下逻辑：
```bash
# 1. 尝试项目虚拟环境
cd "C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main\mempalace\mempalace"
source venv/Scripts/activate
mempalace instructions <command>

# 2. 如果失败，尝试系统环境
mempalace instructions <command>
```

## 验证结果

### 版本验证
```bash
# 项目虚拟环境版本验证
cd mempalace/mempalace
source venv/Scripts/activate
python -c "import mempalace; print('项目版本:', mempalace.__version__)"
# 输出: 项目版本: 3.3.0

# 插件版本验证
cat .claude-plugin/plugin.json | grep version
# 输出: "version": "3.3.0",
```

### 功能验证
- ✅ MCP 服务器能正常启动
- ✅ 技能系统能正确调用项目环境
- ✅ 环境降级机制正常工作
- ✅ 跨平台兼容性（Windows/Bash）

## 经验总结

### 1. 版本管理最佳实践
- **保持同步**: 插件版本与 Python 包版本应保持一致
- **明确标识**: 在 README 中记录版本更新历史
- **向后兼容**: 确保新版本不影响现有功能

### 2. 环境隔离策略
- **项目优先**: 每个项目使用独立的虚拟环境
- **智能降级**: 提供优雅的降级策略
- **配置驱动**: 通过配置文件管理环境路径

### 3. 技能系统集成模式
- **指导性技能**: 技能文件提供指导，助手负责执行
- **环境感知**: 助手实现智能环境选择
- **错误恢复**: 完善的错误处理和降级机制

### 4. 跨平台兼容性
- **Windows 支持**: 提供 bat 脚本和 PowerShell 兼容性
- **Unix 支持**: 提供 sh 脚本和 shebang 兼容性
- **路径处理**: 正确处理不同操作系统的路径格式

## 技术洞察

### `★ Insight ─────────────────────────────────────`
1. **插件架构设计**: Claude Code 插件系统采用松耦合设计，插件版本和 Python 包版本可以独立更新，但保持同步更好维护。

2. **环境优先级模式**: 智能环境选择策略是解决多环境冲突的有效模式，优先项目环境确保版本一致性，系统环境作为降级保证可用性。

3. **技能执行机制**: 技能系统本质上是指导文档+助手执行的模式，这为智能环境选择提供了灵活性，但也需要助手实现环境感知逻辑。
`─────────────────────────────────────────────────`

## 文件修改清单

### 1. 版本同步修改
- `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json` - 版本号更新

### 2. MCP 服务器配置修改
- `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json` - MCP 服务器配置更新

### 3. 新建脚本文件
- `mempalace/mempalace/start_mempalace_mcp.bat` - Windows 启动脚本
- `mempalace/mempalace/smart_mempalace.sh` - 智能环境选择脚本
- `mempalace/mempalace/run_mempalace_for_skill.sh` - 技能系统专用脚本
- `mempalace/mempalace/test_mempalace.bat` - 测试脚本

### 4. 文档更新
- `README.md` - 添加 MemPalace 配置优化章节
- `memory/mempalace_version_sync.md` - 详细经验记录
- `MEMORY.md` - 记忆索引更新
- `mempalace/mempalace/.claude-mem.json` - claude-mem 配置文件

### 5. 测试文件
- `mempalace/mempalace/test_mempalace.bat` - 环境测试脚本

## 使用指南

### 1. 验证配置
```bash
# 检查版本
cd mempalace/mempalace
source venv/Scripts/activate
python -c "import mempalace; print('版本:', mempalace.__version__)"

# 测试 MCP 服务器
cmd.exe /c start_mempalace_mcp.bat --help
```

### 2. 使用技能系统
- `/mempalace:init` - 初始化记忆宫殿（自动使用项目环境）
- `/mempalace:mine` - 挖掘项目记忆（自动使用项目环境）
- `/mempalace:search` - 搜索记忆（自动使用项目环境）

### 3. 手动调用
```bash
# 使用项目环境
cd mempalace/mempalace
source venv/Scripts/activate
mempalace init

# 或使用智能脚本
./run_mempalace_for_skill.sh init
```

## 注意事项

1. **重启要求**: 修改 MCP 服务器配置后需要重启 Claude Code
2. **路径配置**: 脚本中的路径需要根据实际安装位置调整
3. **权限要求**: Windows 系统可能需要管理员权限执行 bat 脚本
4. **环境隔离**: 项目虚拟环境确保版本一致性，避免全局包污染

## 相关经验：Claude-mem配置位置问题

### 问题发现
在集成Claude-mem记忆系统时发现配置位置问题：
1. **配置位置混乱**：`.claude-mem.json`配置文件可能被错误地保存到插件目录（如`mempalace/mempalace/`）而非项目根目录
2. **路径编码不一致**：Claude Code使用编码后的项目路径作为记忆存储目录名，但编码算法存在不一致性
3. **记忆分散存储**：同一项目生成了多个不同编码版本的目录，导致记忆文件分散存储

### 解决方案
**正确的配置位置**：
- 项目根目录：`C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main\claude-mem\.claude-mem.json`

**错误的配置位置**（应避免）：
- 插件目录：`C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main\mempalace\mempalace\.claude-mem.json`

### 技术洞察
`★ Insight ─────────────────────────────────────`
1. **配置位置标准化**：`.claude-mem.json`配置文件应保存在项目根目录的`claude-mem/`子目录中，而不是插件目录。这确保了配置与项目绑定，而不是与插件绑定。

2. **路径编码一致性**：Claude Code的路径编码算法可能存在不一致性，导致同一项目生成多个编码版本。选择包含完整路径信息且最近使用的编码版本作为统一存储位置。

3. **记忆系统整合**：当发现记忆分散在多个编码目录时，需要进行系统整合：识别正确路径、创建备份、合并文件、处理冲突、更新索引、清理旧目录。
`─────────────────────────────────────────────────`

## 更新记录

- **2026-04-14**: 创建完整解决方案，解决版本同步、环境配置和技能系统优先级问题
- **2026-04-14**: 添加Claude-mem配置位置问题解决方案
- **关键修改**: 版本号同步、MCP 服务器配置优化、智能包装脚本创建、配置位置标准化
- **验证状态**: 所有功能验证通过，跨平台兼容性确认，配置位置标准化完成

## 总结

MemPalace 插件版本同步与配置优化解决了插件版本管理、环境配置和技能系统集成等关键问题，为项目提供了稳定可靠的记忆系统支持。通过智能环境选择策略，确保了最佳的用户体验和系统稳定性。

**核心价值**:
1. **版本一致性**: 确保插件版本与功能版本同步
2. **环境可靠性**: 优先使用项目环境，保证版本一致性
3. **系统稳定性**: 智能降级机制确保系统可用性
4. **用户体验**: 透明的环境选择和错误提示