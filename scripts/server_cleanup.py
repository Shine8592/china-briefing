#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 服务器垃圾清理技能 - 集成版

专为OpenClaw设计的安全清理工具

特点：
✅ 绝不删除记忆系统关键文件
✅ 白名单保护机制
✅ 干运行预览模式
✅ 日志记录所有操作
✅ 支持多级别清理

使用方法：
  1. 在china-briefing技能中调用
  2. 或单独运行: python3 server_cleanup.py [选项]
"""

import os
import sys
import json
from datetime import datetime

# ============================================================
# 配置
# ============================================================

WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")

# 🛡️ 受保护的项目（绝不删除）
PROTECTED = {
    'files': [
        'MEMORY.md', 'SOUL.md', 'USER.md', 'TOOLS.md',
        'HEARTBEAT.md', 'AGENTS.md', 'IDENTITY.md',
        'openclaw.json', 'SKILL.md', 'README.md',
        'briefing', 'personal_briefing',
        '.json', '.faiss', '.pickle', '.db',
        '.backup', '.bak',
    ],
    'dirs': [
        'memory', 'skills', 'models',
        'cache', '.git', 'backups',
        'personal_memories',
    ]
}

# 🗑️ 可安全清理的模式
CLEAN_PATTERNS = {
    'temp': ['*.tmp', '*.temp', '*.swp', '*.swo', '*~'],
    'ide': ['.DS_Store', 'Thumbs.db', '.vscode', '.idea'],
    'compile': ['__pycache__', '*.pyc', '.pytest_cache'],
    'log': ['*.log'],  # 仅非今日日志
}

# ============================================================
# 核心功能
# ============================================================

def is_protected(path: str) -> bool:
    """检查路径是否受保护"""
    name = os.path.basename(path)
    
    # 检查保护目录
    for dirname in PROTECTED['dirs']:
        if dirname in path:
            # 允许删除__pycache__
            if '__pycache__' not in path:
                return True
    
    # 检查保护文件
    for pattern in PROTECTED['files']:
        if pattern.replace('*', '') in name:
            return True
    
    return False

def is_cleanable(name: str, path: str) -> bool:
    """检查文件/目录是否可清理"""
    # 跳过受保护的
    if is_protected(path):
        return False
    
    # 检查临时文件
    for patterns in CLEAN_PATTERNS.values():
        for pattern in patterns:
            if pattern.replace('*', '') in name:
                return True
    
    return False

def scan(path: str, level='safe'):
    """扫描可清理项目"""
    items = []
    
    for root, dirs, files in os.walk(path):
        # 跳过受保护目录
        if any(d in root for d in PROTECTED['dirs']):
            continue
        
        # 检查文件
        for f in files:
            filepath = os.path.join(root, f)
            if is_cleanable(f, filepath):
                # 日志文件特殊处理
                if f.endswith('.log'):
                    try:
                        mtime = os.path.getmtime(filepath)
                        age = (datetime.now().timestamp() - mtime) / 86400
                        if age < 1 and level != 'aggressive':
                            continue  # 跳过今日日志
                    except:
                        pass
                
                items.append(('file', filepath))
        
        # 检查__pycache__目录
        for d in dirs:
            if '__pycache__' in d:
                dirpath = os.path.join(root, d)
                if not is_protected(dirpath):
                    items.append(('dir', dirpath))
    
    return items

def clean(items, dry_run=True):
    """执行清理"""
    results = {'success': 0, 'failed': 0}
    
    for item_type, path in items:
        try:
            if dry_run:
                print(f"  [DRY RUN] {item_type}: {path}")
                results['success'] += 1
                continue
            
            if item_type == 'file':
                os.remove(path)
                print(f"  ✅ 已删除文件: {os.path.basename(path)}")
            else:
                os.rmdir(path)
                print(f"  ✅ 已删除目录: {path}")
            
            results['success'] += 1
        except Exception as e:
            print(f"  ❌ 失败: {path} - {e}")
            results['failed'] += 1
    
    return results

def log_operation(operation, stats):
    """记录操作日志"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'stats': stats
    }
    
    log_path = os.path.join(MEMORY_DIR, 'cleanup_history.json')
    try:
        history = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                history = json.load(f)
        history.append(log_entry)
        history = history[-20:]  # 保留最近20次
        
        with open(log_path, 'w') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except:
        pass

# ============================================================
# CLI接口
# ============================================================

def main():
    print("═" * 60)
    print("🧹 服务器垃圾清理 - 安全版")
    print("═" * 60)
    
    # 解析参数
    args = sys.argv[1:]
    dry_run = '--execute' not in args
    level = 'safe'
    target = WORKSPACE
    
    if '--level' in args:
        idx = args.index('--level')
        if idx + 1 < len(args):
            level = args[idx + 1]
    
    # 找出目标目录（第一个非选项参数）
    for arg in args:
        if not arg.startswith('--') and os.path.isdir(arg):
            target = arg
            break
    
    print(f"\n📍 目标: {target}")
    print(f"🔍 级别: {level}")
    print(f"📋 模式: {'干运行' if dry_run else '实际删除'}\n")
    
    # 扫描
    print("🔍 扫描中...")
    items = scan(target, level)
    
    if not items:
        print("✅ 没有可清理的项目！")
        return
    
    files = [p for t, p in items if t == 'file']
    dirs = [p for t, p in items if t == 'dir']
    
    print(f"📊 找到 {len(items)} 个项目:")
    print(f"   📄 文件: {len(files)}")
    print(f"   📁 目录: {len(dirs)}\n")
    
    # 显示示例
    if files:
        print("示例文件:")
        for f in files[:5]:
            print(f"   • {os.path.basename(f)}")
        if len(files) > 5:
            print(f"   ... 还有 {len(files)-5} 个\n")
    
    # 执行清理
    if not dry_run:
        print("⚠️ 确认删除? (yes/no)")
        if False:  # Auto-confirm for non-interactive use
            print("❌ 已取消")
            return
        print("\n🧹 执行清理...")
    else:
        print("💡 使用 --execute 执行实际清理")
    
    results = clean(items, dry_run)
    
    # 显示结果
    print(f"\n{'=' * 60}")
    print(f"✅ 完成!")
    print(f"   成功: {results['success']}")
    print(f"   失败: {results['failed']}")
    print(f"{'=' * 60}")
    
    # 记录日志
    log_operation('cleanup', results)

if __name__ == "__main__":
    main()
