# claude-mem 插件原生二进制文件问题解决方案知识库

## 概述

本文档记录了解决 claude-mem 插件需要 Claude Code 原生二进制文件（claude.cmd）的完整解决方案。由于 claude-mem 插件在源代码版本的项目中没有观察记录，我们在此构建一个完整的知识库。

## 问题描述

### 错误信息
```
plugin:claude-mem:mcp-search - prime_corpus (MCP)(name: "claude-mem-commands")
Error: Error calling Worker API: Worker API error (500): {"error":"Claude Code native binary not found at claude.cmd. Please ensure Claude Code is installed via native installer or specify a valid path with options.pathToClaudeCodeExecutable."}
```

### 问题根源
1. **claude-mem 插件设计**：为原生 Claude Code 安装设计，需要 `claude.cmd` 可执行文件
2. **项目现状**：运行的是源代码版本（`bun run dev`），没有生成原生二进制文件
3. **兼容性问题**：插件无法找到预期的可执行文件路径

## 解决方案矩阵

### 方案A：创建包装脚本（推荐且已验证有效）
**适用场景**：源代码开发环境
**核心思想**：创建 `claude.cmd` 包装脚本，让插件通过 `bun` 运行构建后的代码

### 方案B：构建原生二进制文件
**适用场景**：生产部署环境
**核心思想**：构建项目生成原生二进制文件，配置系统 PATH

### 方案C：配置插件使用当前环境
**适用场景**：高级用户配置
**核心思想**：修改插件配置，指定使用 `bun` 和源代码入口点

## 详细实施指南

### 方案A：创建包装脚本（已验证有效）

#### 步骤1：创建包装脚本 `claude.cmd`

**文件位置**：项目根目录
**文件内容**：
```batch
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
```

#### 步骤2：确保项目已构建
```bash
# 构建项目
bun run build

# 验证构建输出
ls -la dist/
# 应该看到 cli.js 文件（约 25MB）
```

#### 步骤3：PATH 配置

**临时添加到 PATH**：
```bash
export PATH="C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main:$PATH"
```

**永久添加到 PATH**（Windows）：
1. 右键"此电脑" → 属性
2. 高级系统设置 → 环境变量
3. 编辑 PATH，添加项目目录

#### 步骤4：验证配置
```bash
# 测试包装脚本
./claude.cmd --help

# 检查是否在 PATH 中
where claude.cmd
# 应该返回：C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main\claude.cmd
```

### 方案B：构建原生二进制文件

#### 项目构建配置
```json
// package.json
{
  "scripts": {
    "build": "bun build src/entrypoints/cli.tsx --outdir dist --target bun",
    "dev": "bun --feature=BUDDY run src/entrypoints/cli.tsx"
  }
}
```

#### 构建输出结构
```
dist/
└── cli.js          # 构建后的主入口文件（Bun 目标）
```

### 方案C：高级配置选项

#### 环境变量配置
```bash
# 设置 Claude Code 路径
export CLAUDE_CODE_PATH="bun run src/entrypoints/cli.tsx"

# 或设置包装脚本路径
export CLAUDE_CODE_PATH="C:\path\to\project\claude.cmd"
```

#### 插件配置查找
claude-mem 插件配置可能位于：
1. `C:\Users\Administrator\.claude\plugins\cache\thedotmack\claude-mem\12.1.3\.claude-plugin\`
2. `C:\Users\Administrator\.claude\plugins\cache\thedotmack\claude-mem\12.1.3\scripts\`
3. 插件数据目录

## 技术原理

### claude-mem 插件架构
1. **MCP 服务器**：运行在端口 37777
2. **Worker 服务**：通过 `worker-service.cjs` 管理
3. **钩子系统**：通过 hooks.json 配置生命周期钩子

### 包装脚本工作原理
```
claude-mem 插件 → 查找 claude.cmd → 包装脚本 → bun dist/cli.js → Claude Code
```

### 已验证的工作流程
1. ✅ 创建包装脚本 `claude.cmd`
2. ✅ 验证脚本工作：`./claude.cmd --help`
3. ✅ 确认 PATH 包含：`where claude.cmd`
4. ✅ 测试 claude-mem 插件：`prime_corpus` 成功

## 故障排除指南

### 常见问题及解决方案

#### 问题1：包装脚本找不到 dist/cli.js
**症状**：`Error: cli.js not found`
**解决方案**：
```bash
# 确保项目已构建
bun run build

# 验证文件存在
ls -la dist/cli.js
```

#### 问题2：PATH 不包含项目目录
**症状**：`claude.cmd not found`
**解决方案**：
```bash
# 临时添加
export PATH="/path/to/project:$PATH"

# 验证
where claude.cmd
```

#### 问题3：权限问题
**症状**：`Access denied` 或无法执行
**解决方案**：
```bash
# Windows: 确保 .cmd 文件可执行
# 检查文件属性，确保没有阻止执行
```

#### 问题4：Bun 未安装
**症状**：`bun: command not found`
**解决方案**：
```bash
# 安装 Bun
curl -fsSL https://bun.sh/install | bash

# 验证安装
bun --version
```

### 调试步骤
1. **检查包装脚本**：`cat claude.cmd`
2. **检查构建输出**：`ls -la dist/`
3. **检查 PATH**：`echo $PATH`
4. **测试直接运行**：`bun dist/cli.js --help`
5. **测试包装脚本**：`./claude.cmd --version`

## 最佳实践

### 1. 版本控制
将包装脚本添加到版本控制：
```bash
git add claude.cmd
git commit -m "Add claude.cmd wrapper for claude-mem plugin compatibility"
```

### 2. 文档化
在项目 README 中添加说明：
```markdown
## claude-mem 插件兼容性

### 问题
claude-mem 插件需要原生 `claude.cmd` 二进制文件。

### 解决方案
1. 确保项目已构建：`bun run build`
2. 使用包装脚本：`./claude.cmd [args]`
3. 或将项目目录添加到系统 PATH

### 验证
```bash
./claude.cmd --help
where claude.cmd
```
```

### 3. 自动化脚本
创建自动化设置脚本：
```bash
#!/bin/bash
# setup-claude-mem-compatibility.sh

echo "Setting up claude-mem plugin compatibility..."

# 构建项目
echo "Building project..."
bun run build

# 创建包装脚本
echo "Creating wrapper script..."
cat > claude.cmd << 'EOF'
@echo off
bun "%~dp0dist\cli.js" %*
EOF

# 设置执行权限
chmod +x claude.cmd

echo "Setup complete!"
echo "Use ./claude.cmd to run Claude Code."
echo "Ensure project directory is in PATH for claude-mem plugin."
```

### 4. 环境检查脚本
```bash
#!/bin/bash
# check-claude-mem-compatibility.sh

echo "Checking claude-mem plugin compatibility..."

# 检查构建文件
if [ -f "dist/cli.js" ]; then
    echo "✅ dist/cli.js exists"
else
    echo "❌ dist/cli.js not found. Run: bun run build"
fi

# 检查包装脚本
if [ -f "claude.cmd" ]; then
    echo "✅ claude.cmd exists"
else
    echo "❌ claude.cmd not found"
fi

# 检查 PATH
if which claude.cmd >/dev/null 2>&1; then
    echo "✅ claude.cmd is in PATH"
else
    echo "❌ claude.cmd not in PATH"
    echo "Add to PATH: export PATH=\"$(pwd):\$PATH\""
fi

# 测试运行
echo "Testing claude.cmd..."
./claude.cmd --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ claude.cmd works correctly"
else
    echo "❌ claude.cmd failed to run"
fi
```

## 相关知识链接

### 项目文档
- [CLAUDE.md](../CLAUDE.md) - 项目概述和架构
- [claude_mem_binary_fix.md](../memory/claude_mem_binary_fix.md) - 解决方案详细记录

### 技术参考
- **Bun 构建系统**：`bun build --target bun`
- **Windows 批处理脚本**：`.cmd` 文件格式
- **环境变量管理**：PATH 配置原理
- **MCP 服务器架构**：Model Context Protocol

### 相关工具
- **claude-mem 插件**：持久记忆系统
- **Claude Code**：源代码版本 CLI
- **Bun**：JavaScript 运行时

## 更新日志

### 2026-04-16
- 创建完整解决方案文档
- 验证方案A（包装脚本）有效
- 记录所有实施步骤和故障排除方法

### 2026-04-15  
- 首次发现问题：claude-mem 插件需要 claude.cmd
- 创建初始包装脚本
- 验证基本功能

## 贡献指南

### 报告问题
如果遇到新问题，请提供：
1. 完整错误信息
2. 操作系统和环境信息
3. 已尝试的解决方案
4. 相关日志输出

### 改进建议
欢迎提交改进建议：
1. 更优雅的解决方案
2. 额外的兼容性处理
3. 更好的错误提示
4. 自动化工具改进

## 许可证
本文档作为项目文档的一部分，遵循项目相同的许可证。

---

**总结**：通过创建 `claude.cmd` 包装脚本，我们成功解决了 claude-mem 插件需要 Claude Code 原生二进制文件的问题。这个解决方案在源代码开发环境中经过验证，确保 claude-mem 插件能够正常工作。