---
name: china-briefing
description: |
  多尺度中文资讯简报生成。从一条街道到全球，任意地理范围均可生成。
  从主流媒体（Reuters/BBC/新华社）、街道公众号、社交平台（微博/小红书/抖音）
  获取资讯，结构化输出。
  使用场景：用户要求"简报"、"资讯"、"早报"、"晚报"、"周报"、"XX简报"、
  "XX资讯"、"本地新闻"、"国际新闻"、"街道新闻"等。
  外部依赖（四引擎协作，2026-11-18 定案；非排队降级而是按环节各守岗位、关键事实双源交叉）：wb2a（免费/中文源/正文，主力）· Exa（国际权威原站+date/正文）· Tavily（国际通讯社+精确时间）· Firecrawl（硬反爬唯一解，省用）· free_search（全失败兜底）。详见「四引擎协作」章节。
---

# China Briefing — 多尺度中文资讯简报

## ⚠️ 规则优先级（冲突时按此顺序裁决）

1. **安全底线** — 绝不虚构数据，必须用检索工具（wb2a / Exa / Tavily / Firecrawl 四引擎协作 / 腾讯新闻 CLI）获取实时信息
2. **结构完整性** — 必须包含所有必填板块（见简报结构），不可省略
3. **来源可信度** — 每个事实标注来源媒体 + URL，**URL 用超链接形式 `[媒体名](URL)`，不贴裸网址**
4. **内容质量** — 字数、角度、反注水（见质量门禁）
5. **风格优化** — 嘟嘟点评的深度与视角

---

## 核心能力

**任意尺度，一处生成：**
- 全球 → 区域（亚太/欧洲/中东） → 国家 → 省 → 市 → 区 → 街道 → 社区
- 每层自动选择匹配的搜索源（见 `references/search-sources.md`、`references/international-sources.md`）

---

## 📐 两种输出模式（2026-10-29 主人选定 A 型为主）

### A 型 · 快讯模式（**默认**，3 分钟读完 / 800~1000 字）

**目标**：3 分钟知道「今天世界发生了什么、跟我有什么关系」，**但板块齐全，一块不删**。

**结构（六段全保留，逐段压紧）**：

```
① 核心结论      50~80 字：今天的主线 + 为什么重要
② 头条 ×3       每条 = 事实（含来源超链接）+ 嘟嘟点评（判断要狠）
③ 分类热点      表格：领域 | 事件（4~6 行，一行一件事，不解释）
④ 数据看板      表格：指标 | 数值（4~6 行，必须是具体数字）
⑤ 行动建议      表格：优先级 | 建议 | 适用人群（4~5 行）
⑥ 时间窗口      诚实标注覆盖区间（Tavily 日期是软过滤，不得伪装"今日"）
```

**A 型 = 满版但紧，不是删版但短**：

- ✅ 六个板块一个都不少
- ✅ 总量 **800~1000 字**：低于 800 说明信息不足，高于 1000 说明没压紧
- ✅ 点评以判断为主，不复述事实；**每条点评 ≤60 字**
- ✅ 分类热点每行只写一件事，不展开
- ✅ 数据看板只留"能说明问题"的数字，不堆砌
- ❌ 禁止注水词；禁止"值得关注 / 影响深远 / 需持续观察"这类无法被反驳的空判断

**判断句及格线**：

| ❌ 正确但无用 | ✅ 可被反驳 |
|---|---|
| 「这值得关注」 | 「这个数字会在 11 月 3 日之后立刻变，因为……」 |
| 「影响深远」 | 「真正的瓶颈不是算力，是供电」 |
| 「需持续观察」 | 「如果 X 一周内没发生，说明 Y 判断错了」 |

### B 型 · 深挖模式（按需触发）

**触发**：「展开讲讲」「为什么」「给我细一点的」。

在 A 型六段基础上**纵向扩写**（1500 字以上）：每条头条补背景链路、多方观点、时间线；数据看板扩到 8~10 项并注明口径；来源列全并标立场。

---

## 步骤 1：确定尺度并搜索

### 强制规则

1. **必须**调用检索工具搜索实时数据：**四引擎按环节协作**：中文发现 wb2a、国际发现 Exa+Tavily 双源、正文 wb2a --fetch 免费优先、Firecrawl 仅硬反爬；关键事实须两家交叉；`free_search` 仅全失败兜底（禁止仅凭已有知识生成）
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
> 💡 **最省事（新首选）**：`python3 .local/scripts/tavily-search.py "..." -n 8 -d 1 --depth advanced` 做发现 → `python3 .local/scripts/exa-search.py --url "<URL>"` 取正文。两者质量都高于 `free_search__research`（免 Key 蹭 SERP，5 条里常只 1 条真文章、score 全是 0.01639）。

### 🧠 语义检索与正文提取：Exa（2026-10-29 新增）

> **两个用途**：① **语义检索**——"找某主题的相关报道/资料/长文"，比关键词更准；② **正文提取**——对反爬站点用 Exa 的索引拿正文，绕开 Cloudflare/付费墙的硬拦。
> 官方每月约 $10 免费额度。

```sh
python3 .local/scripts/exa-search.py "主题描述" -n 8 --days 7 --text   # 语义检索（带正文摘要）
python3 .local/scripts/exa-search.py --url "<文章URL>"                 # 取正文（走缓存，推荐）
python3 .local/scripts/exa-search.py --url "<文章URL>" --live          # 强制实时抓取（失败自动回退缓存）
python3 .local/scripts/firecrawl-scrape.py "<文章URL>"                 # Exa 拿不到时的备份（1 credit/页，仅 markdown）
```

**能力矩阵（2026-10-29 实测）**：

| 站点 | 走缓存取正文 | 强制实时 |
|---|---|---|
| AP / BBC / Guardian / Economist | ✅ | ✅ |
| **Reuters** | ✅ | ❌ `CRAWL_HTTP_401` |

> Reuters 强制实时会被拒，但缓存能拿到正文——**脚本已自动回退，无需手工切换模式**。

**取源分工（四层，按成本从低到高）**：

| 需求 | 用谁 | 成本 |
|---|---|---|
| 全球新闻**发现**（主力） | **Exa + Tavily**（双源） | Exa 权威原站+date；Tavily 通讯社+精确时间 |
| 某主题的深度资料 / 长文 | **Exa 语义检索** | $4/1k 次 |
| **正文提取（日常首选）** | **Exa `--url`** | **$1/1k 页 ← 最便宜** |
| 正文提取（Exa 拿不到 / JS 渲染 / 硬反爬） | **Firecrawl**（仅 markdown） | 1 credit/页 |
| 国内热点 | 腾讯新闻 CLI | 免费 |
| 兜底 | `free_search` | 免费（质量差） |

> 四层都不可用时，才允许"只取标题+摘要"，并须在来源里注明。

### 💰 免费额度守则（只白嫖，收费即停）

| 引擎 | 免费额度 | 折算 | 账户实测 |
|---|---|---|---|
| Tavily | **1,000 credits/月** | ≈ 1,000 次 basic / 500 次 advanced | 套餐 `Researcher`，已用 19/1,000，`paygo_limit: null`（未开按量付费） |
| Exa | **$10/月**（首月 +$10） | ≈ 2,500 次搜索 / **10,000 页正文** | 无用量接口，需看 dashboard |
| Firecrawl | **1,000 credits/月** | ≈ 1,000 页 / 5,000 条搜索结果 | 剩余 1,017，周期 10-29→11-29 |

**硬性禁止（会快速烧额度）**：

1. ⛔ **Exa Agent 端点** —— 单次 $0.012–$1.00，`auto` 模式上限 $5/次，两次就烧光一个月。
2. ⛔ **Firecrawl 的 JSON / Question / Highlight 格式** —— 各 **+4 credits/页**（一页从 1 变 5）。要结构化数据，先抓 markdown 自己解析。
3. ⛔ **拿 Firecrawl 试错 URL** —— **403/404 的页面照样扣 1 credit**。
4. ⛔ **Firecrawl `/crawl` 整站爬** —— 几秒烧掉几百 credits。
5. ⛔ **给任何一家绑卡 / 开 PAYG** —— 不绑卡时额度用完就是报错（402/429），不会静默扣费；绑了才会真扣钱。

**安全边界**：三家都"无需信用卡"。只要不绑卡，超额即失败，账上不会出钱。


### 🤝 四引擎协作矩阵（2026-11-18 定案：按能力分工，非排队降级）

**原则**：四家强弱互补，不在一条线上——不排队等前一个挂才换，而是按岗位同时参与，关键事实双源交叉。但**不是每条都调四个**（控成本、控速度）：发现阶段按语种各派 2 家，正文阶段免费优先，Firecrawl 只在硬反爬出场。

| 环节 | 主用 | 辅用 | 说明 |
|---|---|---|---|
| 中文发现 | **wb2a** | Exa | wb2a 免费+权威中文源+长正文；Exa 补语义 |
| 国际/英文发现 | **Exa** | Tavily | 两家不同源，正好满足「≥2 家通讯社」门禁 |
| 中文视角补充 | wb2a | — | 英文查询 wb2a 只回中文转述，仅作补充不作国际主源 |
| 正文抓取 | **wb2a --fetch** | Exa --url → Firecrawl | 免费先上；Exa $1/1k 页；Firecrawl 仅硬反爬、403/404 也扣费 |
| 关键事实交叉验证 | 任意两家不同源 | — | 同一事实两家原文印证才写进头条；单源标「待交叉核实」 |

**成本/速度护栏**：发现阶段每期中文线 2 家 + 国际线 2 家即可（不是 4 家全开）；正文能免费就免费；Firecrawl 每次 1 credit、不试错 URL、不整站 crawl；关键数字至少双源，普通条目单源即可。

### 🌍 全球源发现：Exa 主 / Tavily 二备（2026-11-18 按语种分派）

> **定位**：**国际/英文**发现以 Exa 为主（权威原站 + 独立 date + 快 1.4s），Tavily 二备；wb2a 英文查询只返回中文媒体转述（搜狐等），仅作中文视角补充。中文发现另见下节（wb2a 主力）。
>
> ⚠️ 2026-10 曾因**出口 IP 被 api.tavily.com 整站 403** 而停用（与 Key 无关）；2026-10-27 出口 IP 变更为 `47.245.100.81` 后封锁解除，**实测恢复可用**。

```sh
python3 .local/scripts/exa-search.py "英文查询" -n 8 --text   # 国际主力
python3 .local/scripts/tavily-search.py "查询词" -n 8 -d 1        # 国际第二源
# wb2a 英文只回中文转述，国际线最多补 1 次作中文视角，不作主源
```

| 参数 | 说明 |
|---|---|
| `-n` | 返回条数（≤20） |
| `-d` | 仅看近 N 天（`--topic news` 时生效） |
| `--depth` | `basic` / `advanced`（advanced 摘要更完整） |
| `--topic` | `news`（默认，按新闻检索）/ `general` |

输出：标题 / 来源域名 / 日期 / 摘要 / 链接 + 末尾「含日期 N 条」。

**不经 MCP**：直调 REST，Key 在 `.local/secrets/tavily-api-key.txt`（0600）。旧 tavily MCP 是 `npx -y …@latest` + root + 真 Key，供应链面太大，已下线不再启用。

**全球简报的取源顺序**：

1. **Exa**（`python3 .local/scripts/exa-search.py "英文查询" -n 8 --text`）拿权威原站 + date；二备 Tavily（`tavily-search.py -n 8 -d 1`）；要中文视角再补 wb2a
2. 挑 **3~5 家不同立场**媒体（≥2 家通讯社）
3. 需要正文时**首选 `wb2a-search.py --fetch '<URL>'`（免费，实测 gov.cn 14622 字）**；次选 `exa-search.py --url`（$1/1k 页）；再 `firecrawl-scrape.py`（1 credit/页，硬反爬）；都失败才 `free_search__fetch` 直连；同一关键事实至少两家不同源印证才进头条
4. **兜底**：wb2a / Exa / Tavily / Firecrawl 全不可用 → 退回 free_search + 直连抓首页

### 🇨🇳 中文源发现（2026-11-04 改版：Exa 为主）

> **现状（两个中文源都废了）**：
> - `tencent-news-cli`：免费积分耗尽，`code:4007 积分余额不足`，`hot / search / morning / evening / jiaozhen` **全部不可用**（按「收费就停」不买积分包）
> - `free_search` 中文：baidu 只回栏目页、sogou 返回 2024 年旧闻、so360 零贡献 → **不可作为中文信源**
>
> ✅ **中文发现主力 = wb2a**（2026-11-18 实测定案）：中文查询返回人民网 / 中新网 / 央视网 / 中国政府网等权威源当日报道，带长正文、免费、复用 yaner key。注意：① 只认 `{query,max_results}`，脚本已去掉无效 model 参数；② 默认带 `deepseek-harness` UA 触发 DSH 兼容层补 date 键（值可能为 null，真实日期从 URL 如 `2026/11/18` 或正文读取）；③ 国际英文别用 wb2a（会返回中文自媒体），走 Exa/Tavily。

**主路径**：

```sh
python3 .local/scripts/wb2a-search.py "今天国内重要新闻" -n 8   # 主力
python3 .local/scripts/wb2a-search.py "城市名 + 主题"      -n 5
python3 .local/scripts/wb2a-search.py "行业关键词 最新"      -n 5
# 后备：python3 .local/scripts/exa-search.py "同查询" -n 8 --days 1 --text
```

**按尺度**：

| 尺度 | 查询式 | 参数 |
|---|---|---|
| 全国 | 「今日 国内 政策 民生」 | `-n 8 --days 1` |
| 省市 / 区县 | 「城市名 + 主题」 | `-n 5 --days 7` |
| 行业 / 垂直 | 「行业关键词 最新」 | `-n 5 --days 7` |

**降级链（遇错立即换，不重试）**：

```
① wb2a 中文检索       → 主路径
② Exa 中文检索        → 后备（-n 8 --days 1 --text）
③ 直连国内源首页       → 新华网 / 人民网 / 央视网 / 澎湃（free_search__fetch）
③ ddgs（免 Key）      → 「具体查询」兜底，如「寒潮 辽宁 预警 2026年11月」
                         ✅ 实测能拿到当天 15:52 的地方气象预警（带时间、带原文）
                         ❌ 宽泛查询（「今天国内重要新闻」）只回栏目页 → 不可用于发现
                         `python3 .local/scripts/ddgs-search.py "查询" -n 5 --days 7`
④ free_search         → 仅英文可用；中文结果不得作为信源
⑤ tencent-news-cli    → ⛔ 已停用；遇 code:4007 直接跳过，不重试、不在简报里刷错误
```

> **ddgs 与 free_search 的分工**：ddgs 走 DuckDuckGo 官方库（解析稳定、有 retry），free_search 是抓 SERP 的免 Key 聚合器（中文引擎大半熔断、返回旧闻）。**具体事实类查询优先 ddgs**；宽泛新闻发现两者都不行，只能靠 Exa。

**⚠️ 分工**：Exa 负责发现与语义检索；正文用 `exa-search.py --url`（$1/1k 页），拿不到再 `firecrawl-scrape.py`。**不得只用单一来源。**

**⛔ 查证能力说明**：`jiaozhen` 随腾讯新闻一并停用。争议/健康/谣言类说法改为「Exa 或 Firecrawl 拉原文 → 人工比对口径 → 在头条里标注限定条件（如"已发布未施行"/"局部非全线"）」。

### 🔬 科技 / 行业专线（2026-10-29 新增）

**触发**：「科技简报」「AI 周报」「半导体 / 机器人 / 芯片新闻」「某个技术领域最近有什么进展」。

**与常规简报的区别**：科技新闻时效独特、判据不同（看技术路线与量产节奏，而非舆论热度），因此**独立选题**，不塞进时政简报。

**信源白名单（必须锁域名，否则会混进 PR 稿与聚合站）**：

```
arstechnica.com,theverge.com,techcrunch.com,technologyreview.com,
wired.com,reuters.com,nikkei.com,cnbc.com
```

**流程**：

```sh
# 1) 发现（锁定白名单，近 3 天）
python3 .local/scripts/tavily-search.py "AI chip semiconductor robotics" -n 8 -d 3 --depth advanced \
  --domains arstechnica.com,theverge.com,techcrunch.com,technologyreview.com,wired.com,reuters.com,nikkei.com,cnbc.com

# 2) 需要正文的 2~3 篇：wb2a --fetch 免费抓（首选）；Exa 取全文（$1/1k 页，次选）
python3 .local/scripts/exa-search.py --url "<URL>"

# 3) 涉及具体数字（算力/制程/价格/出货量）时：查证并标注口径
tencent-news-cli jiaozhen --query="<具体说法>"
```

**输出结构**（沿用简报骨架，分类换成技术线）：

```
核心结论 → 3 头条（含点评）→ 技术分类（AI 模型 / 芯片制程 / 机器人 / 终端与生态）
→ 数据看板（制程、算力、出货量、价格、发布时间）→ 行动建议（看/等/避）
```

**纪律**：

- ❌ 不用 PR 稿站（newsfilecorp / prnewswire / globenewswire）当信源，只能当线索
- ❌ 不把"厂商发布"写成"行业突破"，标题必须区分「发布 / 量产 / 送样 / 路线图」
- ✅ 涉及"超越 / 首次 / 第一"的表述必须查证；查不到就降级为"据厂商称"
- ✅ 至少 1 条来自**非厂商**的第三方报道或分析

**成本**：一期约 Tavily 8 credits（advanced）+ Exa 2~3 页（$0.003）+ 查证免费。

### 🔍 头条查证（推荐，3 条头条至少查 1 条）

```sh
tencent-news-cli jiaozhen --query="<待查证的说法>"
```

返回：**查证结论 / 查证过程 / 信心分(满分10) / 来源链接**。

**执行标准**：

- 头条涉及**健康、谣言、争议数据、单一来源爆料**时 → 逐条查证
- 结论为「尚无定论」或信心分 < 6 → 头条中必须标注 `⚠️ 该说法存在争议`
- 纯事件报道（某地发生地震）、纯官方数据发布 → 可跳过查证

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

- **free_search__search 超时/失败** → 重试 1 次；仍失败改用 `free_search__research` 或 `free_search__fetch` 直连抓取新闻源首页（2026-10-04 实测可直连：bbc.com / aljazeera.com / cnn.com / dw.com / cna.com.tw / 8world.com / apnews.com / ft.com）
- **某尺度搜索返回 0 结果** → 放宽到相邻更大尺度（街道无结果→搜区级；区级无→市级）
- **搜索引擎整体不可用**（如出口 IP 被限流）→ 退回 `free_search__fetch` 直连抓取新闻源首页；若直连也不通，再用记忆中的最近已知信息并标注"数据来源：历史缓存"
- **⚠️ Reuters 与 Bloomberg 有强反爬** → 直连 `fetch` 只会拿到 `Access Denied` / `Are you a robot?` 拒绝页（**浏览器渲染也绕不过**，2026-10-04 实测）。这两家**只用 `search` / `research` 取标题与摘要，不要依赖直连正文**；需要正文时换 bbc.com / aljazeera.com / apnews.com / dw.com 等。
- **浏览器（Chromium）状态**：已安装于持久盘 `.local/ms-playwright`（658M），由启动脚本导出 `PLAYWRIGHT_BROWSERS_PATH` 指向它。若仍报 `Chromium browser is not installed`，说明 MCP 进程需重启 —— 该判定是**粘性缓存**（失败一次后本进程永久标记不可用）。
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
5. **来源必须完整**：❌"来源：网络" → ✅"来源：[媒体名](URL)"（超链接，不贴裸网址；代码块/命令行内除外）

---

## 🔒 质量门禁（生成后自动检查）

执行 `references/quality-gate.md` 中的实现，逐条检查：

1. 字数 ≥ 800
2. 头条数 = 3（或允许的 2 条+标注）
3. 每条头条包含嘟嘟点评
4. 每个信息来源标注完整，且以 `[媒体名](URL)` 超链接呈现
5. 无注水词
6. 行动建议表非空
7. **争议/健康/谣言类头条已查证** —— 用 `tencent-news-cli jiaozhen --query=` 核过；结论为「尚无定论」或信心分 < 6 的，已标注 `⚠️ 该说法存在争议`
8. **国内/本地简报不得只用单一信源** —— 腾讯新闻 CLI 只作发现入口，关键事实需 ≥2 家来源交叉

**结果判定：**
- 全部通过 → 交付
- 1-2 项不达标 → 修正该部分后交付
- 3 项及以上不达标 → 退回重新生成

---

## 🔧 搜索工具配置

**主用工具（按优先级）**：① `tavily-search.py`（新闻发现）② `exa-search.py`（语义检索 / 正文提取）③ `firecrawl-scrape.py`（硬反爬全文）④ `tencent-news-cli`（国内源）；`free_search`（MCP，免 Key）仅作最后兜底。三者均需 Key，存 `.local/secrets/`（0600）。

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
