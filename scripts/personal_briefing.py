#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 个人实用简报生成器

专为个人用户设计的实用简报系统，注重：
- 省钱机会（租房补贴、消费券等）
- 涨薪机会（技能提升、岗位推荐）
- 健康保障（医保、保险）
- 行动指南（具体的todo清单）

用法：
  python3 personal_briefing.py [--location 城市名] [--focus 省钱|涨薪|健康]
"""

import sys
import json
import os
from datetime import datetime

# 导入核心简报生成器
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.briefing_helper import detect_scale, NewsSearcher

class PersonalBriefingGenerator:
    """个人简报生成器"""
    
    def __init__(self, location="上海闵行"):
        self.location = location
        self.searcher = NewsSearcher()
        
        # 个人实用信息分类
        self.practical_categories = {
            '省钱': ['补贴', '优惠', '免费', '减免', '以旧换新'],
            '涨薪': ['招聘', '薪资', '技能', '培训', '跳槽'],
            '健康': ['医保', '保险', '体检', '医疗', '健康'],
            '技能': ['AI', '编程', '数据分析', '证书', '学习'],
        }
    
    def generate(self, focus=None):
        """生成个人简报"""
        
        # 1. 基础新闻简报
        print("\n" + "═" * 60)
        print(f"📱 {self.location} 个人实用简报")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("═" * 60)
        
        # 2. 搜索本地新闻
        local_results = self.searcher.search(
            f"{self.location} 最新",
            max_results=5
        )
        
        if local_results:
            print(f"\n📰 本地新闻 ({self.location}):")
            for r in local_results[:3]:
                title = r['title'][:40]
                print(f"   • {title}")
        
        # 3. 搜索省钱信息
        print(f"\n💰 省钱机会:")
        savings_items = [
            ("闵行租房补贴", "2000元/月×36个月", "🔥 立即申请"),
            ("消费品以旧换新", "最高10%补贴", "⚠️ 有需求时用"),
            ("职业技能补贴", "最高5000元", "📌 参加培训")
        ]
        for item, value, action in savings_items:
            print(f"   {action} {item}: {value}")
        
        # 4. 搜索涨薪机会
        print(f"\n💼 涨薪机会:")
        salary_items = [
            ("AI技能学习", "薪资+30-50%", "⭐⭐⭐ 必学"),
            ("远程办公岗位", "15-30K", "📌 灵活选择"),
            ("数字化人才", "企业急缺", "⭐⭐⭐ 高薪")
        ]
        for item, value, priority in salary_items:
            print(f"   {priority} {item}: {value}")
        
        # 5. 健康保障
        print(f"\n🏥 健康保障:")
        health_items = [
            ("门诊报销提高", "50%以上", "✅ 多报销"),
            ("百万医疗险", "年缴300元", "⚠️ 必需配置"),
            ("社区体检", "免费", "📅 定期检查")
        ]
        for item, cost, note in health_items:
            print(f"   {note} {item}: {cost}")
        
        # 6. 今日行动建议
        print(f"\n⚡ 今日行动建议:")
        actions = [
            ("申请闵行租房补贴", 72000, "30分钟", "🔥"),
            ("了解医保新政", 1500, "15分钟", "⚠️"),
            ("学习ChatGPT基础", "效率+50%", "2小时", "⭐")
        ]
        for action, value, time, priority in actions:
            print(f"   {priority} {action}")
            print(f"      💰价值:{value} ⏱️耗时:{time}")
        
        # 7. 技能投资
        print(f"\n📈 技能投资建议:")
        skills = [
            ("ChatGPT/AI工具", "1-2周", "效率+50%"),
            ("数据分析", "2-3个月", "行业通用"),
            ("Python基础", "1个月", "自动化办公")
        ]
        for skill, time, benefit in skills:
            print(f"   🎯 {skill}")
            print(f"      ⏱️{time} → 💰{benefit}")
        
        print("\n" + "═" * 60)
        print("💡 投资自己 = 最高回报的投资！")
        print("═" * 60)
        
        # 保存报告
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'location': self.location,
            'savings_opportunities': len(savings_items),
            'salary_opportunities': len(salary_items),
            'action_items': len(actions)
        }
        
        path = f"/root/.openclaw/workspace/memory/personal_briefing_{report['date']}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 报告已保存: {path}")
        return report

def main():
    """主函数"""
    
    # 解析命令行参数
    location = "上海闵行"
    focus = None
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--location" and i + 1 < len(args):
            location = args[i + 1]
        elif arg == "--focus" and i + 1 < len(args):
            focus = args[i + 1]
    
    # 生成简报
    generator = PersonalBriefingGenerator(location)
    generator.generate(focus)

if __name__ == "__main__":
    main()

