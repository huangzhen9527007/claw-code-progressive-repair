#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类问题修复模块
专门处理7个记忆系统分类问题的检测和修复
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any

from .utils import (
    read_frontmatter, contains_chinese, parse_memory_sections,
    normalize_filename, generate_english_filename, guess_memory_type,
    generate_description, validate_frontmatter
)


class ClassificationFixer:
    """分类问题修复器 - 处理7个记忆系统分类问题"""

    def __init__(self, memory_dir: Path):
        """初始化分类修复器

        Args:
            memory_dir: 记忆目录路径
        """
        self.memory_dir = memory_dir
        self.memory_index = memory_dir / "MEMORY.md"

        if not self.memory_index.exists():
            raise FileNotFoundError(f"记忆索引文件不存在: {self.memory_index}")

    def detect_all_issues(self) -> Dict[str, List[str]]:
        """检测所有7个分类问题

        Returns:
            Dict[str, List[str]]: 问题类型到问题列表的映射
        """
        issues = {
            "chinese_filenames_in_english_categories": [],      # 1. 中文文件名问题
            "missing_frontmatter_type": [],                     # 2. 缺少frontmatter类型
            "type_mismatch_frontmatter_index": [],              # 3. 类型不匹配
            "type_metadata_issues": [],                         # 4. 类型元数据问题
            "mixed_language_descriptions": [],                  # 5. 混合语言描述问题
            "inconsistent_naming_conventions": [],              # 6. 不一致的命名约定
            "naming_convention_analysis": []                    # 7. 命名约定问题分析
        }

        # 读取MEMORY.md内容
        memory_content = self.memory_index.read_text(encoding='utf-8')
        sections = parse_memory_sections(memory_content)

        # 检查所有记忆文件
        for memory_file in self.memory_dir.glob("*.md"):
            if memory_file.name == "MEMORY.md":
                continue

            filename = memory_file.name
            file_path = memory_file

            # 1. 检查中文文件名问题
            if self._is_chinese_filename_in_english_category(filename, sections):
                issues["chinese_filenames_in_english_categories"].append(filename)

            # 2. 检查缺少frontmatter类型
            frontmatter = read_frontmatter(file_path)
            if not frontmatter or 'type' not in frontmatter:
                issues["missing_frontmatter_type"].append(filename)

            # 3. 检查类型不匹配
            type_mismatch = self._check_type_mismatch(filename, frontmatter, sections)
            if type_mismatch:
                issues["type_mismatch_frontmatter_index"].append(type_mismatch)

            # 4. 检查类型元数据问题
            type_metadata_issue = self._check_type_metadata_issue(file_path, frontmatter)
            if type_metadata_issue:
                issues["type_metadata_issues"].append(type_metadata_issue)

            # 5. 检查混合语言描述问题（智能检测）
            mixed_language = self._detect_mixed_language_issue(filename, frontmatter)
            if mixed_language:
                issues["mixed_language_descriptions"].append(mixed_language)

            # 6. 检查不一致的命名约定
            if self._has_naming_inconsistency(filename):
                issues["inconsistent_naming_conventions"].append(filename)

        # 7. 命名约定问题分析
        naming_analysis = self._analyze_naming_conventions()
        if naming_analysis:
            issues["naming_convention_analysis"] = naming_analysis

        return issues

    def _is_chinese_filename_in_english_category(self, filename: str, sections: Dict[str, List[str]]) -> bool:
        """检查中文文件名是否在英文分类中

        Args:
            filename: 文件名
            sections: 记忆章节结构

        Returns:
            bool: 如果是中文文件名在英文分类中则返回True
        """
        # 检查文件名是否包含中文
        if not contains_chinese(filename):
            return False

        # 查找文件在哪个章节
        for section_name, items in sections.items():
            for item in items:
                if filename in item:
                    # 检查章节名是否主要是英文（不包含中文）
                    return not contains_chinese(section_name)

        return False

    def _check_type_mismatch(self, filename: str, frontmatter: Optional[Dict],
                            sections: Dict[str, List[str]]) -> Optional[str]:
        """检查frontmatter类型与索引分类是否匹配

        Args:
            filename: 文件名
            frontmatter: frontmatter字典
            sections: 记忆章节结构

        Returns:
            Optional[str]: 如果不匹配则返回问题描述，否则返回None
        """
        if not frontmatter or 'type' not in frontmatter:
            return None

        file_type = frontmatter['type']

        # 查找文件在哪个章节
        for section_name, items in sections.items():
            for item in items:
                if filename in item:
                    # 映射章节名到类型
                    section_to_type = {
                        'User Memories': 'user',
                        'Feedback Memories': 'feedback',
                        'Project Memories': 'project',
                        'Reference Memories': 'reference'
                    }

                    expected_type = section_to_type.get(section_name)
                    if expected_type and file_type != expected_type:
                        return f"{filename}: frontmatter类型为'{file_type}'，但索引在'{section_name}'中（应为'{expected_type}'）"

        return None

    def _check_type_metadata_issue(self, file_path: Path, frontmatter: Optional[Dict]) -> Optional[str]:
        """检查类型元数据问题

        Args:
            file_path: 文件路径
            frontmatter: frontmatter字典

        Returns:
            Optional[str]: 如果存在类型元数据问题则返回描述，否则返回None
        """
        if not frontmatter:
            return f"{file_path.name}: 缺少frontmatter"

        # 检查type字段
        if 'type' not in frontmatter:
            return f"{file_path.name}: 缺少type字段"

        file_type = frontmatter['type']
        valid_types = ['user', 'feedback', 'project', 'reference']

        if file_type not in valid_types:
            return f"{file_path.name}: 无效的类型 '{file_type}'，有效类型为 {valid_types}"

        # 检查其他相关字段
        if 'name' not in frontmatter or not frontmatter['name']:
            return f"{file_path.name}: type为'{file_type}'但缺少name字段"

        if 'description' not in frontmatter or not frontmatter['description']:
            return f"{file_path.name}: type为'{file_type}'但缺少description字段"

        return None

    def _detect_mixed_language_issue(self, filename: str, frontmatter: Optional[Dict]) -> Optional[str]:
        """检测混合语言描述问题（智能版）

        Args:
            filename: 文件名
            frontmatter: frontmatter字典

        Returns:
            Optional[str]: 如果存在不合理的混合语言则返回描述，否则返回None
        """
        if not frontmatter:
            return None

        # 检查description字段
        if 'description' not in frontmatter:
            return None

        description = frontmatter['description']

        # 如果是中文文件名，中文描述是合理的
        if contains_chinese(filename):
            # 中文文件名使用中文描述是合理的
            return None

        # 如果是英文文件名但描述包含中文，这可能是个问题
        if contains_chinese(description):
            return f"{filename}: 英文文件名但描述包含中文 - '{description[:50]}...'"

        return None

    def _has_naming_inconsistency(self, filename: str) -> bool:
        """检查文件名是否存在命名约定不一致

        Args:
            filename: 文件名

        Returns:
            bool: 如果存在命名不一致则返回True
        """
        # 移除.md扩展名
        name_without_ext = filename[:-3] if filename.endswith('.md') else filename

        # 检查命名约定
        # 1. 不应同时包含下划线和连字符
        if '_' in name_without_ext and '-' in name_without_ext:
            return True

        # 2. 不应包含空格
        if ' ' in name_without_ext:
            return True

        # 3. 不应有大写字母（专有名词除外）
        # 这里简单检查，实际可能需要更复杂的逻辑
        if name_without_ext != name_without_ext.lower():
            # 检查是否可能是专有名词或缩写
            if not re.match(r'^[A-Z]+$', name_without_ext):  # 全大写可能是缩写
                return True

        return False

    def _analyze_naming_conventions(self) -> List[str]:
        """分析命名约定问题

        Returns:
            List[str]: 命名约定分析结果
        """
        analysis = []
        naming_patterns = {
            'kebab-case': 0,  # 连字符分隔
            'snake_case': 0,  # 下划线分隔
            'camelCase': 0,   # 驼峰命名
            'PascalCase': 0,  # 帕斯卡命名
            'mixed': 0,       # 混合命名
            'chinese': 0,     # 中文命名
        }

        for memory_file in self.memory_dir.glob("*.md"):
            if memory_file.name == "MEMORY.md":
                continue

            filename = memory_file.name
            name_without_ext = filename[:-3] if filename.endswith('.md') else filename

            # 分类命名模式
            if contains_chinese(name_without_ext):
                naming_patterns['chinese'] += 1
            elif '-' in name_without_ext and '_' not in name_without_ext:
                naming_patterns['kebab-case'] += 1
            elif '_' in name_without_ext and '-' not in name_without_ext:
                naming_patterns['snake_case'] += 1
            elif re.match(r'^[a-z]+[A-Z][a-z]*$', name_without_ext):
                naming_patterns['camelCase'] += 1
            elif re.match(r'^[A-Z][a-z]*([A-Z][a-z]*)*$', name_without_ext):
                naming_patterns['PascalCase'] += 1
            else:
                naming_patterns['mixed'] += 1

        # 生成分析报告
        total_files = sum(naming_patterns.values())
        if total_files > 0:
            analysis.append(f"命名约定分析（共{total_files}个文件）：")
            for pattern, count in naming_patterns.items():
                if count > 0:
                    percentage = (count / total_files) * 100
                    analysis.append(f"  {pattern}: {count}个 ({percentage:.1f}%)")

            # 提供建议
            if naming_patterns['mixed'] > 0:
                analysis.append("建议：统一命名约定，减少混合命名模式")

        return analysis

    def fix_issues(self, issues: Dict[str, List[str]], dry_run: bool = True,
                  fix_naming: bool = False, fix_mixed_language: bool = False) -> Dict[str, Any]:
        """修复检测到的问题

        Args:
            issues: 检测到的问题
            dry_run: 试运行模式，只显示计划不实际执行
            fix_naming: 是否修复命名约定问题
            fix_mixed_language: 是否修复混合语言描述问题

        Returns:
            Dict[str, Any]: 修复计划或结果
        """
        fix_plan = {
            "dry_run": dry_run,
            "files_renamed": [],
            "frontmatter_added": [],
            "type_mismatch_fixed": [],
            "type_metadata_fixed": [],
            "naming_fixed": [],
            "descriptions_fixed": []
        }

        # 1. 修复中文文件名问题
        for filename in issues.get("chinese_filenames_in_english_categories", []):
            english_name = generate_english_filename(filename)
            if not dry_run:
                success = self._rename_file(filename, english_name)
                fix_plan["files_renamed"].append({
                    "from": filename,
                    "to": english_name,
                    "success": success
                })
            else:
                fix_plan["files_renamed"].append({
                    "from": filename,
                    "to": english_name,
                    "success": False
                })

        # 2. 添加缺失的frontmatter类型
        for filename in issues.get("missing_frontmatter_type", []):
            if not dry_run:
                success = self._add_frontmatter(filename)
                fix_plan["frontmatter_added"].append({
                    "file": filename,
                    "success": success
                })
            else:
                fix_plan["frontmatter_added"].append({
                    "file": filename,
                    "success": False
                })

        # 3. 修复类型不匹配
        for issue in issues.get("type_mismatch_frontmatter_index", []):
            if ':' in issue:
                filename = issue.split(':', 1)[0]
                if not dry_run:
                    success = self._fix_type_mismatch(filename)
                    fix_plan["type_mismatch_fixed"].append({
                        "file": filename,
                        "issue": issue,
                        "success": success
                    })
                else:
                    fix_plan["type_mismatch_fixed"].append({
                        "file": filename,
                        "issue": issue,
                        "success": False
                    })

        # 4. 修复类型元数据问题
        for issue in issues.get("type_metadata_issues", []):
            if ':' in issue:
                filename = issue.split(':', 1)[0]
                if not dry_run:
                    success = self._fix_type_metadata(filename)
                    fix_plan["type_metadata_fixed"].append({
                        "file": filename,
                        "issue": issue,
                        "success": success
                    })
                else:
                    fix_plan["type_metadata_fixed"].append({
                        "file": filename,
                        "issue": issue,
                        "success": False
                    })

        # 5. 修复命名约定问题（可选）
        if fix_naming:
            for filename in issues.get("inconsistent_naming_conventions", []):
                new_name = normalize_filename(filename)
                if new_name != filename:
                    if not dry_run:
                        success = self._rename_file(filename, new_name)
                        fix_plan["naming_fixed"].append({
                            "from": filename,
                            "to": new_name,
                            "success": success
                        })
                    else:
                        fix_plan["naming_fixed"].append({
                            "from": filename,
                            "to": new_name,
                            "success": False
                        })

        # 6. 修复混合语言描述问题（可选，默认不修复）
        if fix_mixed_language and issues.get("mixed_language_descriptions"):
            if not dry_run:
                success = self._fix_mixed_language_descriptions()
                fix_plan["descriptions_fixed"].append({
                    "count": len(issues["mixed_language_descriptions"]),
                    "success": success
                })
            else:
                fix_plan["descriptions_fixed"].append({
                    "count": len(issues["mixed_language_descriptions"]),
                    "success": False
                })

        return fix_plan

    def _rename_file(self, old_name: str, new_name: str) -> bool:
        """重命名文件并更新索引

        Args:
            old_name: 旧文件名
            new_name: 新文件名

        Returns:
            bool: 是否成功
        """
        try:
            old_path = self.memory_dir / old_name
            new_path = self.memory_dir / new_name

            if not old_path.exists():
                return False

            # 重命名文件
            shutil.move(str(old_path), str(new_path))

            # 更新MEMORY.md中的引用
            self._update_index_filename(old_name, new_name)

            return True
        except Exception as e:
            print(f"重命名文件失败 {old_name} -> {new_name}: {e}")
            return False

    def _update_index_filename(self, old_name: str, new_name: str):
        """更新MEMORY.md中的文件名引用

        Args:
            old_name: 旧文件名
            new_name: 新文件名
        """
        try:
            content = self.memory_index.read_text(encoding='utf-8')
            updated_content = content.replace(f'({old_name})', f'({new_name})')
            self.memory_index.write_text(updated_content, encoding='utf-8')
        except Exception as e:
            print(f"更新索引文件名失败 {old_name} -> {new_name}: {e}")

    def _add_frontmatter(self, filename: str) -> bool:
        """为文件添加frontmatter

        Args:
            filename: 文件名

        Returns:
            bool: 是否成功
        """
        try:
            file_path = self.memory_dir / filename
            content = file_path.read_text(encoding='utf-8')

            # 猜测类型和生成描述
            memory_type = guess_memory_type(filename, content)
            description = generate_description(filename, content)

            # 创建frontmatter
            frontmatter = f"""---
name: {filename[:-3] if filename.endswith('.md') else filename}
description: {description}
type: {memory_type}
---

"""

            # 如果文件已有内容，添加到前面
            if content.strip():
                new_content = frontmatter + content
            else:
                new_content = frontmatter

            file_path.write_text(new_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"添加frontmatter失败 {filename}: {e}")
            return False

    def _fix_type_mismatch(self, filename: str) -> bool:
        """修复类型不匹配问题

        Args:
            filename: 文件名

        Returns:
            bool: 是否成功
        """
        try:
            file_path = self.memory_dir / filename
            frontmatter = read_frontmatter(file_path)

            if not frontmatter or 'type' not in frontmatter:
                return False

            # 读取MEMORY.md内容
            memory_content = self.memory_index.read_text(encoding='utf-8')
            sections = parse_memory_sections(memory_content)

            # 查找文件在哪个章节
            current_section = None
            for section_name, items in sections.items():
                for item in items:
                    if filename in item:
                        current_section = section_name
                        break
                if current_section:
                    break

            if not current_section:
                return False

            # 确定正确的类型
            section_to_type = {
                'User Memories': 'user',
                'Feedback Memories': 'feedback',
                'Project Memories': 'project',
                'Reference Memories': 'reference'
            }

            correct_type = section_to_type.get(current_section)
            if not correct_type:
                return False

            # 更新frontmatter
            frontmatter['type'] = correct_type

            # 重新写入文件
            self._update_frontmatter(file_path, frontmatter)

            return True
        except Exception as e:
            print(f"修复类型不匹配失败 {filename}: {e}")
            return False

    def _fix_type_metadata(self, filename: str) -> bool:
        """修复类型元数据问题

        Args:
            filename: 文件名

        Returns:
            bool: 是否成功
        """
        try:
            file_path = self.memory_dir / filename
            content = file_path.read_text(encoding='utf-8')

            # 读取或创建frontmatter
            frontmatter = read_frontmatter(file_path) or {}

            # 确保必需字段存在
            if 'name' not in frontmatter or not frontmatter['name']:
                frontmatter['name'] = filename[:-3] if filename.endswith('.md') else filename

            if 'description' not in frontmatter or not frontmatter['description']:
                frontmatter['description'] = generate_description(filename, content)

            if 'type' not in frontmatter or not frontmatter['type']:
                frontmatter['type'] = guess_memory_type(filename, content)

            # 验证类型
            valid_types = ['user', 'feedback', 'project', 'reference']
            if frontmatter['type'] not in valid_types:
                frontmatter['type'] = 'project'  # 默认类型

            # 更新文件
            self._update_frontmatter(file_path, frontmatter)

            return True
        except Exception as e:
            print(f"修复类型元数据失败 {filename}: {e}")
            return False

    def _fix_mixed_language_descriptions(self) -> bool:
        """修复混合语言描述问题

        Returns:
            bool: 是否成功
        """
        # 对于中文项目，混合语言描述可能是合理的
        # 这里只提供基本实现，实际可能需要更复杂的逻辑
        print("注意：混合语言描述修复功能需要根据具体项目需求定制")
        print("对于中文项目，中文描述可能是合理的用户友好设计")
        return False

    def _update_frontmatter(self, file_path: Path, frontmatter: Dict):
        """更新文件的frontmatter

        Args:
            file_path: 文件路径
            frontmatter: 新的frontmatter字典
        """
        import yaml

        content = file_path.read_text(encoding='utf-8')

        # 分离frontmatter和内容
        lines = content.split('\n')
        new_lines = []

        # 添加新的frontmatter
        new_lines.append('---')
        yaml_content = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
        new_lines.extend(yaml_content.strip().split('\n'))
        new_lines.append('---')
        new_lines.append('')  # 空行

        # 保留原有内容（跳过旧的frontmatter）
        in_old_frontmatter = False
        old_frontmatter_ended = False

        for line in lines:
            if line.strip() == '---' and not in_old_frontmatter:
                in_old_frontmatter = True
                continue
            elif line.strip() == '---' and in_old_frontmatter:
                in_old_frontmatter = False
                old_frontmatter_ended = True
                continue

            if not in_old_frontmatter and (old_frontmatter_ended or not lines[0].strip() == '---'):
                new_lines.append(line)

        # 写入文件
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')

    def generate_issue_report(self, issues: Dict[str, List[str]],
                             ignore_mixed_language: bool = True) -> str:
        """生成问题报告

        Args:
            issues: 检测到的问题
            ignore_mixed_language: 是否忽略混合语言描述问题

        Returns:
            str: 格式化的报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("记忆系统分类问题报告")
        report_lines.append("=" * 60)
        report_lines.append("")

        total_issues = 0
        issue_counts = {}

        for issue_type, items in issues.items():
            if ignore_mixed_language and issue_type == "mixed_language_descriptions":
                continue

            if items:
                count = len(items)
                total_issues += count
                issue_counts[issue_type] = count

        report_lines.append(f"总问题数: {total_issues}")
        report_lines.append(f"问题类型数: {len(issue_counts)}")
        report_lines.append("")

        if total_issues == 0:
            report_lines.append("[正常] 未发现分类问题")
        else:
            # 按问题数量排序
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

            for issue_type, count in sorted_issues:
                report_lines.append(f"{self._get_issue_type_name(issue_type)} ({count}个):")
                items = issues[issue_type]

                if issue_type == "naming_convention_analysis":
                    for item in items[:5]:  # 只显示前5个分析结果
                        report_lines.append(f"  {item}")
                    if len(items) > 5:
                        report_lines.append(f"  ... 还有 {len(items) - 5} 个分析结果")
                else:
                    for i, item in enumerate(items[:5], 1):
                        report_lines.append(f"  {i}. {item}")
                    if len(items) > 5:
                        report_lines.append(f"  ... 还有 {len(items) - 5} 个")

                report_lines.append("")

        # 提供修复建议
        if total_issues > 0:
            report_lines.append("修复建议:")
            report_lines.append("-" * 40)

            if "chinese_filenames_in_english_categories" in issue_counts:
                report_lines.append(f"1. 重命名中文文件 ({issue_counts['chinese_filenames_in_english_categories']}个文件)")

            if "missing_frontmatter_type" in issue_counts:
                report_lines.append(f"2. 添加缺失的frontmatter ({issue_counts['missing_frontmatter_type']}个文件)")

            if "type_mismatch_frontmatter_index" in issue_counts:
                report_lines.append(f"3. 修复类型不匹配 ({issue_counts['type_mismatch_frontmatter_index']}个文件)")

            if "inconsistent_naming_conventions" in issue_counts:
                report_lines.append(f"4. 标准化命名约定 ({issue_counts['inconsistent_naming_conventions']}个文件)")

            report_lines.append("-" * 40)
            report_lines.append("使用 --fix 参数进行修复（先使用 --dry-run 查看计划）")

        report_lines.append("=" * 60)

        return '\n'.join(report_lines)

    def _get_issue_type_name(self, issue_type: str) -> str:
        """获取问题类型的中文名称

        Args:
            issue_type: 问题类型标识

        Returns:
            str: 中文名称
        """
        names = {
            "chinese_filenames_in_english_categories": "中文文件名在英文分类中",
            "missing_frontmatter_type": "缺少frontmatter类型",
            "type_mismatch_frontmatter_index": "类型不匹配",
            "type_metadata_issues": "类型元数据问题",
            "mixed_language_descriptions": "混合语言描述",
            "inconsistent_naming_conventions": "不一致的命名约定",
            "naming_convention_analysis": "命名约定分析"
        }
        return names.get(issue_type, issue_type)