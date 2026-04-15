# Cloud Code 项目运行记录

> Maintained by **二次开发团队**
>
> 项目: Cloud Code 二次开发版 (OpenAI兼容API分支)

---

## 一、项目目标

将 claude-code 项目运行起来并新增 OpenAI 兼容 API 支持 + 微信远程控制桥接。

---

## 二、当前状态：已可运行

```bash
bun run dev      # 交互式 CLI
bun run wechat   # 微信远程控制
```

| 测试 | 结果 |
|------|------|
| Anthropic Direct API | ✅ |
| Bedrock / Vertex / Foundry | ✅ |
| **OpenAI 兼容 API（DeepSeek/Ollama/优云智算）** | **✅** |
| 交互式配置界面 | ✅ |
| 配置持久化 & 自动加载 | ✅ |
| 流式对话 | ✅ |
| 工具调用 | ✅ |
| **微信文字收发** | **✅** |
| **微信图片收发（CDN 加解密）** | **✅** |
| **微信文件收发（PDF/DOC 等）** | **✅** |
| **微信语音接收（自动转文字）** | **✅** |
| **微信视频收发（CDN 加解密）** | **✅** |
| **微信 Typing 状态** | **✅** |

---

## 三、OpenAI 兼容适配层改动记录

### 3.1 新增文件

| 文件 | 用途 |
|------|------|
| `src/services/api/openai-compat/index.ts` | 伪 Anthropic 客户端，处理 `.withResponse()` Promise 链 |
| `src/services/api/openai-compat/request-adapter.ts` | Anthropic → OpenAI 请求格式转换 |
| `src/services/api/openai-compat/stream-adapter.ts` | OpenAI SSE → Anthropic 事件流转换 |
| `src/services/api/openai-compat/thinking-adapter.ts` | DeepSeek R1 / QwQ 思考模型适配 |
| `src/components/OpenAICompatSetup.tsx` | 交互式配置界面 |

### 3.2 修改的现有文件

| 文件 | 改动 |
|------|------|
| `src/utils/model/providers.ts` | 类型加 `openai_compat`，`getAPIProvider()` 加检测 |
| `src/utils/model/configs.ts` | 每个 config 加 `openai_compat` 字段 |
| `src/services/api/client.ts` | `getAnthropicClient()` 加 openai_compat 分支 |
| `src/components/ConsoleOAuthFlow.tsx` | 登录界面加第四个选项 + onChange + 状态拦截 |
| `src/entrypoints/cli.tsx` | 启动时从 ~/.claude.json 加载已保存配置 |

### 3.3 已验证

| 提供商 | 模型 | 状态 |
|--------|------|------|
| 优云智算 (api.modelverse.cn) | MiniMax-M2.5, gpt-5.4 | ✅ |

---

## 四、微信桥接改动记录

### 4.1 新增文件

| 文件 | 用途 |
|------|------|
| `scripts/ilink.ts` | 腾讯 iLink Bot API 协议封装（零依赖） |
| `scripts/wechat-bridge.ts` | 微信桥接主脚本 |

### 4.2 ilink.ts 协议封装

- QR 扫码登录（`get_bot_qrcode` → `get_qrcode_status`）
- 长轮询收消息（`getupdates`，hold 35s）
- 发送消息（`sendmessage`，必须带 `context_token`）
- Typing 状态（`getconfig` → `sendtyping`）
- CDN 媒体上传（`getuploadurl` → AES-128-ECB 加密 → CDN upload）
- CDN 媒体下载（CDN download → AES-128-ECB 解密）
- AES key 双格式兼容解析（base64(raw 16 bytes) / base64(hex string)）

### 4.3 wechat-bridge.ts 桥接逻辑

- 收到微信消息 → spawn `bun run cli.tsx -p` → 捕获 stdout → 发回微信
- 文字消息自动分片（1800 字符阈值）
- 图片/文件/视频入站：CDN 下载解密 → 保存临时文件 → 路径告知 cloud-code
- 语音入站：使用微信自动转写文字 + 保存原始 SILK 音频
- 24h token 过期自动提示重新扫码（errcode -14）
- 凭证存储：`~/.wechat-bridge/credentials.json`
- 游标持久化：`~/.wechat-bridge/cursor.json`

### 4.4 修改的现有文件

| 文件 | 改动 |
|------|------|
| `package.json` | 加 `wechat` / `wechat:login` 两条 script |
| `.gitignore` | 加 `credentials.json`、`.wechat-bridge/`、`media/` 等排除项 |

### 4.5 iLink 协议关键 API

| 端点 | 用途 |
|------|------|
| `GET /ilink/bot/get_bot_qrcode?bot_type=3` | 获取登录二维码 |
| `GET /ilink/bot/get_qrcode_status` | 轮询扫码状态 |
| `POST /ilink/bot/getupdates` | 长轮询收消息 |
| `POST /ilink/bot/sendmessage` | 发送消息 |
| `POST /ilink/bot/getconfig` | 获取 typing_ticket |
| `POST /ilink/bot/sendtyping` | 发送输入状态 |
| `POST /ilink/bot/getuploadurl` | 申请媒体上传参数 |

### 4.6 已验证

| 功能 | 状态 |
|------|------|
| 微信扫码登录 | ✅ |
| 文字消息收发 | ✅ |
| 图片收发（CDN AES-128-ECB 加解密） | ✅ |
| 文件收发（PDF/DOC/ZIP 等） | ✅ |
| 视频收发（CDN 加解密） | ✅ |
| 语音接收（微信自动转文字） | ✅ |
| Typing 状态（"正在输入"） | ✅ |
| 24h token 过期重连 | ✅ |
| 长消息自动分片 | ✅ |

---

## 五、MemPalace 插件版本同步与配置优化

### 5.1 问题发现
1. **版本号不同步**: `plugin.json` 版本为 3.0.14，而 `pyproject.toml` 版本为 3.3.0
2. **环境配置问题**: MCP 服务器配置使用系统 Python 环境，而非项目虚拟环境
3. **技能系统环境优先级**: 技能系统无法自动识别项目环境优先级

### 5.2 解决方案

#### 5.2.1 版本号同步
- 更新 `plugin.json` 版本号: `3.0.14` → `3.3.0`
- 确保插件版本与 Python 包版本保持一致

#### 5.2.2 MCP 服务器配置优化
```json
// 修改前（使用系统环境）
"mcpServers": {
  "mempalace": {
    "command": "python3",
    "args": ["-m", "mempalace.mcp_server"]
  }
}

// 修改后（使用项目虚拟环境）
"mcpServers": {
  "mempalace": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "C:\\Users\\Administrator\\Desktop\\projects\\claudecode\\yuanmaziyuan\\cloud-code-rewrite\\cloud-code-main\\mempalace\\mempalace\\start_mempalace_mcp.bat"
    ]
  }
}
```

#### 5.2.3 智能包装脚本
1. **`start_mempalace_mcp.bat`** - Windows 启动脚本
2. **`smart_mempalace.sh`** - 智能环境选择脚本
3. **`run_mempalace_for_skill.sh`** - 技能系统专用脚本

#### 5.2.4 环境优先级策略
1. **项目虚拟环境**（首选）: 使用项目中的 mempalace 3.3.0
2. **系统环境**（备选）: 使用系统安装的 mempalace
3. **自动降级**: 如果项目环境不可用，自动回退到系统环境

### 5.3 验证结果
- ✅ 版本同步验证通过
- ✅ MCP 服务器配置验证通过
- ✅ 技能系统环境优先级验证通过
- ✅ 跨平台兼容性验证通过

### 5.4 经验总结
1. **版本管理最佳实践**: 插件版本与 Python 包版本应保持一致
2. **环境隔离策略**: 每个项目使用独立的虚拟环境，提供智能降级
3. **技能系统集成模式**: 助手实现智能环境选择，确保最佳用户体验
4. **跨平台兼容性**: 提供 Windows 和 Unix 双平台支持

### 5.5 技术洞察
```
★ Insight ─────────────────────────────────────
1. 插件架构设计: Claude Code 插件系统采用松耦合设计，插件版本和 Python 包版本可以独立更新
2. 环境优先级模式: 智能环境选择策略是解决多环境冲突的有效模式
3. 技能执行机制: 技能系统本质上是指导文档+助手执行的模式
─────────────────────────────────────────────────
```

### 5.6 文件修改清单
1. **版本同步修改**: `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json`
2. **MCP 服务器配置**: 同上文件
3. **新建脚本文件**: `start_mempalace_mcp.bat`, `smart_mempalace.sh`, `run_mempalace_for_skill.sh`
4. **文档更新**: README.md, memory/mempalace_version_sync.md, MEMORY.md
5. **配置文件**: `mempalace/mempalace/.claude-mem.json`

### 5.7 更新记录
- **2026-04-14**: 创建完整解决方案，解决版本同步、环境配置和技能系统优先级问题
- **关键修改**: 版本号同步、MCP 服务器配置优化、智能包装脚本创建
- **验证状态**: 所有功能验证通过，跨平台兼容性确认

---

## 五、MemPalace 插件版本同步与配置优化

### 5.1 问题发现
1. **版本号不同步**: `plugin.json` 版本为 3.0.14，而 `pyproject.toml` 版本为 3.3.0
2. **环境配置问题**: MCP 服务器配置使用系统 Python 环境，而非项目虚拟环境
3. **技能系统环境优先级**: 技能系统无法自动识别项目环境优先级

### 5.2 解决方案

#### 5.2.1 版本号同步
- 更新 `plugin.json` 版本号: `3.0.14` → `3.3.0`
- 确保插件版本与 Python 包版本保持一致

#### 5.2.2 MCP 服务器配置优化
```json
// 修改前（使用系统环境）
"mcpServers": {
  "mempalace": {
    "command": "python3",
    "args": ["-m", "mempalace.mcp_server"]
  }
}

// 修改后（使用项目虚拟环境）
"mcpServers": {
  "mempalace": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "C:\\Users\\Administrator\\Desktop\\projects\\claudecode\\yuanmaziyuan\\cloud-code-rewrite\\cloud-code-main\\mempalace\\mempalace\\start_mempalace_mcp.bat"
    ]
  }
}
```

#### 5.2.3 智能包装脚本
1. **`start_mempalace_mcp.bat`** - Windows 启动脚本
2. **`smart_mempalace.sh`** - 智能环境选择脚本
3. **`run_mempalace_for_skill.sh`** - 技能系统专用脚本

#### 5.2.4 环境优先级策略
1. **项目虚拟环境**（首选）: 使用项目中的 mempalace 3.3.0
2. **系统环境**（备选）: 使用系统安装的 mempalace
3. **自动降级**: 如果项目环境不可用，自动回退到系统环境

### 5.3 验证结果
- ✅ 版本同步验证通过
- ✅ MCP 服务器配置验证通过
- ✅ 技能系统环境优先级验证通过
- ✅ 跨平台兼容性验证通过

### 5.4 经验总结
1. **版本管理最佳实践**: 插件版本与 Python 包版本应保持一致
2. **环境隔离策略**: 每个项目使用独立的虚拟环境，提供智能降级
3. **技能系统集成模式**: 助手实现智能环境选择，确保最佳用户体验
4. **跨平台兼容性**: 提供 Windows 和 Unix 双平台支持

### 5.5 技术洞察
```
★ Insight ─────────────────────────────────────
1. 插件架构设计: Claude Code 插件系统采用松耦合设计，插件版本和 Python 包版本可以独立更新
2. 环境优先级模式: 智能环境选择策略是解决多环境冲突的有效模式
3. 技能执行机制: 技能系统本质上是指导文档+助手执行的模式
─────────────────────────────────────────────────
```

### 5.6 文件修改清单
1. **版本同步修改**: `~/.claude/plugins/marketplaces/mempalace/.claude-plugin/plugin.json`
2. **MCP 服务器配置**: 同上文件
3. **新建脚本文件**: `start_mempalace_mcp.bat`, `smart_mempalace.sh`, `run_mempalace_for_skill.sh`
4. **文档更新**: README.md, memory/mempalace_version_sync.md, MEMORY.md
5. **配置文件**: `mempalace/mempalace/.claude-mem.json`

### 5.7 更新记录
- **2026-04-14**: 创建完整解决方案，解决版本同步、环境配置和技能系统优先级问题
- **关键修改**: 版本号同步、MCP 服务器配置优化、智能包装脚本创建
- **验证状态**: 所有功能验证通过，跨平台兼容性确认