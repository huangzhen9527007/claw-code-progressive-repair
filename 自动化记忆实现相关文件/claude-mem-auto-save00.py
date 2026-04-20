#!/usr/bin/env python3
"""
Claude Code 自动记忆保存器 - 简化版

功能：
1. 扫描 Claude Code 会话目录
2. 自动解析 .jsonl 会话文件
3. 提取关键信息并保存到 MemPalace
4. 可以设置为定时任务或手动运行

无需额外依赖，使用纯 Python 实现
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import time

class ClaudeAutoMemorySaver:
    def __init__(self):
        # Claude Code 会话存储目录
        self.claude_projects_dir = Path.home() / ".claude" / "projects"

        # MemPalace 配置
        self.mempalace_cmd = "mempalace"
        self.encoding = "utf-8"

        # 处理状态文件
        self.state_file = Path.home() / ".claude" / "memory_saver_state.json"
        self.processed_files = self.load_state()

        print(f"[TARGET] Claude Code 自动记忆保存器启动")
        print(f"[FOLDER] 扫描目录: {self.claude_projects_dir}")
        print("=" * 60)

    def load_state(self):
        """加载处理状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_state(self):
        """保存处理状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_files), f, ensure_ascii=False, indent=2)
        except:
            pass

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
                            "size": session_file.stat().st_size
                        })

        # 按修改时间排序（最新的优先）
        session_files.sort(key=lambda x: x["path"].stat().st_mtime, reverse=True)
        return session_files

    def parse_session_file(self, session_file):
        """解析会话文件"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 只解析最后100行（最新的对话）
            recent_lines = lines[-100:] if len(lines) > 100 else lines

            session_data = []
            for line in recent_lines:
                try:
                    data = json.loads(line.strip())
                    session_data.append(data)
                except json.JSONDecodeError:
                    continue

            return session_data
        except Exception as e:
            print(f"[ERROR] 解析失败 {session_file.name}: {e}")
            return []

    def extract_conversation_summary(self, session_data):
        """提取对话摘要"""
        user_messages = []
        assistant_responses = []
        tool_calls = []

        for entry in session_data:
            entry_type = entry.get("type", "")

            if entry_type == "user" and "message" in entry:
                msg = entry["message"]
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                    if isinstance(content, str):
                        user_messages.append(content[:500])
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                user_messages.append(item.get("text", "")[:500])

            elif entry_type == "assistant" and "message" in entry:
                msg = entry["message"]
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    assistant_responses.append(item.get("text", "")[:500])
                                elif item.get("type") == "tool_use":
                                    tool_name = item.get("name", "unknown")
                                    tool_calls.append(tool_name)

        # 生成摘要
        summary = ""
        if user_messages:
            summary = f"用户消息: {len(user_messages)}条"
            if user_messages:
                summary += f" | 示例: {user_messages[0][:100]}..."

        if assistant_responses:
            summary += f" | 助手响应: {len(assistant_responses)}条"

        if tool_calls:
            unique_tools = list(set(tool_calls))
            summary += f" | 工具调用: {', '.join(unique_tools[:3])}"

        return summary, user_messages, assistant_responses, tool_calls

    def create_memory_content(self, project_name, file_name, summary, user_msgs, assistant_resps, tool_calls, file_path=None):
        """创建记忆内容"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取文件修改时间
        if file_path and Path(file_path).exists():
            file_time = datetime.fromtimestamp(Path(file_path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        else:
            file_time = timestamp

        content = f"""# Claude Code 会话记忆

## 基本信息
- **项目**: {project_name}
- **会话文件**: {file_name}
- **文件时间**: {file_time}
- **保存时间**: {timestamp}

## 会话摘要
{summary}

## 用户消息示例
{chr(10).join(f'{i+1}. {msg}' for i, msg in enumerate(user_msgs[:5]))}

## 助手响应示例
{chr(10).join(f'{i+1}. {resp}' for i, resp in enumerate(assistant_resps[:5]))}

## 工具调用
{chr(10).join(f'- {tool}' for tool in tool_calls[:10])}

---
*自动保存于 {timestamp}*
"""
        return content

    def save_to_mempalace(self, project_name, session_file, content):
        """保存到 MemPalace"""
        try:
            # 确保 session_file 是 Path 对象
            if isinstance(session_file, str):
                session_file = Path(session_file)

            # 创建临时文件
            temp_dir = Path.home() / ".claude" / "temp_memories"
            temp_dir.mkdir(parents=True, exist_ok=True)

            file_hash = hashlib.md5(str(session_file).encode()).hexdigest()[:8]
            temp_file = temp_dir / f"memory_{file_hash}.md"
            temp_file.write_text(content, encoding='utf-8')

            # 设置环境
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = self.encoding

            # 使用 mempalace add_drawer 命令
            cmd = [
                self.mempalace_cmd, "add_drawer",
                "--wing", "claude_sessions",
                "--room", project_name.replace("-", "_"),
                "--title", f"会话: {session_file.stem}",
                "--content-file", str(temp_file)
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"[OK] 已保存: {project_name}/{session_file.name}")
                return True
            else:
                # 尝试使用更简单的方法
                print(f"[WARNING]  MemPalace 命令失败，尝试替代方法...")
                return self.save_to_mempalace_simple(project_name, session_file, content)

        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            return False

    def save_to_mempalace_simple(self, project_name, session_file, content):
        """简单的保存方法"""
        try:
            # 确保 session_file 是 Path 对象
            if isinstance(session_file, str):
                session_file = Path(session_file)

            # 直接创建记忆文件到 MemPalace 目录
            mempalace_dir = Path.home() / ".mempalace" / "palace" / "claude_sessions" / project_name.replace("-", "_")
            mempalace_dir.mkdir(parents=True, exist_ok=True)

            file_hash = hashlib.md5(str(session_file).encode()).hexdigest()[:8]
            memory_file = mempalace_dir / f"{session_file.stem}_{file_hash}.md"
            memory_file.write_text(content, encoding='utf-8')

            print(f"[OK] 直接保存到: {memory_file}")
            return True
        except Exception as e:
            print(f"[ERROR] 直接保存失败: {e}")
            return False

    def process_sessions(self, max_files=20):
        """处理会话文件"""
        print(f"[SEARCH] 开始扫描会话文件 (最多 {max_files} 个)...")

        session_files = self.get_all_session_files()
        new_files = []

        for file_info in session_files[:max_files]:
            file_path = file_info["path"]
            file_id = f"{file_info['project']}/{file_path.name}"

            if file_id not in self.processed_files:
                new_files.append(file_info)

        print(f"[CHART] 找到 {len(session_files)} 个会话文件，{len(new_files)} 个未处理")

        processed_count = 0
        for file_info in new_files:
            file_path = file_info["path"]
            project_name = file_info["project"]
            file_id = f"{project_name}/{file_path.name}"

            print(f"[REFRESH] 处理: {project_name}/{file_path.name} ({file_info['size']} bytes)")

            # 解析会话
            session_data = self.parse_session_file(file_path)
            if not session_data:
                print(f"  跳过: 无有效数据")
                self.processed_files.add(file_id)
                continue

            # 提取摘要
            summary, user_msgs, assistant_resps, tool_calls = self.extract_conversation_summary(session_data)

            if not summary:
                print(f"  跳过: 无对话内容")
                self.processed_files.add(file_id)
                continue

            print(f"  摘要: {summary}")

            # 创建记忆内容
            content = self.create_memory_content(
                project_name, file_path.name, summary,
                user_msgs, assistant_resps, tool_calls,
                file_path
            )

            # 保存到 MemPalace
            if self.save_to_mempalace(project_name, file_path, content):
                processed_count += 1
                self.processed_files.add(file_id)

            # 避免处理太快
            time.sleep(0.5)

        # 保存状态
        self.save_state()

        print(f"[OK] 处理完成: {processed_count} 个新会话已保存")
        return processed_count

    def run_continuous(self, interval=60):
        """持续运行模式"""
        print(f"[REFRESH] 进入持续运行模式，每 {interval} 秒扫描一次")
        print("按 Ctrl+C 停止")

        try:
            while True:
                print(f"\n[CLOCK] {datetime.now().strftime('%H:%M:%S')} - 开始扫描...")
                self.process_sessions(max_files=10)
                print(f"[SLEEP] 等待 {interval} 秒...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[STOP] 已停止")

def main():
    """主函数"""
    print("=" * 60)
    print("[ROBOT] Claude Code Auto Memory Saver v1.0")
    print("[NOTE] Auto scan and save all sessions to MemPalace")
    print("[UNLOCK] Unlimited access to all session content")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Auto Memory Saver")
    parser.add_argument("--once", action="store_true", help="Run once only")
    parser.add_argument("--continuous", action="store_true", help="Continuous mode")
    parser.add_argument("--interval", type=int, default=60, help="Scan interval (seconds)")
    parser.add_argument("--max-files", type=int, default=20, help="Maximum files to process")

    args = parser.parse_args()

    # 检查 MemPalace
    try:
        result = subprocess.run([sys.executable, "-m", "mempalace", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] MemPalace 可用")
        else:
            print("[WARNING]  MemPalace 可能未正确安装，尝试继续...")
    except:
        print("[WARNING]  无法检查 MemPalace，尝试继续...")

    # 启动保存器
    saver = ClaudeAutoMemorySaver()

    if args.continuous:
        saver.run_continuous(interval=args.interval)
    else:
        saver.process_sessions(max_files=args.max_files)

    print("=" * 60)
    print("[PARTY] 任务完成！")

if __name__ == "__main__":
    main()