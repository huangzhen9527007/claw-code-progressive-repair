# claude-mem 插件命令 API 文档

## 概述

claude-mem 插件是 Claude Code 的记忆增强插件，提供强大的记忆搜索、知识库构建、计划制定和代码探索功能。本文档详细介绍了插件的所有命令、参数和使用方法。

## 插件信息

- **插件名称**: claude-mem
- **版本**: 12.1.0
- **作者**: Alex Newman
- **仓库**: https://github.com/thedotmack/claude-mem
- **许可证**: AGPL-3.0
- **安装位置**: `C:\Users\Administrator\.claude\plugins\cache\thedotmack\claude-mem\12.1.0`

## 核心功能

### 1. 记忆搜索（mem-search）

**用途**: 搜索过去的会话和工作记录

**命令格式**: `/claude-mem:mem-search "关键词"`

**示例**:
- `/claude-mem:mem-search "wechat"`
- `/claude-mem:mem-search "bug"`

#### 三层工作流程（必须遵循）

**重要原则**: 永远不要在没有过滤的情况下获取完整详情，这样可以节省 10 倍 tokens。

##### 第 1 步：搜索 - 获取带 ID 的索引

```javascript
search(query="authentication", limit=20, project="my-project")
```

**参数说明**:
- `query` - 搜索词（字符串）
- `limit` - 最大结果数（默认 20，最大 100）
- `project` - 项目名称过滤器
- `type` - 可选："observations"、"sessions" 或 "prompts"
- `obs_type` - 可选：逗号分隔的 bugfix, feature, decision, discovery, change
- `dateStart` / `dateEnd` - 日期范围（YYYY-MM-DD 格式）
- `orderBy` - 排序方式："date_desc"（默认）、"date_asc"、"relevance"

##### 第 2 步：时间线 - 获取感兴趣结果周围的上下文

```javascript
timeline(anchor=11131, depth_before=3, depth_after=3, project="my-project")
```

或自动查找锚点：

```javascript
timeline(query="authentication", depth_before=3, depth_after=3, project="my-project")
```

##### 第 3 步：获取 - 仅获取过滤后的 ID 的完整详情

```javascript
get_observations(ids=[11131, 10942])
```

**重要**: 批量获取多个观察结果，不要单独请求。

### 2. 知识代理（knowledge-agent）

**用途**: 构建和查询基于 AI 的知识库

#### 工作流程

##### 第 1 步：构建语料库

```javascript
build_corpus name="hooks-expertise" description="Everything about the hooks lifecycle" project="claude-mem" concepts="hooks" limit=500
```

##### 第 2 步：准备语料库

```javascript
prime_corpus name="hooks-expertise"
```

##### 第 3 步：查询

```javascript
query_corpus name="hooks-expertise" question="What are the 5 lifecycle hooks and when does each fire?"
```

##### 第 4 步：列出语料库

```javascript
list_corpora
```

### 3. 制定计划（make-plan）

**用途**: 创建详细的、分阶段的实施计划

#### 计划结构

##### 阶段 0：文档发现（总是第一步）

在计划实施之前，部署"文档发现"子代理来：
1. 搜索并阅读相关文档、示例和现有模式
2. 识别实际的 API、方法和签名
3. 创建简短的"允许的 API"列表
4. 注意要避免的反模式

##### 每个实施阶段必须包括：
1. **要实施什么** - 从文档中复制模式
2. **文档引用** - 引用要遵循的特定文件/行
3. **验证清单** - 如何证明此阶段有效
4. **反模式防护** - 不要做什么

##### 最终阶段：验证
1. 验证所有实现与文档匹配
2. 检查反模式
3. 运行测试确认功能

### 4. 执行计划（do）

**用途**: 使用子代理执行分阶段的实施计划

#### 执行协议

##### 每个阶段期间：
部署"实施"子代理来：
1. 按指定执行实施
2. 从文档复制模式，不要发明
3. 在使用不熟悉的 API 时在代码注释中引用文档来源
4. 如果 API 似乎缺失，停止并验证

##### 每个阶段之后：
部署子代理进行：
1. **运行验证清单** - 证明阶段有效
2. **反模式检查** - 检查计划中的已知不良模式
3. **代码质量审查** - 审查更改
4. **仅在验证通过后提交**

### 5. 智能探索（smart-explore）

**用途**: 使用 tree-sitter AST 解析支持 24 种语言

**支持语言**: JS, TS, Python, Go, Rust, Ruby, Java, C, C++, Kotlin, Swift, PHP, Elixir, Lua, Scala, Bash, Haskell, Zig, CSS, SCSS, TOML, YAML, SQL, Markdown

### 6. 时间线报告（timeline-report）

**用途**: 生成项目时间线报告

### 7. 版本更新（version-bump）

**用途**: 处理版本更新任务

## 命令参考手册

### 搜索命令

| 命令 | 参数 | 描述 | 示例 |
|------|------|------|------|
| `search` | `query`, `limit`, `project`, `type`, `obs_type`, `dateStart`, `dateEnd`, `orderBy` | 搜索记忆 | `search(query="bug", limit=20)` |
| `timeline` | `anchor`, `depth_before`, `depth_after`, `project`, `query` | 获取时间线上下文 | `timeline(anchor=11131, depth_before=3)` |
| `get_observations` | `ids`, `orderBy` | 获取观察详情 | `get_observations(ids=[11131, 10942])` |

### 知识库命令

| 命令 | 参数 | 描述 | 示例 |
|------|------|------|------|
| `build_corpus` | `name`, `description`, `project`, `concepts`, `limit` | 构建知识库语料库 | `build_corpus name="hooks-expertise"` |
| `prime_corpus` | `name` | 准备语料库 | `prime_corpus name="hooks-expertise"` |
| `query_corpus` | `name`, `question` | 查询知识库 | `query_corpus name="hooks-expertise" question="..."` |
| `list_corpora` | 无 | 列出所有语料库 | `list_corpora` |

### 计划命令

| 命令 | 参数 | 描述 | 示例 |
|------|------|------|------|
| `make-plan` | 任务描述 | 制定实施计划 | `/claude-mem:make-plan "实现自动记忆保存功能"` |
| `do` | 阶段编号 | 执行计划阶段 | `/claude-mem:do 1` |

### 探索命令

| 命令 | 参数 | 描述 | 示例 |
|------|------|------|------|
| `smart-explore` | 文件路径/模式 | 智能代码探索 | `/claude-mem:smart-explore "src/**/*.ts"` |
| `timeline-report` | 项目名称 | 生成时间线报告 | `/claude-mem:timeline-report "my-project"` |
| `version-bump` | 版本类型 | 版本更新 | `/claude-mem:version-bump "patch"` |

## 使用场景示例

### 场景 1：查找最近的 bug 修复

```javascript
// 第一步：搜索 bug 修复
search(query="bug", type="observations", obs_type="bugfix", limit=20, project="my-project")

// 第二步：获取时间线上下文
timeline(anchor=11131, depth_before=5, depth_after=5, project="my-project")

// 第三步：获取详情
get_observations(ids=[11131, 10942, 10855], orderBy="date_desc")
```

### 场景 2：构建专业知识库

```javascript
// 第一步：构建语料库
build_corpus name="wechat-integration" description="WeChat integration patterns and solutions" project="cloud-code" concepts="wechat,ilink,bridge" limit=300

// 第二步：准备语料库
prime_corpus name="wechat-integration"

// 第三步：查询
query_corpus name="wechat-integration" question="How to handle WeChat media encryption?"
```

### 场景 3：制定复杂功能实施计划

```javascript
// 制定计划
/claude-mem:make-plan "为项目添加自动记忆保存功能"

// 执行计划
/claude-mem:do 1  // 执行阶段1：文档发现
/claude-mem:do 2  // 执行阶段2：架构设计
/claude-mem:do 3  // 执行阶段3：代码实现
```

## 错误代码和故障排除

### 常见错误

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `MEM001` | 插件未找到 | 检查插件安装路径和配置 |
| `MEM002` | 搜索无结果 | 调整搜索参数或扩大范围 |
| `MEM003` | 语料库构建失败 | 检查项目路径和权限 |
| `MEM004` | 内存不足 | 减少搜索限制或语料库大小 |

### 故障排除步骤

1. **检查插件状态**
   ```bash
   # 查看插件列表
   claude plugins list
   
   # 检查插件配置
   cat ~/.claude/plugins.json
   ```

2. **验证项目路径**
   - 确保项目路径正确
   - 检查项目目录权限

3. **调整搜索参数**
   - 减少 `limit` 参数
   - 使用更具体的 `query`
   - 添加 `project` 过滤器

4. **重建语料库**
   ```javascript
   // 删除旧语料库
   // 重新构建
   build_corpus name="new-corpus" limit=100
   ```

## 最佳实践

### 1. 搜索优化
- **使用项目过滤器**: 始终指定 `project` 参数
- **分阶段获取**: 遵循三层工作流程
- **批量操作**: 批量获取观察结果，减少 API 调用

### 2. 知识库管理
- **保持专注**: 创建专门的知识库（如"钩子架构"、"WeChat集成"）
- **定期更新**: 添加新观察结果后重建语料库
- **合理大小**: 控制语料库大小（建议 100-500 条记录）

### 3. 计划制定
- **文档先行**: 总是从文档发现开始
- **分阶段实施**: 将复杂任务分解为可管理的阶段
- **验证每个阶段**: 确保每个阶段都经过充分测试

### 4. 性能优化
- **缓存结果**: 重复查询时重用结果
- **限制范围**: 使用日期范围和类型过滤器
- **异步处理**: 长时间操作使用异步模式

## 集成示例

### 与 WeChat CLI 集成

```javascript
// 搜索 WeChat 相关解决方案
search(query="wechat cli encoding", type="observations", project="cloud-code", limit=15)

// 构建 WeChat 知识库
build_corpus name="wechat-solutions" description="WeChat CLI encoding and integration solutions" project="cloud-code" concepts="wechat,encoding,cli" limit=200

// 查询特定问题
query_corpus name="wechat-solutions" question="How to fix Chinese encoding issues in WeChat CLI on Windows?"
```

### 与记忆系统集成

```javascript
// 搜索记忆系统配置
search(query="memory system configuration", type="observations", project="cloud-code")

// 获取时间线了解演变过程
timeline(query="memory consolidation", depth_before=10, depth_after=10, project="cloud-code")

// 构建记忆系统知识库
build_corpus name="memory-system" description="Memory system configuration and optimization" project="cloud-code" concepts="memory,configuration,consolidation" limit=150
```

## 更新日志

### v12.1.0
- 新增智能探索功能，支持 24 种编程语言
- 优化三层工作流程，提升搜索效率
- 改进语料库构建算法

### v12.0.0
- 引入知识代理系统
- 添加计划制定和执行功能
- 增强时间线报告功能

## 相关资源

- [claude-mem GitHub 仓库](https://github.com/thedotmack/claude-mem)
- [Claude Code 文档](https://docs.anthropic.com/claude/code)
- [插件开发指南](https://docs.anthropic.com/claude/code/plugins)

---

**文档版本**: 1.0.0  
**最后更新**: 2026-04-19  
**维护者**: 二次开发团队