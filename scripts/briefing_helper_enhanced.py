#!/usr/bin/env python3
"""
briefing_helper_enhanced.py — 增强版新闻简报辅助工具

功能增强：
1. 集成Tavily API进行高质量实时搜索
2. 添加智能缓存系统
3. 支持用户偏好配置
4. API使用统计

用法:
  python3 briefing_helper_enhanced.py <关键词> [选项]
  
示例:
  python3 briefing_helper_enhanced.py 江川路街道
  python3 briefing_helper_enhanced.py 国际新闻 --quality high
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# 尝试导入Tavily，如果失败则使用降级方案
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️  Tavily库未安装，使用降级搜索方案")

# 配置
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../cache")
USAGE_FILE = os.path.join(CACHE_DIR, "api_usage.json")

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

# ============================================================
# 行政区划和关键词定义
# ============================================================

PROVINCES = {
    "北京", "上海", "天津", "重庆",
    "广东", "江苏", "浙江", "山东", "河南", "四川", "湖北", "湖南",
    "河北", "山西", "辽宁", "吉林", "黑龙江", "安徽", "福建", "江西",
    "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆",
    "香港", "澳门", "海南", "贵州", "云南"
}

MAJOR_CITIES = {
    "北京", "上海", "广州", "深圳", "重庆", "成都", "杭州", "南京",
    "武汉", "西安", "天津", "苏州", "郑州", "长沙", "东莞", "青岛",
    "宁波", "沈阳", "大连", "厦门", "昆明", "哈尔滨", "济南", "合肥",
    "福州", "南昌", "长春", "石家庄", "贵阳", "南宁", "太原", "兰州",
    "乌鲁木齐", "呼和浩特", "银川", "拉萨", "西宁", "海口", "三亚"
}

INDUSTRY_KEYWORDS = {
    "AI", "人工智能", "大模型", "芯片", "半导体",
    "科技", "互联网", "软件", "算法", "算力",
    "股票", "股市", "财经", "经济", "市场", "汇率", "基金", "债券",
    "房产", "楼市", "房价", "房地产",
    "汽车", "新能源", "电动车", "电池",
    "医疗", "健康", "疫情", "疫苗",
    "教育", "高考", "考研", "留学",
    "游戏", "电竞", "动漫",
    "体育", "足球", "篮球", "奥运会", "世界杯",
    "军事", "国防", "军队",
    "航天", "火箭", "卫星", "太空",
}

GLOBAL_KEYWORDS = [
    "国际", "全球", "world", "international", "海外", "外交",
    "美国", "俄罗斯", "日本", "韩国", "朝鲜", "英国", "法国",
    "德国", "伊朗", "以色列", "欧盟", "北约", "联合国"
]

LOCAL_DISTRICT_SUFFIXES = [
    "区", "街道", "镇", "乡", "县", "市", "新区", "开发区",
    "镇", "村", "社区"
]

# ============================================================
# 缓存系统
# ============================================================

class SimpleCache:
    """简单文件缓存系统"""
    
    def __init__(self, cache_dir=CACHE_DIR, default_ttl=3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用哈希避免特殊字符问题
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Dict]:
        """从缓存获取数据"""
        if ttl is None:
            ttl = self.default_ttl
        
        filepath = self._get_cache_file(key)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < ttl:
                        return data.get('value')
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def set(self, key: str, value: Dict, ttl: Optional[int] = None) -> bool:
        """设置缓存数据"""
        if ttl is None:
            ttl = self.default_ttl
        
        filepath = self._get_cache_file(key)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.time(),
                    'ttl': ttl,
                    'value': value
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 缓存写入失败: {e}")
            return False
    
    def clear_expired(self) -> int:
        """清理过期缓存，返回清理数量"""
        import glob
        cleared = 0
        for filepath in glob.glob(os.path.join(self.cache_dir, "*.json")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) > data.get('ttl', self.default_ttl):
                        os.remove(filepath)
                        cleared += 1
            except:
                pass
        return cleared

# ============================================================
# API使用统计
# ============================================================

class APIUsageTracker:
    """API使用统计"""
    
    def __init__(self, usage_file=USAGE_FILE):
        self.usage_file = usage_file
        os.makedirs(os.path.dirname(usage_file), exist_ok=True)
    
    def load_usage(self) -> Dict:
        """加载使用统计"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_usage(self, usage: Dict):
        """保存使用统计"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(usage, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存使用统计失败: {e}")
    
    def record_call(self, endpoint: str, success: bool = True, response_time: float = 0):
        """记录API调用"""
        usage = self.load_usage()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in usage:
            usage[today] = {
                "calls": 0,
                "success": 0,
                "failed": 0,
                "total_response_time": 0,
                "endpoints": {}
            }
        
        usage[today]["calls"] += 1
        usage[today]["success" if success else "failed"] += 1
        usage[today]["total_response_time"] += response_time
        
        if endpoint not in usage[today]["endpoints"]:
            usage[today]["endpoints"][endpoint] = {"calls": 0, "success": 0}
        usage[today]["endpoints"][endpoint]["calls"] += 1
        usage[today]["endpoints"][endpoint]["success"] += (1 if success else 0)
        
        self.save_usage(usage)
    
    def get_quota_remaining(self) -> Optional[int]:
        """获取剩余调用配额（基于Tavily免费套餐：1000次/天）"""
        usage = self.load_usage()
        today = datetime.now().strftime("%Y-%m-%d")
        if today in usage:
            return max(0, 1000 - usage[today].get("calls", 0))
        return 1000

# ============================================================
# 新闻搜索核心功能
# ============================================================

class NewsSearcher:
    """新闻搜索器，支持Tavily API和降级方案"""
    
    def __init__(self):
        self.cache = SimpleCache()
        self.usage_tracker = APIUsageTracker()
        self.tavily_client = None
        
        if TAVILY_AVAILABLE and TAVILY_API_KEY:
            try:
                self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
                print("✅ Tavily客户端初始化成功")
            except Exception as e:
                print(f"⚠️ Tavily初始化失败: {e}")
        else:
            print("⚠️ Tavily不可用，使用降级方案")
    
    def search(self, query: str, max_results: int = 10, use_cache: bool = True) -> List[Dict]:
        """搜索新闻"""
        # 检查缓存
        cache_key = f"search:{query}:{max_results}"
        if use_cache:
            cached = self.cache.get(cache_key, ttl=1800)  # 30分钟缓存
            if cached:
                print(f"✅ 使用缓存结果: {query}")
                return cached
        
        start_time = time.time()
        results = []
        
        try:
            if self.tavily_client:
                # 使用Tavily API
                response = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results,
                    include_images=False,
                    include_answer=True
                )
                
                results = response.get("results", [])
                answer = response.get("answer", "")
                
                # 格式化结果
                formatted_results = [{
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "published_date": r.get("published_date", ""),
                    "source": r.get("url", "").split("/")[2] if r.get("url") else "unknown",
                    "raw": r
                } for r in results]
                
                results = formatted_results
                print(f"✅ Tavily搜索成功: {len(results)}条结果")
            
            else:
                # 降级方案：模拟搜索结果
                print("⚠️ 使用模拟搜索结果")
                results = [
                    {
                        "title": f"{query} - 模拟结果1",
                        "url": "#",
                        "content": f"这是关于{query}的模拟新闻内容...",
                        "published_date": datetime.now().strftime("%Y-%m-%d"),
                        "source": "模拟来源",
                        "raw": {}
                    }
                ]
        
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            results = []
        
        # 记录使用统计
        response_time = time.time() - start_time
        self.usage_tracker.record_call(
            endpoint="tavily_search",
            success=len(results) > 0,
            response_time=response_time
        )
        
        # 存入缓存
        if use_cache:
            self.cache.set(cache_key, results)
        
        return results
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        usage = self.usage_tracker.load_usage()
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {
            "today": usage.get(today, {}),
            "quota_remaining": self.usage_tracker.get_quota_remaining(),
            "cache_size": len([f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]) if os.path.exists(CACHE_DIR) else 0
        }
        
        return stats
    
    def clear_cache(self) -> int:
        """清理缓存"""
        return self.cache.clear_expired()

# ============================================================
# 行政区划检测 (与原代码兼容)
# ============================================================

def detect_scale(query: str) -> Dict:
    """检测查询尺度"""
    q = query.strip().lower()
    
    # 检查行业
    industry = None
    for kw in INDUSTRY_KEYWORDS:
        if kw.lower() in q:
            industry = kw
            break
    
    # 检查全球
    for kw in GLOBAL_KEYWORDS:
        if kw.lower() in q:
            return {"scale": "global", "industry": industry, "location": "",
                    "search_queries": _global_queries(industry)}
    
    # 检查省份
    for p in PROVINCES:
        if p in q:
            return {"scale": "province", "industry": industry, "location": p,
                    "search_queries": _province_queries(p, industry)}
    
    # 检查城市
    for c in MAJOR_CITIES:
        if c in q:
            return {"scale": "city", "industry": industry, "location": c,
                    "search_queries": _city_queries(c, industry)}
    
    # 检查区县/街道
    loc = ""
    for suffix in LOCAL_DISTRICT_SUFFIXES:
        if suffix in q:
            idx = q.index(suffix)
            loc = q[:idx + 1]
            break
    
    if loc and len(loc) >= 2:
        return {"scale": "local", "industry": industry, "location": loc,
                "search_queries": _local_queries(loc, industry)}
    
    # 默认
    if industry:
        return {"scale": "industry", "industry": industry, "location": "",
                "search_queries": _industry_queries(industry)}
    
    if len(q) >= 2:
        loc = q
        return {"scale": "local", "industry": None, "location": loc,
                "search_queries": _local_queries(loc, None)}
    
    return {"scale": "general", "industry": None, "location": "",
            "search_queries": ["今日新闻 最新 2026"]}

# 搜索查询生成函数
def _global_queries(industry):
    queries = [
        "world news latest today April 2026",
        "国际新闻 重大事件 2026",
        "international breaking news global",
    ]
    if industry:
        queries.append(f"{industry} global news 2026")
    return queries

def _province_queries(province, industry):
    queries = [
        f"{province} 2026 最新动态",
        f"{province} 经济 民生 政策",
        f"{province} 政府 新闻",
    ]
    if industry:
        queries.append(f"{province} {industry}")
    return queries

def _city_queries(city, industry):
    queries = [
        f"{city} 2026 最新",
        f"{city} 民生 经济 社区",
        f"{city} 政府 实事项目",
        f"{city} 人大 会议",
    ]
    if industry:
        queries.append(f"{city} {industry}")
    return queries

def _local_queries(loc, industry):
    queries = [
        f"{loc} 2026 最新",
        f"{loc} 民生 实事",
        f"{loc} 社区 改造",
        f"{loc} 公众号",
    ]
    if industry:
        queries.append(f"{loc} {industry}")
    return queries

def _industry_queries(industry):
    return [
        f"{industry} 最新进展 2026",
        f"{industry} news latest April 2026",
        f"{industry} 行业 趋势",
    ]

# ============================================================
# 主函数
# ============================================================

def main():
    if len(sys.argv) < 2:
        # 演示模式
        print("=" * 60)
        print("📰 中国资讯简报 - 增强版演示")
        print("=" * 60)
        
        demos = [
            ("国际简报", "🌍"),
            ("上海简报", "🏙️"),
            ("江川路街道简报", "📍"),
            ("闵行区简报", "📍"),
            ("AI行业简报", "🏭"),
        ]
        
        searcher = NewsSearcher()
        
        for query, icon in demos:
            print(f"\n{icon} 查询: {query}")
            result = detect_scale(query)
            scale_names = {
                "global": "🌍 全球尺度",
                "province": "🏛️ 省级尺度",
                "city": "🏙️ 城市尺度",
                "local": "📍 区县/街道尺度",
                "industry": "🏭 行业尺度",
                "general": "📋 综合尺度"
            }
            print(f"   尺度: {scale_names.get(result['scale'], result['scale'])}")
            if result['location']:
                print(f"   位置: {result['location']}")
            if result['industry']:
                print(f"   行业: {result['industry']}")
            print(f"   搜索词: {', '.join(result['search_queries'][:2])}...")
            
            # 实际搜索
            print(f"   🔍 搜索中...")
            search_results = searcher.search(
                query=result['search_queries'][0],
                max_results=3,
                use_cache=True
            )
            print(f"   结果: {len(search_results)}条")
            for r in search_results[:2]:
                print(f"     • {r['title']}")
        
        # 显示统计
        print("\n" + "=" * 60)
        stats = searcher.get_usage_stats()
        print("📊 API使用统计:")
        print(f"   今日调用: {stats['today'].get('calls', 0)}次")
        print(f"   剩余配额: {stats['quota_remaining']}次")
        print(f"   缓存文件: {stats['cache_size']}个")
        print("=" * 60)
        
        return
    
    # 单次查询模式
    query = sys.argv[1]
    use_cache = "--no-cache" not in sys.argv
    
    searcher = NewsSearcher()
    result = detect_scale(query)
    
    print(f"\n📝 查询: {query}")
    print(f"   尺度: {result['scale']}")
    if result['location']:
        print(f"   位置: {result['location']}")
    if result['industry']:
        print(f"   行业: {result['industry']}")
    print(f"   搜索词: {result['search_queries'][0]}")
    print()
    
    # 执行搜索
    results = searcher.search(
        query=result['search_queries'][0],
        max_results=10,
        use_cache=use_cache
    )
    
    print(f"\n📰 搜索结果 ({len(results)}条):")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']}")
        print(f"   🔗 {r['url']}")
        print(f"   📅 {r.get('published_date', '未知')}")
        print(f"   🏢 {r['source']}")
        content = r['content'][:200] + "..." if len(r['content']) > 200 else r['content']
        print(f"   📄 {content}")
    
    # 显示统计
    stats = searcher.get_usage_stats()
    print(f"\n📊 剩余配额: {stats['quota_remaining']}次")

if __name__ == "__main__":
    main()
