# 国际新闻来源库（按尺度选源）

## 使用规则
- 生成简报时，**国际尺度必须包含至少3家不同国家的媒体**
- 每条信息必须标注来源媒体 + 链接
- 避免仅依赖单一源

## 全球尺度的推荐来源

### 西方主流媒体
| 媒体 | 定位 | 获取方式 | 覆盖范围 |
|------|------|---------|---------|
| Reuters | 事实最快，全球覆盖 | Tavily + reuters.com | 全球政治/经济 |
| AP News | 美联社，权威快讯 | Tavily + apnews.com | 全球突发/政治 |
| BBC | 英国视角，国际新闻 | Tavily + bbc.com | 全球/英国/中东 |
| CNN | 美国新闻+全球视角 | Tavily + cnn.com | 美国/全球热点 |
| NYT | 深度分析，调查报道 | Tavily + nytimes.com | 全球深度/政治 |

### 财经媒体
| 媒体 | 定位 | 获取方式 |
|------|------|---------|
| Bloomberg | 全球金融数据 | Tavily + bloomberg.com |
| Financial Times | 经济深度分析 | Tavily + ft.com |
| CNBC | 商业/股市快讯 | Tavily + cnbc.com |
| Wall Street Journal | 商业/政治 | Tavily + wsj.com |

### 中东/欧洲视角
| 媒体 | 定位 | 获取方式 |
|------|------|---------|
| Al Jazeera | 中东独特视角 | Tavily + aljazeera.com |
| DW (Deutsche Welle) | 欧洲视角 | Tavily + dw.com |

### 中国媒体（国际版）
| 媒体 | 定位 | 获取方式 |
|------|------|---------|
| 新华社 | 中国官媒 | Tavily + xinhuanet.com |
| 央视新闻/CCTV | 中国视角 | Tavily + cctv.com |
| 环球时报 | 国际评论 | Tavily + globaltimes.cn |

### 中文商业媒体
| 媒体 | 定位 | 获取方式 |
|------|------|---------|
| 新浪财经 | A股/中概股 | Tavily + finance.sina.com.cn |
| 财联社 | 快讯/电报 | Tavily + cls.cn |
| 澎湃新闻 | 深度调查 | Tavily + thepaper.cn |
| 观察者网 | 时政评论 | Tavily + guancha.cn |
| 36氪 | 科技商业 | Tavily + 36kr.com |

## 技术搜索技巧

### Tavily API 域名限定
```bash
# 仅搜国际媒体
"include_domains": ["reuters.com", "bbc.com", "cnn.com", "apnews.com", "nytimes.com"]

# 仅搜财经媒体
"include_domains": ["bloomberg.com", "reuters.com", "cnbc.com", "ft.com"]

# 混合搜索（国际+国内）
"include_domains": ["reuters.com", "bbc.com", "xinhuanet.com", "thepaper.cn", "sina.com.cn"]
```

### 搜索深度选择
- `search_depth: "advanced"` — 国际/深度话题，获取更完整内容
- `search_depth: "basic"` — 热点速查，更快响应

## 来源多样性规则

| 尺度 | 最少来源数 | 必须包含 |
|------|----------|---------|
| 全球 | 5+ | Reuters + 1家中国官媒 + 1家社区 |
| 全国 | 4+ | 至少2家不同立场 |
| 省市 | 3+ | 官方 + 本地媒体 |
| 区县/街道 | 2+ | 政府官网 + 至少1个来源 |
| 行业 | 3+ | 行业媒体 + 社区 |