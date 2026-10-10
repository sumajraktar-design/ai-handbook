---
id: training-vs-inference
title: "训练 vs 推理"
en: "Training vs Inference"
group: deploy
priority: high
related: [pretraining, cost-and-latency, memory, reasoning-models]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 训练 vs 推理

> 训练是调权重造模型（极贵、只做一次）；推理是用造好的模型回答问题（每次调用都发生）。

**分组**：使用模型 · **重要程度**：开发者必知

## 详细讲解

训练阶段：反复前向传播、计算损失、反向传播、更新权重。需要海量数据和巨大算力，产物是一份固定的权重文件。

推理阶段：权重已经固定不变，模型只做前向传播：读入上下文，一个 Token 一个 Token 地生成输出。你每次调用 API、每次在聊天界面提问，都是一次推理。

注意"推理"这个中文词有两种意思：一是这里说的 Inference（模型运行），二是 Reasoning（逻辑推理，比如推理模型）。读文章时要根据上下文区分。

应用开发者几乎只和推理打交道。和你聊天时，模型并不会因为这次对话而学习或改变权重。

## 打个比方

训练是写一本书，推理是读者每次翻开这本书查内容。书写好之后，翻阅多少次都不会改变书的内容。

## 开发者要注意

- API 费用就是推理费用，按输入和输出的 Token 计费。
- "和 AI 多聊几次它就记住了"是误解，跨对话的"记忆"靠的是 Memory 这类外部机制。

## 相关概念

- [预训练](./pretraining.md)
- [Token 成本与延迟](./cost-and-latency.md)
- [Memory 记忆](./memory.md)
- [推理模型](./reasoning-models.md)
