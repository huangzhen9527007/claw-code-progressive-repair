#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools 统一入口点

这是 memory-tools 插件的统一入口点，整合了所有功能。
"""

import sys
import os

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
    main()