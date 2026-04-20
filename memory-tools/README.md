# Claude Code 记忆工具插件

一个全面的记忆系统管理插件，帮助维护和修复记忆系统完整性。

## 功能特性

### 1. 记忆系统诊断
- **完整性检查**：验证记忆文件数量是否匹配索引数量
- **问题检测**：查找未索引文件、多余索引、重复索引
- **分类验证**：确保文件类型匹配索引分类
- **详细报告**：生成全面的诊断报告

### 2. 分类问题修复
检测并帮助修复7个常见分类问题：

1. **中文文件名在英文分类中** - 将中文文件重命名为英文
2. **混合语言描述** - 标准化索引描述
3. **不一致的分类** - 识别可能分类错误的文件
4. **缺少frontmatter类型声明** - 添加缺失的类型元数据
5. **frontmatter类型与索引不匹配** - 修复分类不匹配
6. **不一致的命名约定** - 标准化文件名格式
7. **缺失或不正确的类型元数据** - 验证并修复类型信息

### 3. 智能修复功能
- **试运行模式**：应用更改前预览
- **智能文件名翻译**：将中文文件名转换为英文
- **frontmatter生成**：自动添加缺失的元数据
- **索引重组**：将文件移动到正确的分类

## 安装

### 先决条件
```bash
pip install PyYAML
```

### 插件安装
1. 将 `memory-tools` 目录复制到Claude Code插件目录：
   ```
   ~/.claude/plugins/local/memory-tools/
   ```

2. 确保Claude Code配置为加载本地插件

3. 验证安装：
   ```bash
   claude-code --help | grep memory
   ```

## 新架构说明

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
└── src/                      # 所有Python源代码
    ├── __init__.py
    ├── memory_tools.py       # 主工具类（整合版）
    ├── cli.py               # 命令行接口
    ├── classification_fixer.py # 分类修复模块
    └── utils.py             # 工具函数
```

### 功能整合
- **完全整合**：将原有多个工具整合为统一架构
- **统一入口**：只需使用 `main.py` 即可访问所有功能
- **向后兼容**：支持所有旧版本命令行参数
- **模块化设计**：代码结构清晰，易于维护和扩展

### 7个分类问题的完整处理
工具完整检测并修复以下7个分类问题：
1. 中文文件名在英文分类中
2. 缺少frontmatter类型声明
3. 类型不匹配（frontmatter与索引）
4. 类型元数据问题
5. 混合语言描述问题（智能处理）
6. 不一致的命名约定
7. 命名约定问题分析

## 新架构说明

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
└── src/                      # 所有Python源代码
    ├── __init__.py
    ├── memory_tools.py       # 主工具类（整合版）
    ├── cli.py               # 命令行接口
    ├── classification_fixer.py # 分类修复模块
    └── utils.py             # 工具函数
```

### 功能整合
- **完全整合**：将原有多个工具整合为统一架构
- **统一入口**：只需使用 `main.py` 即可访问所有功能
- **向后兼容**：支持所有旧版本命令行参数
- **模块化设计**：代码结构清晰，易于维护和扩展

### 7个分类问题的完整处理
工具完整检测并修复以下7个分类问题：
1. 中文文件名在英文分类中
2. 缺少frontmatter类型声明
3. 类型不匹配（frontmatter与索引）
4. 类型元数据问题
5. 混合语言描述问题（智能处理）
6. 不一致的命名约定
7. 命名约定问题分析

## 使用方法

### 统一命令行界面
```bash
# 基本完整性检查
python main.py check

# 详细诊断报告
python main.py report

# 检查分类问题
python main.py classify

# 修复计划预览（试运行）
python main.py fix --dry-run

# 执行修复（谨慎使用）
python main.py fix --execute

# 修复命名约定问题
python main.py fix --execute --fix-naming
```

### 通过Claude Code使用
```bash
# 直接使用技能
claude-code memory-system-diagnosis --help

# 检查记忆系统
claude-code memory-system-diagnosis --check

# 生成分类报告
claude-code memory-system-diagnosis --classification-report
```

## 配置

### 记忆目录检测
工具按以下顺序自动检测记忆目录：
1. 当前工作目录中的 `./memory/`
2. `~/.claude/projects/*/memory/`（最近修改的）
3. `~/.claude/projects/default/memory/`（回退）

### 手动指定目录
```bash
python main.py --memory-dir /path/to/memory report
```

## 输出格式

### 人类可读格式
```bash
python main.py report
```

### JSON格式（用于自动化）
```bash
python main.py report --json
```

## 示例

### 示例1：基本检查
```bash
$ python main.py check
[MEMORY SYSTEM CHECK]
========================================
Memory files: 42
Index entries: 42
[OK] Counts match

[OK] No obvious problems found
========================================
```

### 示例2：分类报告
```bash
$ python main.py classify
============================================================
记忆系统分类问题报告
============================================================

总问题数: 7
问题类型数: 3

不一致的命名约定 (3个):
  1. SUMMARY.md
  2. GUIDE.md
  3. CONFIG.md

类型不匹配 (2个):
  1. config.md: frontmatter类型为'reference'，但索引在'project'中（应为'reference'）
  2. setup.md: frontmatter类型为'project'，但索引在'reference'中（应为'project'）

命名约定分析 (2个):
  命名约定分析（共42个文件）：
    kebab-case: 35个 (83.3%)
    snake_case: 5个 (11.9%)
    mixed: 2个 (4.8%)
  建议：统一命名约定，减少混合命名模式

修复建议:
----------------------------------------
1. 标准化命名约定 (3个文件)
2. 修复类型不匹配 (2个文件)
----------------------------------------
使用 --fix 参数进行修复（先使用 --dry-run 查看计划）
============================================================
```

### 示例3：修复计划预览
```bash
$ python src/memory_system_diagnosis_skill.py --fix-classification
============================================================
分类问题修复计划
============================================================

要重命名的文件 (3):
  用户角色.md → user_role.md
  项目概述.md → project_overview.md
  插件修复.md → plugin_fix.md

要添加frontmatter的文件 (2):
  SUMMARY.md
  GUIDE.md

要移动的索引 (2):
  config.md: Frontmatter类型: reference, 索引在: project
  setup.md: Frontmatter类型: project, 索引在: reference

============================================================
⚠️  这是试运行模式。要执行修复，请设置 dry_run=False
```

## 文件结构

```
memory-tools/
├── README.md                    # 本文档
├── QUICK_START.md              # 快速开始指南
├── plugin.json                 # 插件配置
├── package.json                # Node.js包信息
├── requirements.txt            # Python依赖
├── src/
│   ├── memory_system_diagnosis_skill.py  # 主Python脚本
│   └── memory_diagnosis_cli.py           # CLI包装器
├── skills/
│   └── memory-system-diagnosis/
│       └── SKILL.md            # 技能定义
└── test_*.py                   # 测试脚本
```

## 依赖

- **Python 3.6+**
- **PyYAML**: 用于解析markdown文件中的frontmatter
- **Claude Code**: 用于插件集成

## 测试

```bash
# 运行基本测试
python test_plugin.py

# 测试技能功能
python test_skill.py
```

## 安全特性

1. **试运行模式**：所有修复操作默认使用预览模式
2. **确认提示**：破坏性操作的交互式确认
3. **备份建议**：始终建议在修复前备份
4. **错误恢复**：全面的错误处理防止数据丢失
5. **验证**：应用更改前进行广泛验证

## 最佳实践

1. **始终先使用试运行**：应用更改前预览
2. **备份记忆系统**：修复前复制记忆目录
3. **查看分类报告**：修复前了解问题
4. **在开发环境测试**：先使用测试记忆系统
5. **监控更改**：跟踪修改内容

## 故障排除

### 常见问题

1. **PyYAML未安装**：
   ```bash
   pip install PyYAML
   ```

2. **找不到记忆目录**：
   ```bash
   python src/memory_system_diagnosis_skill.py --memory-dir /path/to/memory --check
   ```

3. **权限错误**：
   - 确保对记忆目录有读写权限
   - 使用适当的用户权限运行

4. **编码问题**：
   - 工具使用UTF-8编码
   - 确保终端支持UTF-8

### 获取帮助
- 查看 `QUICK_START.md` 获取快速设置
- 查看技能文档 `skills/memory-system-diagnosis/SKILL.md`
- 使用提供的测试脚本进行测试

## 贡献

1. Fork仓库
2. 创建特性分支
3. 使用中文文档进行更改
4. 彻底测试
5. 提交拉取请求

## 许可证

此插件按原样提供，用于Claude Code。

## 更新日志

### v1.1.0（当前）
- 添加分类问题检测和修复
- 英文编码确保最大兼容性
- 智能文件名翻译
- 增强的报告功能

### v1.0.0
- 初始发布，包含基本记忆系统诊断
- 完整性检查和问题检测
- 基本修复建议