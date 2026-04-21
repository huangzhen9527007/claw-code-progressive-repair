#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools 工具函数模块
提供共享的工具函数和辅助功能
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any


def find_memory_dir(memory_dir: str = None) -> Path:
    """自动查找记忆目录

    Args:
        memory_dir: 指定的记忆目录路径

    Returns:
        Path: 记忆目录路径

    Raises:
        FileNotFoundError: 如果找不到记忆目录
    """
    if memory_dir:
        path = Path(memory_dir)
        if path.exists() and (path / "MEMORY.md").exists():
            return path
        raise FileNotFoundError(f"指定的记忆目录不存在或无效: {memory_dir}")

    # 1. 检查当前目录下的memory文件夹
    cwd_memory = Path.cwd() / "memory"
    if cwd_memory.exists() and (cwd_memory / "MEMORY.md").exists():
        return cwd_memory

    # 2. 检查.claude/projects目录
    user_home = Path.home()
    claude_projects = user_home / ".claude" / "projects"

    if claude_projects.exists():
        # 查找所有项目目录中的memory文件夹
        memory_dirs = []
        for project_dir in claude_projects.iterdir():
            if project_dir.is_dir():
                memory_path = project_dir / "memory"
                if memory_path.exists() and (memory_path / "MEMORY.md").exists():
                    memory_dirs.append(memory_path)

        if memory_dirs:
            # 如果有多个记忆目录，选择最近修改的
            memory_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return memory_dirs[0]

    # 3. 使用默认路径（当前项目）
    default_path = user_home / ".claude" / "projects" / "C--Users-Administrator-Desktop-projects-claudecode-yuanmaziyuan-cloud-code-rewrite-cloud-code-main" / "memory"
    if default_path.exists():
        return default_path

    raise FileNotFoundError("无法找到记忆目录。请确保记忆系统已初始化或手动指定目录。")


def read_frontmatter(file_path: Path) -> Optional[Dict]:
    """读取Markdown文件的frontmatter

    Args:
        file_path: Markdown文件路径

    Returns:
        Optional[Dict]: frontmatter字典，如果没有frontmatter则返回None
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # 检查是否有frontmatter
        if not content.startswith('---'):
            return None

        # 提取frontmatter部分
        lines = content.split('\n')
        if len(lines) < 2:
            return None

        frontmatter_lines = []
        in_frontmatter = False
        frontmatter_end = False

        for i, line in enumerate(lines):
            if i == 0 and line.strip() == '---':
                in_frontmatter = True
                continue

            if in_frontmatter and line.strip() == '---':
                frontmatter_end = True
                break

            if in_frontmatter:
                frontmatter_lines.append(line)

        if not frontmatter_end or not frontmatter_lines:
            return None

        # 解析YAML
        frontmatter_text = '\n'.join(frontmatter_lines)
        try:
            return yaml.safe_load(frontmatter_text)
        except yaml.YAMLError:
            return None

    except Exception:
        return None


def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符

    Args:
        text: 要检查的文本

    Returns:
        bool: 如果包含中文字符则返回True
    """
    # 中文字符的Unicode范围
    chinese_ranges = [
        (0x4E00, 0x9FFF),    # 基本汉字
        (0x3400, 0x4DBF),    # 扩展A
        (0x20000, 0x2A6DF),  # 扩展B
        (0x2A700, 0x2B73F),  # 扩展C
        (0x2B740, 0x2B81F),  # 扩展D
        (0x2B820, 0x2CEAF),  # 扩展E
        (0x2CEB0, 0x2EBEF),  # 扩展F
        (0x30000, 0x3134F),  # 扩展G
        (0xF900, 0xFAFF),    # 兼容汉字
        (0x2F800, 0x2FA1F),  # 兼容扩展
    ]

    for char in text:
        code = ord(char)
        for start, end in chinese_ranges:
            if start <= code <= end:
                return True
    return False


def extract_indexed_files(memory_content: str) -> List[str]:
    """从MEMORY.md内容中提取所有索引的文件名

    Args:
        memory_content: MEMORY.md文件内容

    Returns:
        List[str]: 索引的文件名列表
    """
    indexed_files = []
    pattern = r'\[.*?\]\((.*?\.md)\)'

    matches = re.findall(pattern, memory_content)
    for match in matches:
        indexed_files.append(match)

    return sorted(indexed_files)


def parse_memory_sections(content: str) -> Dict[str, List[str]]:
    """解析MEMORY.md的章节结构

    Args:
        content: MEMORY.md文件内容

    Returns:
        Dict[str, List[str]]: 章节名到索引行列表的映射
    """
    sections = {}
    current_section = None
    lines = content.split('\n')

    for line in lines:
        line = line.rstrip()

        # 检查是否是章节标题
        if line.startswith('## '):
            current_section = line[3:].strip()
            sections[current_section] = []
        elif current_section and line.strip() and line.startswith('- ['):
            sections[current_section].append(line)

    return sections


def normalize_filename(filename: str) -> str:
    """标准化文件名

    Args:
        filename: 原始文件名

    Returns:
        str: 标准化后的文件名
    """
    # 移除.md扩展名进行处理
    name_without_ext = filename[:-3] if filename.endswith('.md') else filename

    # 替换空格为连字符
    name_without_ext = name_without_ext.replace(' ', '-')

    # 将下划线转换为连字符
    name_without_ext = name_without_ext.replace('_', '-')

    # 转换为小写
    name_without_ext = name_without_ext.lower()

    # 移除重复的连字符
    while '--' in name_without_ext:
        name_without_ext = name_without_ext.replace('--', '-')

    # 移除开头和结尾的连字符
    name_without_ext = name_without_ext.strip('-')

    # 重新添加.md扩展名
    return f"{name_without_ext}.md"


def generate_english_filename(chinese_filename: str) -> str:
    """将中文文件名转换为英文文件名

    Args:
        chinese_filename: 中文文件名（带.md扩展名）

    Returns:
        str: 英文文件名
    """
    # 简单的翻译映射（实际项目中可以使用更复杂的翻译）
    translations = {
        '超级管理员权限': 'super-admin-permissions',
        '用户角色': 'user-role',
        '工具资产管理经验': 'tool-asset-management-experience',
        '分类工具完善经验': 'classification-tools-enhancement-experience',
        'claude-mem 插件原生二进制文件问题解决方案': 'claude-mem-binary-fix',
        'claude-mem 知识库构建': 'claude-mem-knowledge-base',
        'claude-mem PATH 配置查漏补缺总结': 'claude-mem-path-configuration-summary',
        'claude-mem 解决方案完整性检查清单': 'claude-mem-solution-checklist',
        'PATH 配置完整性检查清单': 'path-configuration-checklist',
        'Hookify插件修复': 'hookify-fix',
        'WeChat CLI编码问题解决方案': 'wechat-cli-encoding-fix',
        '项目概述': 'project-overview',
        'claude-mem 插件信息': 'claude-mem-plugin',
        '如何使用 claude-mem 插件': 'how-to-use-claude-mem',
        'claude-mem 插件命令指南': 'claude-mem-command-guide',
        'claude-mem 插件查漏补缺验证报告': 'completeness-verification-report',
        'PATH 环境变量配置指南': 'path-configuration-guide',
        'PATH 配置补充指南': 'path-configuration-supplement',
        'Windows CMD窗口行为关键知识': 'windows-cmd-window-behavior-knowledge',
        'docs文档系统参考资料': 'docs-documentation-system-reference-material',
        'docs文档系统触发提示词示例': 'docs-trigger-prompt-examples',
        'LLM知识库架构模式': 'llm-wiki',
        'Claude Code技能集成模式': 'claude-code-skill-integration-pattern',
        'Claude Code插件系统技术细节': 'claude-code-plugin-system-technical-details',
    }

    # 移除.md扩展名
    name_without_ext = chinese_filename[:-3] if chinese_filename.endswith('.md') else chinese_filename

    # 查找翻译
    if name_without_ext in translations:
        english_name = translations[name_without_ext]
    else:
        # 如果没有预定义的翻译，使用简单的音译
        # 这里使用拼音转换的简化版本
        english_name = name_without_ext.lower().replace(' ', '-')

    # 确保以.md结尾
    if not english_name.endswith('.md'):
        english_name += '.md'

    return english_name


def guess_memory_type(filename: str, content: str = "") -> str:
    """根据文件名和内容猜测记忆类型

    Args:
        filename: 文件名
        content: 文件内容（可选）

    Returns:
        str: 猜测的记忆类型（user, feedback, project, reference）
    """
    filename_lower = filename.lower()

    # 基于文件名的关键词匹配
    if any(keyword in filename_lower for keyword in ['user', 'role', 'permission', '管理员']):
        return 'user'
    elif any(keyword in filename_lower for keyword in ['feedback', '经验', '总结', 'fix', '修复']):
        return 'feedback'
    elif any(keyword in filename_lower for keyword in ['project', '概述', '方案', '解决方案', 'checklist', '清单']):
        return 'project'
    elif any(keyword in filename_lower for keyword in ['reference', '指南', 'guide', '文档', 'docs', '模式', 'pattern']):
        return 'reference'

    # 如果提供了内容，尝试从内容中分析
    if content:
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in ['user', 'role', 'permission', 'preference']):
            return 'user'
        elif any(keyword in content_lower for keyword in ['feedback', 'correct', 'avoid', 'prefer']):
            return 'feedback'
        elif any(keyword in content_lower for keyword in ['project', 'work', 'goal', 'initiative', 'deadline']):
            return 'project'
        elif any(keyword in content_lower for keyword in ['reference', 'resource', 'external', 'system', 'documentation']):
            return 'reference'

    # 默认类型
    return 'project'


def generate_description(filename: str, content: str = "") -> str:
    """生成记忆文件的描述

    Args:
        filename: 文件名
        content: 文件内容（可选）

    Returns:
        str: 生成的描述
    """
    # 移除.md扩展名
    name_without_ext = filename[:-3] if filename.endswith('.md') else filename

    # 简单的描述生成逻辑
    if contains_chinese(name_without_ext):
        # 中文文件名，保持中文描述
        return f"{name_without_ext}的相关信息"
    else:
        # 英文文件名，生成英文描述
        words = name_without_ext.replace('-', ' ').replace('_', ' ').split()
        if words:
            return f"Information about {words[0]}"

    return "Memory file"


def validate_frontmatter(frontmatter: Dict) -> Tuple[bool, List[str]]:
    """验证frontmatter的完整性

    Args:
        frontmatter: frontmatter字典

    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误消息列表)
    """
    errors = []

    if not frontmatter:
        return False, ["frontmatter为空或不存在"]

    # 检查必需字段
    required_fields = ['name', 'description', 'type']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"缺少必需字段: {field}")
        elif not frontmatter[field]:
            errors.append(f"字段为空: {field}")

    # 检查type字段的有效性
    if 'type' in frontmatter:
        valid_types = ['user', 'feedback', 'project', 'reference']
        if frontmatter['type'] not in valid_types:
            errors.append(f"无效的类型: {frontmatter['type']}，有效类型为: {', '.join(valid_types)}")

    return len(errors) == 0, errors