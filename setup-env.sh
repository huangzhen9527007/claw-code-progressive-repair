#!/bin/bash
# Claude Code 环境变量快速配置脚本
# 用法: ./setup-env.sh [provider] [options]

set -e

PROVIDER=""
BASE_URL=""
API_KEY=""
MODEL=""
OUTPUT_FILE=".env"

# 显示帮助信息
show_help() {
    cat << EOF
Claude Code 环境变量快速配置脚本

用法: $0 [provider] [options]

支持的提供商:
  deepseek     - DeepSeek API
  ollama       - 本地 Ollama
  qwen         - 阿里通义千问
  anthropic    - Anthropic 官方 API
  custom       - 自定义配置

选项:
  -h, --help          显示此帮助信息
  -u, --url URL       API 基础 URL
  -k, --key KEY       API 密钥
  -m, --model MODEL   模型名称
  -o, --output FILE   输出文件 (默认: .env)

示例:
  $0 deepseek -k sk-xxx -m deepseek-chat
  $0 ollama -m llama3.2
  $0 custom -u https://api.example.com -k sk-xxx -m custom-model
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        deepseek|ollama|qwen|anthropic|custom)
            PROVIDER="$1"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -k|--key)
            API_KEY="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "错误: 未知参数 $1"
            show_help
            exit 1
            ;;
    esac
done

# 如果没有指定提供商，显示帮助
if [[ -z "$PROVIDER" ]]; then
    show_help
    exit 1
fi

# 根据提供商设置默认值
case $PROVIDER in
    deepseek)
        BASE_URL="${BASE_URL:-https://api.deepseek.com}"
        MODEL="${MODEL:-deepseek-chat}"
        echo "配置 DeepSeek API..."
        ;;
    ollama)
        BASE_URL="${BASE_URL:-http://localhost:11434}"
        API_KEY="${API_KEY:-ollama}"
        MODEL="${MODEL:-llama3.2}"
        echo "配置本地 Ollama..."
        ;;
    qwen)
        BASE_URL="${BASE_URL:-https://dashscope.aliyuncs.com/compatible-mode/v1}"
        MODEL="${MODEL:-qwen-plus}"
        echo "配置阿里通义千问..."
        ;;
    anthropic)
        echo "配置 Anthropic 官方 API..."
        # 对于 Anthropic，不使用 OPENAI_COMPAT 变量
        cat > "$OUTPUT_FILE" << EOF
# ============================================
# Claude Code 环境变量配置 (Anthropic)
# ============================================

# 上下文窗口配置
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400

# 输出token配置
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192

# Anthropic API配置
ANTHROPIC_API_KEY=${API_KEY:-sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}
ANTHROPIC_BASE_URL=${BASE_URL:-https://api.anthropic.com}
ANTHROPIC_MODEL=${MODEL:-claude-3-5-sonnet-20241022}

# 性能配置
API_TIMEOUT_MS=600000
EOF
        echo "配置已保存到 $OUTPUT_FILE"
        exit 0
        ;;
    custom)
        if [[ -z "$BASE_URL" ]] || [[ -z "$MODEL" ]]; then
            echo "错误: 自定义配置需要 --url 和 --model 参数"
            exit 1
        fi
        echo "配置自定义 API..."
        ;;
esac

# 生成 .env 文件
cat > "$OUTPUT_FILE" << EOF
# ============================================
# Claude Code 环境变量配置 ($PROVIDER)
# ============================================

# 上下文窗口配置
CLAUDE_CODE_MAX_CONTEXT_TOKENS=102400
CLAUDE_CODE_AUTO_COMPACT_WINDOW=102400

# 输出token配置
CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
CLAUDE_CODE_MAX_OUTPUT_TOKENS_OPENAI=8192

# OpenAI兼容API配置
CLAUDE_CODE_USE_OPENAI_COMPAT=true
OPENAI_COMPAT_BASE_URL=$BASE_URL
OPENAI_COMPAT_API_KEY=$API_KEY
OPENAI_COMPAT_MODEL=$MODEL

# 性能配置
API_TIMEOUT_MS=600000
EOF

echo "配置已保存到 $OUTPUT_FILE"
echo ""
echo "启动 Claude Code:"
echo "  bun run dev"
echo ""
echo "查看完整配置选项:"
echo "  查看 .env.example 文件"
echo "  或运行: cat .env.example"