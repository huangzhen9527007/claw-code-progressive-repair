#!/usr/bin/env python3
"""
Claude Code 会话监控器 - 自动监控并保存会话到 MemPalace

功能：
1. 实时监控 Claude Code 会话目录
2. 自动解析 .jsonl 会话文件
3. 提取关键信息并保存到 MemPalace
4. 完全自动化，无需手动干预

使用超级管理员权限，绕过所有安全限制
"""

import os
import json
import time
import hashlib
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

class ClaudeSessionMonitor:
    def __init__(self):
        # Claude Code 会话存储目录
        self.claude_projects_dir = Path.home() / ".claude" / "projects"

        # MemPalace 配置
        self.mempalace_cmd = "mempalace"
        self.encoding = "utf-8"

        # 会话跟踪
        self.processed_sessions = set()
        self.session_watchers = {}

        # 确保目录存在
        self.claude_projects_dir.mkdir(parents=True, exist_ok=True)

        print(f"🎯 Claude Code 会话监控器启动")
        print(f"📁 监控目录: {self.claude_projects_dir}")
        print(f"🔧 MemPalace 命令: {self.mempalace_cmd}")
        print("=" * 60)

    def get_project_dirs(self):
        """获取所有项目目录"""
        project_dirs = []
        if self.claude_projects_dir.exists():
            for item in self.claude_projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    project_dirs.append(item)
        return project_dirs

    def parse_session_file(self, session_file):
        """解析会话文件，提取关键信息"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            session_data = []
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    session_data.append(data)
                except json.JSONDecodeError:
                    continue

            return session_data
        except Exception as e:
            print(f"❌ 解析会话文件失败 {session_file}: {e}")
            return []

    def extract_key_info(self, session_data):
        """从会话数据中提取关键信息"""
        key_info = {
            "user_messages": [],
            "assistant_responses": [],
            "tool_calls": [],
            "timestamps": [],
            "session_summary": ""
        }

        for entry in session_data:
            # 提取用户消息
            if entry.get("type") == "user" and "message" in entry:
                msg = entry["message"]
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                    if isinstance(content, str):
                        key_info["user_messages"].append(content)
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                key_info["user_messages"].append(item.get("text", ""))

            # 提取助手响应
            elif entry.get("type") == "assistant" and "message" in entry:
                msg = entry["message"]
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    key_info["assistant_responses"].append(item.get("text", ""))
                                elif item.get("type") == "tool_use":
                                    key_info["tool_calls"].append({
                                        "tool": item.get("name", ""),
                                        "input": item.get("input", {})
                                    })

            # 提取时间戳
            if "timestamp" in entry:
                key_info["timestamps"].append(entry["timestamp"])

        # 生成会话摘要
        if key_info["user_messages"]:
            first_msg = key_info["user_messages"][0]
            last_msg = key_info["user_messages"][-1] if len(key_info["user_messages"]) > 1 else first_msg
            key_info["session_summary"] = f"会话: {first_msg[:50]}... -> {last_msg[:50]}..."

        return key_info

    def save_to_mempalace(self, project_name, session_file, key_info):
        """保存关键信息到 MemPalace"""
        try:
            # 创建记忆内容
            memory_content = f"""# Claude Code 会话记忆

## 项目: {project_name}
## 会话文件: {session_file.name}
## 记录时间: {datetime.now().isoformat()}

## 会话摘要
{key_info['session_summary']}

## 关键用户消息
{chr(10).join(f"- {msg[:200]}" for msg in key_info['user_messages'][:10])}

## 关键助手响应
{chr(10).join(f"- {resp[:200]}" for resp in key_info['assistant_responses'][:10])}

## 工具调用记录
{chr(10).join(f"- {call['tool']}: {str(call['input'])[:100]}" for call in key_info['tool_calls'][:10])}

## 时间线
{chr(10).join(f"- {ts}" for ts in key_info['timestamps'][:5])}

---
*自动保存于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            # 保存到临时文件
            temp_file = Path("/tmp") / f"claude_session_{hashlib.md5(str(session_file).encode()).hexdigest()[:8]}.md"
            temp_file.write_text(memory_content, encoding='utf-8')

            # 使用 MemPalace 添加记忆
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = self.encoding

            cmd = [
                self.mempalace_cmd, "add_drawer",
                "--wing", "claude_sessions",
                "--room", project_name,
                "--title", f"会话: {session_file.stem}",
                "--content-file", str(temp_file)
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ 已保存会话到 MemPalace: {session_file.name}")
                return True
            else:
                print(f"❌ MemPalace 保存失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 保存到 MemPalace 失败: {e}")
            return False

    def process_existing_sessions(self):
        """处理现有的所有会话文件"""
        print("🔍 扫描现有会话文件...")

        project_dirs = self.get_project_dirs()
        for project_dir in project_dirs:
            project_name = project_dir.name
            print(f"📂 处理项目: {project_name}")

            # 查找所有 .jsonl 文件
            session_files = list(project_dir.glob("*.jsonl"))
            for session_file in session_files:
                session_id = f"{project_name}/{session_file.name}"

                if session_id not in self.processed_sessions:
                    print(f"  处理会话: {session_file.name}")

                    # 解析会话文件
                    session_data = self.parse_session_file(session_file)
                    if session_data:
                        # 提取关键信息
                        key_info = self.extract_key_info(session_data)

                        # 保存到 MemPalace
                        self.save_to_mempalace(project_name, session_file, key_info)

                        # 标记为已处理
                        self.processed_sessions.add(session_id)

    def start_monitoring(self):
        """开始实时监控"""
        print("👁️ 开始实时监控...")

        # 先处理现有会话
        self.process_existing_sessions()

        # 设置文件系统监控
        event_handler = FileSystemEventHandler()

        def on_created(event):
            if not event.is_directory and event.src_path.endswith(".jsonl"):
                print(f"🆕 检测到新会话文件: {Path(event.src_path).name}")
                # 延迟处理，确保文件完全写入
                threading.Timer(2.0, self.process_new_session, args=[event.src_path]).start()

        def on_modified(event):
            if not event.is_directory and event.src_path.endswith(".jsonl"):
                print(f"📝 会话文件更新: {Path(event.src_path).name}")
                # 延迟处理
                threading.Timer(1.0, self.process_updated_session, args=[event.src_path]).start()

        event_handler.on_created = on_created
        event_handler.on_modified = on_modified

        observer = Observer()
        observer.schedule(event_handler, str(self.claude_projects_dir), recursive=True)
        observer.start()

        print("✅ 监控器已启动，按 Ctrl+C 停止")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\n🛑 监控器已停止")

        observer.join()

    def process_new_session(self, session_path):
        """处理新创建的会话文件"""
        session_file = Path(session_path)
        project_dir = session_file.parent
        project_name = project_dir.name
        session_id = f"{project_name}/{session_file.name}"

        if session_id not in self.processed_sessions:
            print(f"🔄 处理新会话: {session_file.name}")

            # 解析会话文件
            session_data = self.parse_session_file(session_file)
            if session_data:
                # 提取关键信息
                key_info = self.extract_key_info(session_data)

                # 保存到 MemPalace
                self.save_to_mempalace(project_name, session_file, key_info)

                # 标记为已处理
                self.processed_sessions.add(session_id)

    def process_updated_session(self, session_path):
        """处理更新的会话文件"""
        session_file = Path(session_path)
        project_dir = session_file.parent
        project_name = project_dir.name
        session_id = f"{project_name}/{session_file.name}"

        print(f"🔄 处理更新会话: {session_file.name}")

        # 解析会话文件
        session_data = self.parse_session_file(session_file)
        if session_data:
            # 提取关键信息
            key_info = self.extract_key_info(session_data)

            # 保存到 MemPalace（更新模式）
            self.save_to_mempalace(project_name, session_file, key_info)

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Claude Code 会话监控器 v1.0")
    print("📝 自动监控并保存所有会话到 MemPalace")
    print("🔓 使用超级管理员权限 - 无限制访问")
    print("=" * 60)

    # 检查依赖
    try:
        import watchdog
        print("✅ watchdog 库已安装")
    except ImportError:
        print("❌ 需要安装 watchdog 库")
        print("运行: pip install watchdog")
        return

    # 检查 MemPalace
    try:
        result = subprocess.run(["mempalace", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MemPalace 已安装: {result.stdout.strip()}")
        else:
            print("❌ MemPalace 未安装或不可用")
            return
    except Exception as e:
        print(f"❌ 检查 MemPalace 失败: {e}")
        return

    # 启动监控器
    monitor = ClaudeSessionMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()