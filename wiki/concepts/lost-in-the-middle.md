---
id: lost-in-the-middle
title: "迷失在中间"
en: "Lost in the Middle"
group: arch
priority: medium
related: [context-window, attention, rerank]
demo: ContextWindow
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 迷失在中间

> 上下文很长时，模型容易忽略放在中间位置的信息。

**分组**：大模型结构 · **重要程度**：很常见，要懂

## 动画演示

> 原手册中有可交互的动画（组件名 `ContextWindow`），待迁移为 Vue 组件。

## 详细讲解

2023 年有研究把一条关键信息放在长文档的不同位置，测试模型能否找到它。结果画出来是一条 U 形曲线：信息在开头或结尾时准确率高，在中间时明显下降。

可能的原因包括：注意力需要在越来越多的 Token 之间分配，信息被稀释；训练数据里重要内容常出现在开头和结尾，模型学到了这种位置偏好；模型训练时见过的超长文本相对较少。

较新的模型在这方面有很大改善，但上下文越长、信息越分散，问题依然越明显。

## 打个比方

听一场三小时的讲座，你通常记得开场和结尾讲了什么，中间那一段最容易走神。

## 开发者要注意

- 和任务最相关的资料放在靠近问题的位置。
- RAG 时不要一次塞太多检索结果，精选几段比塞几十段效果更好。

## 相关概念

- [上下文窗口](./context-window.md)
- [注意力机制](./attention.md)
- [Rerank 重排序](./rerank.md)
