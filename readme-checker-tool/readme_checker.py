#!/usr/bin/env python3
"""
README.md文档检查与修复工具
自动检测和修复README.md文档中的重复内容、格式问题等
"""

import re
import sys
import argparse
import difflib
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set, Optional
import hashlib
from datetime import datetime


class READMEChecker:
    """README.md文档检查器"""

    def __init__(self, file_path: str = "README.md", similarity_threshold: float = 0.8):
        self.file_path = Path(file_path)
        self.similarity_threshold = similarity_threshold
        self.lines = []
        self.problems = []
        self.stats = {
            'total_lines': 0,
            'total_titles': 0,
            'total_code_blocks': 0,
            'total_links': 0,
            'total_lists': 0,
            'duplicate_titles': 0,
            'duplicate_paragraphs': 0,
            'format_issues': 0,
            'hierarchy_issues': 0
        }

    def load_file(self) -> bool:
        """加载文件"""
        try:
            if not self.file_path.exists():
                print(f"错误：文件不存在: {self.file_path}")
                return False

            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()

            self.stats['total_lines'] = len(self.lines)
            return True
        except Exception as e:
            print(f"加载文件时出错: {e}")
            return False

    def analyze(self):
        """分析文档"""
        if not self.lines:
            if not self.load_file():
                return

        print(f"分析文档: {self.file_path}")
        print(f"总行数: {self.stats['total_lines']}")

        # 检测各种问题
        self._detect_duplicate_titles()
        self._detect_duplicate_paragraphs()
        self._detect_format_issues()
        self._detect_hierarchy_issues()
        self._collect_statistics()

    def _detect_duplicate_titles(self):
        """检测重复标题"""
        title_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        titles = []

        for i, line in enumerate(self.lines):
            match = title_pattern.match(line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                titles.append((i, level, text, line))

        # 按标题文本分组
        title_groups = defaultdict(list)
        for i, level, text, line in titles:
            title_groups[text].append((i, level, line))

        # 找出重复标题
        for text, occurrences in title_groups.items():
            if len(occurrences) > 1:
                self.stats['duplicate_titles'] += len(occurrences) - 1
                line_numbers = [str(i+1) for i, _, _ in occurrences]
                self.problems.append({
                    'type': 'duplicate_title',
                    'severity': 'medium',
                    'message': f"重复标题: '{text}'",
                    'details': f"出现在第 {', '.join(line_numbers)} 行",
                    'lines': [i for i, _, _ in occurrences],
                    'data': {'text': text, 'occurrences': occurrences}
                })

        self.stats['total_titles'] = len(titles)

    def _detect_duplicate_paragraphs(self):
        """检测重复段落"""
        # 首先识别段落（连续的非空行）
        paragraphs = []
        current_para = []
        current_start = 0

        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped:  # 非空行
                if not current_para:
                    current_start = i
                current_para.append(stripped)
            else:  # 空行，段落结束
                if current_para:
                    paragraphs.append((current_start, i-1, ' '.join(current_para)))
                    current_para = []

        # 处理最后一个段落
        if current_para:
            paragraphs.append((current_start, len(self.lines)-1, ' '.join(current_para)))

        # 计算段落哈希值用于快速去重
        para_hashes = defaultdict(list)
        for start, end, text in paragraphs:
            # 跳过太短的段落
            if len(text) < 20:
                continue

            # 计算文本哈希
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            para_hashes[text_hash].append((start, end, text))

        # 找出重复段落
        for text_hash, occurrences in para_hashes.items():
            if len(occurrences) > 1:
                self.stats['duplicate_paragraphs'] += len(occurrences) - 1
                line_ranges = [f"{start+1}-{end+1}" for start, end, _ in occurrences]
                sample_text = occurrences[0][2][:100] + "..." if len(occurrences[0][2]) > 100 else occurrences[0][2]

                self.problems.append({
                    'type': 'duplicate_paragraph',
                    'severity': 'high',
                    'message': f"重复段落 ({len(occurrences)} 处)",
                    'details': f"出现在第 {', '.join(line_ranges)} 行",
                    'lines': [start for start, _, _ in occurrences],
                    'data': {
                        'text_hash': text_hash,
                        'occurrences': occurrences,
                        'sample_text': sample_text
                    }
                })

    def _detect_format_issues(self):
        """检测格式问题"""
        # 检查链接格式
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        bad_link_pattern = re.compile(r'\[([^\]]+)\]([^(]|$)')  # 缺少括号的链接

        for i, line in enumerate(self.lines):
            # 检查坏的链接格式
            if bad_link_pattern.search(line) and not link_pattern.search(line):
                self.stats['format_issues'] += 1
                self.problems.append({
                    'type': 'bad_link_format',
                    'severity': 'low',
                    'message': "链接格式不正确",
                    'details': f"第 {i+1} 行: 可能缺少括号的链接",
                    'lines': [i],
                    'data': {'line': line.strip()}
                })

            # 统计链接
            if link_pattern.search(line):
                self.stats['total_links'] += len(link_pattern.findall(line))

            # 统计代码块
            if line.strip().startswith('```'):
                self.stats['total_code_blocks'] += 1

            # 统计列表项
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                self.stats['total_lists'] += 1

    def _detect_hierarchy_issues(self):
        """检测标题层级问题"""
        title_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        title_levels = []

        for i, line in enumerate(self.lines):
            match = title_pattern.match(line.strip())
            if match:
                level = len(match.group(1))
                title_levels.append((i, level))

        # 检查层级跳跃（如从##直接跳到####，跳过###）
        for idx in range(1, len(title_levels)):
            prev_line, prev_level = title_levels[idx-1]
            curr_line, curr_level = title_levels[idx]

            if curr_level > prev_level + 1:
                self.stats['hierarchy_issues'] += 1
                self.problems.append({
                    'type': 'hierarchy_jump',
                    'severity': 'low',
                    'message': "标题层级跳跃",
                    'details': f"第 {prev_line+1} 行 (级别{prev_level}) → 第 {curr_line+1} 行 (级别{curr_level})",
                    'lines': [prev_line, curr_line],
                    'data': {'prev_level': prev_level, 'curr_level': curr_level}
                })

    def _collect_statistics(self):
        """收集统计信息"""
        # 已经在前面的方法中收集了大部分统计信息
        pass

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append(f"README.md 检查报告")
        report.append("=" * 50)
        report.append("")

        # 文档统计
        report.append("文档统计：")
        report.append(f"- 总行数：{self.stats['total_lines']}")
        report.append(f"- 标题数：{self.stats['total_titles']}")
        report.append(f"- 代码块数：{self.stats['total_code_blocks']}")
        report.append(f"- 链接数：{self.stats['total_links']}")
        report.append(f"- 列表项数：{self.stats['total_lists']}")
        report.append("")

        # 问题统计
        report.append("问题检测：")
        report.append(f"- 重复标题：{self.stats['duplicate_titles']}处")
        report.append(f"- 重复段落：{self.stats['duplicate_paragraphs']}处")
        report.append(f"- 格式问题：{self.stats['format_issues']}处")
        report.append(f"- 层级问题：{self.stats['hierarchy_issues']}处")
        report.append("")

        # 详细问题列表
        if self.problems:
            report.append("详细问题列表：")
            for idx, problem in enumerate(self.problems, 1):
                severity_icon = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(problem['severity'], '⚪')

                report.append(f"{idx}. {severity_icon} {problem['message']}")
                report.append(f"   详情：{problem['details']}")
                if 'sample_text' in problem.get('data', {}):
                    report.append(f"   示例：{problem['data']['sample_text']}")
            report.append("")

        # 建议操作
        if self.problems:
            report.append("建议操作：")
            action_idx = 1

            # 处理重复标题
            duplicate_titles = [p for p in self.problems if p['type'] == 'duplicate_title']
            for problem in duplicate_titles:
                text = problem['data']['text']
                lines = problem['lines']
                if len(lines) > 1:
                    keep_line = lines[0] + 1
                    remove_lines = [l+1 for l in lines[1:]]
                    report.append(f"{action_idx}. 合并重复标题 '{text}'：保留第{keep_line}行，删除第{', '.join(map(str, remove_lines))}行")
                    action_idx += 1

            # 处理重复段落
            duplicate_paragraphs = [p for p in self.problems if p['type'] == 'duplicate_paragraph']
            for problem in duplicate_paragraphs:
                occurrences = problem['data']['occurrences']
                if len(occurrences) > 1:
                    keep_range = f"{occurrences[0][0]+1}-{occurrences[0][1]+1}"
                    remove_ranges = [f"{start+1}-{end+1}" for start, end, _ in occurrences[1:]]
                    report.append(f"{action_idx}. 合并重复段落：保留第{keep_range}行，删除第{', '.join(remove_ranges)}行")
                    action_idx += 1

            # 处理格式问题
            format_issues = [p for p in self.problems if p['type'] in ['bad_link_format', 'hierarchy_jump']]
            for problem in format_issues:
                line_num = problem['lines'][0] + 1
                if problem['type'] == 'bad_link_format':
                    report.append(f"{action_idx}. 修复第{line_num}行的链接格式")
                elif problem['type'] == 'hierarchy_jump':
                    report.append(f"{action_idx}. 检查第{line_num}行的标题层级")
                action_idx += 1

        return '\n'.join(report)

    def fix_issues(self, backup: bool = True) -> bool:
        """修复检测到的问题"""
        if not self.problems:
            print("没有需要修复的问题")
            return True

        # 创建备份
        if backup:
            backup_path = self.file_path.with_suffix(f".md.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            try:
                with open(self.file_path, 'r', encoding='utf-8') as src, \
                     open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"已创建备份: {backup_path}")
            except Exception as e:
                print(f"创建备份时出错: {e}")
                return False

        # 读取文件内容
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return False

        lines = content.splitlines(keepends=True)
        lines_to_remove = set()

        # 处理重复标题（保留第一个，删除后面的）
        duplicate_titles = [p for p in self.problems if p['type'] == 'duplicate_title']
        for problem in duplicate_titles:
            title_lines = problem['lines']
            if len(title_lines) > 1:
                # 保留第一个，标记后面的要删除
                for line_num in title_lines[1:]:
                    lines_to_remove.add(line_num)

        # 处理重复段落（保留第一个，删除后面的）
        duplicate_paragraphs = [p for p in self.problems if p['type'] == 'duplicate_paragraph']
        for problem in duplicate_paragraphs:
            occurrences = problem['data']['occurrences']
            if len(occurrences) > 1:
                # 保留第一个段落，删除后面的
                for start, end, _ in occurrences[1:]:
                    for line_num in range(start, end + 1):
                        lines_to_remove.add(line_num)

        # 应用删除
        if lines_to_remove:
            new_lines = []
            for i, line in enumerate(lines):
                if i not in lines_to_remove:
                    new_lines.append(line)

            # 写入修复后的文件
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

                print(f"已修复 {len(lines_to_remove)} 行重复内容")
                return True
            except Exception as e:
                print(f"写入文件时出错: {e}")
                return False

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='README.md文档检查与修复工具')
    parser.add_argument('--file', '-f', default='README.md', help='要检查的文件路径')
    parser.add_argument('--fix', '-x', action='store_true', help='自动修复检测到的问题')
    parser.add_argument('--report', '-r', action='store_true', help='生成详细报告')
    parser.add_argument('--backup', '-b', action='store_true', default=True, help='修复前创建备份')
    parser.add_argument('--similarity', '-s', type=float, default=0.8, help='相似度阈值（0.0-1.0）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')

    args = parser.parse_args()

    # 创建检查器
    checker = READMEChecker(args.file, args.similarity)

    if not checker.load_file():
        sys.exit(1)

    # 分析文档
    checker.analyze()

    # 生成报告
    if args.report or args.verbose:
        report = checker.generate_report()
        print(report)

    # 修复问题
    if args.fix:
        print("\n开始修复问题...")
        if checker.fix_issues(args.backup):
            print("修复完成")
        else:
            print("修复失败")
            sys.exit(1)

    # 如果没有问题，输出成功信息
    if not checker.problems:
        print("✓ 文档检查完成，未发现问题")
    else:
        print(f"\n发现 {len(checker.problems)} 个问题")
        if not args.fix:
            print("使用 --fix 参数自动修复问题")


if __name__ == '__main__':
    main()