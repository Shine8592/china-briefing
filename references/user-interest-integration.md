# User Interest Integration for China Briefing

This document describes how the china-briefing skill incorporates the user's stated interests (housing, employment, social security, prices, policies, skill upgrades) into the search term generation process.

## Workflow
1. **Determine Scale & Base Terms** – As per the skill's usage flow, the agent first identifies the geographic scope (global, national, provincial, municipal, district/street, etc.) and drafts a base search query (e.g., "上海 最新 新闻").
2. **Retrieve User Interests** – The agent consults its persistent memory (via the semantic-memory-auto skill or direct memory recall) for the user‑interest entry:
   ```
   用户对住房、就业、社保、物价、政策、技能提升有兴趣；偏好性价比优先、经久耐用、不伤害身体的消费。
   ```
3. **Expand Query** – Each interest keyword is appended to the base term to generate a set of focused queries, e.g.:
   - 上海 最新 新闻 住房
   - 上海 最新 新闻 就业
   - 上海 最新 新闻 社保
   - 上海 最新 新闻 物价
   - 上海 最新 新闻 政策
   - 上海 最新 新闻 技能提升
   The base query itself is also retained to ensure broad coverage.
4. **Execute Searches** – The expanded query list is fed to the Tavily API (via web_search) to collect real‑time sources.
5. **Synthesis** – Results are filtered, deduplicated, and woven into the briefing sections, ensuring that at least one source per interest area appears when available.

## Benefits
- Increases relevance of generated briefings to the user's personal concerns without requiring the user to restate interests each time.
- Aligns with the skill’s requirement to “调用语义记忆获取用户兴趣偏好” while keeping the core search‑and‑report pipeline unchanged.

## Maintenance
- If the user’s interests change, update the corresponding memory entry (via the memory tool) – the china-briefing skill will automatically pick up the new terms on the next run.
- No changes to the skill’s core logic are needed; only the memory entry drives the dynamic query expansion.
