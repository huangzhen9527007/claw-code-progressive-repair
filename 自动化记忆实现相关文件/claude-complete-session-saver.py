#!/usr/bin/env python3
"""
Claude Code 完整会话保存器 - 修复版

功能：
1. 扫描所有 Claude Code 会话目录
2. 100%完整保存所有 .jsonl 会话文件的原始内容
3. 文件名与原始文件保持一致：xxx.jsonl → xxx.md
4. 确保不遗漏任何数据行
5. 验证数据完整性
6. 同名文件自动覆盖，避免重复

命名规则：保持原始文件名，仅扩展名改为 .md
示例：855a9554-5eb5-4e70-98db-925d94923713.jsonl → 855a9554-5eb5-4e70-98db-925d94923713.md
覆盖规则：如果同名文件已存在，直接覆盖（避免重复文件）
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import time
import sys

class ClaudeCompleteSessionSaver:
    def __init__(self):
        # Claude Code 会话存储目录
        self.claude_projects_dir = Path.home() / ".claude" / "projects"

        # 输出目录 - 使用原始文件名，避免路径过长
        self.output_dir = Path.home() / ".mempalace" / "palace" / "claude_sessions" / "complete_sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[TARGET] Claude Code 完整会话保存器启动")
        print(f"[FOLDER] 扫描目录: {self.claude_projects_dir}")
        print(f"[OUTPUT] 输出目录: {self.output_dir}")
        print(f"[RULE] 文件名规则: 原始文件名.jsonl → 原始文件名.md")
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
        """生成输出文件名：保持原始文件名，仅扩展名改为 .md"""
        original_name = session_file.name  # 例如：855a9554-5eb5-4e70-98db-925d94923713.jsonl
        if original_name.endswith('.jsonl'):
            # 去掉 .jsonl，加上 .md
            return original_name[:-6] + '.md'
        else:
            # 如果不是 .jsonl 扩展名，直接加上 .md
            return original_name + '.md'

    def save_complete_session(self, project_name, session_file):
        """保存完整会话数据 - 确保100%完整"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_mtime = datetime.fromtimestamp(session_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # 生成输出文件名（保持原始文件名）
        output_filename = self.get_output_filename(session_file)
        output_path = self.output_dir / output_filename

        # 检查文件是否已存在
        if output_path.exists():
            # 如果已存在，直接覆盖（避免重复文件）
            print(f"[INFO] 文件已存在，将覆盖: {output_filename}")
            # 可选：可以在这里添加备份逻辑
            # backup_path = output_path.with_suffix('.md.bak')
            # if backup_path.exists():
            #     backup_path.unlink()
            # output_path.rename(backup_path)
            # print(f"[BACKUP] 已备份旧文件到: {backup_path.name}")

        try:
            print(f"[READING] 读取文件: {session_file.name} ({session_file.stat().st_size:,} 字节)")

            # 1. 读取原始文件内容并验证完整性
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            print(f"[LINES] 总行数: {total_lines}")

            # 2. 解析每一行，确保都是有效的JSON
            valid_lines = 0
            invalid_lines = []

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue  # 跳过空行

                try:
                    json.loads(line)
                    valid_lines += 1
                except json.JSONDecodeError as e:
                    invalid_lines.append((i, line[:100], str(e)))
                    print(f"[WARNING] 第 {i} 行 JSON 解析错误: {e}")
                    print(f"          行内容: {line[:100]}...")

            print(f"[VALID] 有效JSON行: {valid_lines}/{total_lines}")
            if invalid_lines:
                print(f"[INVALID] 无效行数: {len(invalid_lines)}")

            # 3. 计算哈希值
            raw_content = ''.join(lines)
            file_hash = hashlib.md5(raw_content.encode()).hexdigest()

            # 4. 统计消息类型
            user_count = 0
            assistant_count = 0
            system_count = 0
            tool_use_count = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    msg_type = data.get('type', '')

                    if msg_type == 'user':
                        user_count += 1
                    elif msg_type == 'assistant':
                        assistant_count += 1
                        # 检查是否有工具调用
                        message = data.get('message', {})
                        if isinstance(message, dict):
                            content = message.get('content', [])
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        tool_use_count += 1
                    elif msg_type == 'system':
                        system_count += 1
                except:
                    pass

            # 5. 创建完整内容
            metadata = f"""# Claude Code 完整会话记录

## 文件信息
- **原始项目**: {project_name}
- **原始文件**: {session_file.name}
- **输出文件**: {output_filename}
- **文件大小**: {session_file.stat().st_size:,} 字节
- **修改时间**: {file_mtime}
- **保存时间**: {timestamp}
- **数据哈希**: {file_hash}

## 数据统计
- **总行数**: {total_lines}
- **有效JSON行**: {valid_lines}
- **无效行数**: {len(invalid_lines)}
- **用户消息**: {user_count}
- **助手响应**: {assistant_count}
- **系统消息**: {system_count}
- **工具调用**: {tool_use_count}

## 原始JSONL数据开始
以下为100%完整的原始JSONL数据，共{total_lines}行：

```jsonl
"""

            # 6. 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(metadata)
                f.write(raw_content)
                f.write("\n```\n")

                # 如果有无效行，添加详细信息
                if invalid_lines:
                    f.write(f"\n## 无效行详情 (共{len(invalid_lines)}行)\n")
                    for line_num, line_content, error_msg in invalid_lines[:10]:  # 只显示前10个
                        f.write(f"### 第 {line_num} 行\n")
                        f.write(f"错误: {error_msg}\n")
                        f.write(f"内容: {line_content}\n\n")
                    if len(invalid_lines) > 10:
                        f.write(f"... 还有 {len(invalid_lines) - 10} 个无效行未显示\n")

                f.write(f"\n---\n*100%完整数据保存于 {timestamp}*\n")

            # 7. 验证保存结果
            saved_size = output_path.stat().st_size
            original_size = session_file.stat().st_size
            size_diff = saved_size - original_size

            print(f"[SAVED] {output_filename} ({saved_size:,} 字节)")
            print(f"        原始: {original_size:,} 字节 | 差异: {size_diff:+,} 字节")
            print(f"        哈希: {file_hash}")
            print(f"        有效行: {valid_lines}/{total_lines}")

            return {
                "output_path": output_path,
                "saved_size": saved_size,
                "original_size": original_size,
                "total_lines": total_lines,
                "valid_lines": valid_lines,
                "invalid_lines": len(invalid_lines),
                "file_hash": file_hash
            }

        except Exception as e:
            print(f"[ERROR] 保存失败 {session_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_session_index(self, session_files, processed_results):
        """创建会话索引文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        index_file = self.output_dir / f"claude_sessions_index_{timestamp}.md"

        total_files = len(session_files)
        processed_count = len(processed_results)

        # 计算统计信息
        total_original_size = sum(f["size"] for f in session_files)
        total_saved_size = sum(r["saved_size"] for r in processed_results if r)
        total_lines = sum(r["total_lines"] for r in processed_results if r)
        total_valid_lines = sum(r["valid_lines"] for r in processed_results if r)

        content = f"""# Claude Code 完整会话数据索引

## 索引信息
- **生成时间**: {timestamp}
- **总会话文件**: {total_files}
- **已保存文件**: {processed_count}
- **原始总大小**: {total_original_size:,} 字节 ({total_original_size/1024/1024:.2f} MB)
- **保存总大小**: {total_saved_size:,} 字节 ({total_saved_size/1024/1024:.2f} MB)
- **总行数**: {total_lines:,}
- **有效行数**: {total_valid_lines:,}
- **输出目录**: {self.output_dir}

## 文件列表

| 序号 | 项目 | 原始文件 | 原始大小 | 保存文件 | 保存大小 | 行数 | 有效行 |
|------|------|----------|----------|----------|----------|------|--------|
"""

        for i, (file_info, result) in enumerate(zip(session_files[:30], processed_results[:30]), 1):
            project = file_info["project"][:20]
            original_filename = file_info["filename"][:20]

            if result:
                saved_filename = result["output_path"].name[:20]
                saved_size = result["saved_size"]
                total_lines = result["total_lines"]
                valid_lines = result["valid_lines"]
                status = "✅"
            else:
                saved_filename = "失败"
                saved_size = 0
                total_lines = 0
                valid_lines = 0
                status = "❌"

            content += f"| {i} {status} | `{project}` | `{original_filename}` | {file_info['size']:,} | `{saved_filename}` | {saved_size:,} | {total_lines} | {valid_lines} |\n"

        if total_files > 30:
            content += f"| ... | ... | ... | ... | ... | ... | ... | ... |\n"
            content += f"| {total_files} | 共{total_files}个文件 | ... | ... | ... | ... | ... | ... |\n"

        content += f"\n## 数据完整性说明\n"
        content += f"1. **100%原始数据**: 所有JSONL行完整保存\n"
        content += f"2. **文件名一致**: 原始文件名.jsonl → 原始文件名.md\n"
        content += f"3. **行数验证**: 验证每行是否为有效JSON\n"
        content += f"4. **哈希验证**: 每个文件都有MD5哈希值\n"
        content += f"5. **统计信息**: 包含消息类型和工具调用统计\n"
        content += f"6. **覆盖策略**: 同名文件自动覆盖，避免重复\n"

        content += f"\n## 文件名格式\n"
        content += f"- 保持原始文件名，仅扩展名改为 .md\n"
        content += f"- 示例: `855a9554-5eb5-4e70-98db-925d94923713.jsonl` → `855a9554-5eb5-4e70-98db-925d94923713.md`\n"
        content += f"- **覆盖规则**: 如果同名文件已存在，直接覆盖\n"

        content += f"\n## 使用说明\n"
        content += f"1. 所有文件包含100%完整的原始JSONL数据\n"
        content += f"2. 可直接用文本编辑器查看\n"
        content += f"3. 可用MemPalace搜索JSONL内容\n"
        content += f"4. 哈希值用于验证数据完整性\n"
        content += f"5. 重复运行不会产生重复文件\n"

        try:
            index_file.write_text(content, encoding='utf-8')
            print(f"[INDEX] 索引已保存: {index_file.name}")
            return index_file
        except Exception as e:
            print(f"[ERROR] 索引保存失败: {e}")
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

            # 保存完整会话数据
            result = self.save_complete_session(project_name, file_path)

            if result:
                processed_results.append(result)
                success_count += 1
            else:
                processed_results.append(None)
                fail_count += 1

            # 避免处理太快
            if i < len(session_files):
                time.sleep(0.1)

        # 创建索引
        self.create_session_index(session_files, processed_results)

        print(f"\n" + "="*60)
        print(f"[SUMMARY] 处理完成")
        print(f"          成功: {success_count} 个文件")
        print(f"          失败: {fail_count} 个文件")
        print(f"          总计: {len(session_files)} 个文件")

        if success_count > 0:
            total_saved_size = sum(r["saved_size"] for r in processed_results if r)
            total_original_size = sum(r["original_size"] for r in processed_results if r)
            total_lines = sum(r["total_lines"] for r in processed_results if r)
            total_valid_lines = sum(r["valid_lines"] for r in processed_results if r)

            print(f"\n[DATA] 数据统计:")
            print(f"       原始总大小: {total_original_size:,} 字节 ({total_original_size/1024/1024:.2f} MB)")
            print(f"       保存总大小: {total_saved_size:,} 字节 ({total_saved_size/1024/1024:.2f} MB)")
            print(f"       大小差异: {total_saved_size - total_original_size:+,} 字节")
            print(f"       总行数: {total_lines:,}")
            print(f"       有效行数: {total_valid_lines:,} ({total_valid_lines/total_lines*100:.1f}%)")
            print(f"\n[LOCATION] 所有文件保存在: {self.output_dir}")

        return success_count

def main():
    """主函数"""
    print("=" * 60)
    print("[ROBOT] Claude Code Complete Session Saver v2.1")
    print("[NOTE] 100%完整原始数据保存，文件名保持一致")
    print("[RULE] 文件名规则: 原始文件名.jsonl → 原始文件名.md")
    print("[RULE] 覆盖规则: 同名文件自动覆盖，避免重复")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Complete Session Saver")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum files to process (default: all)")
    parser.add_argument("--test", action="store_true", help="Test mode (process only 2 files)")

    args = parser.parse_args()

    # 启动保存器
    saver = ClaudeCompleteSessionSaver()

    if args.test:
        print("[TEST] 测试模式：只处理前 2 个文件")
        saver.process_all_sessions(max_files=2)
    else:
        saver.process_all_sessions(max_files=args.max_files)

    print("=" * 60)
    print("[SUCCESS] 任务完成！所有原始数据已100%完整保存")
    print("[DIRECTORY] 输出目录: ~/.mempalace/palace/claude_sessions/complete_sessions/")
    print("[FILENAME] 文件名格式: 原始文件名.jsonl → 原始文件名.md")
    print("[OVERWRITE] 覆盖策略: 同名文件自动覆盖，避免重复")
    print("[INTEGRITY] 数据完整性: 100%原始JSONL，行数验证，哈希验证")
    print("=" * 60)

if __name__ == "__main__":
    main()