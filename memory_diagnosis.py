#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统诊断工具 - 主入口脚本
从项目根目录调用记忆系统诊断工具
"""

import sys
import os
from pathlib import Path

def main():
    """主函数"""
    # 获取工具目录
    tool_dir = Path(__file__).parent / "memory-diagnosis-tool"

    if not tool_dir.exists():
        print(f"错误: 工具目录不存在: {tool_dir}")
        sys.exit(1)

    # 添加工具目录到Python路径
    sys.path.insert(0, str(tool_dir))

    # 导入并运行CLI工具
    try:
        from memory_diagnosis_cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"错误: 无法导入记忆系统诊断工具: {e}")
        print(f"请确保以下文件存在:")
        print(f"  {tool_dir}/memory_system_diagnosis_skill.py")
        print(f"  {tool_dir}/memory_diagnosis_cli.py")
        sys.exit(1)
    except Exception as e:
        print(f"运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()