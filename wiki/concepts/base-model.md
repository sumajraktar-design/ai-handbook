---
id: base-model
title: "基座模型"
en: "Base Model"
group: train
priority: medium
related: [pretraining, sft]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 基座模型

> 只经过预训练的模型，知识丰富，但只会续写，还不会当助手。

**分组**：训练与对齐 · **重要程度**：很常见，要懂

## 详细讲解

基座模型的行为就是"续写最可能出现的文字"。你问它"法国的首都是哪里？"，它可能不回答，而是接着写"德国的首都是哪里？意大利的首都是哪里？"，因为在网上，这种问句后面经常跟着更多问题（比如一份试卷）。

基座模型是后续所有微调的起点。很多开源模型会同时发布两个版本：Base 版（基座）和 Instruct / Chat 版（经过指令微调的助手版）。

基座模型对研究者和需要深度定制的团队有价值，普通应用开发直接用 Instruct / Chat 版即可。

## 打个比方

一个读完所有书但从没和人聊过天的学者，你说一句话，他只会顺着往下"背书"。

## 开发者要注意

- 下载开源模型时，注意区分 base 和 instruct 版本，做对话应用要用 instruct 版。

## 相关概念

- [预训练](./pretraining.md)
- [监督微调 SFT](./sft.md)
