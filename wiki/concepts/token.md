---
id: token
title: "Token（词元）"
en: "Token"
group: arch
priority: high
related: [tokenizer, embedding, context-window, cost-and-latency]
demo: Tokenizer
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Token（词元）

> 模型读写文字的最小单位，文字会先被切成一个个 Token 再处理。

**分组**：大模型结构 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `Tokenizer`），待迁移为 Vue 组件。

## 详细讲解

神经网络只能处理数字，所以文字必须先被切成小块，每块对应一个编号。这些小块就是 Token。切法不是简单的按字或按词，而是按训练时统计出来的常见片段：常见词整个算一个 Token，罕见词被拆成几块。

粗略估算：英文大约 1 个 Token 对应 0.75 个单词；中文大约 1 个汉字对应 1 到 2 个 Token，具体取决于模型的分词器。不同模型对同一段话切出的 Token 数可能不一样。

Token 是大模型世界的通用计量单位：上下文窗口大小用 Token 计算，API 费用按 Token 收费，生成速度用"每秒多少 Token"衡量。

模型一次只生成一个 Token。你看到回答一个字一个字地出现，就是因为它真的在逐个 Token 地生成。

## 打个比方

Token 像乐高积木：常用的形状有现成的大块，奇怪的形状就用几个小块拼出来。

## 开发者要注意

- 估算成本和是否超出上下文限制时，要按 Token 算而不是按字数算。
- 模型对单个字母、数字的处理不太擅长（比如数单词里有几个 r），部分原因就是它看到的是 Token 而不是字母。

## 相关概念

- [分词器](./tokenizer.md)
- [词向量 / 嵌入](./embedding.md)
- [上下文窗口](./context-window.md)
- [Token 成本与延迟](./cost-and-latency.md)
