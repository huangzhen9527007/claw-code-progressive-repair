# 项目文档目录

## 概述

`docs/` 目录是 Cloud Code 项目的技术文档和解决方案知识库。这里存储了项目开发过程中遇到的技术问题、解决方案、架构文档和最佳实践。

## 目录结构

```
docs/
├── README.md                    # 本文件，目录说明
├── solutions/                   # 技术解决方案文档
│   ├── README.md               # 解决方案目录说明
│   └── claude-mem-binary-fix/  # claude-mem插件二进制文件问题解决方案
├── architecture/                # 架构设计文档
│   └── README.md               # 架构文档说明
├── api/                        # API文档
│   └── README.md               # API文档说明
├── deployment/                 # 部署指南
│   └── README.md               # 部署指南说明
├── development/                # 开发指南
│   └── README.md               # 开发指南说明
└── troubleshooting/            # 故障排除手册
    └── README.md               # 故障排除说明
```

## 文档分类说明

### 1. solutions/ - 技术解决方案
记录项目中遇到的具体技术问题和解决方案。每个解决方案应该包含：
- 问题描述
- 解决方案矩阵
- 详细实施步骤
- 验证方法
- 故障排除

**当前解决方案：**
- [claude-mem插件原生二进制文件问题](./solutions/claude-mem-binary-fix/)
- [Hookify插件Windows兼容性修复](./solutions/hookify-windows-compatibility/)
- [WeChat CLI编码问题解决方案](./solutions/wechat-cli-encoding-fix/)
- [记忆系统整合与配置优化](./solutions/memory-system-consolidation/)
- [自动记忆保存功能集成解决方案](./solutions/auto-memory-saver-integration.md)
- [自动记忆保存功能集成解决方案](./solutions/auto-memory-saver-integration.md)

### 2. architecture/ - 架构设计
项目架构设计文档，包括：
- 系统架构图
- 组件设计
- 数据流设计
- 技术选型说明

**当前架构文档：**
- [LLM知识库架构模式](./architecture/llm-wiki-architecture.md)

**当前架构文档：**
- [LLM知识库架构模式](./architecture/llm-wiki-architecture.md)

### 3. api/ - API文档
项目API接口文档，包括：
- OpenAI兼容API适配器
- WeChat Bridge API
- 内部服务API

### 4. deployment/ - 部署指南
项目部署相关文档，包括：
- 环境要求
- 部署步骤
- 配置说明
- 监控和维护

### 5. development/ - 开发指南
开发相关文档，包括：
- 开发环境搭建
- 代码规范
- 测试指南
- 贡献指南

**当前开发文档：**
- [PATH环境变量配置指南](./development/path-configuration-guide.md)
- [文档系统操作指南](./development/documentation-system-operations-guide.md)
- [文档系统触发提示词指南](./development/trigger-prompt-examples-guide.md)

### 6. troubleshooting/ - 故障排除
常见问题故障排除手册，包括：
- 常见错误及解决方案
- 调试方法
- 日志分析

**当前故障排除文档：**
- [Windows CMD窗口行为问题排查指南](./troubleshooting/windows-cmd-window-behavior.md)

**当前故障排除文档：**
- [Windows CMD窗口行为问题排查指南](./troubleshooting/windows-cmd-window-behavior.md)

## 文档编写规范

### 文件命名
- 使用英文小写字母、数字和连字符
- 文件名应描述文档内容
- 示例：`claude-mem-binary-fix-knowledge-base.md`

### 文档结构
每个文档应该包含：
1. **标题和概述** - 文档目的和范围
2. **问题描述** - 详细描述问题
3. **解决方案** - 完整的解决方案
4. **实施步骤** - 逐步实施指南
5. **验证方法** - 如何验证解决方案有效
6. **故障排除** - 常见问题及解决方法
7. **参考资料** - 相关文档和链接

### 版本控制
- 所有文档都纳入版本控制
- 重要更新需要更新文档
- 保持文档与代码同步

## 与记忆系统的关系

### 项目文档 (`docs/`) vs 用户记忆 (`~/.claude/.../memory/`)

| 方面 | 项目文档 (`docs/`) | 用户记忆 (`memory/`) |
|------|-------------------|---------------------|
| **位置** | 项目代码目录中 | 用户配置目录中 |
| **内容** | 技术解决方案、架构文档 | 个人工作记忆、经验总结 |
| **版本控制** | 是，Git管理 | 否，个人存储 |
| **共享性** | 团队共享 | 个人使用 |
| **更新频率** | 代码变更时更新 | 工作过程中实时更新 |
| **目的** | 项目技术文档 | 个人工作效率提升 |

### 协作建议
1. **从记忆到文档**：重要的技术经验可以从记忆系统整理到项目文档
2. **文档引用记忆**：项目文档可以引用相关记忆条目
3. **保持一致性**：确保两者信息一致但不重复

## 如何贡献

### 添加新文档
1. 确定文档分类（solutions/architecture/api等）
2. 创建文档文件，遵循命名规范
3. 按照文档结构编写内容
4. 更新相关目录的README.md
5. 提交Pull Request

### 更新现有文档
1. 检查文档是否需要更新
2. 更新内容，保持结构完整
3. 更新版本和日期信息
4. 验证内容准确性

### 文档审核
- 技术解决方案需要经过验证
- 架构文档需要团队评审
- API文档需要与代码同步

## 相关链接

- [项目README](../README.md) - 项目总览
- [CLAUDE.md](../CLAUDE.md) - Claude Code工作指南
- [记忆系统](../../../.claude/projects/C--Users-Administrator-Desktop-projects-claudecode-yuanmaziyuan-cloud-code-rewrite-cloud-code-main/memory/) - 用户记忆系统

## 更新日志

### 2026-04-19
- 创建docs目录说明文档
- 定义目录结构和文档规范
- 说明与记忆系统的关系

### 2026-04-19 (更新)
- 添加自动记忆保存功能集成解决方案文档
- 添加Windows CMD窗口行为问题排查指南
- 添加PATH环境变量配置指南
- 更新各目录README.md文件链接
- 创建记忆知识整理工作成果总结文档

### 2026-04-19 (更新)
- 添加自动记忆保存功能集成解决方案文档
- 添加Windows CMD窗口行为问题排查指南
- 添加PATH环境变量配置指南
- 更新各目录README.md文件链接
- 创建记忆知识整理工作成果总结文档

### 2026-04-19 (新增)
- 添加文档系统操作指南（从记忆系统提取知识到项目文档的完整流程）
- 添加LLM知识库架构模式文档（使用LLM构建个人知识库的架构参考）
- 添加文档系统触发提示词指南（具体的触发提示词示例和模板）
- 优化文档分类和结构

---

**维护提示**：保持文档的时效性和准确性，定期review和更新文档内容。