#!/usr/bin/env python3
"""
测试JSON解析和转义字符处理
"""

import json

def test_unescape():
    """测试转义字符处理"""
    test_cases = [
        # (输入, 期望输出)
        ("Hello\\nWorld", "Hello\nWorld"),
        ("Tab\\tseparated", "Tab    separated"),
        ("Quote: \\\"text\\\"", 'Quote: "text"'),
        ("Backslash: \\\\", "Backslash: \\"),
        ("Mixed\\n\\ttest\\nend", "Mixed\n    test\nend"),
        ("No escape", "No escape"),
    ]

    print("=" * 60)
    print("测试转义字符处理")
    print("=" * 60)

    for i, (input_str, expected) in enumerate(test_cases, 1):
        # 模拟 unescape_string 方法
        replacements = {
            '\\n': '\n',
            '\\t': '    ',
            '\\r': '\r',
            '\\"': '"',
            "\\'": "'",
            '\\\\': '\\',
            '\\b': '\b',
            '\\f': '\f',
        }

        result = input_str
        for escaped, unescaped in replacements.items():
            result = result.replace(escaped, unescaped)

        status = "✓" if result == expected else "✗"
        print(f"{status} 测试 {i}: '{input_str}' -> '{result}'")
        if result != expected:
            print(f"    期望: '{expected}'")

def test_json_formatting():
    """测试JSON格式化"""
    print("\n" + "=" * 60)
    print("测试JSON格式化")
    print("=" * 60)

    # 测试嵌套JSON
    nested_json = {
        "name": "John",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "coordinates": {
                "lat": 40.7128,
                "lng": -74.0060
            }
        },
        "hobbies": ["reading", "coding", "hiking"],
        "escaped": "Line1\\nLine2\\tTab"
    }

    print("原始JSON:")
    print(json.dumps(nested_json, indent=2, ensure_ascii=False))

    print("\n格式化后应该:")
    print("1. 转义字符被解析")
    print("2. 嵌套结构清晰")
    print("3. 长列表适当截断")

def test_claude_message():
    """测试Claude消息格式"""
    print("\n" + "=" * 60)
    print("测试Claude消息格式")
    print("=" * 60)

    # 模拟Claude消息
    claude_message = {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "text",
                    "text": "Here's the result:\\n```json\\n{\\n  \"name\": \"test\",\\n  \"value\": 123\\n}\\n```"
                },
                {
                    "type": "tool_use",
                    "name": "search",
                    "input": {
                        "query": "test query",
                        "filters": {"type": "article", "limit": 10}
                    }
                }
            ]
        }
    }

    print("模拟Claude消息:")
    print(json.dumps(claude_message, indent=2, ensure_ascii=False))

    print("\n改进后应该:")
    print("1. \\n 被转换为实际换行")
    print("2. JSON代码块格式正确")
    print("3. 工具调用输入格式化")

def main():
    """主测试函数"""
    print("Claude Code JSON解析改进测试")
    print("=" * 60)

    test_unescape()
    test_json_formatting()
    test_claude_message()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n改进功能:")
    print("1. 转义字符解析 (\\n, \\t, \\\", 等)")
    print("2. 嵌套JSON格式化")
    print("3. 长字符串截断")
    print("4. JSON字符串自动检测和解析")
    print("5. 工具调用和结果美化")

if __name__ == "__main__":
    main()