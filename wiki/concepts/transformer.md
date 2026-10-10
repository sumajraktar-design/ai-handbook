---
id: transformer
title: "Transformer"
en: "Transformer"
group: arch
priority: high
related: [attention, token, embedding, mixture-of-experts, context-window]
demo: TransformerLayers
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Transformer

> 2017 年提出的神经网络结构，核心是注意力机制，今天几乎所有大语言模型都基于它。

**分组**：大模型结构 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `TransformerLayers`），待迁移为 Vue 组件。

## 详细讲解

Transformer 出自 Google 在 2017 年发表的论文《Attention Is All You Need》。它原本用于机器翻译，后来发现非常适合做大规模语言模型。GPT 的全称 Generative Pre-trained Transformer，最后那个 T 就是它。

一个 Transformer 由很多个相同的"块"堆叠而成。每个块主要有两部分：注意力层（让每个词去看句子里的其他词，收集上下文信息）和前馈网络层（对每个词的信息做进一步加工，大量"知识"被认为存储在这里）。大模型会把这样的块堆几十到上百层。

它取代之前的 RNN 主要有两个原因。第一，注意力让任意两个词都能直接关联，距离再远也不会遗忘。第二，它可以并行计算：RNN 必须一个词一个词按顺序处理，Transformer 可以同时处理整句，非常适合用大量 GPU 训练，模型因此能越做越大。

GPT、Claude、Gemini、Grok、Llama、Qwen、DeepSeek 等主流大语言模型都属于 Transformer 家族，具体细节各有改良，比如有的使用混合专家结构（MoE）。

## 打个比方

RNN 像一个人从头到尾逐字读书，读到后面容易忘了前面；Transformer 像把整本书摊开在桌上，每个词都能同时看到其他所有词。

## 开发者要注意

- 理解 Transformer 的计算量随上下文长度快速增长（标准注意力大约是长度的平方），就能理解为什么长上下文又贵又慢。

## 相关概念

- [注意力机制](./attention.md)
- [Token（词元）](./token.md)
- [词向量 / 嵌入](./embedding.md)
- [MoE 混合专家](./mixture-of-experts.md)
- [上下文窗口](./context-window.md)
