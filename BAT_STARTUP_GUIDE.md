# Claude Code Startup Guide for Windows

## Available Batch Files

### 1. `run.bat` (Simplest)
- Minimal checks and setup
- Good for quick testing

### 2. `start.bat` (Recommended)
- Basic environment checks
- Helpful error messages
- Auto-creates .env file

### 3. `TUI启动器.bat` (Full-featured)
- Comprehensive checks
- Detailed error reporting
- Best for troubleshooting

### 4. `桌面版启动器.bat` (Desktop version)
- For desktop app version
- Requires built desktop directory

## Quick Start

1. **First time setup:**
   ```bash
   # Install dependencies
   bun install
   
   # Configure API (edit .env file)
   # Default uses local Ollama at http://localhost:11434
   ```

2. **Run the app:**
   - Double-click `run.bat` or `start.bat`

## API Configuration

Edit `.env` file to configure your API:

### Option A: Local Ollama (Easiest)
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=http://localhost:11434
OPENAI_COMPAT_API_KEY=ollama
OPENAI_COMPAT_MODEL=llama3.2
```

### Option B: DeepSeek API
```env
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=https://api.deepseek.com
OPENAI_COMPAT_API_KEY=your-deepseek-api-key
OPENAI_COMPAT_MODEL=deepseek-chat
```

### Option C: Anthropic Official API
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

## Troubleshooting

### "Bun not found"
- Install Bun from https://bun.sh/
- Restart command prompt after installation

### API Error 403
- Check API configuration in `.env` file
- Make sure API service is running (for local Ollama)
- Verify API key is correct (for cloud services)

### Encoding issues
- Use `run.bat` or `start.bat` (English only)
- Avoid Chinese characters in batch files

### Dependencies not installed
- Run `bun install` manually
- Delete `node_modules` folder and run again

## Manual Commands

```bash
# Install dependencies
bun install

# Run development mode
bun run dev

# Build the app
bun run build

# Run desktop version
bun run desktop
```

## Notes
- Batch files use UTF-8 encoding (chcp 65001)
- All batch files create `.env` from `.env.example` if missing
- Check `启动说明.txt` for Chinese instructions