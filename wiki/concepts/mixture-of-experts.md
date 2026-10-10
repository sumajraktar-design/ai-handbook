---
id: mixture-of-experts
title: "MoE 混合专家"
en: "Mixture of Experts"
group: arch
priority: low
related: [parameters, transformer]
demo: MixtureOfExperts
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# MoE 混合专家

> 模型内部分成很多"专家"子网络，每个 Token 只激活其中少数几个。

**分组**：大模型结构 · **重要程度**：了解即可

## 动画演示

> 原手册中有可交互的动画（组件名 `MixtureOfExperts`），待迁移为 Vue 组件。

## 详细讲解

普通模型处理每个 Token 时，所有参数都要参与计算。MoE 模型把前馈网络层拆成很多个"专家"，再加一个"路由器"，负责判断当前 Token 该交给哪几个专家处理。

好处是：总参数可以做得非常大（知识容量大），但每个 Token 只用到一小部分参数（计算量小、速度快）。比如一个模型总共有几千亿参数，但每次只激活其中几百亿。

代价是：所有专家的参数仍然要全部装进内存，对硬件要求依然很高；训练也更复杂，要防止路由器总是只用某几个专家。

多个知名开源模型（例如 Mixtral、DeepSeek 的部分版本）都公开采用了 MoE 结构。

## 打个比方

一家大医院有很多科室专家，分诊台（路由器）根据病情只把你送到相关的两三个科室，不需要所有医生都来看你。

## 开发者要注意

- 看到模型标注类似"总参数 / 激活参数"两个数字时，通常就是 MoE 模型。

## 相关概念

- [参数量（7B、70B）](./parameters.md)
- [Transformer](./transformer.md)
