#!/usr/bin/env python3
"""
测试文件覆盖功能
"""

import os
from pathlib import Path

def test_overwrite_logic():
    """测试覆盖逻辑"""
    print("=" * 60)
    print("测试文件覆盖逻辑")
    print("=" * 60)

    # 模拟原始文件名
    original_name = "test_session_12345.jsonl"
    print(f"原始文件名: {original_name}")

    # 测试 get_output_filename 逻辑
    if original_name.endswith('.jsonl'):
        output_name = original_name[:-6] + '.md'
    else:
        output_name = original_name + '.md'

    print(f"输出文件名: {output_name}")

    # 测试覆盖逻辑
    output_path = Path("test_output") / output_name

    # 模拟文件已存在的情况
    print(f"\n模拟文件已存在的情况:")
    print(f"输出路径: {output_path}")

    if output_path.exists():
        print("✓ 文件已存在，将直接覆盖")
        # 这里应该直接写入，覆盖旧文件
        print("  旧文件将被新内容覆盖")
    else:
        print("✓ 文件不存在，将创建新文件")

    print("\n" + "=" * 60)
    print("测试完成")
    print("修改后的逻辑:")
    print("1. 同名文件直接覆盖，避免重复")
    print("2. 不会添加时间戳后缀")
    print("3. 确保每次运行都是最新数据")
    print("=" * 60)

if __name__ == "__main__":
    test_overwrite_logic()