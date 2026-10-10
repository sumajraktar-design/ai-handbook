---
id: parameters
title: "参数量（7B、70B）"
en: "Parameters"
group: arch
priority: high
related: [neuron, quantization, mixture-of-experts, scaling-laws, cost-and-latency]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 参数量（7B、70B）

> 模型里权重的总数，B 是 Billion（十亿），70B 就是 700 亿个参数。

**分组**：大模型结构 · **重要程度**：开发者必知

## 详细讲解

参数就是神经网络里所有可调节的权重。参数越多，模型能存储的知识和能表达的规律越复杂，通常也越聪明。

参数量直接决定运行成本：每个参数要占内存。以常见的 16 位精度为例，每个参数 2 字节，一个 70B 模型光权重就需要约 140GB 显存，普通电脑根本跑不动。量化可以把这个数字大幅压缩。

参数多不等于一定更强。训练数据的质量和数量、训练方法、模型结构都很重要。一个训练得好的小模型，可能比训练得差的大模型更好用。闭源模型（Claude、GPT 等）通常不公布参数量。

对 MoE 模型，要区分"总参数"和"激活参数"：总参数很大，但每次计算只用到其中一小部分。

## 打个比方

参数量像图书馆的藏书容量：容量越大能放的书越多，但书本身选得好不好（数据质量）同样关键。

## 开发者要注意

- 选开源模型时，先看你的硬件能跑多大的模型，再看效果。
- 同一家的模型系列通常分大中小几档：大的聪明但贵慢，小的便宜快速，按任务选择。

## 相关概念

- [神经元](./neuron.md)
- [量化 / 本地部署](./quantization.md)
- [MoE 混合专家](./mixture-of-experts.md)
- [Scaling Law 规模定律](./scaling-laws.md)
- [Token 成本与延迟](./cost-and-latency.md)
