# Claude Code 环境变量配置指南

本文档详细介绍了Claude Code支持的所有环境变量及其使用方法。

## 目录
1. [快速开始](#快速开始)
2. [环境变量优先级](#环境变量优先级)
3. [API提供商配置](#api提供商配置)
   - [OpenAI兼容API](#openai兼容api)
   - [Anthropic官方API](#anthropic官方api)
   - [AWS Bedrock](#aws-bedrock)
   - [Google Vertex AI](#google-vertex-ai)
   - [Microsoft Foundry](#microsoft-foundry)
4. [性能调优](#性能调优)
5. [功能标志](#功能标志)
6. [调试和日志](#调试和日志)
7. [常见问题](#常见问题)

## 快速开始

### 方法1：使用`.env`文件
在项目根目录创建`.env`文件：

```env
# 启用OpenAI兼容API
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_COMPAT_MODEL=deepseek-chat

# 上下文窗口配置
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400

# 输出token配置
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192
```

### 方法2：命令行设置
```bash
export CLAUDE_CODE_USE_OPENAI_COMPAT=true
export OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
export OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export OPENAI_COMPAT_MODEL=deepseek-chat
bun run dev
```

## 环境变量优先级

### 1. `max_tokens`优先级（OpenAI兼容API）
在OpenAI兼容API中，`max_tokens`的确定顺序为：
1. `CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI` - OpenAI特定设置
2. `CLAUDE_CODE_MAX_OUTPUT_TOKENS` - 全局设置
3. `anthropicParams.max_tokens` - 原始请求值
4. `8192` - 默认值

### 2. 上下文窗口优先级
1. `CLAUDE_CODE_MAX_CONTEXT_TOKENS`环境变量
2. 模型能力检测
3. `102400` - 默认值

### 3. 配置加载优先级
1. 命令行参数
2. `.env`文件
3. 系统环境变量
4. 默认值

## API提供商配置

### OpenAI兼容API
支持DeepSeek、Ollama、Qwen、MiniMax等任何OpenAI兼容API。

```env
# 必须设置此项以启用OpenAI兼容API
CLAUDE_CODE_USE_OPENAI_COMPAT=true

# API基础URL
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com

# API密钥（如果需要认证）
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 模型名称
OPENAI_COMPAT_MODEL=deepseek-chat
```

#### 常见配置示例

**DeepSeek:**
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_COMPAT_MODEL=deepseek-chat
```

**本地Ollama:**
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=http://localhost:11434
OPENAI_COMPAT_API_KEY=ollama
OPENAI_COMPAT_MODEL=llama3.2
```

**Qwen:**
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_COMPAT_MODEL=qwen-plus
```

### Anthropic官方API
使用Claude官方API。

```env
# API密钥
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# API基础URL（可选）
ANTHROPIC_BASE_URL=https://api.anthropic.com

# 默认模型
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# 小快速模型（用于工具调用等场景）
ANTHROPIC_SMALL_FAST_MODEL=claude-3-5-haiku-20241022
```

### AWS Bedrock
```env
# 启用Bedrock
CLAUDE_CODE_USE_BEDROCK=true

# AWS凭证通过AWS SDK默认方式配置
# 需要设置AWS_REGION或AWS_DEFAULT_REGION
```

### Google Vertex AI
```env
# 启用Vertex AI
CLAUDE_CODE_USE_VERTEX=true

# GCP项目ID
ANTHROPIC_VERTEX_PROJECT_ID=your-project-id

# GCP区域
CLOUD_ML_REGION=us-east5
```

### Microsoft Foundry
```env
# 启用Foundry
CLAUDE_CODE_USE_FOUNDRY=true

# Azure资源名称
ANTHROPIC_FOUNDRY_RESOURCE=your-resource-name

# 或直接设置基础URL
ANTHROPIC_FOUNDRY_BASE_URL=https://your-resource.services.ai.azure.com
```

## 性能调优

### 上下文窗口配置
```env
# 最大上下文token数
# 默认：102400
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400

# 自动压缩阈值
# 当上下文使用超过此值时触发自动压缩
# 默认：102400
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400
```

### 输出token配置
```env
# 全局最大输出token数
# 影响所有API提供商
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192

# OpenAI兼容API特定的max_tokens
# 仅影响OpenAI兼容API，优先级最高
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192
```

### 超时配置
```env
# API请求超时时间（毫秒）
# 默认：600000（10分钟）
API_TIMEOUT_MS=600000
```

### 流量控制
```env
# 禁用非必要流量（隐私模式）
# 禁用分析、遥测等非必要流量
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=false
```

## 功能标志

```env
# 禁用思考功能
CLAUDE_CODE_DISABLE_THINKING=false

# 简化输出模式
CLAUDE_CODE_STREAMLINED_OUTPUT=false

# 裸模式（跳过hooks、LSP、插件同步等）
CLAUDE_CODE_SIMPLE=false

# 禁用1M上下文（HIPAA合规性）
CLAUDE_CODE_DISABLE_1M_CONTEXT=false
```

## 调试和日志

```env
# 调试日志级别
DEBUG=*

# 维护项目工作目录
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=false
```

## 常见问题

### Q1: 如何选择API提供商？
- **OpenAI兼容API**：推荐，支持最多第三方服务
- **Anthropic官方API**：需要Claude订阅
- **AWS Bedrock**：适合AWS用户
- **Google Vertex AI**：适合GCP用户
- **Microsoft Foundry**：适合Azure用户

### Q2: 环境变量不生效？
1. 检查`.env`文件是否在项目根目录
2. 检查环境变量名称是否正确（区分大小写）
3. 检查是否有拼写错误
4. 重启应用使环境变量生效

### Q3: 如何查看当前使用的配置？
启动时查看控制台输出，会显示当前使用的API提供商和配置。

### Q4: 多个API提供商都配置了怎么办？
优先级顺序：
1. OpenAI兼容API（如果`CLAUDE_CODE_USE_OPENAI_COMPAT=true`）
2. Bedrock（如果`CLAUDE_CODE_USE_BEDROCK=true`）
3. Vertex AI（如果`CLAUDE_CODE_USE_VERTEX=true`）
4. Foundry（如果`CLAUDE_CODE_USE_FOUNDRY=true`）
5. Anthropic官方API（默认）

### Q5: 如何为不同项目使用不同配置？
创建多个`.env`文件，如`.env.deepseek`、`.env.ollama`，使用时重命名或复制：
```bash
cp .env.deepseek .env
bun run dev
```

## 参考
- [完整环境变量列表](.env.example)
- [项目README](../README.md)
- [OpenAI兼容API适配器](../src/services/api/openai-compat/)