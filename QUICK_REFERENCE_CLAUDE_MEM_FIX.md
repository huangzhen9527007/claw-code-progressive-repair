# claude-mem 插件兼容性快速参考

## 问题
claude-mem 插件需要 `claude.cmd` 原生二进制文件，但项目是源代码版本。

## 一键解决方案

### 步骤1：创建包装脚本
```bash
cat > claude.cmd << 'EOF'
@echo off
bun "%~dp0dist\cli.js" %*
EOF
```

### 步骤2：构建项目
```bash
bun run build
```

### 步骤3：添加到 PATH
```bash
# 临时添加（当前会话）
export PATH="$(pwd):$PATH"

# 永久添加（Windows）
# 1. 系统属性 → 高级 → 环境变量
# 2. 编辑 PATH，添加项目目录
```

### 步骤4：验证
```bash
# 测试包装脚本
./claude.cmd --help

# 检查 PATH
where claude.cmd
```

## 验证命令

```bash
# 完整验证脚本
#!/bin/bash
echo "1. 检查构建文件:"
ls -la dist/cli.js && echo "✅" || echo "❌ 运行: bun run build"

echo "2. 检查包装脚本:"
[ -f claude.cmd ] && echo "✅" || echo "❌ 创建 claude.cmd"

echo "3. 检查 PATH:"
which claude.cmd && echo "✅" || echo "❌ 添加到 PATH"

echo "4. 测试运行:"
./claude.cmd --version >/dev/null 2>&1 && echo "✅" || echo "❌ 检查错误"
```

## 故障排除

### 如果仍然报错：
1. **确保 Bun 已安装**：`bun --version`
2. **重新构建项目**：`bun run build`
3. **检查文件权限**：确保 `claude.cmd` 可执行
4. **重启终端**：使 PATH 更改生效

### 快速诊断：
```bash
# 运行诊断脚本
curl -s https://raw.githubusercontent.com/your-repo/diagnose.sh | bash
```

## 自动化脚本

保存为 `fix-claude-mem.sh`：
```bash
#!/bin/bash
echo "修复 claude-mem 插件兼容性..."
bun run build
cat > claude.cmd << 'EOF'
@echo off
bun "%~dp0dist\cli.js" %*
EOF
chmod +x claude.cmd
echo "✅ 完成！使用 ./claude.cmd 运行 Claude Code"
```

## 相关文档
- 完整解决方案：`docs/claude-mem-binary-fix-knowledge-base.md`
- 记忆记录：`memory/claude_mem_binary_fix.md`
- 项目概述：`CLAUDE.md`

---

**提示**：将此文件放在项目根目录，方便快速参考。