#!/usr/bin/env python3
"""
quality_gate.py — 简报质量门禁系统

功能：
1. 检查简报是否符合质量标准
2. 检测注水内容
3. 返回详细的检查结果和修改建议

用法:
  python3 quality_gate.py <简报文件路径>
  python3 quality_gate.py --text "简报内容"
"""

import sys
import re
import json
from typing import List, Dict, Tuple

# ============================================================
# 质量标准配置
# ============================================================

QUALITY_CONFIG = {
    "min_words": 800,           # 最少字数
    "max_words": 2500,          # 最多字数
    "min_headlines": 3,         # 最少头条数
    "min_categories": 2,        # 最少分类数
    "min_sources": 3,           # 最少来源数
    "headline_min_words": 150,  # 每条头条最少字数
    "headline_max_words": 300,  # 每条头条最多字数
    "comment_keywords": ["嘟嘟点评", "点评", "看法", "我认为", "意味着"],
}

# 注水词列表（优化版）
WATER_WORDS = [
    "暂无相关信息", "暂无数据", "敬请期待", "持续关注",
    "本文将持续", "未有报道", "暂无更新"
]

# 注水词排除规则（这些场景下的"无"是合理的）
WATER_WORDS_EXCLUDE = [
    r'|优先级\s*|.\s*行动\s*|.\s*原因\s*|',  # 表格内容
    r'无论|无限|无私|无畏',  # 正常词语
]

# 必填部分
REQUIRED_SECTIONS = [
    "🌍 核心结论",
    "📌",  # 速报部分
    "📊 分类热点",
    "🎯 行动建议"
]


# ============================================================
# 核心检查函数
# ============================================================

def check_word_count(text: str) -> Tuple[bool, str, int]:
    """检查字数"""
    word_count = len(text)
    min_words = QUALITY_CONFIG["min_words"]
    max_words = QUALITY_CONFIG["max_words"]
    
    if word_count < min_words:
        return False, f"字数不足（{word_count}/{min_words}），需补充内容", word_count
    if word_count > max_words:
        return False, f"字数过多（{word_count}/{max_words}），需精简内容", word_count
    
    return True, f"字数达标（{word_count}字）", word_count


def check_headlines(text: str) -> Tuple[bool, str, int]:
    """检查头条数量和质量"""
    # 匹配头条（支持多种格式）
    # 格式1: **头条1** 内容
    # 格式2: **头条1：标题** 内容
    # 格式3: ### 头条1
    patterns = [
        r'\*\*头条\d+[：:].*?\*\*.*?(?=\*\*头条\d+[：:]|###|\n\*\*|$)',  # **头条1：标题** 内容
        r'\*\*头条\d+\*\*.*?(?=\*\*头条\d+\*\*|###|$)',  # **头条1** 内容
        r'###\s*头条\d+.*?(?=###\s*头条\d+|###|$)',  # ### 头条1
        r'####\s*头条\d+.*?(?=####\s*头条\d+|###|$)',  # #### 头条1
    ]
    
    headlines = []
    for pattern in patterns:
        headlines = re.findall(pattern, text, re.DOTALL)
        if headlines:
            break
    
    count = len(headlines)
    min_headlines = QUALITY_CONFIG["min_headlines"]
    
    if count < min_headlines:
        return False, f"头条数不足（{count}/{min_headlines}），需补充{3-count}条头条", count
    
    # 检查每条头条的字数
    short_headlines = []
    for i, h in enumerate(headlines, 1):
        h_words = len(h)
        if h_words < QUALITY_CONFIG["headline_min_words"]:
            short_headlines.append(f"头条{i}（{h_words}字）")
    
    if short_headlines:
        return False, f"以下头条字数不足：{', '.join(short_headlines)}", count
    
    return True, f"头条数量达标（{count}条）", count


def check_dudu_comments(text: str) -> Tuple[bool, str, int]:
    """检查嘟嘟点评"""
    comment_keywords = QUALITY_CONFIG["comment_keywords"]
    
    # 检查是否有点评关键词
    has_comment = any(kw in text for kw in comment_keywords)
    
    if not has_comment:
        return False, "缺少嘟嘟点评，每条头条需包含观点/分析", 0
    
    # 统计点评数量
    comment_count = 0
    for kw in comment_keywords:
        comment_count += text.count(kw)
    
    # 每条头条应该有至少1个点评
    headline_count = len(re.findall(r'\*\*头条\d+\*\*', text))
    if comment_count < headline_count:
        return False, f"点评数不足（{comment_count}/{headline_count}），每条头条需有点评", comment_count
    
    return True, f"嘟嘟点评完整（{comment_count}处）", comment_count


def check_sources(text: str) -> Tuple[bool, str, int]:
    """检查来源标注"""
    # 匹配来源标注（**来源** 或 来源：）
    source_patterns = [
        r'\*\*来源\*\*.*?(\n|$)',
        r'来源：.*?(\n|$)',
        r'🏢\s*.+',
    ]
    
    source_count = 0
    for pattern in source_patterns:
        source_count += len(re.findall(pattern, text))
    
    min_sources = QUALITY_CONFIG["min_sources"]
    
    if source_count < min_sources:
        return False, f"来源标注不足（{source_count}/{min_sources}），补充来源", source_count
    
    # 检查是否有"未知"、"网络"等无效来源
    # 改进：只检测"来源：网络"这种格式，而不是任意位置的"网络"
    invalid_sources = ["未知", "互联网", "unknown", "网络来源"]
    found_invalid = []
    for s in invalid_sources:
        # 只检查"来源：XXX"这种格式
        import re
        pattern = r'来源[：:]\s*' + re.escape(s) + r'[^\n]*'
        if re.search(pattern, text):
            found_invalid.append(s)
    
    # 特殊处理："网络"这个词需要更精准的判断
    if '网络' in text:
        # 检查是否是"来源：网络"或"来源:网络"
        if re.search(r'来源[：:]\s*网络', text):
            found_invalid.append('网络（来源标注）')
    
    if found_invalid:
        return False, f"发现无效来源：{', '.join(found_invalid)}，请标注具体媒体", source_count
    
    return True, f"来源标注完整（{source_count}处）", source_count


def check_water_words(text: str) -> Tuple[bool, str, List[str]]:
    """检查注水词（优化版）"""
    found = []
    for ww in WATER_WORDS:
        if ww in text:
            # 统计出现次数
            count = text.count(ww)
            found.append(f"{ww}（{count}次）")
    
    # 特殊处理：检查"无"是否真的是注水
    # 排除场景：表格内容、正常词语
    if "无" in text:
        # 简单判断：如果"无"在表格里（行动建议表格），可能是合理的
        # 更严谨的做法：检查"无"的上下文
        lines = text.split('\n')
        for line in lines:
            if '|' in line and '无' in line:
                # 表格中的"无"，跳过
                continue
            elif '无' in line and len(line.strip()) < 10:
                # 单独成行的"无"，可能是注水
                found.append("无（疑似注水）")
                break
    
    if found:
        return False, f"发现注水词：{', '.join(found)}，请重写", found
    
    return True, "未发现注水词", []


def check_required_sections(text: str) -> Tuple[bool, str, List[str]]:
    """检查必填部分"""
    missing = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            missing.append(section)
    
    if missing:
        return False, f"缺少必填部分：{', '.join(missing)}", missing
    
    return True, "必填部分完整", []


def check_action_suggestions(text: str) -> Tuple[bool, str, str]:
    """检查行动建议是否为空"""
    # 提取行动建议部分
    if "🎯 行动建议" in text:
        # 找到行动建议部分直到下一个###或文件结束
        pattern = r'🎯 行动建议.*?(?=###|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            section = match.group(0)
            # 检查是否有实质性的建议（不是只有"无"或空表）
            if "无" in section and len(section) < 100:
                return False, "行动建议为空或只有'无'，需补充具体建议", section[:200]
            return True, "行动建议完整", section[:200]
    
    return False, "未找到行动建议部分", ""


# ============================================================
# 主检查函数
# ============================================================

def quality_check(text: str) -> Dict:
    """
    执行完整的质量检查
    
    返回：
    {
        "passed": True/False,
        "score": 85,  # 质量分数 0-100
        "word_count": 1200,
        "checks": [...],  # 详细检查结果
        "errors": [...],   # 错误列表
        "suggestions": [...] # 修改建议
    }
    """
    results = {
        "passed": True,
        "score": 100,
        "word_count": 0,
        "checks": [],
        "errors": [],
        "suggestions": []
    }
    
    # 1. 字数检查
    ok, msg, word_count = check_word_count(text)
    results["word_count"] = word_count
    results["checks"].append({"name": "字数检查", "passed": ok, "message": msg})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 30
        results["suggestions"].append("补充更多新闻内容，每条头条至少150字")
    
    # 2. 头条检查
    ok, msg, headline_count = check_headlines(text)
    results["checks"].append({"name": "头条检查", "passed": ok, "message": msg, "count": headline_count})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 25
        results["suggestions"].append("补充头条数量，每条包含事实+背景+观点")
    
    # 3. 嘟嘟点评检查
    ok, msg, comment_count = check_dudu_comments(text)
    results["checks"].append({"name": "嘟嘟点评", "passed": ok, "message": msg, "count": comment_count})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 20
        results["suggestions"].append("为每条头条添加'嘟嘟点评'，包含背景分析和观点")
    
    # 4. 来源检查
    ok, msg, source_count = check_sources(text)
    results["checks"].append({"name": "来源标注", "passed": ok, "message": msg, "count": source_count})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 15
        results["suggestions"].append("标注每条信息的来源媒体和URL")
    
    # 5. 注水词检查
    ok, msg, found_words = check_water_words(text)
    results["checks"].append({"name": "注水词检查", "passed": ok, "message": msg, "words": found_words})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 20
        results["suggestions"].append("删除空话套话，用实质性内容补充")
    
    # 6. 必填部分检查
    ok, msg, missing = check_required_sections(text)
    results["checks"].append({"name": "必填部分", "passed": ok, "message": msg, "missing": missing})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 20
        results["suggestions"].append("补充缺少的部分：{}".format(', '.join(missing)))
    
    # 7. 行动建议检查
    ok, msg, section = check_action_suggestions(text)
    results["checks"].append({"name": "行动建议", "passed": ok, "message": msg})
    if not ok:
        results["passed"] = False
        results["errors"].append(msg)
        results["score"] -= 10
        results["suggestions"].append("在行动建议中补充具体可行的建议")
    
    # 确保分数不低于0
    results["score"] = max(0, results["score"])
    
    return results


# ============================================================
# 命令行接口
# ============================================================

def print_report(results: Dict):
    """打印检查报告"""
    print("=" * 70)
    print("📊 简报质量检查报告")
    print("=" * 70)
    
    # 总体结果
    status = "✅ 通过" if results["passed"] else "❌ 未通过"
    print(f"\n总体结果：{status}")
    print(f"质量分数：{results['score']}/100")
    print(f"字数统计：{results['word_count']}字")
    
    # 详细检查
    print(f"\n{'-' * 70}")
    print("详细检查：")
    for check in results["checks"]:
        icon = "✅" if check["passed"] else "❌"
        print(f"  {icon} {check['name']}: {check['message']}")
    
    # 错误列表
    if results["errors"]:
        print(f"\n{'-' * 70}")
        print("❌ 发现的问题：")
        for i, error in enumerate(results["errors"], 1):
            print(f"  {i}. {error}")
    
    # 修改建议
    if results["suggestions"]:
        print(f"\n{'-' * 70}")
        print("💡 修改建议：")
        for i, suggestion in enumerate(results["suggestions"], 1):
            print(f"  {i}. {suggestion}")
    
    print("=" * 70)
    
    # 返回退出码（0=通过，1=未通过）
    return 0 if results["passed"] else 1


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 quality_gate.py <简报文件路径>")
        print("  python3 quality_gate.py --text '简报内容'")
        sys.exit(1)
    
    # 读取内容
    if sys.argv[1] == "--text":
        if len(sys.argv) < 3:
            print("❌ 请提供简报内容")
            sys.exit(1)
        text = sys.argv[2]
    else:
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)
    
    # 执行检查
    results = quality_check(text)
    
    # 打印报告
    exit_code = print_report(results)
    
    # 输出JSON（供程序调用）
    if "--json" in sys.argv:
        print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
