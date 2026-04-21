# Memory Tools Plugin - 快速启动指南

## 1. 验证插件安装

首先，确认插件目录存在：
```bash
ls -la "C:/Users/Administrator/.claude/plugins/local/memory-tools/"
```

应该看到以下结构：
```
memory-tools/
├── plugin.json
├── README.md
├── test_skill.py
├── src/
│   └── memory_system_diagnosis_skill.py
└── skills/
    └── memory-system-diagnosis/
        └── SKILL.md
```

## 2. 测试插件功能

运行测试脚本验证插件是否工作：
```bash
cd "C:/Users/Administrator/.claude/plugins/local/memory-tools"
python test_skill.py
```

如果看到类似以下输出，说明插件工作正常：
```
测试记忆系统诊断工具...
============================================================
记忆目录: C:\Users\Administrator\.claude\projects\...\memory
索引文件: C:\Users\Administrator\.claude\projects\...\memory\MEMORY.md

1. 获取记忆文件...
   找到 51 个记忆文件

2. 获取索引文件...
   找到 52 个索引条目

3. 检查数量匹配...
   文件数量: 51, 索引数量: 52, 匹配: False

4. 查找未索引文件...
   没有未索引文件

5. 查找多余索引...
   没有多余索引

6. 查找重复索引...
   发现 1 个重复索引:
     - claude_code_local_plugin_skill_system.md (出现2次)

7. 生成诊断报告...
   报告已生成，包含 3 条建议

============================================================
测试完成！

[WARNING] 发现问题:
   duplicate_indexes: 1 个
   category_mismatches: 2 个
```

## 3. 清理Claude Code缓存

如果这是第一次安装或修改了插件配置，需要清理缓存：
```bash
rm -rf "C:/Users/Administrator/.claude/plugins/cache/*"
```

## 4. 重启Claude Code

关闭并重新启动Claude Code，让插件重新加载。

## 5. 在Claude Code中使用插件

### 方法一：使用技能命令
在Claude Code中输入：
```
/memory-tools:memory-system-diagnosis
```

### 方法二：使用自然语言
在Claude Code中直接说：
- "检查记忆系统"
- "memory system check"
- "记忆系统诊断"

### 方法三：使用完整命令
```
/memory-tools:memory-system-diagnosis --action report
```

## 6. 常用命令示例

### 快速检查
```bash
/memory-tools:memory-system-diagnosis --action check
```

### 详细报告
```bash
/memory-tools:memory-system-diagnosis --action report
```

### 分类问题检查
```bash
/memory-tools:memory-system-diagnosis --action classify
```

### 修复计划
```bash
/memory-tools:memory-system-diagnosis --action fix-plan
```

### 分类修复计划
```bash
/memory-tools:memory-system-diagnosis --action classify-fix
```

### JSON格式输出
```bash
/memory-tools:memory-system-diagnosis --action report --json
```

## 7. 故障排除

### 问题1：技能无法加载
**症状**：输入`/`后看不到`memory-tools:memory-system-diagnosis`

**解决步骤**：
1. 检查插件目录结构是否正确
2. 清理缓存：`rm -rf ~/.claude/plugins/cache/*`
3. 重启Claude Code
4. 检查`plugin.json`中的`skills`字段

### 问题2：Python依赖错误
**症状**：`ImportError: No module named 'yaml'`

**解决方案**：
```bash
pip install PyYAML
```

### 问题3：找不到记忆目录
**症状**：`FileNotFoundError: Memory directory not found`

**解决方案**：
```bash
/memory-tools:memory-system-diagnosis --memory-dir "C:/Users/Administrator/.claude/projects/.../memory"
```

## 8. 验证成功

成功标志：
1. 输入`/`然后按Tab键，能看到`memory-tools:memory-system-diagnosis`在技能列表中
2. 可以直接使用命令：`/memory-tools:memory-system-diagnosis`
3. 可以使用自然语言触发：说"检查记忆系统"或"memory system check"

## 9. 定期维护建议

建议每周运行一次记忆系统检查：
```bash
/memory-tools:memory-system-diagnosis --action report
```

如果发现问题，先查看修复计划：
```bash
/memory-tools:memory-system-diagnosis --action fix-plan
```

确认无误后再执行修复（谨慎使用）：
```bash
/memory-tools:memory-system-diagnosis --action fix
```

## 10. 获取帮助

查看完整文档：
```bash
cat "C:/Users/Administrator/.claude/plugins/local/memory-tools/README.md"
```

或者直接查看技能帮助：
```bash
/memory-tools:memory-system-diagnosis --help
```

---

**提示**：这个插件可以大大节省大模型token消耗，提高记忆系统维护的准确性和效率。建议将其集成到日常开发工作流中。