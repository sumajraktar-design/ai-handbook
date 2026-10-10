---
id: prompt-engineering
title: "提示词工程"
en: "Prompt Engineering"
group: app
priority: high
related: [system-prompt, structured-output, evals, reasoning-models, context-engineering]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 提示词工程

> 通过设计输入内容，让模型输出更准确、更符合需求的结果。

**分组**：应用开发 · **重要程度**：开发者必知

## 详细讲解

模型的输出高度依赖输入。同样的模型，提示词写得好坏，效果可能天差地别。提示词工程是做 AI 应用时投入最小、回报最大的技能。

最重要的原则是"像给一位聪明但不了解情况的新同事交代任务"：说清楚背景（这是什么项目、给谁用）、目标（要达成什么）、约束（字数、格式、语气、不要做什么）以及判断标准（什么样算好）。

常用技巧：给示例（Few-shot，展示一两个输入输出的样例）；要求先分步分析再下结论（思维链，Chain of Thought）；用 XML 标签或分隔符把指令、资料、问题分开；指定输出格式；给模型一个"不知道就说不知道"的出口；复杂任务拆成多步，每步一次调用（提示链）。

提示词需要迭代：写一版 → 用一批测试问题跑 → 看哪里不好 → 修改。这就要用到评测。

## 打个比方

给装修师傅交代需求：只说"装好看点"，结果全凭运气；说清楚风格、预算、哪面墙要放书架，结果才可控。

## 开发者要注意

- 提示词也是代码，建议放进版本控制，每次修改都跑一遍评测。
- 解释"为什么"比只下命令更有效，模型能据此推断边界情况。

## 相关概念

- [System Prompt 系统提示词](./system-prompt.md)
- [结构化输出](./structured-output.md)
- [评测](./evals.md)
- [推理模型](./reasoning-models.md)
- [上下文工程](./context-engineering.md)
