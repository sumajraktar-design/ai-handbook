---
id: alignment
title: "对齐"
en: "Alignment"
group: train
priority: medium
related: [rlhf, constitutional-ai, prompt-injection]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 对齐

> 让 AI 的行为符合人类的意图和价值观：有帮助、诚实、不造成伤害。

**分组**：训练与对齐 · **重要程度**：很常见，要懂

## 详细讲解

一个只会预测下一个词的模型，并不天然知道人类想要什么。它可能照着用户字面意思做了事，却不是用户真正想要的；也可能把网上学到的有害内容输出出来。对齐就是解决"模型能力"和"人类意图"之间差距的研究领域。

前面讲的 SFT、RLHF、宪法 AI，都是目前常用的对齐手段。

对齐也关注更长远的问题：随着 AI 越来越强，怎样确保它的目标和人类一致、行为可预测、出了问题能被发现和纠正。可解释性研究（理解模型内部到底在计算什么）就是其中一个重要方向。

## 打个比方

招来一个非常能干的员工，对齐就是确保他的能干用在公司真正想要的方向上。

## 开发者要注意

- 你在 System Prompt 里定义产品的规则和边界，可以看作应用层面的"对齐"。

## 相关概念

- [RLHF 人类反馈强化学习](./rlhf.md)
- [宪法 AI](./constitutional-ai.md)
- [提示注入](./prompt-injection.md)
