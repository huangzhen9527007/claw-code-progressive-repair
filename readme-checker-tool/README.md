# README 文档检查与修复工具

一个自动化的Python工具，用于检查和修复README.md文档中的重复内容、格式问题和其他常见问题。

## 功能特性

### 1. 重复内容检测
- **标题重复检测**：检测重复的标题（##、###等）
- **段落重复检测**：检测重复的段落内容
- **列表重复检测**：检测重复的列表项
- **表格重复检测**：检测重复的表格内容

### 2. 格式问题检测
- **标题层级检查**：检查标题层级是否正确（如###后面应该是####，而不是##）
- **链接格式检查**：检查Markdown链接格式是否正确
- **代码块格式检查**：检查代码块格式是否正确
- **列表格式检查**：检查列表格式是否一致

### 3. 内容优化
- **合并重复内容**：自动合并重复的段落和列表
- **修复格式问题**：自动修复检测到的格式问题
- **生成修复报告**：生成详细的修复报告
- **备份原始文件**：在修复前自动备份原始文件

### 4. 智能分析
- **内容相似度分析**：使用文本相似度算法检测相似内容
- **结构分析**：分析文档结构，识别异常模式
- **统计报告**：生成文档统计报告（字数、标题数、代码块数等）

## 使用方法

### 基本使用
```bash
# 检查README.md文档
python readme_checker.py

# 检查指定文档
python readme_checker.py --file path/to/your/README.md

# 检查并自动修复
python readme_checker.py --fix

# 生成详细报告
python readme_checker.py --report
```

### 命令行参数
| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--file` | `-f` | 要检查的文件路径 | `README.md` |
| `--fix` | `-x` | 自动修复检测到的问题 | `False` |
| `--report` | `-r` | 生成详细报告 | `False` |
| `--backup` | `-b` | 修复前创建备份 | `True` |
| `--similarity` | `-s` | 相似度阈值（0.0-1.0） | `0.8` |
| `--verbose` | `-v` | 详细输出模式 | `False` |

### 示例
```bash
# 基本检查
python readme_checker.py

# 检查并修复
python readme_checker.py --fix --verbose

# 检查指定文件并生成报告
python readme_checker.py --file docs/README.md --report

# 使用自定义相似度阈值
python readme_checker.py --similarity 0.9 --fix
```

## 检测规则

### 1. 标题重复规则
- 检测完全相同的标题（包括层级）
- 检测相似标题（相似度 > 阈值）
- 检测不合理的标题层级跳跃

### 2. 内容重复规则
- 检测完全相同的段落
- 检测高度相似的段落（相似度 > 阈值）
- 检测重复的列表项
- 检测重复的表格行

### 3. 格式规则
- Markdown标题格式：`# Title`、`## Subtitle`等
- 链接格式：`[text](url)`
- 代码块格式：```language\ncode\n```
- 列表格式：`- item` 或 `1. item`

## 输出示例

### 检查报告
```
README.md 检查报告
===================

文档统计：
- 总行数：2274
- 标题数：45
- 代码块数：12
- 链接数：8
- 列表项数：56

问题检测：
- 重复标题：3处
- 重复段落：2处
- 格式问题：5处
- 层级问题：1处

建议操作：
1. 合并第120-135行和第450-465行的重复内容
2. 修复第78行的标题层级
3. 修复第210行的链接格式
```

### 修复报告
```
README.md 修复报告
===================

修复操作：
- 已合并重复标题：## 功能特性 → 保留1处，删除2处
- 已合并重复段落：第120-135行与第450-465行合并
- 已修复标题层级：第78行 ### → ####
- 已修复链接格式：第210行 [text]url → [text](url)

备份文件：
- 原始文件已备份为：README.md.backup_20240420_143022
```

## 技术实现

### 核心算法
1. **文本相似度计算**：使用Levenshtein距离和Jaccard相似度
2. **模式匹配**：使用正则表达式匹配Markdown元素
3. **结构分析**：使用栈数据结构分析标题层级
4. **差异检测**：使用difflib进行内容差异分析

### 模块设计
- `checker.py` - 主检查器类
- `formatter.py` - 格式修复器类
- `analyzer.py` - 文档分析器类
- `reporter.py` - 报告生成器类
- `utils.py` - 工具函数

### 依赖
- Python 3.7+
- 标准库：`re`, `difflib`, `collections`, `pathlib`

## 集成到Claude Code技能

### 技能配置
```json
{
  "name": "readme-checker",
  "description": "检查和修复README.md文档的重复内容和格式问题",
  "triggerWords": [
    "/检查readme",
    "/readme检查",
    "/修复readme",
    "/readme修复"
  ],
  "command": "python readme_checker.py"
}
```

### 触发词
- `/检查readme` - 检查README.md文档
- `/readme检查` - 检查README.md文档
- `/修复readme` - 检查并修复README.md文档
- `/readme修复` - 检查并修复README.md文档

## 最佳实践

### 1. 定期检查
```bash
# 每周运行一次检查
python readme_checker.py --report >> readme_check.log
```

### 2. 版本控制集成
```bash
# 在提交前检查README.md
pre-commit:
  - python readme_checker.py --fix
```

### 3. CI/CD集成
```yaml
# GitHub Actions示例
name: README Check
on: [push, pull_request]
jobs:
  check-readme:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check README
        run: python readme_checker.py --report
```

## 故障排除

### 常见问题
1. **权限问题**：确保有文件读写权限
2. **编码问题**：文件使用UTF-8编码
3. **内存问题**：大文件可能需要更多内存
4. **性能问题**：相似度计算可能较慢，可调整阈值

### 调试模式
```bash
# 启用调试输出
python readme_checker.py --verbose

# 查看详细日志
python readme_checker.py --verbose 2> debug.log
```

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境
```bash
# 克隆仓库
git clone <repository>

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/
```

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解
- 编写单元测试
- 更新文档

## 许可证

MIT License