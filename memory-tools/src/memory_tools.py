#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools 主工具类
整合记忆系统诊断和分类问题修复功能
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any

from .utils import find_memory_dir, extract_indexed_files, read_frontmatter
from .classification_fixer import ClassificationFixer


class MemoryTools:
    """Memory Tools 主工具类 - 整合所有功能"""

    def __init__(self, memory_dir: str = None):
        """初始化 Memory Tools

        Args:
            memory_dir: 记忆目录路径，如果为None则自动检测
        """
        self.memory_dir = find_memory_dir(memory_dir)
        self.memory_index = self.memory_dir / "MEMORY.md"

        # 初始化分类修复器
        self.classification_fixer = ClassificationFixer(self.memory_dir)

        # 验证目录和文件
        if not self.memory_index.exists():
            raise FileNotFoundError(f"记忆索引文件不存在: {self.memory_index}")

    # ==================== 基本检查功能 ====================

    def get_memory_files(self) -> List[str]:
        """获取所有记忆文件（排除MEMORY.md和插件目录）

        Returns:
            List[str]: 记忆文件名列表（包含相对路径，使用正斜杠）
        """
        files = []
        exclude_dirs = {'.claudian', '.obsidian', '.claude'}

        # 递归搜索所有.md文件
        for f in self.memory_dir.rglob("*.md"):
            # 排除MEMORY.md
            if f.name == "MEMORY.md":
                continue

            # 检查是否在排除的目录中
            in_excluded_dir = False
            for part in f.relative_to(self.memory_dir).parts:
                if part in exclude_dirs:
                    in_excluded_dir = True
                    break

            if not in_excluded_dir:
                # 获取相对路径并规范化分隔符
                rel_path = f.relative_to(self.memory_dir)
                # 将Windows反斜杠转换为正斜杠，确保跨平台兼容性
                normalized_path = str(rel_path).replace('\\', '/')
                files.append(normalized_path)

        return sorted(files)

    def get_indexed_files(self) -> List[str]:
        """从MEMORY.md中提取所有索引的文件名

        Returns:
            List[str]: 索引的文件名列表
        """
        content = self.memory_index.read_text(encoding='utf-8')
        return extract_indexed_files(content)

    def check_file_count_match(self) -> Tuple[bool, int, int]:
        """检查记忆文件数量与索引数量是否匹配

        Returns:
            Tuple[bool, int, int]: (是否匹配, 记忆文件数, 索引条目数)
        """
        memory_files = self.get_memory_files()
        indexed_files = self.get_indexed_files()

        file_count = len(memory_files)
        index_count = len(indexed_files)

        return (file_count == index_count, file_count, index_count)

    def find_unindexed_files(self) -> List[str]:
        """查找未索引的文件

        Returns:
            List[str]: 未索引的文件名列表
        """
        memory_files = set(self.get_memory_files())
        indexed_files = set(self.get_indexed_files())

        unindexed = sorted(memory_files - indexed_files)
        return unindexed

    def find_extra_indexes(self) -> List[str]:
        """查找多余的索引（文件不存在但被索引）

        Returns:
            List[str]: 多余的索引文件名列表
        """
        memory_files = set(self.get_memory_files())
        indexed_files = set(self.get_indexed_files())

        extra = sorted(indexed_files - memory_files)
        return extra

    def find_duplicate_indexes(self) -> Dict[str, int]:
        """查找重复的索引条目

        Returns:
            Dict[str, int]: 文件名到出现次数的映射
        """
        indexed_files = self.get_indexed_files()
        duplicates = {}

        for filename in indexed_files:
            duplicates[filename] = duplicates.get(filename, 0) + 1

        # 只返回出现次数大于1的文件
        return {k: v for k, v in duplicates.items() if v > 1}

    def check_index_categories(self) -> Dict[str, List[str]]:
        """检查索引分类

        Returns:
            Dict[str, List[str]]: 分类名到文件列表的映射
        """
        content = self.memory_index.read_text(encoding='utf-8')
        categories = {}

        current_category = None
        lines = content.split('\n')

        for line in lines:
            line = line.rstrip()

            # 检查是否是分类标题
            if line.startswith('## '):
                current_category = line[3:].strip()
                categories[current_category] = []
            elif current_category and line.strip() and line.startswith('- ['):
                # 提取文件名
                match = re.search(r'\[.*?\]\((.*?\.md)\)', line)
                if match:
                    filename = match.group(1)
                    categories[current_category].append(filename)

        return categories

    # ==================== 诊断报告功能 ====================

    def generate_diagnosis_report(self) -> Dict[str, Any]:
        """生成完整的诊断报告

        Returns:
            Dict[str, Any]: 诊断报告字典
        """
        report = {
            "basic_stats": {},
            "problems": {},
            "classification_issues": {},
            "recommendations": []
        }

        # 基本统计
        match_result, file_count, index_count = self.check_file_count_match()
        report["basic_stats"] = {
            "memory_files": file_count,
            "index_entries": index_count,
            "counts_match": match_result
        }

        # 问题检测
        unindexed = self.find_unindexed_files()
        extra = self.find_extra_indexes()
        duplicates = self.find_duplicate_indexes()

        report["problems"] = {
            "unindexed_files": unindexed,
            "extra_indexes": extra,
            "duplicate_indexes": duplicates
        }

        # 分类问题检测
        classification_issues = self.classification_fixer.detect_all_issues()
        report["classification_issues"] = classification_issues

        # 生成建议
        recommendations = []

        if not match_result:
            diff = abs(file_count - index_count)
            recommendations.append(f"记忆文件数量 ({file_count}) 与索引条目数量 ({index_count}) 不匹配，相差 {diff} 个")

        if unindexed:
            recommendations.append(f"发现 {len(unindexed)} 个未索引的文件，需要添加到 MEMORY.md")

        if extra:
            recommendations.append(f"发现 {len(extra)} 个多余的索引条目，对应的文件不存在，需要从 MEMORY.md 中移除")

        if duplicates:
            recommendations.append(f"发现 {len(duplicates)} 个文件被重复索引，需要清理重复条目")

        # 分类问题建议
        total_classification_issues = 0
        for issue_type, items in classification_issues.items():
            if issue_type != "naming_convention_analysis" and items:
                total_classification_issues += len(items)

        if total_classification_issues > 0:
            recommendations.append(f"发现 {total_classification_issues} 个分类问题，建议运行分类修复")

        if not any([unindexed, extra, duplicates]) and total_classification_issues == 0:
            recommendations.append("记忆系统健康，无需修复")

        report["recommendations"] = recommendations

        return report

    def print_report(self, report: Dict[str, Any] = None):
        """打印诊断报告

        Args:
            report: 诊断报告字典，如果为None则生成新报告
        """
        if report is None:
            report = self.generate_diagnosis_report()

        # 基本统计
        stats = report["basic_stats"]
        print(f"[STATS] Basic statistics - 基本统计:")
        print(f"  Memory files: {stats['memory_files']} - 记忆文件数量: {stats['memory_files']}")
        print(f"  Index entries: {stats['index_entries']} - 索引条目数量: {stats['index_entries']}")

        if stats["counts_match"]:
            print("  [OK] Counts match - 数量匹配")
        else:
            diff = abs(stats['memory_files'] - stats['index_entries'])
            print(f"  [WARNING] Counts don't match (difference: {diff}) - 数量不匹配 (相差 {diff} 个)")

        print()

        # 问题报告
        problems = report["problems"]
        has_problems = False

        if problems["unindexed_files"]:
            has_problems = True
            print(f"[ISSUE] Unindexed files ({len(problems['unindexed_files'])}): - 未索引的文件 ({len(problems['unindexed_files'])}个):")
            for i, filename in enumerate(problems["unindexed_files"][:5], 1):
                print(f"  {i}. {filename}")
            if len(problems["unindexed_files"]) > 5:
                print(f"  ... and {len(problems['unindexed_files']) - 5} more - 还有 {len(problems['unindexed_files']) - 5} 个")

        if problems["extra_indexes"]:
            has_problems = True
            print(f"\n[ISSUE] Extra indexes ({len(problems['extra_indexes'])}): - 多余的索引 ({len(problems['extra_indexes'])}个):")
            for i, filename in enumerate(problems["extra_indexes"][:5], 1):
                print(f"  {i}. {filename}")
            if len(problems["extra_indexes"]) > 5:
                print(f"  ... and {len(problems['extra_indexes']) - 5} more - 还有 {len(problems['extra_indexes']) - 5} 个")

        if problems["duplicate_indexes"]:
            has_problems = True
            print(f"\n[ISSUE] Duplicate indexes ({len(problems['duplicate_indexes'])}): - 重复的索引 ({len(problems['duplicate_indexes'])}个):")
            for i, (filename, count) in enumerate(list(problems["duplicate_indexes"].items())[:5], 1):
                print(f"  {i}. {filename} (appears {count} times) - (出现 {count} 次)")
            if len(problems["duplicate_indexes"]) > 5:
                print(f"  ... and {len(problems['duplicate_indexes']) - 5} more - 还有 {len(problems['duplicate_indexes']) - 5} 个")

        # 分类问题报告
        classification_issues = report["classification_issues"]
        classification_problems = False

        for issue_type, items in classification_issues.items():
            if issue_type != "naming_convention_analysis" and items:
                classification_problems = True
                break

        if classification_problems:
            print("\n[CLASSIFICATION] Classification issues found - 发现分类问题:")
            total_issues = 0

            for issue_type, items in classification_issues.items():
                if issue_type != "naming_convention_analysis" and items:
                    issue_name = self.classification_fixer._get_issue_type_name(issue_type)
                    print(f"  {issue_name}: {len(items)} - {len(items)}个")
                    total_issues += len(items)

            print(f"  Total classification issues: {total_issues} - 总分类问题数: {total_issues}")
            print("  Use --classification-report for details - 使用 --classification-report 查看详细分类问题")

        if not has_problems and not classification_problems:
            print("[OK] No issues found - 未发现问题")

        print()

        # 建议
        recommendations = report["recommendations"]
        if recommendations:
            print("[RECOMMENDATIONS] - [建议]:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print("=" * 60)
        print("Diagnosis completed - 诊断完成")
        print("=" * 60)

    # ==================== 分类问题功能 ====================

    def generate_classification_report(self, ignore_mixed_language: bool = True) -> str:
        """生成分类问题报告

        Args:
            ignore_mixed_language: 是否忽略混合语言描述问题

        Returns:
            str: 分类问题报告
        """
        issues = self.classification_fixer.detect_all_issues()
        return self.classification_fixer.generate_issue_report(issues, ignore_mixed_language)

    def fix_classification_issues(self, dry_run: bool = True, fix_naming: bool = False,
                                 fix_mixed_language: bool = False) -> Dict[str, Any]:
        """修复分类问题

        Args:
            dry_run: 试运行模式，只显示计划不实际执行
            fix_naming: 是否修复命名约定问题
            fix_mixed_language: 是否修复混合语言描述问题

        Returns:
            Dict[str, Any]: 修复计划或结果
        """
        issues = self.classification_fixer.detect_all_issues()
        return self.classification_fixer.fix_issues(issues, dry_run, fix_naming, fix_mixed_language)

    def print_fix_plan(self, fix_plan: Dict[str, Any]):
        """打印修复计划

        Args:
            fix_plan: 修复计划字典
        """
        print("=" * 60)
        if fix_plan["dry_run"]:
            print("修复计划（试运行模式）")
        else:
            print("修复结果")
        print("=" * 60)
        print()

        total_changes = 0

        # 文件重命名（中文文件名）
        if fix_plan["files_renamed"]:
            print("1. 重命名中文文件:")
            for rename in fix_plan["files_renamed"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: {rename['from']} -> {rename['to']}")
                else:
                    status = "成功" if rename["success"] else "失败"
                    print(f"  执行: {rename['from']} -> {rename['to']} [{status}]")
                total_changes += 1
            print()

        # 添加frontmatter
        if fix_plan["frontmatter_added"]:
            print("2. 添加缺失的frontmatter:")
            for addition in fix_plan["frontmatter_added"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: 为 {addition['file']} 添加frontmatter")
                else:
                    status = "成功" if addition["success"] else "失败"
                    print(f"  执行: 为 {addition['file']} 添加frontmatter [{status}]")
                total_changes += 1
            print()

        # 修复类型不匹配
        if fix_plan["type_mismatch_fixed"]:
            print("3. 修复类型不匹配:")
            for fix in fix_plan["type_mismatch_fixed"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: 修复 {fix['file']} 的类型不匹配")
                else:
                    status = "成功" if fix["success"] else "失败"
                    print(f"  执行: 修复 {fix['file']} 的类型不匹配 [{status}]")
                total_changes += 1
            print()

        # 修复类型元数据
        if fix_plan["type_metadata_fixed"]:
            print("4. 修复类型元数据:")
            for fix in fix_plan["type_metadata_fixed"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: 修复 {fix['file']} 的类型元数据")
                else:
                    status = "成功" if fix["success"] else "失败"
                    print(f"  执行: 修复 {fix['file']} 的类型元数据 [{status}]")
                total_changes += 1
            print()

        # 修复命名约定
        if fix_plan["naming_fixed"]:
            print("5. 标准化命名约定:")
            for rename in fix_plan["naming_fixed"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: {rename['from']} -> {rename['to']}")
                else:
                    status = "成功" if rename["success"] else "失败"
                    print(f"  执行: {rename['from']} -> {rename['to']} [{status}]")
                total_changes += 1
            print()

        # 修复混合语言描述
        if fix_plan["descriptions_fixed"]:
            print("6. 修复混合语言描述:")
            for fix in fix_plan["descriptions_fixed"]:
                if fix_plan["dry_run"]:
                    print(f"  计划: 修复 {fix['count']} 个混合语言描述")
                else:
                    status = "成功" if fix["success"] else "失败"
                    print(f"  执行: 修复混合语言描述 [{status}]")
                total_changes += 1
            print()

        if total_changes == 0:
            print("无需修复")

        print("=" * 60)
        if fix_plan["dry_run"]:
            print(f"总计: {total_changes} 个计划更改")
            print("使用 --fix-execute 参数执行修复")
        else:
            print(f"总计: {total_changes} 个更改已执行")
        print("=" * 60)

    # ==================== 修复功能 ====================

    def fix_problems(self, dry_run: bool = True) -> Dict[str, Any]:
        """修复检测到的问题（完整修复）

        Args:
            dry_run: 试运行模式

        Returns:
            Dict[str, Any]: 修复结果
        """
        # 注意：完整修复功能需要谨慎实现
        # 这里主要处理分类问题，其他问题需要用户手动处理
        print("注意：完整修复功能主要处理分类问题")
        print("其他问题（未索引文件、多余索引、重复索引）建议手动处理")
        print()

        return self.fix_classification_issues(dry_run=dry_run)

    # ==================== JSON输出功能 ====================

    def generate_json_report(self) -> str:
        """生成JSON格式的报告

        Returns:
            str: JSON格式的报告
        """
        report = self.generate_diagnosis_report()
        return json.dumps(report, ensure_ascii=False, indent=2)

    def generate_classification_json(self, ignore_mixed_language: bool = True) -> str:
        """生成JSON格式的分类问题报告

        Args:
            ignore_mixed_language: 是否忽略混合语言描述问题

        Returns:
            str: JSON格式的分类问题报告
        """
        issues = self.classification_fixer.detect_all_issues()

        if ignore_mixed_language and "mixed_language_descriptions" in issues:
            del issues["mixed_language_descriptions"]

        return json.dumps(issues, ensure_ascii=False, indent=2)