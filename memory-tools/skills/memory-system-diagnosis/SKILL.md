---
name: memory-system-diagnosis
description: Memory System Diagnosis Tool - Automatically checks memory system integrity and fixes classification issues
---

# 记忆系统诊断技能

## 概述

记忆系统诊断工具，自动检查记忆系统完整性，检测未索引文件、多余索引、重复索引，并修复7个分类问题。

## 功能特性

1. **完整性检查**：检查记忆文件数量是否匹配索引数量
2. **问题检测**：查找未索引文件、多余索引、重复索引
3. **分类检查**：检查记忆文件类型是否匹配索引分类
4. **分类问题修复**：检测并修复7个分类问题
5. **详细报告**：生成完整的诊断报告
6. **修复建议**：提供具体的修复建议

## 7个分类问题

工具检测并帮助修复以下7个分类问题：

1. **中文文件名在英文分类中** - 将中文文件重命名为英文
2. **混合语言描述** - 标准化索引描述
3. **不一致的分类** - 识别可能分类错误的文件
4. **缺少frontmatter类型声明** - 添加缺失的类型元数据
5. **frontmatter类型与索引不匹配** - 修复分类不匹配
6. **不一致的命名约定** - 标准化文件名格式
7. **缺失或不正确的类型元数据** - 验证并修复类型信息

## 使用方法

### 基本检查
```bash
# 检查基本统计
python memory_system_diagnosis_skill.py --check

# 生成详细报告
python memory_system_diagnosis_skill.py --report

# 显示修复计划（试运行）
python memory_system_diagnosis_skill.py --fix

# 执行修复（谨慎使用）
python memory_system_diagnosis_skill.py --fix-execute
```

### 分类功能
```bash
# 检查分类问题
python memory_system_diagnosis_skill.py --classification-report

# 修复分类问题
python memory_system_diagnosis_skill.py --fix-classification
```

### 使用action参数
```bash
# 使用--action参数的替代语法
python memory_system_diagnosis_skill.py --action check
python memory_system_diagnosis_skill.py --action report
python memory_system_diagnosis_skill.py --action fix-plan
python memory_system_diagnosis_skill.py --action fix
python memory_system_diagnosis_skill.py --action classify
python memory_system_diagnosis_skill.py --action classify-fix
```

### JSON输出
```bash
# JSON格式输出
python memory_system_diagnosis_skill.py --report --json
python memory_system_diagnosis_skill.py --check --json
python memory_system_diagnosis_skill.py --classification-report --json
```

### 指定记忆目录
```bash
python memory_system_diagnosis_skill.py --memory-dir /path/to/memory --report
```

## 输出示例

### 基本检查输出
```
记忆文件: 25, 索引条目: 25, 匹配: True
```

### 详细报告输出
```
============================================================
记忆系统诊断报告
============================================================

[统计] 基本统计:
  记忆文件数量: 25
  索引条目数量: 25
  [正常] 数量匹配

[正常] 未发现问题

[建议]:
  1. 记忆系统健康，无需修复

============================================================
诊断完成
============================================================
```

### 分类问题报告输出
```
============================================================
分类问题报告
============================================================

摘要:
  发现的问题总数: 15
  问题类型数量: 5
  有问题的文件数: 8

详细问题:

  中文文件名在英文分类中 (7):
    - 超级管理员权限.md
    - 用户角色.md
    - Hookify插件修复.md
    - WeChat CLI编码问题解决方案.md
    - 项目概述.md
    - claude-mem 插件信息.md
    - 如何使用 claude-mem 插件.md

  缺少frontmatter类型 (3):
    - HOOKIFY_FIX_SUMMARY.md
    - TUI_LAUNCHER_UPDATE.md
    - SESSION_SAVER_README.md

建议:
  1. 将中文文件名重命名为英文以提高兼容性
  2. 为记忆文件添加缺失的frontmatter类型声明

============================================================
```

## 问题类型

1. **未索引文件**：存在于memory目录但未在MEMORY.md中索引的文件
2. **多余索引**：在MEMORY.md中索引但文件不存在的条目
3. **重复索引**：同一个文件在MEMORY.md中被多次索引
4. **分类不匹配**：文件类型与索引分类不匹配
5. **分类问题**：上述7个具体的分类问题

## 技术实现

- 自动检测当前项目的记忆目录
- 支持从多个记忆目录自动选择
- 完整的错误处理和用户友好的错误信息
- 支持试运行模式，避免意外修改
- 英文编码确保最大兼容性
- 智能文件名翻译，中文转英文
- 使用PyYAML解析frontmatter

## 安装要求

```bash
pip install PyYAML
```

## 注意事项

1. 修复操作会修改MEMORY.md和记忆文件 - 先使用试运行模式
2. 分类检查依赖于记忆文件frontmatter中的type字段
3. 工具自动查找记忆目录，也可手动指定
4. 分类修复包括将中文文件重命名为英文名称
5. 执行修复前始终备份记忆系统
6. 工具设计为使用英文编码确保最大兼容性

## 与Claude Code集成

此技能已集成到Claude Code插件中。安装后，可以直接从Claude Code使用：

```bash
# 通过Claude Code使用技能
claude-code memory-system-diagnosis --help
```

## 开发

工具使用Python 3编写，遵循以下约定：
- 所有编程代码使用纯英文
- 文档和注释使用中文
- UTF-8编码确保最大兼容性
- 全面的错误处理
- 模块化设计便于维护