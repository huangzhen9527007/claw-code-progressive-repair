#!/bin/bash
# 使用 mempalace 的脚本

MEMPA_DIR="mempalace/mempalace"

# 激活虚拟环境
source "$MEMPA_DIR/venv/Scripts/activate"

# 执行 mempalace 命令
python -m mempalace "$@"