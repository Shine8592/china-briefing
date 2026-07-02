# 质量门禁（单一实现源）

SKILL.md 引用此文件作为质量检查的唯⼀权威实现。所有检查逻辑统一在此维护。

## 检查清单

```python
def quality_gate(briefing_text: str) -> list[str]:
    \"\"\"生成后强制检查，返回所有不达标项。空列表=通过。\"\"\"
    errors = []

    # 1. 字数检查
    if len(briefing_text) < 800:
        errors.append(f"字数不足（{len(briefing_text)}/800），补充内容")

    # 2. 头条数量检查
    headline_count = briefing_text.count('**头条')
    if headline_count < 2:
        errors.append(f"头条数不足（{headline_count}），至少需要 2 条")
    elif headline_count != 3:
        errors.append(f"头条数={headline_count}（标准为 3），已标注信息足以交付")

    # 3. 嘟嘟点评检查
    if '**嘟嘟点评:**' not in briefing_text and '嘟嘟点评' not in briefing_text:
        errors.append("缺少嘟嘟点评，补充观点")

    # 4. 来源标注检查
    if 'https://' not in briefing_text:
        errors.append("缺少来源 URL，补充链接")
    if '来源' not in briefing_text:
        errors.append("缺少来源标注，补充媒体名称")

    # 5. 行动建议检查
    if '行动建议' in briefing_text:
        section = briefing_text.split('行动建议')[1][:200]
        if not any(m in section for m in ['高', '中', '低']):
            errors.append("行动建议表为空，补充至多 1 行建议")

    # 6. 注水词检查
    water_words = ['暂无', '敬请期待', '持续关注', '暂无数据', '不予置评']
    for ww in water_words:
        if ww in briefing_text:
            errors.append(f"发现注水词「{ww}」，重写该部分")

    return errors
```

## 判定规则

| 不合格项数 | 处理方式 |
|-----------|---------|
| 0 | ✅ 交付 |
| 1-2 | ⚠️ 修正不合格项后交付 |
| 3+ | ❌ 退回重新生成 |

## 使用方式

```python
errors = quality_gate(briefing)
if not errors:
    print("✅ 质量达标，可交付")
else:
    for e in errors:
        print(f"  - {e}")
    if len(errors) >= 3:
        print("❌ 退回重新生成")
    else:
        print("⚠️ 修正后交付")
```
