#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Tools 命令行接口
统一入口点，支持所有功能
"""

import sys
import argparse
from pathlib import Path

from .memory_tools import MemoryTools


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Memory Tools - 记忆系统诊断和维护工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s check                     # 基本检查
  %(prog)s report                    # 完整报告
  %(prog)s classify                  # 分类问题报告
  %(prog)s fix --dry-run             # 显示修复计划
  %(prog)s fix --execute             # 执行修复
  %(prog)s --json report             # JSON格式报告
  %(prog)s --memory-dir /path check  # 指定记忆目录

兼容旧参数:
  %(prog)s --check                   # 同 check
  %(prog)s --report                  # 同 report
  %(prog)s --fix                     # 同 fix --dry-run
  %(prog)s --fix-execute             # 同 fix --execute
  %(prog)s --classification-report   # 同 classify
  %(prog)s --fix-classification      # 同 fix --execute --fix-naming
        """
    )

    # 主命令
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # check 命令
    check_parser = subparsers.add_parser('check', help='基本检查')
    check_parser.add_argument('--json', action='store_true', help='JSON格式输出')

    # report 命令
    report_parser = subparsers.add_parser('report', help='完整诊断报告')
    report_parser.add_argument('--json', action='store_true', help='JSON格式输出')

    # classify 命令
    classify_parser = subparsers.add_parser('classify', help='分类问题报告')
    classify_parser.add_argument('--json', action='store_true', help='JSON格式输出')
    classify_parser.add_argument('--include-mixed-language', action='store_true',
                                help='包含混合语言描述问题')

    # fix 命令
    fix_parser = subparsers.add_parser('fix', help='修复问题')
    fix_parser.add_argument('--execute', action='store_true', help='执行修复（默认只显示计划）')
    fix_parser.add_argument('--dry-run', action='store_true', help='试运行模式（默认）')
    fix_parser.add_argument('--fix-naming', action='store_true', help='修复命名约定问题')
    fix_parser.add_argument('--fix-mixed-language', action='store_true',
                           help='修复混合语言描述问题')

    # 兼容旧参数的选项
    parser.add_argument('--check', action='store_true', help='基本检查（兼容旧参数）')
    parser.add_argument('--report', action='store_true', help='完整报告（兼容旧参数）')
    parser.add_argument('--fix', action='store_true', help='显示修复计划（兼容旧参数）')
    parser.add_argument('--fix-execute', action='store_true', help='执行修复（兼容旧参数）')
    parser.add_argument('--classification-report', action='store_true',
                       help='分类问题报告（兼容旧参数）')
    parser.add_argument('--fix-classification', action='store_true',
                       help='修复分类问题（兼容旧参数）')

    # 通用选项
    parser.add_argument('--memory-dir', help='记忆目录路径（默认自动检测）')
    parser.add_argument('--json', action='store_true', help='JSON格式输出（全局选项）')
    parser.add_argument('--action', help='动作（兼容旧参数：check/report/fix-plan/fix/classify/classify-fix）')

    return parser


def handle_check(args, memory_tools):
    """处理check命令"""
    if args.json:
        report = memory_tools.generate_diagnosis_report()
        import json
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        match_result, file_count, index_count = memory_tools.check_file_count_match()

        print("[MEMORY SYSTEM CHECK]")
        print("=" * 40)
        print(f"Memory files: {file_count}")
        print(f"Index entries: {index_count}")

        if match_result:
            print("[OK] Counts match")
        else:
            print(f"[ERROR] Counts don't match (difference: {abs(file_count - index_count)})")

        # 快速问题检查
        unindexed = memory_tools.find_unindexed_files()
        extra = memory_tools.find_extra_indexes()
        duplicates = memory_tools.find_duplicate_indexes()

        if unindexed:
            print(f"\n[WARNING] Unindexed files: {len(unindexed)}")
            for i, filename in enumerate(unindexed[:5], 1):
                print(f"   {i}. {filename}")
            if len(unindexed) > 5:
                print(f"   ... and {len(unindexed) - 5} more")

        if extra:
            print(f"\n[WARNING] Extra indexes: {len(extra)}")
            for i, filename in enumerate(extra[:5], 1):
                print(f"   {i}. {filename}")
            if len(extra) > 5:
                print(f"   ... and {len(extra) - 5} more")

        if duplicates:
            print(f"\n[WARNING] Duplicate indexes: {len(duplicates)}")
            for i, (filename, count) in enumerate(list(duplicates.items())[:5], 1):
                print(f"   {i}. {filename} (appears {count} times)")
            if len(duplicates) > 5:
                print(f"   ... and {len(duplicates) - 5} more")

        if not any([unindexed, extra, duplicates]):
            print("\n[OK] No obvious problems found")

        print("=" * 40)


def handle_report(args, memory_tools):
    """处理report命令"""
    if args.json:
        print(memory_tools.generate_json_report())
    else:
        memory_tools.print_report()


def handle_classify(args, memory_tools):
    """处理classify命令"""
    if args.json:
        print(memory_tools.generate_classification_json(not args.include_mixed_language))
    else:
        report = memory_tools.generate_classification_report(not args.include_mixed_language)
        print(report)


def handle_fix(args, memory_tools):
    """处理fix命令"""
    dry_run = not args.execute
    if args.dry_run:
        dry_run = True

    fix_plan = memory_tools.fix_classification_issues(
        dry_run=dry_run,
        fix_naming=args.fix_naming,
        fix_mixed_language=args.fix_mixed_language
    )

    memory_tools.print_fix_plan(fix_plan)


def handle_compatibility_args(args, memory_tools):
    """处理兼容旧参数"""
    if args.check:
        handle_check(args, memory_tools)
    elif args.report:
        handle_report(args, memory_tools)
    elif args.fix:
        # --fix 对应试运行模式
        temp_args = argparse.Namespace(execute=False, dry_run=True, fix_naming=False, fix_mixed_language=False)
        handle_fix(temp_args, memory_tools)
    elif args.fix_execute:
        # --fix-execute 对应执行修复
        temp_args = argparse.Namespace(execute=True, dry_run=False, fix_naming=True, fix_mixed_language=False)
        handle_fix(temp_args, memory_tools)
    elif args.classification_report:
        temp_args = argparse.Namespace(json=args.json, include_mixed_language=False)
        handle_classify(temp_args, memory_tools)
    elif args.fix_classification:
        temp_args = argparse.Namespace(execute=True, dry_run=False, fix_naming=True, fix_mixed_language=False)
        handle_fix(temp_args, memory_tools)
    elif args.action:
        # 处理 --action 参数
        action = args.action.lower()
        if action == 'check':
            handle_check(args, memory_tools)
        elif action == 'report':
            handle_report(args, memory_tools)
        elif action == 'fix-plan':
            temp_args = argparse.Namespace(execute=False, dry_run=True, fix_naming=False, fix_mixed_language=False)
            handle_fix(temp_args, memory_tools)
        elif action == 'fix':
            temp_args = argparse.Namespace(execute=True, dry_run=False, fix_naming=True, fix_mixed_language=False)
            handle_fix(temp_args, memory_tools)
        elif action == 'classify':
            temp_args = argparse.Namespace(json=args.json, include_mixed_language=False)
            handle_classify(temp_args, memory_tools)
        elif action == 'classify-fix':
            temp_args = argparse.Namespace(execute=True, dry_run=False, fix_naming=True, fix_mixed_language=False)
            handle_fix(temp_args, memory_tools)
        else:
            print(f"未知的action: {args.action}")
            sys.exit(1)


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # 初始化MemoryTools
        memory_tools = MemoryTools(args.memory_dir)

        # 处理命令
        if args.command:
            if args.command == 'check':
                handle_check(args, memory_tools)
            elif args.command == 'report':
                handle_report(args, memory_tools)
            elif args.command == 'classify':
                handle_classify(args, memory_tools)
            elif args.command == 'fix':
                handle_fix(args, memory_tools)
            else:
                parser.print_help()
                sys.exit(1)
        elif any([args.check, args.report, args.fix, args.fix_execute,
                 args.classification_report, args.fix_classification, args.action]):
            # 处理兼容旧参数
            handle_compatibility_args(args, memory_tools)
        else:
            # 默认显示帮助
            parser.print_help()

    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("请确保记忆系统已初始化或使用 --memory-dir 参数指定正确的目录")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()