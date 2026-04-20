#!/usr/bin/env python3
"""
Claude Code 可读会话保存器 - 增强版

功能：
1. 扫描所有 Claude Code 会话目录
2. 将 JSONL 格式转换为易读的 Markdown 格式
3. 按对话顺序组织内容
4. 提取关键信息（用户消息、助手回复、工具调用等）
5. 生成结构化的对话记录
6. 处理转义字符（\\n, \\t, \\", 等）
7. 格式化嵌套 JSON 数据
8. 自动检测和解析 JSON 字符串

输出格式：
- 对话按时间顺序排列
- 用户消息和助手回复清晰区分
- 工具调用和结果格式化显示
- 转义字符转换为可读格式
- 嵌套 JSON 结构清晰展示
- 元数据单独展示
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import time
import sys
from collections import OrderedDict

class ClaudeReadableSessionSaver:
    def __init__(self):
        # Claude Code 会话存储目录
        self.claude_projects_dir = Path.home() / ".claude" / "projects"

        # 输出目录
        self.output_dir = Path.home() / ".mempalace" / "palace" / "claude_sessions" / "readable_sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[TARGET] Claude Code 可读会话保存器启动")
        print(f"[FOLDER] 扫描目录: {self.claude_projects_dir}")
        print(f"[OUTPUT] 输出目录: {self.output_dir}")
        print(f"[FORMAT] 输出格式: 结构化可读 Markdown")
        print("=" * 60)

    def get_all_session_files(self):
        """获取所有会话文件"""
        session_files = []

        if self.claude_projects_dir.exists():
            for project_dir in self.claude_projects_dir.iterdir():
                if project_dir.is_dir() and not project_dir.name.startswith("."):
                    for session_file in project_dir.glob("*.jsonl"):
                        session_files.append({
                            "path": session_file,
                            "project": project_dir.name,
                            "filename": session_file.name,
                            "size": session_file.stat().st_size,
                            "mtime": session_file.stat().st_mtime
                        })

        # 按修改时间排序（最新的优先）
        session_files.sort(key=lambda x: x["mtime"], reverse=True)
        return session_files

    def get_output_filename(self, session_file):
        """生成输出文件名：保持原始文件名，扩展名改为 _readable.md"""
        original_name = session_file.name  # 例如：855a9554-5eb5-4e70-98db-925d94923713.jsonl
        if original_name.endswith('.jsonl'):
            # 去掉 .jsonl，加上 _readable.md
            return original_name[:-6] + '_readable.md'
        else:
            # 如果不是 .jsonl 扩展名，直接加上 _readable.md
            return original_name + '_readable.md'

    def format_timestamp(self, timestamp_str):
        """格式化时间戳"""
        try:
            # 尝试解析 ISO 格式时间戳
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str

    def unescape_string(self, text):
        """处理转义字符，将 \n, \t, \" 等转换为可读格式"""
        if not isinstance(text, str):
            return text

        # 替换常见的转义序列
        replacements = {
            '\\n': '\n',      # 换行
            '\\t': '    ',    # 制表符（4个空格）
            '\\r': '\r',      # 回车
            '\\"': '"',       # 双引号
            "\\'": "'",       # 单引号
            '\\\\': '\\',     # 反斜杠
            '\\b': '\b',      # 退格
            '\\f': '\f',      # 换页
        }

        result = text
        for escaped, unescaped in replacements.items():
            result = result.replace(escaped, unescaped)

        return result

    def format_json_for_display(self, data, indent=2, max_depth=3, current_depth=0):
        """格式化JSON数据为可读文本，处理嵌套和转义字符"""
        if current_depth >= max_depth:
            return json.dumps(data, ensure_ascii=False)[:100] + "..." if len(str(data)) > 100 else json.dumps(data, ensure_ascii=False)

        if isinstance(data, dict):
            if not data:
                return "{}"

            lines = []
            for key, value in data.items():
                formatted_value = self.format_json_for_display(value, indent, max_depth, current_depth + 1)
                lines.append(f"{' ' * (indent * (current_depth + 1))}{key}: {formatted_value}")

            if current_depth == 0:
                return '\n'.join(lines)
            else:
                return '{\n' + '\n'.join(lines) + '\n' + ' ' * (indent * current_depth) + '}'

        elif isinstance(data, list):
            if not data:
                return "[]"

            if len(data) <= 3:  # 短列表直接显示
                items = [self.format_json_for_display(item, indent, max_depth, current_depth + 1) for item in data]
                return '[' + ', '.join(items) + ']'
            else:  # 长列表分行显示
                lines = []
                for i, item in enumerate(data[:5]):  # 只显示前5个
                    formatted_item = self.format_json_for_display(item, indent, max_depth, current_depth + 1)
                    lines.append(f"{' ' * (indent * (current_depth + 1))}{formatted_item}")

                if len(data) > 5:
                    lines.append(f"{' ' * (indent * (current_depth + 1))}... 还有 {len(data) - 5} 个元素")

                return '[\n' + '\n'.join(lines) + '\n' + ' ' * (indent * current_depth) + ']'

        elif isinstance(data, str):
            # 处理转义字符
            unescaped = self.unescape_string(data)

            # 如果字符串包含JSON，尝试解析
            if data.strip().startswith('{') or data.strip().startswith('['):
                try:
                    parsed = json.loads(data)
                    return self.format_json_for_display(parsed, indent, max_depth, current_depth + 1)
                except:
                    pass

            # 长字符串截断
            if len(unescaped) > 200:
                return f'"{unescaped[:200]}..." (共{len(unescaped)}字符)'
            else:
                return f'"{unescaped}"'

        elif data is None:
            return "null"

        else:
            return str(data)

    def format_message_content(self, content):
        """格式化消息内容，处理嵌套JSON和转义字符"""
        if isinstance(content, str):
            # 处理纯字符串内容
            unescaped = self.unescape_string(content.strip())

            # 检查是否是JSON字符串
            content_stripped = content.strip()
            if (content_stripped.startswith('{') and content_stripped.endswith('}')) or \
               (content_stripped.startswith('[') and content_stripped.endswith(']')):
                try:
                    parsed = json.loads(content)
                    return f"```json\n{self.format_json_for_display(parsed)}\n```"
                except json.JSONDecodeError:
                    # 如果不是有效JSON，返回原始内容
                    return unescaped

            return unescaped

        elif isinstance(content, list):
            # 处理内容数组
            formatted_parts = []
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get('type', '')
                    if item_type == 'text':
                        text = item.get('text', '')
                        if text:
                            formatted_text = self.format_message_content(text)
                            formatted_parts.append(formatted_text)

                    elif item_type == 'tool_use':
                        tool_name = item.get('name', '未知工具')
                        tool_input = item.get('input', {})
                        formatted_parts.append(f"\n### 🛠️ 工具调用: {tool_name}")

                        if tool_input:
                            formatted_input = self.format_json_for_display(tool_input)
                            formatted_parts.append(f"**输入**:\n```json\n{formatted_input}\n```")

                    elif item_type == 'tool_result':
                        tool_name = item.get('tool_name', '未知工具')
                        content_data = item.get('content', '')
                        formatted_parts.append(f"\n### 📋 工具结果: {tool_name}")

                        if content_data:
                            if isinstance(content_data, (dict, list)):
                                formatted_content = self.format_json_for_display(content_data)
                                formatted_parts.append(f"```json\n{formatted_content}\n```")
                            else:
                                # 尝试解析字符串内容
                                formatted_content = self.format_message_content(str(content_data))
                                formatted_parts.append(f"{formatted_content}")

                elif isinstance(item, str):
                    formatted_text = self.format_message_content(item)
                    formatted_parts.append(formatted_text)

            return '\n'.join(filter(None, formatted_parts))

        elif isinstance(content, (dict, list)):
            # 直接是字典或列表
            return f"```json\n{self.format_json_for_display(content)}\n```"

        else:
            return str(content)

    def parse_session_data(self, lines):
        """解析会话数据，提取结构化信息"""
        messages = []
        metadata = {
            "session_id": None,
            "project_name": None,
            "start_time": None,
            "end_time": None,
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "tool_calls": 0,
            "queue_operations": 0
        }

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                msg_type = data.get('type', '')

                # 更新元数据
                metadata["total_messages"] += 1

                if msg_type == 'queue-operation':
                    metadata["queue_operations"] += 1
                    operation = data.get('operation', '')
                    timestamp = data.get('timestamp', '')
                    if operation == 'enqueue' and not metadata["start_time"]:
                        metadata["start_time"] = timestamp
                    messages.append({
                        "type": "queue",
                        "operation": operation,
                        "timestamp": timestamp,
                        "raw": data
                    })

                elif msg_type == 'user':
                    metadata["user_messages"] += 1
                    message_data = data.get('message', {})
                    content = message_data.get('content', '')
                    messages.append({
                        "type": "user",
                        "content": self.format_message_content(content),
                        "timestamp": data.get('timestamp', ''),
                        "uuid": data.get('uuid', ''),
                        "session_id": data.get('sessionId', ''),
                        "raw": data
                    })
                    if not metadata["session_id"]:
                        metadata["session_id"] = data.get('sessionId')

                elif msg_type == 'assistant':
                    metadata["assistant_messages"] += 1
                    message_data = data.get('message', {})
                    content = message_data.get('content', [])

                    # 统计工具调用
                    tool_calls = 0
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'tool_use':
                                tool_calls += 1
                    metadata["tool_calls"] += tool_calls

                    messages.append({
                        "type": "assistant",
                        "content": self.format_message_content(content),
                        "timestamp": data.get('timestamp', ''),
                        "uuid": data.get('uuid', ''),
                        "model": message_data.get('model', ''),
                        "stop_reason": message_data.get('stop_reason', ''),
                        "usage": message_data.get('usage', {}),
                        "tool_calls": tool_calls,
                        "raw": data
                    })

                elif msg_type == 'last-prompt':
                    messages.append({
                        "type": "last_prompt",
                        "prompt": data.get('lastPrompt', ''),
                        "timestamp": data.get('timestamp', ''),
                        "session_id": data.get('sessionId', ''),
                        "raw": data
                    })

                elif msg_type == 'system':
                    messages.append({
                        "type": "system",
                        "content": data.get('content', ''),
                        "timestamp": data.get('timestamp', ''),
                        "raw": data
                    })

                else:
                    # 其他类型的消息
                    messages.append({
                        "type": "other",
                        "msg_type": msg_type,
                        "data": data,
                        "raw": data
                    })

            except json.JSONDecodeError as e:
                print(f"[WARNING] 第 {line_num} 行 JSON 解析错误: {e}")
                messages.append({
                    "type": "error",
                    "line_num": line_num,
                    "error": str(e),
                    "raw_line": line[:200]
                })

        # 设置结束时间（最后一条消息的时间）
        if messages:
            last_msg = messages[-1]
            if 'timestamp' in last_msg and last_msg['timestamp']:
                metadata["end_time"] = last_msg['timestamp']

        return messages, metadata

    def generate_readable_markdown(self, project_name, session_file, messages, metadata):
        """生成可读的Markdown内容"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_mtime = datetime.fromtimestamp(session_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # 生成输出文件名
        output_filename = self.get_output_filename(session_file)
        output_path = self.output_dir / output_filename

        # 检查文件是否已存在
        if output_path.exists():
            print(f"[INFO] 文件已存在，将覆盖: {output_filename}")

        # 构建Markdown内容
        md_content = []

        # 1. 标题和元数据
        md_content.append(f"# Claude Code 会话记录 - 可读版\n")
        md_content.append(f"**原始项目**: {project_name}\n")
        md_content.append(f"**原始文件**: {session_file.name}\n")
        md_content.append(f"**会话ID**: {metadata['session_id'] or '未知'}\n")
        md_content.append(f"**文件修改时间**: {file_mtime}\n")
        md_content.append(f"**转换时间**: {timestamp}\n")
        md_content.append(f"**会话时长**: {self.format_timestamp(metadata['start_time']) if metadata['start_time'] else '未知'} - {self.format_timestamp(metadata['end_time']) if metadata['end_time'] else '未知'}\n")

        # 2. 统计信息表格
        md_content.append(f"\n## 📊 会话统计\n")
        md_content.append("| 指标 | 数量 |\n")
        md_content.append("|------|------|\n")
        md_content.append(f"| 总消息数 | {metadata['total_messages']} |\n")
        md_content.append(f"| 用户消息 | {metadata['user_messages']} |\n")
        md_content.append(f"| 助手回复 | {metadata['assistant_messages']} |\n")
        md_content.append(f"| 工具调用 | {metadata['tool_calls']} |\n")
        md_content.append(f"| 队列操作 | {metadata['queue_operations']} |\n")

        # 3. 对话内容
        md_content.append(f"\n## 💬 对话记录\n")

        conversation_count = 0
        for i, msg in enumerate(messages):
            if msg['type'] in ['user', 'assistant']:
                conversation_count += 1

                if msg['type'] == 'user':
                    md_content.append(f"\n### 👤 用户 ({conversation_count})\n")
                    md_content.append(f"**时间**: {self.format_timestamp(msg.get('timestamp', ''))}\n")
                    md_content.append(f"**UUID**: `{msg.get('uuid', '')}`\n")
                    md_content.append(f"\n{msg['content']}\n")

                elif msg['type'] == 'assistant':
                    md_content.append(f"\n### 🤖 助手 ({conversation_count})\n")
                    md_content.append(f"**时间**: {self.format_timestamp(msg.get('timestamp', ''))}\n")
                    md_content.append(f"**UUID**: `{msg.get('uuid', '')}`\n")
                    md_content.append(f"**模型**: {msg.get('model', '未知')}\n")
                    md_content.append(f"**停止原因**: {msg.get('stop_reason', '未知')}\n")

                    if msg.get('tool_calls', 0) > 0:
                        md_content.append(f"**工具调用**: {msg['tool_calls']} 次\n")

                    # 显示Token使用情况
                    usage = msg.get('usage', {})
                    if usage:
                        input_tokens = usage.get('input_tokens', 0)
                        output_tokens = usage.get('output_tokens', 0)
                        total_tokens = input_tokens + output_tokens
                        md_content.append(f"**Token使用**: 输入 {input_tokens} | 输出 {output_tokens} | 总计 {total_tokens}\n")

                    # 格式化内容，确保转义字符被正确处理
                    formatted_content = msg['content']
                    if formatted_content:
                        md_content.append(f"\n{formatted_content}\n")
                    else:
                        md_content.append(f"\n*(空内容)*\n")

        # 4. 其他消息类型
        other_messages = [msg for msg in messages if msg['type'] not in ['user', 'assistant']]
        if other_messages:
            md_content.append(f"\n## ⚙️ 系统消息\n")

            for msg in other_messages:
                if msg['type'] == 'queue':
                    operation = msg.get('operation', '')
                    timestamp = msg.get('timestamp', '')
                    md_content.append(f"- **队列操作**: {operation} ({self.format_timestamp(timestamp)})\n")

                elif msg['type'] == 'last_prompt':
                    prompt = msg.get('prompt', '')
                    md_content.append(f"- **最后提示**: {prompt}\n")

                elif msg['type'] == 'system':
                    content = msg.get('content', '')
                    md_content.append(f"- **系统消息**: {content}\n")

                elif msg['type'] == 'error':
                    line_num = msg.get('line_num', 0)
                    error = msg.get('error', '')
                    md_content.append(f"- **解析错误** (第{line_num}行): {error}\n")

        # 5. 原始数据链接
        md_content.append(f"\n---\n")
        md_content.append(f"*转换完成于 {timestamp}*\n")
        md_content.append(f"*原始JSONL数据已完整保存，可通过原始文件名查找*\n")

        # 写入文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))

            saved_size = output_path.stat().st_size
            print(f"[SAVED] {output_filename} ({saved_size:,} 字节)")
            print(f"        对话轮次: {conversation_count}")
            print(f"        用户消息: {metadata['user_messages']}")
            print(f"        助手回复: {metadata['assistant_messages']}")
            print(f"        工具调用: {metadata['tool_calls']}")

            return {
                "output_path": output_path,
                "saved_size": saved_size,
                "conversation_count": conversation_count,
                "user_messages": metadata['user_messages'],
                "assistant_messages": metadata['assistant_messages'],
                "tool_calls": metadata['tool_calls']
            }

        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_readable_session(self, project_name, session_file):
        """保存可读会话数据"""
        print(f"[READING] 读取文件: {session_file.name} ({session_file.stat().st_size:,} 字节)")

        try:
            # 读取原始文件
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            print(f"[LINES] 总行数: {total_lines}")

            # 解析会话数据
            messages, metadata = self.parse_session_data(lines)

            # 生成可读Markdown
            result = self.generate_readable_markdown(project_name, session_file, messages, metadata)

            return result

        except Exception as e:
            print(f"[ERROR] 处理失败 {session_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def process_all_sessions(self, max_files=None):
        """处理所有会话文件"""
        print(f"[SEARCH] 开始扫描会话文件...")

        session_files = self.get_all_session_files()
        print(f"[FOUND] 找到 {len(session_files)} 个会话文件")

        if max_files:
            session_files = session_files[:max_files]
            print(f"[LIMIT] 限制处理前 {max_files} 个文件")

        processed_results = []
        success_count = 0
        fail_count = 0

        for i, file_info in enumerate(session_files, 1):
            file_path = file_info["path"]
            project_name = file_info["project"]

            print(f"\n[PROCESS] ({i}/{len(session_files)}) 处理: {project_name[:30]}/{file_path.name[:30]}")
            print(f"         大小: {file_info['size']:,} 字节")

            # 保存可读会话数据
            result = self.save_readable_session(project_name, file_path)

            if result:
                processed_results.append(result)
                success_count += 1
            else:
                processed_results.append(None)
                fail_count += 1

            # 避免处理太快
            if i < len(session_files):
                time.sleep(0.1)

        print(f"\n" + "="*60)
        print(f"[SUMMARY] 处理完成")
        print(f"          成功: {success_count} 个文件")
        print(f"          失败: {fail_count} 个文件")
        print(f"          总计: {len(session_files)} 个文件")

        if success_count > 0:
            total_conversations = sum(r["conversation_count"] for r in processed_results if r)
            total_user_msgs = sum(r["user_messages"] for r in processed_results if r)
            total_assistant_msgs = sum(r["assistant_messages"] for r in processed_results if r)
            total_tool_calls = sum(r["tool_calls"] for r in processed_results if r)

            print(f"\n[DATA] 数据统计:")
            print(f"       总对话轮次: {total_conversations}")
            print(f"       总用户消息: {total_user_msgs}")
            print(f"       总助手回复: {total_assistant_msgs}")
            print(f"       总工具调用: {total_tool_calls}")
            print(f"\n[LOCATION] 所有文件保存在: {self.output_dir}")

        return success_count

def main():
    """主函数"""
    print("=" * 60)
    print("[ROBOT] Claude Code Readable Session Saver v2.0")
    print("[NOTE] 将JSONL转换为易读的Markdown格式")
    print("[FORMAT] 结构化对话记录，包含统计信息和格式化内容")
    print("[ENHANCED] 转义字符解析 + 嵌套JSON格式化")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Readable Session Saver")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum files to process (default: all)")
    parser.add_argument("--test", action="store_true", help="Test mode (process only 2 files)")

    args = parser.parse_args()

    # 启动保存器
    saver = ClaudeReadableSessionSaver()

    if args.test:
        print("[TEST] 测试模式：只处理前 2 个文件")
        saver.process_all_sessions(max_files=2)
    else:
        saver.process_all_sessions(max_files=args.max_files)

    print("=" * 60)
    print("[SUCCESS] 任务完成！所有会话已转换为可读格式")
    print("[DIRECTORY] 输出目录: ~/.mempalace/palace/claude_sessions/readable_sessions/")
    print("[FILENAME] 文件名格式: 原始文件名_readable.md")
    print("[FEATURES] 功能:")
    print("          1. 结构化对话记录")
    print("          2. 统计信息表格")
    print("          3. 格式化消息内容")
    print("          4. 工具调用展示")
    print("          5. Token使用统计")
    print("          6. 转义字符解析 (\\n, \\t, \\\", 等)")
    print("          7. 嵌套JSON格式化")
    print("          8. JSON字符串自动检测")
    print("=" * 60)

if __name__ == "__main__":
    main()