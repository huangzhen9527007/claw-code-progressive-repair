"""
Memory Tools 插件 - 记忆系统诊断和维护工具

此包提供记忆系统完整性检查、分类问题检测和修复功能。
"""

__version__ = "1.0.0"
__author__ = "Claude Code Assistant"

from .memory_tools import MemoryTools
from .classification_fixer import ClassificationFixer
from .cli import main as cli_main

__all__ = ["MemoryTools", "ClassificationFixer", "cli_main"]