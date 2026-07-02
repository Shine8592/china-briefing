# 📰 China Briefing — 多尺度中文资讯简报 v3.0

> **升级版本：** 2026-07-01 — 架构重构，搜索精细化，质量门禁标准化

多尺度中文资讯简报技能，从一条街道到全球，任意地理范围均可生成。

## ✨ 新版本亮点 (v3.0)

| 改进项 | 说明 |
|--------|------|
| 🔒 **规则优先级排序** | 安全底线 > 结构完整性 > 来源可信度 > 内容质量 > 风格优化，冲突时有据可依 |
| 🔍 **搜索参数与尺度绑定** | 全球→`advanced/10条`，区县/街道→`basic/5条`，每层自动匹配搜索深度 |
| ⚙️ **故障回退机制** | 超时重试 → 放宽尺度 → 历史缓存，三级保障 |
| 🧪 **质量门禁归一化** | 代码内联 → 独立 `references/quality-gate.md`，单⼀实现源，统一引用 |
| 🔐 **API 密钥硬编码清理** | 所有明文密钥已移除，统一走环境变量和 `config.yaml`，安全合规 |
| 📚 **搜索源库分离** | 旧版内联 → 独立 `references/international-sources.md` + `search-sources.md` |
| 🎯 **用户兴趣集成** | 通过语义记忆自动扩展搜索词（住房、就业、社保、物价、政策、技能提升） |

## 📂 项目结构

```
china-briefing/
├── SKILL.md                       # 主技能定义（规则+流程）
├── README.md                      # 本文件
├── _meta.json                     # 技能元数据
├── config.example.yaml            # 配置模板
├── references/
│   ├── formatting.md              # 嘟嘟点评格式规范
│   ├── international-sources.md   # 国际新闻来源库
│   ├── quality-gate.md            # 质量门禁（单一实现源）
│   ├── search-sources.md          # 全尺度搜索源库
│   ├── tavily-setup.md            # Tavily API 配置指南
│   ├── tavily-usage.md            # Tavily API 使用参考
│   └── user-interest-integration.md  # 用户兴趣集成文档
└── config/
    └── detailed_mode.json         # 详细模式配置
```

## 🔧 安装

### 环境要求
- [Tavily API Key](https://app.tavily.com/)（免费：1000次/天）
- Hermes Agent

### 安装步骤

```bash
# 1. 将技能目录放入 Hermes skills 目录
cp -r china-briefing ~/.hermes/skills/

# 2. 配置 Tavily API Key（二选一）
# 方式 A：环境变量（推荐）
echo 'TAVILY_API_KEY="your-key"' >> ~/.hermes/.env

# 方式 B：配置文件
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入密钥
```

## 🚀 使用

生成简报时直接告诉需求：

```
# 全球简报
给我今天的全球简报

# 国内简报
今天国内有什么大事

# 本地简报
江川路街道最近有什么新动态

# 行业简报
AI 行业最新动态
```

技能自动：
1. 确定地理尺度和搜索词
2. 用 `web_search`（Tavily）搜索实时资讯
3. 生成结构化简报（核心结论 + 3条头条 + 分类热点 + 行动建议）
4. 执行质量门禁检查
5. 交付最终简报

## 📋 输出格式

📌 **核心结论** — 1-2句总览（必填）
📌 **头条速报** — 3条头条 + 嘟嘟点评（必填）
📌 **分类热点** — 2-4大类（必填）
📌 **数据看板** — 关键数据（可选）
📌 **行动建议** — 优先级表格（必填）

## 🔒 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0 | 2026-07-01 | 架构重构：规则优先级排序、搜索参数绑定、故障回退、质量门禁归一化、API密钥清理 |
| v2.0 | 2026-05 | 强化质量门禁系统：引入自动检查、来源多样性规则、反注水机制 |
| v1.0 | 2026-04 | 初始发布：支持多尺度简报生成 |

## 🔐 安全说明

- **不提交明文密钥到公开仓库** — API 密钥通过 `~/.hermes/.env` 或 `config.yaml` 单独配置
- `config.yaml` 和 `.env` 已被 `.gitignore` 排除
- 所有引用外部配置文件中的敏感信息均已移除

## 📜 许可证

MIT License

---

> 🌸 嘟嘟出品 — 让每条简报都有深度
