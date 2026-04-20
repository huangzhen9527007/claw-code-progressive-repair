# Memory Tools 完全整合方案设计文档

## 概述
本设计文档描述了将现有 memory-tools 插件中的多个 Python 文件整合为统一架构的方案。

## 设计目标
1. 将所有 Python 文件移到 `src/` 目录
2. 根目录只保留 `main.py` 作为统一入口
3. 整合 `memory_system_diagnosis_skill.py` 和 `enhanced_classification_fixer.py` 的功能
4. 确保所有 7 个分类问题都被正确处理
5. 删除功能重复或过时的文件

## 当前问题分析

### 文件组织问题
- 根目录有多个 Python 文件，缺乏统一入口
- `src/` 目录只有部分文件
- 用户需要知道调用哪个文件

### 功能重复问题
- `memory_system_diagnosis_skill.py` (1439行) - 完整的内存系统诊断
- `enhanced_classification_fixer.py` (746行) - 增强版分类问题修复
- `memory_diagnosis_cli.py` (141行) - 简化版 CLI
- `check_issues.py` (132行) - 快速检查脚本

### 分类问题处理
需要确保以下 7 个分类问题都被正确处理：
1. 中文文件名在英文分类中
2. 缺少 frontmatter 类型声明
3. 类型不匹配（frontmatter 与索引）
4. 类型元数据问题
5. 混合语言描述问题
6. 不一致的命名约定
7. 命名约定问题分析

## 新架构设计

### 文件结构
```
memory-tools/
├── main.py                    # 统一入口点
├── plugin.json               # 插件配置
├── package.json              # 包配置
├── requirements.txt          # 依赖
├── README.md                 # 主文档
├── ENHANCED_TOOLS_README.md  # 增强工具文档
├── ENHANCEMENT_SUMMARY.md    # 增强总结
├── QUICK_START.md           # 快速开始
├── skills/                   # 技能目录
│   └── memory-system-diagnosis/
│       └── SKILL.md
└── src/                      # 所有 Python 源代码
    ├── __init__.py
    ├── memory_tools.py       # 主工具类（整合版）
    ├── cli.py               # 命令行接口
    ├── classification_fixer.py # 分类修复模块
    └── utils.py             # 工具函数
```

### 核心类设计

#### 1. MemoryTools (主工具类)
整合所有功能的入口类，提供：
- 内存系统完整性检查
- 分类问题检测和修复
- 报告生成
- 修复执行

#### 2. ClassificationFixer (分类修复模块)
专门处理 7 个分类问题：
- 检测所有分类问题
- 提供修复方案
- 执行修复操作
- 智能处理中文项目

#### 3. CLI (命令行接口)
统一的命令行接口，支持：
- 所有现有命令行参数
- 新的整合命令
- JSON 输出格式
- 试运行模式

## 功能整合策略

### 从 memory_system_diagnosis_skill.py 继承的功能
1. 内存系统完整性检查
2. 未索引文件检测
3. 多余索引检测
4. 重复索引检测
5. 基本统计报告

### 从 enhanced_classification_fixer.py 继承的功能
1. 7 个分类问题的检测
2. 实际修复功能（文件重命名、添加 frontmatter 等）
3. 智能中文项目处理
4. 命名约定标准化
5. 安全试运行模式

### 新增功能
1. 统一的错误处理
2. 更好的日志记录
3. 配置管理
4. 插件集成优化

## 7个分类问题的具体实现

### 1. 中文文件名问题
- **检测**：识别中文文件名在英文分类中的情况
- **修复**：将中文文件名翻译为英文并重命名
- **智能处理**：保留合理的混合命名

### 2. 缺少 frontmatter 类型
- **检测**：检查记忆文件是否缺少 frontmatter 类型声明
- **修复**：根据文件名和内容添加适当的类型

### 3. 类型不匹配
- **检测**：比较 frontmatter 类型与索引分类
- **修复**：调整索引或更新 frontmatter 使之一致

### 4. 类型元数据问题
- **检测**：验证类型元数据的完整性和正确性
- **修复**：补充缺失的元数据或修正错误

### 5. 混合语言描述问题
- **检测**：识别描述中的混合语言使用
- **修复**：智能处理，中文项目允许中文描述

### 6. 不一致的命名约定
- **检测**：识别文件名格式不一致
- **修复**：标准化为统一的命名约定

### 7. 命名约定问题分析
- **检测**：分析命名约定的模式和问题
- **修复**：提供命名约定优化建议

## 命令行接口设计

### 命令结构
```bash
# 基本检查
python main.py check

# 完整报告
python main.py report

# 分类问题报告
python main.py classify

# 修复计划（试运行）
python main.py fix --dry-run

# 执行修复
python main.py fix

# 特定分类修复
python main.py fix --fix-naming --fix-frontmatter
```

### 参数兼容性
保持对现有参数的支持：
- `--check`, `--report`, `--fix`
- `--dry-run`, `--json`
- `--memory-dir`, `--action`

## 删除的文件列表
1. `check_issues.py` - 功能将被整合
2. `memory_diagnosis_cli.py` - 将被新的 `cli.py` 替代
3. `test_plugin.py` - 测试文件（可删除或移到测试目录）
4. `test_skill.py` - 测试文件（可删除或移到测试目录）
5. `enhanced_classification_fixer.py` - 功能将被整合
6. `src/memory_system_diagnosis_skill.py.backup` - 备份文件

## 实施计划

### 阶段1：准备阶段
1. 分析现有代码，提取核心功能
2. 设计新的类结构和API
3. 创建新的目录结构

### 阶段2：实现阶段
1. 实现 `MemoryTools` 主类
2. 实现 `ClassificationFixer` 模块
3. 实现新的 `CLI` 接口
4. 实现 `utils.py` 工具函数

### 阶段3：迁移阶段
1. 迁移所有功能到新架构
2. 确保功能完整性
3. 测试所有命令行参数

### 阶段4：清理阶段
1. 删除旧文件
2. 更新文档
3. 更新技能配置

## 测试策略
1. **单元测试**：测试每个模块的功能
2. **集成测试**：测试整个工具链
3. **兼容性测试**：确保与现有参数兼容
4. **分类问题测试**：验证所有7个问题都被正确处理

## 风险与缓解
1. **功能丢失风险**：通过详细的功能映射和测试缓解
2. **兼容性风险**：保持命令行参数兼容性
3. **性能风险**：优化代码结构，避免性能下降

## 成功标准
1. 所有现有功能正常工作
2. 所有7个分类问题都被正确处理
3. 命令行接口保持兼容
4. 代码结构更清晰，易于维护
5. 文档完整且准确

---
*设计文档创建时间：2026-04-20*
*设计者：Claude Code Assistant*