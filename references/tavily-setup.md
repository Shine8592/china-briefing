# Tavily API 配置指南

## 获取 API Key
- 注册：https://app.tavily.com
- 免费套餐：1000 次/天，30 次/分钟

## 配置方式（双重保障）

### 方式 1：环境变量（推荐）
写入 `~/.hermes/.env`：
```
TAVILY_API_KEY="tvly-dev-xxxx"
```

### 方式 2：技能配置文件
在技能目录下的 `config.yaml` 中配置：
```yaml
api_keys:
  tavily: "tvly-dev-xxxx"
```

## API 调用示例

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "'"$TAVILY_API_KEY"'",
    "query": "搜索关键词",
    "search_depth": "advanced",
    "max_results": 10
  }'
```

## 参数说明
| 参数 | 必填 | 说明 |
|------|------|------|
| api_key | 是 | Tavily API key |
| query | 是 | 搜索查询词 |
| search_depth | 否 | "basic"或"advanced"，默认"basic" |
| include_domains | 否 | 限定搜索域名列表 |
| exclude_domains | 否 | 排除搜索域名列表 |
| max_results | 否 | 最大结果数，默认5，最大20 |