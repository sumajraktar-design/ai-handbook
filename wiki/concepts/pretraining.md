---
id: pretraining
title: "预训练"
en: "Pre-training"
group: train
priority: high
related: [base-model, learning-paradigms, knowledge-cutoff, sft, scaling-laws]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 预训练

> 在海量文本上让模型反复"猜下一个词"，学会语言和世界知识。

**分组**：训练与对齐 · **重要程度**：开发者必知

## 详细讲解

预训练是造大模型的第一步，也是最花钱的一步。训练数据来自网页、书籍、论文、代码等，规模可达几万亿 Token。训练任务只有一个：给定前面的文字，预测下一个 Token。

这个看似简单的任务，要做到极好，模型就不得不学会很多东西：语法、事实知识、常识推理、代码逻辑、不同文体的写法。可以说，知识是"预测下一个词"的副产品。

预训练需要成千上万张 GPU 连续运行数周到数月，成本极高，所以只有少数机构能从头训练前沿大模型。训练完成后得到的模型叫基座模型。

训练数据有截止时间，之后的事情模型不知道，这就是知识截止日期的来源。数据里的偏见和错误，也会被模型一并学进去。

## 打个比方

让一个人把图书馆里所有的书读一遍，他会变得博学，但还不知道怎么当一个好助手。

## 开发者要注意

- 应用开发者几乎不会做预训练，但要知道模型的知识边界由预训练数据决定。

## 相关概念

- [基座模型](./base-model.md)
- [监督 / 无监督 / 自监督](./learning-paradigms.md)
- [知识截止日期](./knowledge-cutoff.md)
- [监督微调 SFT](./sft.md)
- [Scaling Law 规模定律](./scaling-laws.md)
