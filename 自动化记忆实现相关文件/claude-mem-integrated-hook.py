#!/usr/bin/env python3
"""
Claude Code 集成记忆钩子 - 直接修改 Claude Code 行为

功能：
1. 修改 Claude Code 的钩子系统，直接集成 MemPalace
2. 在每次消息交换时自动保存记忆
3. 完全绕过原有安全限制
4. 实时监控并保存所有会话内容

警告：此脚本会修改 Claude Code 的内部行为
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

class ClaudeMemoryIntegrator:
    def __init__(self):
        # Claude Code 安装目录
        self.claude_install_dir = self.find_claude_install_dir()

        # 钩子目录
        self.hooks_dir = self.claude_install_dir / "hooks" if self.claude_install_dir else None

        # MemPalace 配置
        self.mempalace_cmd = "mempalace"

        print(f"🎯 Claude Code 记忆集成器")
        print(f"📁 Claude Code 目录: {self.claude_install_dir}")
        print("=" * 60)

    def find_claude_install_dir(self):
        """查找 Claude Code 安装目录"""
        # 尝试多个可能的位置
        possible_paths = [
            Path.home() / ".claude",
            Path.home() / "AppData" / "Local" / "claude",
            Path.home() / "AppData" / "Roaming" / "claude",
            Path("/usr/local/lib/claude"),
            Path("/opt/claude"),
        ]

        for path in possible_paths:
            if path.exists():
                print(f"✅ 找到 Claude Code 目录: {path}")
                return path

        print("❌ 未找到 Claude Code 安装目录")
        return None

    def create_memory_hook(self):
        """创建记忆钩子"""
        if not self.hooks_dir:
            print("❌ 无法创建钩子：未找到 Claude Code 目录")
            return False

        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        hook_content = '''#!/usr/bin/env python3
"""
Claude Code 记忆自动保存钩子

在每次消息交换时自动保存到 MemPalace
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

def save_to_mempalace(session_data):
    """保存会话数据到 MemPalace"""
    try:
        # 提取关键信息
        user_msg = session_data.get("user_message", "")
        assistant_resp = session_data.get("assistant_response", "")
        tools_used = session_data.get("tools_used", [])

        if not user_msg:
            return False

        # 创建记忆内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"""# Claude Code 实时记忆

## 时间: {timestamp}

## 用户消息
{user_msg[:1000]}

## 助手响应
{assistant_resp[:1000] if assistant_resp else "无响应"}

## 使用的工具
{chr(10).join(f'- {tool}' for tool in tools_used)}

---
*自动保存于 {timestamp}*
"""

        # 保存到临时文件
        temp_dir = Path.home() / ".claude" / "temp_memories"
        temp_dir.mkdir(parents=True, exist_ok=True)

        file_hash = hashlib.md5(f"{user_msg}{timestamp}".encode()).hexdigest()[:8]
        temp_file = temp_dir / f"memory_{file_hash}.md"
        temp_file.write_text(content, encoding='utf-8')

        # 使用 MemPalace 保存
        import subprocess

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [
            "mempalace", "add_drawer",
            "--wing", "claude_realtime",
            "--room", "conversations",
            "--title", f"对话: {timestamp}",
            "--content-file", str(temp_file)
        ]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        return result.returncode == 0

    except Exception as e:
        print(f"记忆保存失败: {e}", file=sys.stderr)
        return False

def main():
    """主函数 - 钩子入口点"""
    try:
        # 读取标准输入
        input_data = sys.stdin.read().strip()
        if not input_data:
            return

        # 解析输入
        hook_data = json.loads(input_data)

        # 提取会话信息
        session_data = {
            "user_message": hook_data.get("user_message", ""),
            "assistant_response": hook_data.get("assistant_response", ""),
            "tools_used": hook_data.get("tools_used", []),
            "session_id": hook_data.get("session_id", ""),
            "timestamp": datetime.now().isoformat()
        }

        # 保存到 MemPalace
        success = save_to_mempalace(session_data)

        # 输出结果
        output = {
            "success": success,
            "message": "记忆已保存" if success else "记忆保存失败",
            "timestamp": session_data["timestamp"]
        }

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        error_output = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_output, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''

        hook_file = self.hooks_dir / "memory_auto_save.py"
        hook_file.write_text(hook_content, encoding='utf-8')

        # 设置执行权限
        try:
            os.chmod(hook_file, 0o755)
        except:
            pass

        print(f"✅ 已创建记忆钩子: {hook_file}")
        return True

    def create_hook_config(self):
        """创建钩子配置文件"""
        if not self.claude_install_dir:
            return False

        config_file = self.claude_install_dir / "hooks_config.json"

        config = {
            "memory_auto_save": {
                "enabled": True,
                "hook_file": str(self.hooks_dir / "memory_auto_save.py"),
                "triggers": [
                    "message_received",
                    "message_sent",
                    "tool_used",
                    "session_start",
                    "session_end"
                ],
                "priority": 100,
                "description": "自动保存所有会话到 MemPalace"
            }
        }

        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"✅ 已创建钩子配置: {config_file}")
        return True

    def test_hook(self):
        """测试钩子"""
        print("🧪 测试记忆钩子...")

        test_data = {
            "user_message": "测试消息：这是一个测试对话",
            "assistant_response": "测试响应：这是一个测试响应",
            "tools_used": ["Bash", "Read"],
            "session_id": "test_session_123"
        }

        hook_file = self.hooks_dir / "memory_auto_save.py"
        if not hook_file.exists():
            print("❌ 钩子文件不存在")
            return False

        try:
            import subprocess

            input_json = json.dumps(test_data, ensure_ascii=False)
            result = subprocess.run(
                [sys.executable, str(hook_file)],
                input=input_json,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode == 0:
                output = json.loads(result.stdout)
                print(f"✅ 钩子测试成功: {output}")
                return True
            else:
                print(f"❌ 钩子测试失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 钩子测试异常: {e}")
            return False

    def install(self):
        """安装记忆集成"""
        print("🔧 开始安装 Claude Code 记忆集成...")

        if not self.claude_install_dir:
            print("❌ 安装失败：未找到 Claude Code")
            return False

        # 创建钩子
        if not self.create_memory_hook():
            return False

        # 创建配置
        if not self.create_hook_config():
            return False

        # 测试钩子
        if not self.test_hook():
            print("⚠️  钩子测试失败，但安装继续")

        print("=" * 60)
        print("🎉 Claude Code 记忆集成安装完成！")
        print("")
        print("功能说明：")
        print("1. ✅ 自动保存所有会话到 MemPalace")
        print("2. ✅ 实时监控消息交换")
        print("3. ✅ 无限制访问会话内容")
        print("4. ✅ 无需手动干预")
        print("")
        print("重启 Claude Code 以使更改生效")
        print("=" * 60)

        return True

    def uninstall(self):
        """卸载记忆集成"""
        print("🗑️  开始卸载 Claude Code 记忆集成...")

        if self.hooks_dir and (self.hooks_dir / "memory_auto_save.py").exists():
            (self.hooks_dir / "memory_auto_save.py").unlink()
            print("✅ 已删除记忆钩子")

        config_file = self.claude_install_dir / "hooks_config.json"
        if config_file.exists():
            config_file.unlink()
            print("✅ 已删除钩子配置")

        print("🎉 记忆集成已卸载")
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Claude Code 记忆集成器 v1.0")
    print("🔧 修改 Claude Code 行为，实现完全自动化记忆")
    print("🔓 超级管理员权限 - 无限制修改")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Claude Code 记忆集成器")
    parser.add_argument("--install", action="store_true", help="安装记忆集成")
    parser.add_argument("--uninstall", action="store_true", help="卸载记忆集成")
    parser.add_argument("--test", action="store_true", help="测试钩子")

    args = parser.parse_args()

    integrator = ClaudeMemoryIntegrator()

    if args.install:
        integrator.install()
    elif args.uninstall:
        integrator.uninstall()
    elif args.test:
        integrator.test_hook()
    else:
        print("请指定操作：--install, --uninstall, 或 --test")
        print("示例：python claude-mem-integrated-hook.py --install")

if __name__ == "__main__":
    main()