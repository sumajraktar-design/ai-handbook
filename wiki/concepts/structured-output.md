---
id: structured-output
title: "结构化输出"
en: "Structured Output"
group: app
priority: high
related: [tool-use, prompt-engineering, hallucination]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 结构化输出

> 让模型按照固定格式（通常是 JSON）输出，方便程序直接解析使用。

**分组**：应用开发 · **重要程度**：开发者必知

## 详细讲解

模型默认输出自由文本，程序很难可靠地从中提取信息。结构化输出让模型按照你定义的结构返回数据，比如 {"sentiment":"positive","score":0.9}。

实现方式有几种可靠程度：在提示词里要求输出 JSON（最简单，但偶尔格式出错）；利用工具调用，把想要的结构定义成工具参数（模型会按参数结构填写）；使用 API 提供的结构化输出功能，按 JSON Schema 强制约束生成，可靠性最高。

即使格式正确，内容仍可能有误（比如分类判断错误），所以程序拿到数据后仍应做校验，例如 Python 里用 Pydantic 校验字段类型和取值范围。

## 打个比方

让人填一张表格，而不是写一篇作文：每一栏要填什么都规定好了，收回来直接录入系统。

## 开发者要注意

- 前后端对接 AI 时几乎必用。
- Python 里可以用 Pydantic 定义模型类，再转换成 JSON Schema 交给 API。
- 字段名和描述写清楚，模型会参考描述来填写。

## 代码示例

```python
from pydantic import BaseModel

class Review(BaseModel):
    sentiment: str   # positive / negative / neutral
    score: float     # 0 到 1
    keywords: list[str]

# 把 Review 的 JSON Schema 交给 API 的结构化输出 / 工具参数，
# 拿到结果后再校验一次：
data = Review.model_validate_json(model_output)
```

## 相关概念

- [Tool 工具调用](./tool-use.md)
- [提示词工程](./prompt-engineering.md)
- [幻觉](./hallucination.md)
