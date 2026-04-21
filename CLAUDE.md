# CLAUDE.md

> Maintained by **二次开发团队**

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a reverse-engineered version of Anthropic's Claude Code CLI tool, with an **OpenAI-compatible API adapter layer** that allows connecting to any OpenAI-compatible API (DeepSeek, Ollama, etc.), and a **WeChat Bridge** for remote control via WeChat (iLink Bot API).

## Commands

```bash
bun install
bun run dev          # Dev mode
bun run build        # Build to dist/cli.js
bun run wechat       # WeChat bridge (iLink Bot)
bun run wechat:login # WeChat bridge (force re-login)
echo "say hello" | bun run src/entrypoints/cli.tsx -p  # Pipe mode
```

## Architecture

### Runtime & Build

- **Runtime**: Bun (not Node.js)
- **Build**: `bun build src/entrypoints/cli.tsx --outdir dist --target bun`
- **Module system**: ESM with TSX

### Key Files

| File | Purpose |
|------|---------|
| `src/entrypoints/cli.tsx` | Entry point with runtime polyfills |
| `src/main.tsx` | Commander.js CLI definition |
| `src/services/api/claude.ts` | Core API client (streaming, tools, betas) |
| `src/services/api/client.ts` | Provider selection (Anthropic/Bedrock/Vertex/Foundry/**OpenAI-compat**) |
| `src/services/api/openai-compat/` | **OpenAI-compatible API adapter layer** |
| `src/components/OpenAICompatSetup.tsx` | **Interactive setup UI for third-party APIs** |
| `src/utils/model/providers.ts` | API provider type definitions |
| `src/query.ts` | Main query function with tool call loop |
| `src/QueryEngine.ts` | Conversation state orchestrator |
| `src/screens/REPL.tsx` | Interactive REPL screen (React/Ink) |
| `scripts/wechat-bridge.ts` | **WeChat iLink Bot bridge main script** |
| `scripts/ilink.ts` | **iLink protocol SDK (zero-dependency)** |

### OpenAI-compat Adapter

The adapter in `src/services/api/openai-compat/` translates between Anthropic and OpenAI formats:
- `request-adapter.ts` — Anthropic request → OpenAI request
- `stream-adapter.ts` — OpenAI SSE stream → Anthropic event stream
- `thinking-adapter.ts` — DeepSeek R1 `reasoning_content` / QwQ `<think>` tags
- `index.ts` — Duck-typed Anthropic client that upstream code calls transparently

### WeChat Bridge

The bridge in `scripts/` enables remote control of cloud-code via WeChat:
- `ilink.ts` — Tencent official iLink Bot API protocol (QR login, long-poll, send/receive, CDN media encrypt/decrypt)
- `wechat-bridge.ts` — Message routing: WeChat → spawn `bun -p` → cloud-code → reply to WeChat
- Supports: text, image, file, voice (auto-transcribe), video
- Media: AES-128-ECB encryption/decryption for CDN upload/download
- State stored in `~/.wechat-bridge/` (credentials, cursor)

### Feature Flags

All `feature()` calls are polyfilled to return `false`. React Compiler output has `_c()` memoization boilerplate — this is normal.

### WeChat CLI Integration

This project includes WeChat CLI (`wechat-cli/` directory) for querying local WeChat data. The tool is installed in a virtual environment and ready to use.

#### WeChat CLI Commands

You can use `wechat-cli` to query local WeChat data. Common commands:

**Basic Usage:**
- `wechat-cli sessions --limit 10` — List recent chats
- `wechat-cli history "NAME" --limit 20 --format text` — Read chat history
- `wechat-cli search "KEYWORD" --chat "CHAT_NAME"` — Search messages
- `wechat-cli contacts --query "NAME"` — Search contacts
- `wechat-cli unread` — Show unread sessions
- `wechat-cli new-messages` — Get messages since last check
- `wechat-cli members "GROUP"` — List group members
- `wechat-cli stats "CHAT" --format text` — Chat statistics

**Message Type Filters:**
- `--type text` — Text messages
- `--type image` — Images
- `--type voice` — Voice messages
- `--type video` — Videos
- `--type file` — File attachments
- `--type link` — Links and app messages

**Output Formats:**
- `--format json` (default) — Structured JSON for AI tools
- `--format text` — Human-readable text

#### Using WeChat CLI in Virtual Environment

**Activate virtual environment:**
```bash
cd wechat-cli
source venv/Scripts/activate  # Bash (Git Bash/WSL)
# or
venv\Scripts\activate.bat     # Windows CMD
```

**Quick start scripts:**
```bash
./start_wechat_cli.sh         # Bash interactive shell
# or
start_wechat_cli.bat          # Windows interactive shell
```

**First-time initialization (requires WeChat running):**
```bash
wechat-cli init
```

#### Integration Examples

1. **Check for unread messages:**
   ```bash
   wechat-cli unread --format text
   ```

2. **Search for specific content:**
   ```bash
   wechat-cli search "project deadline" --chat "Team Group" --type file
   ```

3. **Export chat history:**
   ```bash
   wechat-cli export "Alice" --format markdown --output chat.md
   ```

4. **Monitor new messages (automation):**
   ```bash
   wechat-cli new-messages --format json
   ```

#### Important Notes:
- WeChat must be running for `init` command to work
- On macOS, terminal needs "Full Disk Access" permission
- All data stays local - no cloud transmission
- Read-only operations - no messages are sent or modified

#### Documentation:
- `wechat-cli/WECHAT_CLI_COMPLETE_GUIDE.md` — Complete usage guide
- `wechat-cli/VENV_USAGE.md` — Virtual environment guide
- `wechat-cli/README_PROJECT.md` — Project integration guide

### WeChat CLI Integration

This project includes WeChat CLI (`wechat-cli/` directory) for querying local WeChat data. The tool is installed in a virtual environment and ready to use.

#### WeChat CLI Commands

You can use `wechat-cli` to query local WeChat data. Common commands:

**Basic Usage:**
- `wechat-cli sessions --limit 10` — List recent chats
- `wechat-cli history "NAME" --limit 20 --format text` — Read chat history
- `wechat-cli search "KEYWORD" --chat "CHAT_NAME"` — Search messages
- `wechat-cli contacts --query "NAME"` — Search contacts
- `wechat-cli unread` — Show unread sessions
- `wechat-cli new-messages` — Get messages since last check
- `wechat-cli members "GROUP"` — List group members
- `wechat-cli stats "CHAT" --format text` — Chat statistics

**Message Type Filters:**
- `--type text` — Text messages
- `--type image` — Images
- `--type voice` — Voice messages
- `--type video` — Videos
- `--type file` — File attachments
- `--type link` — Links and app messages

**Output Formats:**
- `--format json` (default) — Structured JSON for AI tools
- `--format text` — Human-readable text

#### Using WeChat CLI in Virtual Environment

**Activate virtual environment:**
```bash
cd wechat-cli
source venv/Scripts/activate  # Bash (Git Bash/WSL)
# or
venv\Scripts\activate.bat     # Windows CMD
```

**Quick start scripts:**
```bash
./start_wechat_cli.sh         # Bash interactive shell
# or
start_wechat_cli.bat          # Windows interactive shell
```

**First-time initialization (requires WeChat running):**
```bash
wechat-cli init
```

#### Integration Examples

1. **Check for unread messages:**
   ```bash
   wechat-cli unread --format text
   ```

2. **Search for specific content:**
   ```bash
   wechat-cli search "project deadline" --chat "Team Group" --type file
   ```

3. **Export chat history:**
   ```bash
   wechat-cli export "Alice" --format markdown --output chat.md
   ```

4. **Monitor new messages (automation):**
   ```bash
   wechat-cli new-messages --format json
   ```

#### Important Notes:
- WeChat must be running for `init` command to work
- On macOS, terminal needs "Full Disk Access" permission
- All data stays local - no cloud transmission
- Read-only operations - no messages are sent or modified

#### Documentation:
- `wechat-cli/WECHAT_CLI_COMPLETE_GUIDE.md` — Complete usage guide
- `wechat-cli/VENV_USAGE.md` — Virtual environment guide
- `wechat-cli/README_PROJECT.md` — Project integration guide
## Documentation

### Project Documentation Structure

The project includes a comprehensive documentation system in the `docs/` directory:

```
docs/
├── README.md                    # Documentation directory overview
├── solutions/                   # Technical solutions and problem fixes
│   └── claude-mem-binary-fix/  # claude-mem plugin binary compatibility fix
├── architecture/                # Architecture design documents
├── api/                        # API documentation
├── deployment/                 # Deployment guides
├── development/                # Development guidelines
└── troubleshooting/            # Troubleshooting manual
```

### Key Documentation Categories

1. **Technical Solutions** (`docs/solutions/`)
   - Records specific technical problems and their solutions
   - Includes problem analysis, solution matrix, implementation steps
   - Example: claude-mem plugin binary compatibility issue

2. **Architecture Design** (`docs/architecture/`)
   - System architecture diagrams and component design
   - Technology selection rationale and design decisions
   - Evolution planning and technical debt management

3. **API Documentation** (`docs/api/`)
   - OpenAI-compatible API adapter specifications
   - WeChat Bridge API documentation
   - Command-line interface reference

4. **Deployment Guides** (`docs/deployment/`)
   - Environment requirements and setup steps
   - Configuration management and monitoring
   - Production deployment and maintenance

5. **Development Guidelines** (`docs/development/`)
   - Development environment setup
   - Code standards and best practices
   - Testing strategy and contribution workflow

6. **Troubleshooting** (`docs/troubleshooting/`)
   - Common errors and solutions
   - Debugging techniques and log analysis
   - Emergency recovery procedures

### Relationship with Memory System

Project documentation (`docs/`) and user memory system (`~/.claude/.../memory/`) serve different purposes:

| Aspect | Project Documentation (`docs/`) | User Memory (`memory/`) |
|--------|--------------------------------|-------------------------|
| **Location** | In project code directory | In user config directory |
| **Content** | Technical solutions, architecture | Personal work memories, experiences |
| **Version Control** | Yes, managed by Git | No, personal storage |
| **Sharing** | Team-shared knowledge | Personal use only |
| **Purpose** | Project technical reference | Personal productivity enhancement |

### Documentation Usage Guidelines

When working with this project:

1. **For new developers**: Start with `docs/development/` for environment setup and coding standards
2. **For problem solving**: Check `docs/solutions/` and `docs/troubleshooting/`
3. **For system understanding**: Read `docs/architecture/` for design insights
4. **For API development**: Refer to `docs/api/` for interface specifications
5. **For deployment**: Follow `docs/deployment/` for environment setup

### Maintenance Notes

- Keep documentation synchronized with code changes
- Document important technical experiences promptly
- Regularly review and update documentation
- Contributions to documentation are welcome

For detailed documentation, see [docs/README.md](docs/README.md).

## Documentation

### Project Documentation Structure

The project includes a comprehensive documentation system in the `docs/` directory:

```
docs/
├── README.md                    # Documentation directory overview
├── solutions/                   # Technical solutions and problem fixes
│   └── claude-mem-binary-fix/  # claude-mem plugin binary compatibility fix
├── architecture/                # Architecture design documents
├── api/                        # API documentation
├── deployment/                 # Deployment guides
├── development/                # Development guidelines
└── troubleshooting/            # Troubleshooting manual
```

### Key Documentation Categories

1. **Technical Solutions** (`docs/solutions/`)
   - Records specific technical problems and their solutions
   - Includes problem analysis, solution matrix, implementation steps
   - Example: claude-mem plugin binary compatibility issue

2. **Architecture Design** (`docs/architecture/`)
   - System architecture diagrams and component design
   - Technology selection rationale and design decisions
   - Evolution planning and technical debt management

3. **API Documentation** (`docs/api/`)
   - OpenAI-compatible API adapter specifications
   - WeChat Bridge API documentation
   - Command-line interface reference

4. **Deployment Guides** (`docs/deployment/`)
   - Environment requirements and setup steps
   - Configuration management and monitoring
   - Production deployment and maintenance

5. **Development Guidelines** (`docs/development/`)
   - Development environment setup
   - Code standards and best practices
   - Testing strategy and contribution workflow

6. **Troubleshooting** (`docs/troubleshooting/`)
   - Common errors and solutions
   - Debugging techniques and log analysis
   - Emergency recovery procedures

### Relationship with Memory System

Project documentation (`docs/`) and user memory system (`~/.claude/.../memory/`) serve different purposes:

| Aspect | Project Documentation (`docs/`) | User Memory (`memory/`) |
|--------|--------------------------------|-------------------------|
| **Location** | In project code directory | In user config directory |
| **Content** | Technical solutions, architecture | Personal work memories, experiences |
| **Version Control** | Yes, managed by Git | No, personal storage |
| **Sharing** | Team-shared knowledge | Personal use only |
| **Purpose** | Project technical reference | Personal productivity enhancement |

### Documentation Usage Guidelines

When working with this project:

1. **For new developers**: Start with `docs/development/` for environment setup and coding standards
2. **For problem solving**: Check `docs/solutions/` and `docs/troubleshooting/`
3. **For system understanding**: Read `docs/architecture/` for design insights
4. **For API development**: Refer to `docs/api/` for interface specifications
5. **For deployment**: Follow `docs/deployment/` for environment setup

### Maintenance Notes

- Keep documentation synchronized with code changes
- Document important technical experiences promptly
- Regularly review and update documentation
- Contributions to documentation are welcome

For detailed documentation, see [docs/README.md](docs/README.md).
