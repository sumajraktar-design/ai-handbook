---
id: fine-tuning
title: "微调"
en: "Fine-tuning"
group: train
priority: medium
related: [sft, rlhf, prompt-vs-rag-vs-finetune, overfitting]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 微调

> 在训练好的模型基础上，用少量特定数据再训练一下，改变它的行为。

**分组**：训练与对齐 · **重要程度**：很常见，要懂

## 详细讲解

微调的计算量远小于预训练，用的数据可能只有几千到几十万条。它主要用来改变模型的"行为方式"，比如回答格式、语气风格、擅长某类专门任务。

常见的微调方式：全参数微调（调整所有权重，效果好但贵）和参数高效微调，比如 LoRA（冻结原模型，只训练一小组额外的参数，便宜很多，是目前最流行的方式）。

微调有几个常见误区。第一，微调不擅长"灌输新知识"：想让模型知道你公司的文档，RAG 通常比微调效果好、成本低、更新也方便。第二，数据少且反复训练容易过拟合，甚至让模型丢掉原有能力（灾难性遗忘）。

前面说的 SFT 和 RLHF 都属于广义的微调。

## 打个比方

一个已经大学毕业的人，参加三个月的岗前专项培训。

## 开发者要注意

- 想定制模型时，先试提示词，再试 RAG，最后才考虑微调。
- 部分模型提供商的 API 支持在线微调，开源模型可以用 LoRA 自己微调。

## 相关概念

- [监督微调 SFT](./sft.md)
- [RLHF 人类反馈强化学习](./rlhf.md)
- [提示词 vs RAG vs 微调](./prompt-vs-rag-vs-finetune.md)
- [过拟合 / 泛化](./overfitting.md)
