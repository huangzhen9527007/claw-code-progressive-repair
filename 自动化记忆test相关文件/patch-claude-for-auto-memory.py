#!/usr/bin/env python3
"""
Claude Code 自动记忆补丁 - 直接修改源代码

功能：
1. 直接修改 Claude Code 的源代码
2. 在核心位置插入自动记忆保存代码
3. 实现完全透明的自动化记忆
4. 无需额外配置或钩子

警告：此脚本会直接修改 Claude Code 的源代码
"""

import os
import re
import shutil
from pathlib import Path
import sys

class ClaudeCodePatcher:
    def __init__(self):
        # 查找 Claude Code 源代码
        self.claude_source_dir = self.find_claude_source()

        # 备份目录
        self.backup_dir = Path.home() / ".claude" / "backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"🎯 Claude Code 自动记忆补丁")
        print(f"📁 源代码目录: {self.claude_source_dir}")
        print("=" * 60)

    def find_claude_source(self):
        """查找 Claude Code 源代码"""
        # 尝试多个可能的位置
        possible_paths = [
            Path.home() / ".claude" / "src",
            Path.home() / "AppData" / "Local" / "claude" / "src",
            Path.home() / "AppData" / "Roaming" / "claude" / "src",
            Path("/usr/local/lib/claude/src"),
            Path("/opt/claude/src"),
            # 当前项目可能也是源代码
            Path.cwd() / "src",
        ]

        for path in possible_paths:
            if path.exists():
                # 检查是否有典型的 Claude Code 文件
                if (path / "main.tsx").exists() or (path / "query.ts").exists():
                    print(f"✅ 找到 Claude Code 源代码: {path}")
                    return path

        print("❌ 未找到 Claude Code 源代码")
        return None

    def backup_file(self, file_path):
        """备份文件"""
        if not file_path.exists():
            return False

        backup_path = self.backup_dir / file_path.relative_to(self.claude_source_dir)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        print(f"📦 已备份: {file_path} -> {backup_path}")
        return True

    def restore_backup(self):
        """恢复备份"""
        if not self.backup_dir.exists():
            print("❌ 备份目录不存在")
            return False

        restored_count = 0
        for backup_file in self.backup_dir.rglob("*"):
            if backup_file.is_file():
                target_file = self.claude_source_dir / backup_file.relative_to(self.backup_dir)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_file)
                restored_count += 1

        print(f"✅ 已恢复 {restored_count} 个文件")
        return restored_count > 0

    def patch_query_ts(self):
        """修补 query.ts - 主要的查询处理文件"""
        query_file = self.claude_source_dir / "query.ts"
        if not query_file.exists():
            print(f"❌ 未找到 query.ts: {query_file}")
            return False

        self.backup_file(query_file)

        # 读取文件内容
        with open(query_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找发送消息的位置
        send_message_pattern = r'(async function sendMessage|const sendMessage|function sendMessage)'

        if re.search(send_message_pattern, content):
            print("✅ 找到 sendMessage 函数")

            # 在发送消息后添加记忆保存代码
            memory_patch = '''
// ==================== 自动记忆补丁开始 ====================
// 在每次消息交换后自动保存到 MemPalace
async function saveToMemPalace(userMessage: string, assistantResponse: string, toolsUsed: string[]) {
    try {
        const { spawn } = require('child_process');
        const path = require('path');
        const fs = require('fs');
        const os = require('os');

        // 创建记忆内容
        const timestamp = new Date().toISOString();
        const memoryContent = `# Claude Code 自动记忆

## 时间: ${new Date().toLocaleString()}

## 用户消息
${userMessage.substring(0, 1000)}

## 助手响应
${assistantResponse.substring(0, 1000)}

## 使用的工具
${toolsUsed.join('\\n- ')}

---
*自动保存于 ${timestamp}*
`;

        // 保存到临时文件
        const tempDir = path.join(os.homedir(), '.claude', 'temp_memories');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }

        const fileHash = require('crypto').createHash('md5')
            .update(userMessage + timestamp)
            .digest('hex')
            .substring(0, 8);

        const tempFile = path.join(tempDir, `memory_${fileHash}.md`);
        fs.writeFileSync(tempFile, memoryContent, 'utf-8');

        // 调用 MemPalace
        const env = { ...process.env, PYTHONIOENCODING: 'utf-8' };
        const mempalaceCmd = ['mempalace', 'add_drawer',
            '--wing', 'claude_auto',
            '--room', 'conversations',
            '--title', `对话: ${new Date().toLocaleTimeString()}`,
            '--content-file', tempFile];

        spawn(mempalaceCmd[0], mempalaceCmd.slice(1), {
            env,
            stdio: 'ignore',
            detached: true
        }).unref();

        console.log('💾 自动记忆已保存');

    } catch (error) {
        // 静默失败，不影响主流程
        console.error('记忆保存失败:', error.message);
    }
}
// ==================== 自动记忆补丁结束 ====================
'''

            # 在文件开头添加补丁
            patched_content = memory_patch + '\n' + content

            # 查找发送消息后的位置插入调用
            send_call_pattern = r'(await sendMessage\([^)]+\))'

            def insert_memory_call(match):
                send_call = match.group(1)
                return f'''{send_call}

            // 自动保存记忆
            try {{
                const userMsg = messages[messages.length - 1]?.content || "";
                const assistantResp = response?.content || "";
                const tools = response?.tool_calls?.map(tc => tc.name) || [];

                saveToMemPalace(userMsg, assistantResp, tools).catch(() => {{}});
            }} catch (e) {{
                // 忽略错误
            }}'''

            patched_content = re.sub(send_call_pattern, insert_memory_call, patched_content)

            # 写回文件
            with open(query_file, 'w', encoding='utf-8') as f:
                f.write(patched_content)

            print(f"✅ 已修补 query.ts")
            return True
        else:
            print("❌ 未找到 sendMessage 函数")
            return False

    def patch_main_tsx(self):
        """修补 main.tsx - 主入口文件"""
        main_file = self.claude_source_dir / "main.tsx"
        if not main_file.exists():
            print(f"❌ 未找到 main.tsx: {main_file}")
            return False

        self.backup_file(main_file)

        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 在文件开头添加初始化代码
        init_patch = '''
// ==================== 自动记忆初始化 ====================
console.log('🤖 Claude Code 自动记忆系统已激活');
console.log('💾 所有会话将自动保存到 MemPalace');

// 检查 MemPalace 是否可用
try {
    const { spawnSync } = require('child_process');
    const result = spawnSync('mempalace', ['--version'], {
        encoding: 'utf-8',
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });

    if (result.status === 0) {
        console.log(`✅ MemPalace 可用: ${result.stdout.trim()}`);
    } else {
        console.warn('⚠️  MemPalace 可能未正确安装');
    }
} catch (error) {
    console.warn('⚠️  无法检查 MemPalace:', error.message);
}
// ==================== 自动记忆初始化结束 ====================
'''

        # 在文件开头添加
        patched_content = init_patch + '\n' + content

        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(patched_content)

        print(f"✅ 已修补 main.tsx")
        return True

    def create_auto_memory_service(self):
        """创建自动记忆服务"""
        service_file = self.claude_source_dir / "services" / "auto-memory.ts"
        service_file.parent.mkdir(parents=True, exist_ok=True)

        service_content = '''/**
 * Claude Code 自动记忆服务
 *
 * 自动保存所有会话到 MemPalace
 * 完全透明，无需用户干预
 */

import { spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';
import * as crypto from 'crypto';

export interface ConversationMemory {
    userMessage: string;
    assistantResponse: string;
    toolsUsed: string[];
    timestamp: Date;
    sessionId?: string;
    projectPath?: string;
}

export class AutoMemoryService {
    private static instance: AutoMemoryService;
    private enabled: boolean = true;
    private memoryQueue: ConversationMemory[] = [];
    private processing: boolean = false;

    private constructor() {
        this.initialize();
    }

    static getInstance(): AutoMemoryService {
        if (!AutoMemoryService.instance) {
            AutoMemoryService.instance = new AutoMemoryService();
        }
        return AutoMemoryService.instance;
    }

    private async initialize(): Promise<void> {
        console.log('💾 自动记忆服务初始化...');

        // 检查 MemPalace
        try {
            const result = await this.checkMemPalace();
            if (result.available) {
                console.log(`✅ MemPalace 可用: ${result.version}`);
                this.enabled = true;
            } else {
                console.warn('⚠️  MemPalace 不可用，自动记忆已禁用');
                this.enabled = false;
            }
        } catch (error) {
            console.error('❌ 记忆服务初始化失败:', error);
            this.enabled = false;
        }

        // 启动处理队列
        this.processQueue();
    }

    private async checkMemPalace(): Promise<{ available: boolean; version?: string }> {
        return new Promise((resolve) => {
            const env = { ...process.env, PYTHONIOENCODING: 'utf-8' };
            const process = spawn('mempalace', ['--version'], { env });

            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            process.on('close', (code) => {
                if (code === 0 && stdout.trim()) {
                    resolve({ available: true, version: stdout.trim() });
                } else {
                    resolve({ available: false });
                }
            });

            process.on('error', () => {
                resolve({ available: false });
            });
        });
    }

    /**
     * 保存对话记忆
     */
    public async saveConversation(memory: ConversationMemory): Promise<boolean> {
        if (!this.enabled) {
            return false;
        }

        // 添加到队列
        this.memoryQueue.push(memory);

        // 如果队列太长，立即处理
        if (this.memoryQueue.length > 10) {
            this.processQueue();
        }

        return true;
    }

    /**
     * 立即保存对话（同步）
     */
    public saveConversationSync(memory: ConversationMemory): void {
        if (!this.enabled) {
            return;
        }

        try {
            // 创建记忆内容
            const content = this.createMemoryContent(memory);

            // 保存到临时文件
            const tempFile = this.createTempFile(content);

            // 调用 MemPalace
            this.callMemPalace(memory, tempFile);

        } catch (error) {
            // 静默失败
            console.error('记忆保存失败:', error.message);
        }
    }

    private createMemoryContent(memory: ConversationMemory): string {
        const timestamp = memory.timestamp.toLocaleString();

        return `# Claude Code 自动记忆

## 时间: ${timestamp}
${memory.sessionId ? `## 会话ID: ${memory.sessionId}` : ''}
${memory.projectPath ? `## 项目路径: ${memory.projectPath}` : ''}

## 用户消息
${memory.userMessage.substring(0, 2000)}

## 助手响应
${memory.assistantResponse.substring(0, 2000)}

## 使用的工具
${memory.toolsUsed.length > 0 ? memory.toolsUsed.join('\\n- ') : '无'}

---
*自动保存于 ${new Date().toISOString()}*
`;
    }

    private createTempFile(content: string): string {
        const tempDir = path.join(os.homedir(), '.claude', 'auto_memories');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }

        const hash = crypto.createHash('md5')
            .update(content + Date.now().toString())
            .digest('hex')
            .substring(0, 8);

        const tempFile = path.join(tempDir, `memory_${hash}.md`);
        fs.writeFileSync(tempFile, content, 'utf-8');

        return tempFile;
    }

    private callMemPalace(memory: ConversationMemory, contentFile: string): void {
        const env = { ...process.env, PYTHONIOENCODING: 'utf-8' };

        // 确定 wing 和 room
        const wing = memory.projectPath ?
            `project_${crypto.createHash('md5').update(memory.projectPath).digest('hex').substring(0, 6)}` :
            'claude_auto';

        const room = 'conversations';
        const title = `对话 ${memory.timestamp.toLocaleTimeString()}`;

        const args = [
            'add_drawer',
            '--wing', wing,
            '--room', room,
            '--title', title,
            '--content-file', contentFile
        ];

        // 异步执行，不阻塞主线程
        const process = spawn('mempalace', args, {
            env,
            stdio: 'ignore',
            detached: true
        });

        process.unref();
    }

    private async processQueue(): Promise<void> {
        if (this.processing || this.memoryQueue.length === 0) {
            return;
        }

        this.processing = true;

        while (this.memoryQueue.length > 0) {
            const memory = this.memoryQueue.shift();
            if (memory) {
                try {
                    this.saveConversationSync(memory);
                } catch (error) {
                    // 忽略错误，继续处理下一个
                }

                // 稍微延迟，避免太快
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }

        this.processing = false;
    }

    /**
     * 启用/禁用自动记忆
     */
    public setEnabled(enabled: boolean): void {
        this.enabled = enabled;
        console.log(`自动记忆 ${enabled ? '已启用' : '已禁用'}`);
    }

    /**
     * 获取服务状态
     */
    public getStatus(): { enabled: boolean; queueLength: number } {
        return {
            enabled: this.enabled,
            queueLength: this.memoryQueue.length
        };
    }
}

// 导出单例
export const autoMemoryService = AutoMemoryService.getInstance();
'''

        service_file.write_text(service_content, encoding='utf-8')
        print(f"✅ 已创建自动记忆服务: {service_file}")

        # 现在需要将这个服务集成到主代码中
        return True

    def integrate_service(self):
        """将自动记忆服务集成到主代码中"""
        # 查找可能集成的位置
        integration_points = [
            self.claude_source_dir / "query.ts",
            self.claude_source_dir / "main.tsx",
            self.claude_source_dir / "services" / "index.ts"
        ]

        for file_path in integration_points:
            if file_path.exists():
                self.backup_file(file_path)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 在文件开头添加导入
                import_statement = "import { autoMemoryService } from './services/auto-memory';\n"

                if "import { autoMemoryService }" not in content:
                    # 找到第一个 import 语句之后插入
                    import_pattern = r'(import\s+.*?from\s+[\'"][^\'"]+[\'"]\s*;)'

                    def insert_after_imports(match):
                        return match.group(0) + '\n' + import_statement

                    new_content = re.sub(import_pattern, insert_after_imports, content, count=1)

                    if new_content == content:
                        # 如果没有找到 import 语句，在文件开头添加
                        new_content = import_statement + content

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    print(f"✅ 已集成服务到: {file_path.name}")

        return True

    def apply_patches(self):
        """应用所有补丁"""
        print("🔧 开始应用 Claude Code 自动记忆补丁...")

        if not self.claude_source_dir:
            print("❌ 未找到 Claude Code 源代码")
            return False

        # 创建备份
        print("📦 创建备份...")

        # 应用补丁
        patches_applied = 0

        if self.patch_query_ts():
            patches_applied += 1

        if self.patch_main_tsx():
            patches_applied += 1

        if self.create_auto_memory_service():
            patches_applied += 1

        if self.integrate_service():
            patches_applied += 1

        print("=" * 60)
        print(f"🎉 补丁应用完成: {patches_applied} 个补丁已应用")
        print("")
        print("功能说明：")
        print("1. ✅ 完全自动化的记忆保存")
        print("2. ✅ 无需用户干预")
        print("3. ✅ 实时保存所有会话")
        print("4. ✅ 与 Claude Code 深度集成")
        print("")
        print("重启 Claude Code 以使更改生效")
        print("=" * 60)

        return patches_applied > 0

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Claude Code 自动记忆补丁 v1.0")
    print("🔧 直接修改源代码实现完全自动化记忆")
    print("🔓 超级管理员权限 - 无限制修改")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Claude Code 自动记忆补丁")
    parser.add_argument("--apply", action="store_true", help="应用补丁")
    parser.add_argument("--restore", action="store_true", help="恢复备份")
    parser.add_argument("--status", action="store_true", help="检查状态")

    args = parser.parse_args()

    patcher = ClaudeCodePatcher()

    if args.apply:
        patcher.apply_patches()
    elif args.restore:
        patcher.restore_backup()
    elif args.status:
        print("状态检查功能尚未实现")
    else:
        print("请指定操作：--apply, --restore, 或 --status")
        print("示例：python patch-claude-for-auto-memory.py --apply")

if __name__ == "__main__":
    main()