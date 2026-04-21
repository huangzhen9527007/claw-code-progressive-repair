#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools 统一入口点

这是 memory-tools 插件的统一入口点，整合了所有功能。
"""

import sys
import os
import locale

# 设置UTF-8编码以确保跨平台兼容性
def setup_encoding():
    """设置系统编码为UTF-8"""
    try:
        # 设置标准流的编码
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')

        # 设置locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # 设置环境变量
        os.environ['PYTHONIOENCODING'] = 'utf-8'

        print("[INFO] UTF-8 encoding configured successfully", file=sys.stderr)
    except Exception as e:
        print(f"[WARNING] Failed to configure UTF-8 encoding: {e}", file=sys.stderr)
        print("[INFO] Trying alternative encoding methods...", file=sys.stderr)

# 添加当前目录到Python路径，以便导入src模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.cli import main
except ImportError as e:
    print(f"导入错误: {e}")
    print("当前Python路径:", sys.path)
    print("请确保src目录中包含必要的模块")
    sys.exit(1)

if __name__ == "__main__":
    # 设置编码
    setup_encoding()
    main()