# Cloud Code (OpenAI Compatible Fork) - 增强版

 Claude Code CLI 逆向还原项目的二次开发版本adoresever/cloud-code：**新增 OpenAI 兼容 API 适配层** + **微信远程控制桥接**。本版本在adoresever/cloud-code项目基础上进行了全面优化和增强。

> Maintained by **二次开发团队**
>
> 基于Claude Code CLI逆向还原项目的二次开发版本，新增OpenAI兼容API适配层和微信远程控制桥接。本版本在adoresever/cloud-code项目基础上进行了五大核心改进。

## 🚀 新旧项目对比：五大核心改进

本项目主要基于衍生项目（adoresever/cloud-code）及其他相关衍生项目（T8版和土豆版）进行了全面优化，主要改进点如下：

### 一、便捷配置.env双端启动和内置选项卡配置同时并存

**原项目问题：**
- 没有`.env`文件支持，只能通过环境变量或交互式界面配置
- 缺少配置持久化和管理机制

**本版本改进：**
1. **新增`.env`文件系统**：
   - `.env.example`：完整的配置模板（180+行详细配置）
   - `.env`：用户配置文件
   - `ENVIRONMENT_VARIABLES.md`：详细配置文档（58个配置项说明）

2. **双端配置支持**：
   - 环境变量配置（`.env`文件）
   - 交互式配置界面（`OpenAICompatSetup.tsx`）
   - 配置自动保存到`~/.claude.json`

3. **预设提供商**：
   ```typescript
   const PROVIDER_PRESETS = [
     { label: '优云智算', value: 'modelverse' },
     { label: 'DeepSeek', value: 'deepseek' },
     { label: 'Ollama (local)', value: 'ollama' },
     { label: 'Custom URL', value: 'custom' },
   ];
   ```

### 二、.env配置优化，覆盖更多配置，尽量完整

**原项目问题：**
- 只有基本的OpenAI兼容API配置
- 缺少上下文窗口、输出限制等高级配置
- 没有配置文档

**本版本改进：**
1. **完整的配置分类**：
   - API提供商配置（OpenAI兼容、Anthropic、Bedrock、Vertex、Foundry）
   - 上下文窗口配置（`CLAUDE_CODE_MAX_CONTEXT_TOKENS`）
   - 输出token配置（`CLAUDE_CODE_MAX_OUTPUT_TOKENS`）
   - 性能调优配置（`API_TIMEOUT_MS`）
   - 功能标志配置（`CLAUDE_CODE_DISABLE_THINKING`等）

2. **详细的文档说明**：
   - `ENVIRONMENT_VARIABLES.md`：58个配置项的详细说明
   - 配置优先级说明
   - 常见问题解答

3. **配置示例丰富**：
   ```env
   # 示例1：使用DeepSeek作为OpenAI兼容API
   CLAUDE_CODE_USE_OPENAI_COMPAT=true
   OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
   OPENAI_COMPAT_API_KEY=sk-xxx
   OPENAI_COMPAT_MODEL=deepseek-chat
   
   # 示例2：使用本地Ollama
   CLAUDE_CODE_USE_OPENAI_COMPAT=true
   OPENAI_COMPAT_BASE_URL=http://localhost:11434
   OPENAI_COMPAT_API_KEY=ollama
   OPENAI_COMPAT_MODEL=llama3.2
   ```

### 三、解决国产模型适配和兼容性问题

**原项目问题**：
- 直接使用anthropicParams.max_tokens，没有环境变量覆盖
- 国产模型可能因token限制返回API错误
- 缺少消息序列处理优化

**本版本改进**：
```typescript
// Determine max_tokens value for OpenAI-compatible APIs
// Priority (from highest to lowest):
// 1. CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI - OpenAI-specific override
// 2. CLAUDE_CODE_MAX_OUTPUT_TOKENS - Global setting for all APIs
// 3. anthropicParams.max_tokens - From original Anthropic request
// 4. Default 8192 - Fallback value
let maxTokens = 8192;

// 1. Check for OpenAI-specific environment variable (highest priority)
if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI) {
  const openaiMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI, 10);
  if (!isNaN(openaiMaxTokens) && openaiMaxTokens > 0) {
    maxTokens = openaiMaxTokens;
  }
}
// 2. Check for global environment variable
else if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS) {
  const envMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS, 10);
  if (!isNaN(envMaxTokens) && envMaxTokens > 0) {
    maxTokens = envMaxTokens;
  }
}
// 3. Use anthropicParams.max_tokens if no environment variables set
else if (anthropicParams.max_tokens !== undefined && anthropicParams.max_tokens > 0) {
  maxTokens = anthropicParams.max_tokens;
}
// 4. Default to 8192 (already set)
```

**新增的消息序列处理**：
```typescript
function postprocessMessages(messages: any[]): any[] {
  // 解决国产模型对连续相同角色消息的兼容性问题
  // Anthropic允许连续相同角色消息，但OpenAI格式要求严格交替
  // 国产模型（MiniMax、GLM、Qwen等）对此处理不一致
}
```

**解决的问题**：
- **API error问题**：通过优先级处理max_tokens，避免国产模型token限制错误
- **MAX_OUTPUT_TOKENS问题**：支持环境变量覆盖，适配不同模型的token限制
- **MAXIMUM CONTEXT LENGTH问题**：通过`CLAUDE_CODE_MAX_CONTEXT_TOKENS`配置上下文窗口
- **消息序列兼容性**：`postprocessMessages()`解决国产模型对消息格式的严格要求

### 四、环境变量的优先级适配和模型配置优先级适配问题

**原项目问题**：
- 简单的环境变量检查，没有优先级系统
- 缺少配置加载优先级定义
- 模型选择逻辑简单

**本版本改进**：

1. **max_tokens优先级系统**（已在上文展示）
2. **配置加载优先级**：
   ```
   1. 命令行参数
   2. .env文件
   3. 系统环境变量
   4. 默认值
   ```

3. **API提供商优先级**：
   ```
   1. OpenAI兼容API（如果CLAUDE_CODE_USE_OPENAI_COMPAT=true）
   2. Bedrock（如果CLAUDE_CODE_USE_BEDROCK=true）
   3. Vertex AI（如果CLAUDE_CODE_USE_VERTEX=true）
   4. Foundry（如果CLAUDE_CODE_USE_FOUNDRY=true）
   5. Anthropic官方API（默认）
   ```

4. **上下文窗口优先级**：
   ```
   1. CLAUDE_CODE_MAX_CONTEXT_TOKENS环境变量
   2. 模型能力检测
   3. 102400 - 默认值
   ```

### 五、硬编码参数转为环境变量实现更灵活的配置

**原项目问题**：
- 许多参数硬编码在代码中
- 无法根据用户需求调整
- 缺少性能调优选项

**本版本改进**：

1. **上下文窗口配置**：
   ```env
   # 最大上下文token数（默认：102400）
   CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
   
   # 自动压缩阈值（默认：102400）
   CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400
   
   # 禁用1M上下文（HIPAA合规性）
   CLAUDE_CODE_DISABLE_1M_CONTEXT=false
   ```

2. **输出限制配置**：
   ```env
   # 全局最大输出token数（影响所有API提供商）
   CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
   
   # OpenAI兼容API特定的max_tokens（优先级最高）
   CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192
   ```

3. **性能配置**：
   ```env
   # API请求超时时间（毫秒）（默认：600000，10分钟）
   API_TIMEOUT_MS=600000
   
   # 禁用非必要流量（隐私模式）
   CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=false
   ```

4. **功能标志**：
   ```env
   # 禁用思考功能
   CLAUDE_CODE_DISABLE_THINKING=false
   
   # 简化输出模式
   CLAUDE_CODE_STREAMLINED_OUTPUT=false
   
   # 裸模式（跳过hooks、LSP、插件同步等）
   CLAUDE_CODE_SIMPLE=false
   ```

### 六、其他重要改进

1. **项目文档完善**：
   - 新增`BAT_STARTUP_GUIDE.md`：Windows启动指南
   - 新增`启动说明.txt`：中文使用说明
   - 更新`RECORD.md`：详细开发记录
   - 更新`TODO.md`：清晰的待办事项

2. **Windows支持优化**：
   - 新增`TUI启动器.bat`、`run.bat`、`start.bat`、`桌面版启动器.bat`
   - 新增`test_path.bat`：路径测试脚本
   - 新增`setup-env.sh`：环境设置脚本

3. **Electron桌面版支持**：
   ```json
   "scripts": {
     "desktop": "cd desktop && electron .",
     "desktop:dev": "concurrently \"cd desktop && electron .\" \"cd desktop && bun run dev\""
   }
   ```

### 总结对比表

| 功能 | 原项目 | 本版本 | 改进点 |
|------|--------|--------|--------|
| 配置方式 | 环境变量/交互界面 | .env文件+交互界面+配置文件 | 三端配置并存 |
| 配置文档 | 无 | ENVIRONMENT_VARIABLES.md（详细） | 完整配置指南 |
| 国产模型适配 | 基础适配 | 深度优化（消息序列、token优先级） | 解决API错误 |
| 环境变量优先级 | 无明确规则 | 四级优先级系统 | 避免配置冲突 |
| 硬编码参数 | 较多 | 大部分转为环境变量 | 高度可配置 |
| Windows支持 | 基础 | 完整（bat脚本、桌面版） | 更好的Windows体验 |
| 项目文档 | 基础README | 多文档系统 | 更易上手 |
| 性能调优 | 有限 | 全面的性能配置 | 更好的性能控制 |

**核心改进总结**：
1. **配置系统全面升级**：从单一配置到多端配置，支持环境变量优先级
2. **国产模型深度优化**：专门解决DeepSeek、MiniMax、Qwen等国产模型的兼容性问题
3. **用户体验大幅提升**：交互式配置、配置持久化、详细文档
4. **灵活性极大增强**：硬编码参数转为环境变量，支持高度定制
5. **平台支持更完善**：特别是Windows平台的优化支持

---

## 功能特性

## 功能特性

- **OpenAI 兼容 API 适配层** — 接入 DeepSeek、MiniMax、Ollama、优云智算等任意 OpenAI 兼容 API
- **微信远程控制** — 通过腾讯官方 iLink Bot API（ClawBot 插件），在手机微信中远程操控 cloud-code
- **🐾 /buddy 宠物系统** — 已解锁 Claude Code 隐藏的 Tamagotchi 终端宠物，18 物种 × 5 稀有度 × Shiny，支持暴力搜索最稀有组合
- 支持文字、图片、文件、语音、视频的收发
- 零外部依赖（微信桥接），纯 Bun 原生 API

## 快速开始

### 环境要求

- [Bun](https://bun.sh/) >= 1.3.11（必须最新版，`bun upgrade`）
- Node.js >= 18
- 微信 iOS 最新版 + ClawBot 插件（我 → 设置 → 插件 → ClawBot）

### 安装 & 运行

```bash
bun install
bun run dev
```

启动后选择第四个选项 `OpenAI-compatible API`，按引导输入 API 地址、Key、模型名即可：

```
Select login method:
  1. Claude account with subscription · Pro, Max, Team, or Enterprise
  2. Anthropic Console account · API usage billing
  3. 3rd-party platform · Amazon Bedrock, Microsoft Foundry, or Vertex AI
❯ 4. OpenAI-compatible API · DeepSeek, Ollama, QwQ, etc.
```

配置自动保存到 `~/.claude.json`，下次启动无需重复输入。

### 环境变量方式（可选）

```bash
export CLAUDE_CODE_USE_OPENAI_COMPAT=1
export OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
export OPENAI_COMPAT_API_KEY=sk-xxx
export OPENAI_COMPAT_MODEL=deepseek-chat
bun run dev
```

## 高级配置

### 环境变量配置系统

本版本提供了完整的环境变量配置系统，支持180+个配置项。以下是核心配置分类：

#### 1. API提供商配置
```env
# OpenAI兼容API（推荐使用）
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
OPENAI_COMPAT_API_KEY=sk-xxx
OPENAI_COMPAT_MODEL=deepseek-chat

# Anthropic官方API（备用）
ANTHROPIC_API_KEY=sk-ant-api03-xxx
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# AWS Bedrock
CLAUDE_CODE_USE_BEDROCK=false

# Google Vertex AI
CLAUDE_CODE_USE_VERTEX=false

# Microsoft Foundry
CLAUDE_CODE_USE_FOUNDRY=false
```

#### 2. 上下文窗口配置
```env
# 最大上下文token数（默认：102400）
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400

# 自动压缩阈值（当上下文使用超过此值时触发自动压缩）
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400

# 禁用1M上下文（HIPAA合规性）
CLAUDE_CODE_DISABLE_1M_CONTEXT=false
```

#### 3. 输出token配置（优先级系统）
```env
# 全局最大输出token数（影响所有API提供商）
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192

# OpenAI兼容API特定的max_tokens（优先级最高）
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192
```

**优先级顺序**：
1. `CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI` - OpenAI特定设置
2. `CLAUDE_CODE_MAX_OUTPUT_TOKENS` - 全局设置
3. `anthropicParams.max_tokens` - 原始请求值
4. `8192` - 默认值

#### 4. 性能调优配置
```env
# API请求超时时间（毫秒）（默认：600000，10分钟）
API_TIMEOUT_MS=600000

# 禁用非必要流量（隐私模式）
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=false

# 维护项目工作目录
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=false
```

#### 5. 功能标志配置
```env
# 禁用思考功能
CLAUDE_CODE_DISABLE_THINKING=false

# 简化输出模式
CLAUDE_CODE_STREAMLINED_OUTPUT=false

# 裸模式（跳过hooks、LSP、插件同步等）
CLAUDE_CODE_SIMPLE=false
```

#### 6. 调试和日志配置
```env
# 调试日志级别
DEBUG=*

# 授权标志（用于启动和发布控制）
AUTHORIZED=true
```

### 配置优先级系统

#### 配置加载优先级
1. 命令行参数
2. `.env`文件
3. 系统环境变量
4. 默认值

#### API提供商优先级
1. OpenAI兼容API（如果`CLAUDE_CODE_USE_OPENAI_COMPAT=true`）
2. Bedrock（如果`CLAUDE_CODE_USE_BEDROCK=true`）
3. Vertex AI（如果`CLAUDE_CODE_USE_VERTEX=true`）
4. Foundry（如果`CLAUDE_CODE_USE_FOUNDRY=true`）
5. Anthropic官方API（默认）

#### 上下文窗口优先级
1. `CLAUDE_CODE_MAX_CONTEXT_TOKENS`环境变量
2. 模型能力检测
3. `102400` - 默认值

### 使用.env文件配置（推荐）

创建 `.env` 文件在项目根目录，内容示例：

```env
# ============================================
# OpenAI兼容API配置（取消注释以启用）
# ============================================

# 启用OpenAI兼容API
CLAUDE_CODE_USE_OPENAI_COMPAT=true

# OpenAI兼容API基础URL
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com

# OpenAI兼容API密钥
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI兼容API模型名称
OPENAI_COMPAT_MODEL=deepseek-chat

# ============================================
# 上下文窗口配置
# ============================================

# 最大上下文token数
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400

# 自动压缩窗口阈值
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400

# ============================================
# 输出token配置
# ============================================

# 全局最大输出token数
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192

# OpenAI兼容API特定的max_tokens设置（优先级最高）
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192

# ============================================
# 性能配置
# ============================================

# API超时时间（毫秒）
API_TIMEOUT_MS=600000

# 禁用非必要流量
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=false
```

### 常见配置示例

#### 示例1：使用DeepSeek作为OpenAI兼容API
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
OPENAI_COMPAT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_COMPAT_MODEL=deepseek-chat
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192
```

#### 示例2：使用本地Ollama
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=http://localhost:11434
OPENAI_COMPAT_API_KEY=ollama
OPENAI_COMPAT_MODEL=llama3.2
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=4096
```

#### 示例3：使用Anthropic官方API
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
```

详细的环境变量说明请参考：
- [`.env.example`](.env.example) - 完整的环境变量示例（180+行）
- [`ENVIRONMENT_VARIABLES.md`](ENVIRONMENT_VARIABLES.md) - 详细的环境变量配置指南（58个配置项说明）

## 微信远程控制

在手机微信中远程控制电脑上的 cloud-code，基于腾讯官方 iLink Bot API，**不会封号**。

### 使用方法

```bash
# 启动微信桥接（首次会显示二维码，微信扫码）
bun run wechat

# 强制重新扫码
bun run wechat:login
```

扫码成功后，在微信中给 ClawBot 发消息即可远程使用 cloud-code。

### 支持的消息类型

| 类型 | 入站（微信→Bot） | 出站（Bot→微信） |
|:----:|:---:|:---:|
| 文字 | ✅ 自动分片 | ✅ 自动分片 |
| 图片 | ✅ CDN 下载解密 | ✅ CDN 加密上传 |
| 文件 | ✅ 任意文件类型 | ✅ 任意文件类型 |
| 语音 | ✅ 自动转文字 | — |
| 视频 | ✅ CDN 下载解密 | ✅ CDN 加密上传 |

### 架构

```
手机微信 ──发消息──→ iLink API (ilinkai.weixin.qq.com)
                         ↑ HTTP 长轮询
                     wechat-bridge.ts
                         ↓ spawn bun -p
                     cloud-code CLI
                         ↓
                     OpenAI 兼容适配层 → LLM API
                         ↓
                     stdout → sendmessage → 微信
```

### 技术细节

- 协议: 腾讯官方 iLink Bot API（HTTP/JSON，非逆向）
- 媒体加密: AES-128-ECB + PKCS7 padding
- CDN: `novac2c.cdn.weixin.qq.com/c2c`
- Token 有效期: 24 小时，过期自动提示重新扫码
- 凭证存储: `~/.wechat-bridge/`（不在项目目录内）

## OpenAI 兼容 API 适配层

### 支持的 API 提供商

| 提供商 | Base URL | 示例模型 | 特点 |
|--------|----------|----------|------|
| 优云智算 | `https://api.modelverse.cn/v1` | MiniMax-M2.5, gpt-5.4 | 国产优质模型，支持长上下文 |
| DeepSeek | `https://api.deepseek.com` | deepseek-chat, deepseek-reasoner | 性价比高，支持思考模型 |
| Ollama | `http://localhost:11434` | qwen2.5:7b, llama3 | 本地部署，隐私安全 |
| Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-plus, qwen-max | 阿里通义千问 |
| 任意 OpenAI 兼容 API | 自定义 URL | 自定义模型名 | 支持任何兼容OpenAI格式的API |

### 适配层架构

适配层位于 `src/services/api/openai-compat/`，通过 duck-typing 伪装 Anthropic SDK 客户端，上游代码零改动：

```
claude.ts → getAnthropicClient() → createOpenAICompatClient()
  ├─ request-adapter.ts: Anthropic params → OpenAI params
  ├─ fetch() → 第三方 API
  └─ stream-adapter.ts: OpenAI SSE → Anthropic 事件流
```

### 核心适配组件

#### 1. 请求适配器 (`request-adapter.ts`)
- **格式转换**：Anthropic消息格式 → OpenAI聊天完成格式
- **系统提示处理**：Anthropic的top-level `system`字段 → OpenAI的`role=system`消息
- **多模态支持**：图像base64编码 → data URI格式
- **工具调用适配**：`input_schema` → `function.parameters`，`tool_result` → `role=tool`
- **消息序列优化**：`postprocessMessages()`解决国产模型对连续相同角色消息的兼容性问题

#### 2. 流式适配器 (`stream-adapter.ts`)
- **流式转换**：OpenAI SSE流 → Anthropic事件流
- **状态管理**：维护转换状态，处理复杂的块生命周期
- **工具调用跟踪**：处理OpenAI流式工具调用
- **思考标签解析**：支持QwQ-style模型的`<think>`标签

#### 3. 思考适配器 (`thinking-adapter.ts`)
- **思考模型支持**：DeepSeek R1的`reasoning_content`处理
- **标签解析**：QwQ模型的`<think>`标签解析
- **思考内容提取**：从响应中提取思考内容

### 国产模型兼容性优化

#### 解决的主要问题：
1. **API error问题**：通过优先级处理max_tokens，避免国产模型token限制错误
2. **MAX_OUTPUT_TOKENS问题**：支持环境变量覆盖，适配不同模型的token限制
3. **MAXIMUM CONTEXT LENGTH问题**：通过`CLAUDE_CODE_MAX_CONTEXT_TOKENS`配置上下文窗口
4. **消息序列兼容性**：`postprocessMessages()`解决国产模型对消息格式的严格要求

#### 消息序列处理优化：
```typescript
function postprocessMessages(messages: any[]): any[] {
  // Anthropic允许连续相同角色消息，但OpenAI格式要求严格交替
  // 国产模型（MiniMax、GLM、Qwen等）对此处理不一致
  // 此函数合并连续相同角色的消息，确保兼容性
}
```

### 配置自动加载

启动时自动从以下位置加载配置：
1. `~/.claude.json` - 用户配置文件（交互式配置保存位置）
2. `.env`文件 - 项目环境变量
3. 系统环境变量

配置优先级确保用户配置不会被意外覆盖。

## 项目结构

```
cloud-code/
├── src/
│   ├── entrypoints/cli.tsx                # 入口（含 OpenAI 配置自动加载）
│   ├── buddy/                             # 🐾 Tamagotchi 宠物系统（已解锁）
│   │   ├── companion.ts                   # 确定性抽卡逻辑（Mulberry32 PRNG）
│   │   ├── CompanionSprite.tsx            # 终端精灵渲染（React + Ink）
│   │   ├── sprites.ts                     # 18 物种 × 3 帧 ASCII art
│   │   ├── types.ts                       # 物种/稀有度/属性类型定义
│   │   ├── prompt.ts                      # Companion 提示词注入
│   │   └── useBuddyNotification.tsx       # 彩虹通知 hook
│   ├── commands/
│   │   └── buddy/index.ts                 # /buddy 命令实现（已补全）
│   ├── services/api/
│   │   ├── client.ts                      # Provider 选择（含 openai_compat 分支）
│   │   └── openai-compat/                 # OpenAI 兼容适配层
│   │       ├── index.ts                   # 伪 Anthropic 客户端
│   │       ├── request-adapter.ts         # 请求格式转换
│   │       ├── stream-adapter.ts          # 流式响应转换
│   │       └── thinking-adapter.ts        # 思考模型适配
│   └── components/
│       └── OpenAICompatSetup.tsx          # 交互式配置界面
├── scripts/
│   ├── wechat-bridge.ts                   # 微信桥接主脚本
│   └── ilink.ts                           # iLink 协议封装
├── CLAUDE.md
├── README.md
├── RECORD.md
└── TODO.md
```

## 其他命令

```bash
# 管道模式
echo "say hello" | bun run src/entrypoints/cli.tsx -p

# 构建
bun run build
```

## 🐾 /buddy 宠物系统（已解锁）

2026年3月31日 Claude Code v2.1.88 源码泄露事件中，社区在 `src/buddy/` 目录发现了一个完整但被编译时 flag 隐藏的 **Tamagotchi 风格终端宠物系统**。本项目已将其完整解锁——你的 AI 编程助手现在有了一只会卖萌的伙伴。

### 它长什么样？

```
                                                                              -+-
❯ 帮我重构这个函数                                                           /^\  /^\
  ⎿  好的，让我看看这个函数的结构…                                          <  @  @  >
                                                                            (   ~~   )
                                                                             `-vvvv-´
                                                                              Ember
```

宠物常驻在终端右侧，有 3 帧待机动画（500ms/帧）。宽终端（≥100列）显示完整 ASCII 精灵 + 语音气泡；窄终端压缩为一行脸部表情。用 `/buddy pet` 撸它时会飘出爱心动画。

### 物种图鉴

共 **18 个物种**，每个都有独立的 5 行×12 字符 ASCII art 和 3 帧动画：

| 物种 | 脸 | 特点 |
|------|:---:|------|
| 🦆 duck | `(·>` | 经典小黄鸭，尾巴会摇 |
| 🪿 goose | `(·>` | 脖子会伸缩，有攻击性 |
| 🫧 blob | `(··)` | 会膨胀收缩的果冻 |
| 🐱 cat | `=·ω·=` | ω 嘴，尾巴会晃 |
| 🐉 dragon | `<·~·>` | 头顶冒烟，有翅膀 |
| 🐙 octopus | `~(··)~` | 触手会交替摆动 |
| 🦉 owl | `(·)(·)` | 大眼睛，会眨眼 |
| 🐧 penguin | `(·>)` | 翅膀会拍 |
| 🐢 turtle | `[·_·]` | 壳上花纹会变 |
| 🐌 snail | `·(@)` | 壳上有螺旋纹 |
| 👻 ghost | `/··\` | 底部波浪飘动 |
| 🦎 axolotl | `}·.·{` | 腮会左右摆动 |
| 🫏 capybara | `(·oo·)` | 最大号的脸 |
| 🌵 cactus | `\|·  ·\|` | 手臂会上下 |
| 🤖 robot | `[··]` | 天线会闪 |
| 🐇 rabbit | `(··..)` | 耳朵会歪 |
| 🍄 mushroom | `\|·  ·\|` | 帽子斑点会变 |
| 🐈‍⬛ chonk | `(·.·)` | 大胖猫，尾巴摇 |

### 稀有度体系

| 稀有度 | 概率 | 颜色 | 星级 | 帽子 | 属性下限 |
|--------|:----:|:----:|:----:|:----:|:--------:|
| Common | 60% | 灰色 | ★ | 无 | 5 |
| Uncommon | 25% | 绿色 | ★★ | 随机 | 15 |
| Rare | 10% | 蓝色 | ★★★ | 随机 | 25 |
| Epic | 4% | 金色 | ★★★★ | 随机 | 35 |
| **Legendary** | **1%** | **红色** | **★★★★★** | **随机** | **50** |

在此基础上，每只 buddy 还有独立的 **1% Shiny 概率**（发光特效）。

**最稀有的组合是 ✦ SHINY LEGENDARY — 总概率 0.01%（万分之一）。**

每只 buddy 还有 5 个属性：DEBUGGING、PATIENCE、CHAOS、WISDOM、SNARK。一个高峰属性（可达 100）、一个低谷属性（可低至 1）、其余随机分布。Legendary 的属性下限为 50，远高于 Common 的 5。

装饰系统包含 6 种眼型（`·` `✦` `×` `◉` `@` `°`）和 7 种帽子（crown 👑、tophat 🎩、propeller、halo、wizard 🧙、beanie、tinyduck 🦆）。

### 快速上手

```bash
# 启动（已默认配置 --feature=BUDDY）
bun run dev

# 孵化宠物（首次）或查看卡片
/buddy

# 撸宠物（飘爱心）
/buddy pet

# 隐藏 / 恢复
/buddy mute
/buddy unmute
```

### 解锁原理

仅需 **3 处改动**，不触碰任何核心功能代码：

| # | 文件 | 改动 | 说明 |
|:-:|------|------|------|
| ① | `package.json` | dev 命令加 `--feature=BUDDY` | Bun 原生运行时 flag，让 `feature('BUDDY')` 返回 true |
| ② | `src/commands/buddy/index.ts` | 从空 stub 补全为完整命令 | 泄露源码中此文件为自动生成的空壳 |
| ③ | `src/buddy/companion.ts` | 修改 SALT 值（可选） | 选择想要的 buddy 物种和稀有度 |

**对主体功能的影响：零。** `--feature=BUDDY` 仅解锁 buddy 子系统，代码编辑、API 通信、权限管理、会话管理等核心模块完全不受影响。唯一副作用是有 companion 时 system prompt 多注入约 5 行提示词（告诉模型旁边有只宠物）。

### 重新抽卡（换 buddy）

你的 buddy 由 `hash(userId + SALT)` 确定性生成——同一 userId + SALT 永远得到同一只。想换一只需要改种子：

```bash
# 1. 修改 SALT（数字随便换）
sed -i "s/const SALT = .*/const SALT = 'friend-2026-新数字'/" src/buddy/companion.ts

# 2. 清除旧 companion 数据
#    Linux / macOS:
bun -e "const fs=require('fs'),p=require('os').homedir()+'/.claude.json';
const c=JSON.parse(fs.readFileSync(p,'utf-8'));delete c.companion;
fs.writeFileSync(p,JSON.stringify(c,null,2));console.log('cleared')"

#    Windows (PowerShell):
bun -e "const fs=require('fs'),p=require('os').homedir()+'\\.claude.json';const c=JSON.parse(fs.readFileSync(p,'utf-8'));delete c.companion;fs.writeFileSync(p,JSON.stringify(c,null,2));console.log('cleared')"

# 3. 重启并输入 /buddy
bun run dev
```

### 暴力搜索最稀有的 buddy

不想靠运气？可以用脚本预先搜索哪个 SALT 值能出 Legendary 甚至 Shiny Legendary。

**第一步：获取你的 userId**

```bash
# Linux / macOS
grep userID ~/.claude.json

# Windows (PowerShell)
Select-String userID $env:USERPROFILE\.claude.json
```

**第二步：运行搜索脚本**

将下面脚本保存为 `search-buddy.mjs`，把 `uid` 替换为你的真实 userId：

```javascript
// search-buddy.mjs — 用 bun 运行: bun run search-buddy.mjs
const SPECIES = ['duck','goose','blob','cat','dragon','octopus','owl','penguin',
  'turtle','snail','ghost','axolotl','capybara','cactus','robot','rabbit','mushroom','chonk'];
const RARITIES = ['common','uncommon','rare','epic','legendary'];
const W = {common:60,uncommon:25,rare:10,epic:4,legendary:1};
const EYES = ['·','✦','×','◉','@','°'];
const HATS = ['none','crown','tophat','propeller','halo','wizard','beanie','tinyduck'];

function mulberry32(seed) {
  let a = seed >>> 0;
  return function() {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function bunHash(s) { return Number(BigInt(Bun.hash(s)) & 0xffffffffn); }
function pick(rng, arr) { return arr[Math.floor(rng() * arr.length)]; }
function rollRarity(rng) {
  let r = rng() * 100;
  for (const x of RARITIES) { r -= W[x]; if (r < 0) return x; }
  return 'common';
}

// ⚠️ 替换为你的真实 userId
const uid = '你的userID';
const MAX = 500000;

console.log(`Searching ${MAX} salts for user: ${uid.slice(0,16)}...`);
console.log('---');

let legendaryCount = 0;
for (let i = 0; i < MAX; i++) {
  const salt = 'friend-2026-' + i;
  const rng = mulberry32(bunHash(uid + salt));
  const rarity = rollRarity(rng);
  if (rarity !== 'legendary') continue;
  legendaryCount++;
  const species = pick(rng, SPECIES);
  const eye = pick(rng, EYES);
  const hat = pick(rng, HATS);
  const shiny = rng() < 0.01;
  const tag = shiny ? '✦ SHINY ' : '';
  console.log(`${tag}LEGENDARY ${species} — eye:${eye} hat:${hat} — salt: "${salt}"`);
  if (shiny) {
    console.log(`\n🎉 SHINY LEGENDARY found! Total legendaries scanned: ${legendaryCount}`);
    console.log(`👉 Use this salt: ${salt}`);
    process.exit(0);
  }
}
console.log(`\nScanned ${MAX} salts, found ${legendaryCount} legendaries (no shiny). Try increasing MAX.`);
```

```bash
# ⚠️ 必须用 bun 运行（依赖 Bun.hash，Node.js 无此函数）
bun run search-buddy.mjs
```

**第三步：应用找到的 salt**

```bash
# 替换 SALT（以找到的值为例）
sed -i "s/const SALT = .*/const SALT = 'friend-2026-47899'/" src/buddy/companion.ts

# Windows (PowerShell) 等效命令：
(Get-Content src/buddy/companion.ts) -replace "const SALT = .*", "const SALT = 'friend-2026-47899'" | Set-Content src/buddy/companion.ts
```

然后清 companion、重启、`/buddy` 即可。

> **跨平台说明**：搜索脚本依赖 `Bun.hash()` 内置函数，此函数在 **Linux、macOS、Windows** 上的 Bun 运行时中行为一致，搜索结果跨平台通用。但 `sed` 命令在 Windows 上不可用，请使用上方提供的 PowerShell 等效命令。

### 只改名字和个性描述

不想换物种，只是想给宠物改个名字？直接编辑 config 文件：

```bash
# 查看当前 companion
grep -A5 companion ~/.claude.json      # Linux/macOS
Select-String companion $env:USERPROFILE\.claude.json   # Windows

# 手动编辑 ~/.claude.json 中的 companion.name 和 companion.personality 字段即可
```

> **注意**：外观（物种、稀有度、眼型、帽子）由 userId hash 实时计算，不存在 config 中，无法通过编辑 config 伪造。这是原版的防作弊设计。

## 技术实现细节

### 核心代码改进

#### 1. 环境变量优先级系统 (`request-adapter.ts:30-56`)
```typescript
// Determine max_tokens value for OpenAI-compatible APIs
// Priority (from highest to lowest):
// 1. CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI - OpenAI-specific override
// 2. CLAUDE_CODE_MAX_OUTPUT_TOKENS - Global setting for all APIs
// 3. anthropicParams.max_tokens - From original Anthropic request
// 4. Default 8192 - Fallback value
let maxTokens = 8192;

// 1. Check for OpenAI-specific environment variable (highest priority)
if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI) {
  const openaiMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI, 10);
  if (!isNaN(openaiMaxTokens) && openaiMaxTokens > 0) {
    maxTokens = openaiMaxTokens;
  }
}
// 2. Check for global environment variable
else if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS) {
  const envMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS, 10);
  if (!isNaN(envMaxTokens) && envMaxTokens > 0) {
    maxTokens = envMaxTokens;
  }
}
// 3. Use anthropicParams.max_tokens if no environment variables set
else if (anthropicParams.max_tokens !== undefined && anthropicParams.max_tokens > 0) {
  maxTokens = anthropicParams.max_tokens;
}
// 4. Default to 8192 (already set)
```

#### 2. 消息序列处理优化 (`request-adapter.ts:124-200`)
```typescript
function postprocessMessages(messages: any[]): any[] {
  const result: any[] = [];

  for (const msg of messages) {
    // Skip completely empty assistant messages (thinking-only after conversion)
    if (
      msg.role === 'assistant' &&
      !msg.content &&
      (!msg.tool_calls || msg.tool_calls.length === 0)
    ) {
      continue;
    }

    const prev = result[result.length - 1];

    // Merge consecutive assistant messages
    if (prev && prev.role === 'assistant' && msg.role === 'assistant') {
      // Merge text content
      const prevText = prev.content || '';
      const curText = msg.content || '';
      if (curText) {
        prev.content = prevText ? prevText + '\n' + curText : curText;
      }
      // Merge tool_calls arrays
      if (msg.tool_calls && msg.tool_calls.length > 0) {
        if (!prev.tool_calls) {
          prev.tool_calls = [];
        }
        prev.tool_calls.push(...msg.tool_calls);
      }
      continue;
    }

    // Merge consecutive user messages (can happen after tool_result expansion)
    if (prev && prev.role === 'user' && msg.role === 'user') {
      // ... merge logic ...
      continue;
    }

    // Normal case: different role, just push
    result.push({ ...msg });
  }

  return result;
}
```

#### 3. 交互式配置组件 (`OpenAICompatSetup.tsx`)
- **预设提供商选择**：优云智算、DeepSeek、Ollama、自定义URL
- **智能URL处理**：自动添加`/v1`后缀
- **配置验证**：输入验证和错误提示
- **配置持久化**：自动保存到`~/.claude.json`

### 新增文件列表

| 文件 | 用途 | 改进点 |
|------|------|--------|
| `.env.example` | 环境变量模板 | 180+行完整配置示例 |
| `ENVIRONMENT_VARIABLES.md` | 环境变量文档 | 58个配置项详细说明 |
| `BAT_STARTUP_GUIDE.md` | Windows启动指南 | 针对Windows用户的详细指南 |
| `启动说明.txt` | 中文使用说明 | 简化上手流程 |
| `TUI启动器.bat` | Windows启动脚本 | 一键启动TUI界面 |
| `桌面版启动器.bat` | 桌面版启动脚本 | 一键启动Electron桌面版 |
| `test-electron.js` | Electron测试 | 桌面版功能测试 |
| `setup-env.sh` | 环境设置脚本 | 自动化环境配置 |

### 修改的关键文件

| 文件 | 原项目 | 本版本 | 改进内容 |
|------|--------|--------|----------|
| `src/services/api/openai-compat/request-adapter.ts` | 简单格式转换 | 完整适配器 | 添加max_tokens优先级、消息序列处理 |
| `src/services/api/client.ts` | 基础提供商选择 | 增强提供商选择 | 添加OpenAI兼容API分支，支持环境变量检测 |
| `src/components/OpenAICompatSetup.tsx` | 基础配置界面 | 增强配置界面 | 添加预设提供商、智能URL处理、配置验证 |
| `src/utils/envUtils.ts` | 基础环境工具 | 增强环境工具 | 添加`isEnvTruthy`、`parseEnvVars`等工具函数 |
| `package.json` | 基础脚本 | 增强脚本 | 添加`desktop`、`desktop:dev`等桌面版脚本 |

### 解决的具体问题

#### 问题1：国产模型API错误
- **原因**：国产模型对token限制严格，原项目直接使用anthropicParams.max_tokens
- **解决方案**：添加max_tokens优先级系统，支持环境变量覆盖
- **代码位置**：`request-adapter.ts:30-56`

#### 问题2：消息序列兼容性
- **原因**：Anthropic允许连续相同角色消息，但OpenAI格式要求严格交替
- **解决方案**：`postprocessMessages()`函数合并连续相同角色消息
- **代码位置**：`request-adapter.ts:124-200`

#### 问题3：配置管理混乱
- **原因**：原项目缺少统一的配置管理系统
- **解决方案**：创建完整的`.env`文件系统和配置文档
- **相关文件**：`.env.example`、`ENVIRONMENT_VARIABLES.md`

#### 问题4：Windows支持不足
- **原因**：原项目主要针对Unix-like系统
- **解决方案**：添加bat启动脚本、桌面版支持、路径处理优化
- **相关文件**：`TUI启动器.bat`、`桌面版启动器.bat`、`test_path.bat`

### 性能优化

1. **上下文窗口优化**：
   - `CLAUDE_CODE_MAX_CONTEXT_TOKENS`：控制最大上下文token数
   - `CLAUDE_CODE_AUTO_COMPACT_WINDOW`：自动压缩阈值

2. **输出限制优化**：
   - `CLAUDE_CODE_MAX_OUTPUT_TOKENS`：全局输出限制
   - `CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI`：OpenAI特定限制

3. **超时控制**：
   - `API_TIMEOUT_MS`：API请求超时时间（默认10分钟）

4. **流量控制**：
   - `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`：禁用非必要流量

### 扩展性设计

1. **模块化适配器**：OpenAI兼容适配器独立模块，易于扩展新提供商
2. **配置驱动**：所有参数通过环境变量配置，无需修改代码
3. **优先级系统**：清晰的配置优先级，避免冲突
4. **向后兼容**：保持与原项目的API兼容性

## 技术实现细节

### 核心代码改进

#### 1. 环境变量优先级系统 (`request-adapter.ts:30-56`)
```typescript
// Determine max_tokens value for OpenAI-compatible APIs
// Priority (from highest to lowest):
// 1. CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI - OpenAI-specific override
// 2. CLAUDE_CODE_MAX_OUTPUT_TOKENS - Global setting for all APIs
// 3. anthropicParams.max_tokens - From original Anthropic request
// 4. Default 8192 - Fallback value
let maxTokens = 8192;

// 1. Check for OpenAI-specific environment variable (highest priority)
if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI) {
  const openaiMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI, 10);
  if (!isNaN(openaiMaxTokens) && openaiMaxTokens > 0) {
    maxTokens = openaiMaxTokens;
  }
}
// 2. Check for global environment variable
else if (process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS) {
  const envMaxTokens = parseInt(process.env.CLAUDE_CODE_MAX_OUTPUT_TOKENS, 10);
  if (!isNaN(envMaxTokens) && envMaxTokens > 0) {
    maxTokens = envMaxTokens;
  }
}
// 3. Use anthropicParams.max_tokens if no environment variables set
else if (anthropicParams.max_tokens !== undefined && anthropicParams.max_tokens > 0) {
  maxTokens = anthropicParams.max_tokens;
}
// 4. Default to 8192 (already set)
```

#### 2. 消息序列处理优化 (`request-adapter.ts:124-200`)
```typescript
function postprocessMessages(messages: any[]): any[] {
  const result: any[] = [];

  for (const msg of messages) {
    // Skip completely empty assistant messages (thinking-only after conversion)
    if (
      msg.role === 'assistant' &&
      !msg.content &&
      (!msg.tool_calls || msg.tool_calls.length === 0)
    ) {
      continue;
    }

    const prev = result[result.length - 1];

    // Merge consecutive assistant messages
    if (prev && prev.role === 'assistant' && msg.role === 'assistant') {
      // Merge text content
      const prevText = prev.content || '';
      const curText = msg.content || '';
      if (curText) {
        prev.content = prevText ? prevText + '\n' + curText : curText;
      }
      // Merge tool_calls arrays
      if (msg.tool_calls && msg.tool_calls.length > 0) {
        if (!prev.tool_calls) {
          prev.tool_calls = [];
        }
        prev.tool_calls.push(...msg.tool_calls);
      }
      continue;
    }

    // Merge consecutive user messages (can happen after tool_result expansion)
    if (prev && prev.role === 'user' && msg.role === 'user') {
      // ... merge logic ...
      continue;
    }

    // Normal case: different role, just push
    result.push({ ...msg });
  }

  return result;
}
```

#### 3. 交互式配置组件 (`OpenAICompatSetup.tsx`)
- **预设提供商选择**：优云智算、DeepSeek、Ollama、自定义URL
- **智能URL处理**：自动添加`/v1`后缀
- **配置验证**：输入验证和错误提示
- **配置持久化**：自动保存到`~/.claude.json`

### 新增文件列表

| 文件 | 用途 | 改进点 |
|------|------|--------|
| `.env.example` | 环境变量模板 | 180+行完整配置示例 |
| `ENVIRONMENT_VARIABLES.md` | 环境变量文档 | 58个配置项详细说明 |
| `BAT_STARTUP_GUIDE.md` | Windows启动指南 | 针对Windows用户的详细指南 |
| `启动说明.txt` | 中文使用说明 | 简化上手流程 |
| `TUI启动器.bat` | Windows启动脚本 | 一键启动TUI界面 |
| `桌面版启动器.bat` | 桌面版启动脚本 | 一键启动Electron桌面版 |
| `test-electron.js` | Electron测试 | 桌面版功能测试 |
| `setup-env.sh` | 环境设置脚本 | 自动化环境配置 |

### 修改的关键文件

| 文件 | 原项目 | 本版本 | 改进内容 |
|------|--------|--------|----------|
| `src/services/api/openai-compat/request-adapter.ts` | 简单格式转换 | 完整适配器 | 添加max_tokens优先级、消息序列处理 |
| `src/services/api/client.ts` | 基础提供商选择 | 增强提供商选择 | 添加OpenAI兼容API分支，支持环境变量检测 |
| `src/components/OpenAICompatSetup.tsx` | 基础配置界面 | 增强配置界面 | 添加预设提供商、智能URL处理、配置验证 |
| `src/utils/envUtils.ts` | 基础环境工具 | 增强环境工具 | 添加`isEnvTruthy`、`parseEnvVars`等工具函数 |
| `package.json` | 基础脚本 | 增强脚本 | 添加`desktop`、`desktop:dev`等桌面版脚本 |

### 解决的具体问题

#### 问题1：国产模型API错误
- **原因**：国产模型对token限制严格，原项目直接使用anthropicParams.max_tokens
- **解决方案**：添加max_tokens优先级系统，支持环境变量覆盖
- **代码位置**：`request-adapter.ts:30-56`

#### 问题2：消息序列兼容性
- **原因**：Anthropic允许连续相同角色消息，但OpenAI格式要求严格交替
- **解决方案**：`postprocessMessages()`函数合并连续相同角色消息
- **代码位置**：`request-adapter.ts:124-200`

#### 问题3：配置管理混乱
- **原因**：原项目缺少统一的配置管理系统
- **解决方案**：创建完整的`.env`文件系统和配置文档
- **相关文件**：`.env.example`、`ENVIRONMENT_VARIABLES.md`

#### 问题4：Windows支持不足
- **原因**：原项目主要针对Unix-like系统
- **解决方案**：添加bat启动脚本、桌面版支持、路径处理优化
- **相关文件**：`TUI启动器.bat`、`桌面版启动器.bat`、`test_path.bat`

### 性能优化

1. **上下文窗口优化**：
   - `CLAUDE_CODE_MAX_CONTEXT_TOKENS`：控制最大上下文token数
   - `CLAUDE_CODE_AUTO_COMPACT_WINDOW`：自动压缩阈值

2. **输出限制优化**：
   - `CLAUDE_CODE_MAX_OUTPUT_TOKENS`：全局输出限制
   - `CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI`：OpenAI特定限制

3. **超时控制**：
   - `API_TIMEOUT_MS`：API请求超时时间（默认10分钟）

4. **流量控制**：
   - `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`：禁用非必要流量

### 扩展性设计

1. **模块化适配器**：OpenAI兼容适配器独立模块，易于扩展新提供商
2. **配置驱动**：所有参数通过环境变量配置，无需修改代码
3. **优先级系统**：清晰的配置优先级，避免冲突
4. **向后兼容**：保持与原项目的API兼容性

## 许可证

本项目仅供学习研究用途。

## 致谢

本项目基于多个开源项目的代码和思想，特别感谢以下项目：

### 核心基础项目
- **[Claude Code CLI](https://claude.com/claude-code)** - Anthropic官方的Claude Code CLI工具，提供了基础架构和功能
- **[adoresever/cloud-code](https://github.com/adoresever/cloud-code)** - 本项目的主要基础，提供了OpenAI兼容API适配层和微信远程控制桥接的核心实现

### 相关衍生项目
- **[instructkr/claw-code](https://github.com/instructkr/claw-code.git)** - 提供了完全重构的相关实现思路和技术参考
- **[AICoderTudou/claude-code-tudou](https://github.com/AICoderTudou/claude-code-tudou.git)** - 在国产模型适配和启动优化方面提供了有价值的参考
- **[T8mars/claude-code-t8](https://github.com/T8mars/claude-code-t8)** - 在国产模型适配和启动优化方面提供了有价值的参考

### 技术栈和工具
- **Bun** - 高性能的JavaScript运行时
- **React + Ink** - 终端UI框架
- **TypeScript** - 类型安全的JavaScript超集
- **OpenAI兼容API生态** - DeepSeek、MiniMax、Ollama、Qwen等国产模型提供商

### 社区贡献
感谢所有为这些项目做出贡献的开发者，以及提供反馈和建议的用户。开源社区的协作精神使得这个项目能够不断完善和进步。

### 特别说明
本项目是在上述开源项目的基础上进行的二次开发和优化，主要改进点包括：
1. 完整的`.env`配置系统优化
2. 国产模型深度兼容性适配
3. 环境变量优先级系统
4. Windows平台支持增强
5. 项目文档完善

我们尊重所有原项目的许可证和版权，本项目仅供学习研究用途。

---

**版本信息**：增强版 v1.0.0  
**更新日期**：2026-04-11  
**主要改进**：五大核心改进，全面优化国产模型兼容性和用户体验