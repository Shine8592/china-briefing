---
name: china-briefing
description: |
  多尺度中文资讯简报生成。从一条街道到全球，任意地理范围均可生成。
  从主流媒体（Reuters/BBC/新华社）、街道公众号、社交平台（微博/小红书/抖音）
  获取资讯，结构化输出。
  使用场景：用户要求"简报"、"资讯"、"早报"、"晚报"、"周报"、"XX简报"、
  "XX资讯"、"本地新闻"、"国际新闻"、"街道新闻"等。
  外部依赖：free_search MCP 工具（免 API Key 多引擎搜索）。核心：free_search__search（搜索）、
  free_search__research（搜索+抓正文，最省事）、free_search__fetch / read_doc（直连抓取与文档解析）。
---

# China Briefing — 多尺度中文资讯简报

## ⚠️ 规则优先级（冲突时按此顺序裁决）

1. **安全底线** — 绝不虚构数据，必须用 `free_search` 工具获取实时信息
2. **结构完整性** — 必须包含所有必填板块（见简报结构），不可省略
3. **来源可信度** — 每个事实标注来源媒体 + URL
4. **内容质量** — 字数、角度、反注水（见质量门禁）
5. **风格优化** — 嘟嘟点评的深度与视角

---

## 核心能力

**任意尺度，一处生成：**
- 全球 → 区域（亚太/欧洲/中东） → 国家 → 省 → 市 → 区 → 街道 → 社区
- 每层自动选择匹配的搜索源（见 `references/search-sources.md`、`references/international-sources.md`）

---

## 步骤 1：确定尺度并搜索

### 强制规则

1. **必须**调用 `free_search__search` 工具搜索实时数据（禁止仅凭已有知识生成）
2. **必须**按简报尺度选择搜索源：
   - **全球简报**：仅搜国际源（reuters.com, bbc.com, bloomberg.com, apnews.com, cnbc.com, aljazeera.com 等），不混入国内新闻
   - **国内简报**：仅搜国内源（xinhuanet.com, thepaper.cn, scio.gov.cn, gov.cn, cctv.com 等）
   - **本地简报**：搜本地政务 + 本地媒体
3. **必须**按尺度执行多次搜索覆盖不同角度：
   - **全球简报**：至少 2 次（国际政治 + 国际经济）
   - **国内简报**：至少 2 次（政策 + 民生）
   - **本地简报**：至少 2 次（政务 + 社会）
4. 每次搜索使用 `include_domains` 限定范围
5. 用 `memory` 工具检索用户兴趣（住房、就业、社保、物价、政策、技能提升），与地理范围组合成扩展搜索词
6. 用户兴趣集成细节见 `references/user-interest-integration.md`

### 搜索参数与尺度绑定

| 尺度 | `max_results` | `freshness` | `category` | `include_domains` 示例 |
|------|---------------|-------------|-----------|----------------------|
| 全球/国家 | 10 | `day` | `news` | reuters.com, bbc.com, apnews.com, aljazeera.com |
| 省市 | 8 | `week` | `news` | 本地官媒, 市政府网, 省级日报 |
| 区县/街道 | 5 | `week` | — | 政府官网, 政务公众号, 社区 |
| 行业/垂直 | 8 | `week` | — | 行业媒体, 社区平台 |

> ✅ **`free_search__search` 实测可用参数**：`query` / `engines` / `max_results` / `freshness`(day\|week\|month\|year) / `include_domains` / `exclude_domains` / `category` / `include_text` / `exclude_text` / `use_cache` / `max_age_hours` / `format`。
> ⚠️ **不存在 `search_depth` 参数**（旧 Tavily 遗留，传了无效）——只有 `free_search__research` 才有 `depth`（= 抓取正文的篇数）。
> 💡 **最省事**：`free_search__research(question=..., depth=3, category="news", freshness="day")` 一步拿到「搜索 + 正文」，比 `search` 更适合简报。

### 搜索源库（详见 reference 文件）

- 国内源：`references/search-sources.md`
- 国际源：`references/international-sources.md`

| 尺度 | 最少来源数 | 必须包含 |
|------|----------|---------|
| 全球 | 5+ | ≥2 家国际通讯社（Reuters / AP）+ ≥2 家不同立场媒体（如 BBC + Al Jazeera）｜**不混入国内源** |
| 全国 | 4+ | 至少2家不同立场 |
| 省市 | 3+ | 官方 + 本地 |
| 区县/街道 | 2+ | 政府官网 + 至少1个来源 |
| 行业 | 3+ | 行业媒体 + 社区 |

### ⚠️ 故障回退

- **free_search__search 超时/失败** → 重试 1 次；仍失败改用 `free_search__research` 或 `free_search__fetch` 直连抓取主要新闻源首页（实测可达：bbc.com / aljazeera.com / cnn.com / dw.com / cna.com.tw / 8world.com）
- **某尺度搜索返回 0 结果** → 放宽到相邻更大尺度（街道无结果→搜区级；区级无→市级）
- **搜索引擎整体不可用**（如出口 IP 被限流）→ 退回 `free_search__fetch` 直连抓取新闻源首页；若直连也不通，再用记忆中的最近已知信息并标注"数据来源：历史缓存"
- **⚠️ JS 重站点拿不到正文**（bloomberg.com / ft.com 等）→ 报 `Playwright's Chromium browser is not installed`。这类站点只能取到标题/URL，**不要依赖其正文**；需要正文时换 bbc.com / aljazeera.com / apnews.com 等可直接解析的源，或先安装 Chromium（见下）。
- **注**：`tavily_mcp` / `web_search` 自 2026-10 起因出口 IP 被 api.tavily.com 整站 403，**已废弃，不要用作回退路径**
- **注**：`free_search` 共 11 个工具（search / research / fetch / fetch_batch / read_doc / compare / paper_graph / cache_search / engines / extract_structured / download）。`read_doc` 读 PDF/DOCX/XLSX/PPTX/EPUB 是**可用**的。

---

## 步骤 2：生成简报结构

> 每个板块的顺序不可调换。必填不可省略。

### 🌍 核心结论 [必填，50-100字]
1-2 句总结本期最重要的趋势或结论。

### 📌 {日期} {地点} 速报 [必填，3条头条]

每条头条结构：
```
**头条{n}** [事实描述 100-200字] + **嘟嘟点评:** [个人视角/观点 50-100字]
```

⚠️ 检查：
- 头条数 = 3（不足 3 条可用时：减少到 2 条并标注"本期仅 2 条优质新闻"，绝不凑数）
- 每条必须含**嘟嘟点评**
- 嘟嘟点评格式：`**嘟嘟点评:** ` 后接观点（见 `references/formatting.md`）
- 字数弹性：信息充足→200-300字，信息较少→100-200字，不硬凑

### 📊 分类热点 [必填，2-4类，每类2-4条]
每类每条 30-80 字。分类数不足 2 时用相邻主题补充。

### 📈 数据看板 [可选]
关键数据表格（含来源）。

### 🎯 行动建议 [必填，非空]

| 优先级 | 行动 | 原因 |
|--------|------|------|
| 高 | ... | ... |
| 中 | ... | ... |
| 低 | ... | ... |

---

## 🚫 反注水规则（强制执行）

1. **禁止空话套话**：拒绝"暂无""敬请期待""持续关注""暂无数据"
2. **禁止无内容头条**：每条必须含事实+背景+嘟嘟观点
3. **禁止重复凑数**：同一信息换说法说两遍 → 合并
4. **嘟嘟点评必须有观点**：❌"XX报道了XXX" → ✅"这意味着…我看好/担心…"
5. **来源必须完整**：❌"来源：网络" → ✅"来源：媒体名 + URL"

---

## 🔒 质量门禁（生成后自动检查）

执行 `references/quality-gate.md` 中的实现，逐条检查：

1. 字数 ≥ 800
2. 头条数 = 3（或允许的 2 条+标注）
3. 每条头条包含嘟嘟点评
4. 每个信息来源标注完整
5. 无注水词
6. 行动建议表非空

**结果判定：**
- 全部通过 → 交付
- 1-2 项不达标 → 修正该部分后交付
- 3 项及以上不达标 → 退回重新生成

---

## 🔧 搜索工具配置

**主用工具：`free_search`（MCP，免 API Key）** —— 无需任何密钥或配置文件，开箱即用。

| 工具 | 用途 |
|------|------|
| `free_search__search` | 关键词搜索，支持 `include_domains` / `max_results` / `freshness` / `category` / `engines`（**无 `search_depth`**） |
| `free_search__research` | 一次调用 = 搜索 + 抓取前 N 篇正文，直接返回带引用的 Markdown 简报（最省事） |
| `free_search__fetch` / `free_search__fetch_batch` | 抓取指定 URL 正文（多源直连兜底） |
| `free_search__read_doc` | 读取 PDF / DOCX / XLSX / PPTX / EPUB |

**已废弃**：Tavily（`tavily_mcp` 与内置 `web_search`）。自 2026-10 起本机出口 IP 被 `api.tavily.com` 整站 403（`server: awselb/2.0`），非 Key 失效。旧文档 `references/tavily-setup.md`、`references/tavily-usage.md` 仅作存档。

---

## 使用流程

1. **确定尺度+搜索词** — 判断地理范围+用户兴趣扩展
2. **搜索** — 按尺度参数表调用 `free_search__search`（或 `free_search__research`），满足最少来源数
3. **生成初稿** — 严格按简报结构，每板块必填
4. **质量门禁** — 执行 `references/quality-gate.md` 检查
5. **交付** — 输出最终简报（不达标则修正或重新生成）
