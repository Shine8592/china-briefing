# 📰 China Briefing — Multi-scale Chinese News Briefing v4 · Four-Engine Collaboration

> **Version:** v4.0 (2026-11-18) — upgraded from a single engine / linear fallback chain to a **four-engine, role-based collaboration** with **two-source cross-verification** for key facts.

A multi-scale Chinese news briefing skill. Generate a structured, sourced, insight-rich briefing for any geographic scope — from a single street neighborhood to the whole world.

---

## ✨ What's New in v4.0: Four-Engine Collaboration Matrix

**Core idea**: the four search engines have complementary strengths and are not on a single axis. Instead of waiting for one to fail before falling back, each engine **holds its own role by stage**, and key facts are **cross-checked by two independent sources**. It does **not** call all four for every query — calls are precise per scenario to control cost and latency.

| Stage | Primary | Secondary | Notes |
|---|---|---|---|
| Chinese-language discovery | **wb2a** | Exa | wb2a: free, authoritative Chinese sources, long snippets; Exa adds semantic search |
| International / English discovery | **Exa** | Tavily | Two distinct sources naturally satisfy the "≥2 news agencies" gate |
| Chinese-perspective supplement | wb2a | — | For English queries wb2a returns Chinese-language paraphrases; supplement only, never the primary international source |
| Full-text extraction | **wb2a `--fetch`** | Exa `--url` → Firecrawl | Free first; Exa \$1/1k pages; Firecrawl only for hard anti-bot, even 403/404 costs 1 credit |
| Key-fact cross-verification | any two distinct sources | — | A fact enters a headline only when two sources confirm it; single-source items are marked "pending cross-check" |

**Engine capability comparison (measured 2026-11-18)**

| Engine | Chinese discovery | International English | Full text | Native date | Cost |
|---|---|---|---|---|---|
| **wb2a** | ★★★ | ★ (Chinese paraphrase) | ★★★ free | needs DSH UA, may be null | Free |
| **Exa** | ★★ | ★★★ authoritative originals | ★★ | Yes | \$4/1k searches, \$1/1k pages |
| **Tavily** | ★ | ★★★ agencies + precise time | ★ snippets only | GMT timestamp | 1–2 credits/call |
| **Firecrawl** | — | — | ★★★ only solution for hard anti-bot | — | 1 credit/page |

**Cost / speed guardrails**

- Per issue: 2 engines for the Chinese line + 2 for the international line — **do not open all four**
- Prefer free full-text extraction (wb2a `--fetch`); Firecrawl only for hard anti-bot cases
- ⛔ Never probe URLs with Firecrawl (403/404 still costs a credit); never run `/crawl` site-wide
- Key figures need at least two sources; ordinary items can be single-source

> 📌 **Key lesson**: writing a consistent "signal" into the docs is more effective than hard constraints. Contradictory instructions (an earlier version said both "wb2a is the global primary" and "wb2a is only an international supplement") pushed the executing model toward the free, all-purpose engine. v4.0 removed the contradictions; three measured runs then converged naturally on the correct split.

---

## ✨ Inherited Capabilities (v3.0 and earlier)

| Capability | Description |
|---|---|
| 🔒 Rule priority ordering | Safety > structural integrity > source credibility > content quality > style |
| 🔍 Scale-bound search | Global → multi-source multi-line; district/street → specific queries |
| 🧪 Unified quality gate | Standalone `references/quality-gate.md`, single source of truth |
| 🔐 No hardcoded keys | Keys never committed; use provider config / environment variables |
| 📚 Separated source libraries | International and all-scale sources in separate docs |
| 🎯 User-interest integration | Semantic memory expands search terms (housing, jobs, social security, prices, policy, etc.) |

---

## 📂 Project Structure

```
china-briefing/
├── SKILL.md                          # Main skill definition (rules + flow + four-engine matrix)
├── README.md                         # Chinese documentation
├── README_EN.md                      # This file
├── _meta.json                        # Skill metadata
├── config.example.yaml               # Config template
├── config/
│   └── detailed_mode.json            # Detailed-mode config
├── references/
│   ├── formatting.md                 # Commentary style guide
│   ├── international-sources.md      # International source library
│   ├── quality-gate.md               # Quality gate (single source of truth)
│   ├── search-sources.md             # All-scale search source library
│   ├── search-templates.md           # Search templates
│   ├── source-library.md             # News source library
│   ├── user-interest-integration.md  # User-interest integration
│   ├── tavily-setup.md               # [Deprecated] Tavily setup (archived)
│   └── tavily-usage.md               # [Deprecated] Tavily usage (archived)
└── scripts/
    ├── briefing_helper.py
    ├── briefing_helper_enhanced.py
    ├── personal_briefing.py
    ├── quality_gate.py
    └── server_cleanup.py
```

---

## 🔧 Installation

**Requirements**

- QwenPaw / Hermes Agent (with Skill tool support)
- Search engines you actually have configured (not all four are mandatory):
  - **wb2a / Exa / Tavily / Firecrawl** scripts or MCP tools
  - wb2a reuses the `yaner` provider API key; endpoints `POST https://token.yaner.fun/v1/search` and `POST /v1/fetch` (passthrough to Tencent CodeBuddy agenttool; queries are free)
  - Exa / Tavily / Firecrawl keys go through environment variables or `config.yaml` — **never commit plaintext**

```bash
# Place the skill in your workspace
cp -r china-briefing <workspace>/skills/

# Keep private config local only; never commit
cp config.example.yaml config.yaml   # then fill in your own keys (excluded by .gitignore)
```

---

## 🚀 Usage

Just state your request:

```
Give me today's global briefing
What's happening in China today
Recent news about Jiangchuan Road neighborhood
Latest updates in the AI industry
```

The skill automatically:
1. Determines the geographic scale and search lines (Chinese / international)
2. Calls search engines per the four-engine matrix (role-based, two-source cross-check for key facts)
3. Generates a structured briefing
4. Runs the quality gate
5. Delivers the final briefing

---

## 📋 Output Format

- 📌 **Core Conclusion** — 1–2 sentence overview (required)
- 📌 **Top Headlines** — 3 headlines with commentary (required; each with fact + source link + commentary)
- 📌 **Categorized Hotspots** — 2–4 categories (required)
- 📌 **Data Dashboard** — key figures (optional)
- 📌 **Action Recommendations** — priority table (required)
- 📌 **Time Window** — honestly state the coverage range; never disguise multi-day content as "today"

Sources use `[Media Name](URL)` hyperlinks, never bare URLs; media names in Chinese translation.

---

## 🔒 Version History

| Version | Date | Notes |
|---|---|---|
| **v4.0** | 2026-11-18 | Four-engine collaboration matrix: wb2a/Exa/Tavily/Firecrawl by stage, two-source cross-verification, cost/speed guardrails; removed contradictory wording |
| v3.1 | 2026-10-04 | Search backend switch: web_search/tavily → free_search MCP |
| v3.0 | 2026-07-01 | Architecture refactor: rule priority, scale binding, fallback, unified quality gate, key cleanup |
| v2.0 | 2026-05 | Stronger quality gate: auto checks, source diversity, anti-padding |
| v1.0 | 2026-04 | Initial release: multi-scale briefing generation |

---

## 🔐 Security

- **Never commit plaintext keys to a public repo** — all keys go through provider config or environment variables
- `config.yaml`, `.env`, `*_api_key*`, `*_secret*` are all excluded by `.gitignore`
- The wb2a endpoint reuses existing provider credentials; no new on-disk keys
- Third-party search services (including Tencent CodeBuddy agenttool) are unofficial channels; stability depends on their upstream. The skill keeps `free_search` as a last-resort fallback.

## 📜 License

MIT License

---

> 🌸 By Dudu — making every briefing carry real depth
