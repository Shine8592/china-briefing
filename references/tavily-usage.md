# Tavily API 使用参考

## 基本用法

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "$TAVILY_API_KEY",
    "query": "搜索关键词",
    "search_depth": "advanced",
    "max_results": 10
  }'
```

## 限定来源搜索

### 仅国际源
```bash
"include_domains": ["reuters.com", "bbc.com", "cnn.com", "apnews.com", "nytimes.com", "bloomberg.com", "aljazeera.com"]
```

### 仅国内源
```bash
"include_domains": ["xinhuanet.com", "sina.com.cn", "thepaper.cn", "cctv.com", "163.com"]
```

## 深度搜索 vs 基础搜索

| 模式 | 参数 | 速度 | 质量 |
|------|------|------|------|
| 基础 | `search_depth: "basic"` | 快（1-2s） | 摘要级 |
| 高级 | `search_depth: "advanced"` | 慢（3-5s） | 全文级 |

给用户生成简报时，**必须使用 `advanced`** 模式。

## 设置

- 环境变量方式：`TAVILY_API_KEY` 写入 `~/.hermes/.env`
- 配置文件方式：`config.yaml` 中 `api_keys.tavily` 字段
- 当前有效 API Key：从 `~/.hermes/.env` 读取（`TAVILY_API_KEY`）或 `config.yaml` 的 `api_keys.tavily`