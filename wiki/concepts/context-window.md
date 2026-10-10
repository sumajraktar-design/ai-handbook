---
id: context-window
title: "上下文窗口"
en: "Context Window"
group: arch
priority: high
related: [context-engineering, compaction, lost-in-the-middle, memory, rag]
demo: ContextWindow
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 上下文窗口

> 模型一次最多能"看到"多少个 Token，是它唯一能读取的信息范围。

**分组**：大模型结构 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `ContextWindow`），待迁移为 Vue 组件。

## 详细讲解

模型本身没有记忆。每次你发消息，应用会把系统指令、对话历史、你的新问题、工具结果等全部打包，一次性送进模型。这个"包"的最大容量就是上下文窗口，单位是 Token，同时包括输入和模型的输出。

超出窗口的内容，模型就完全看不到了。所以对话太长时，应用要么删掉最早的内容，要么把旧内容压缩成摘要。

窗口大不等于用得好。研究发现，上下文很长时，模型对开头和结尾的信息利用得比较好，中间的容易被忽略。此外，上下文越长，计算越慢、费用越高。

可以把模型的知识分成两种来源：权重里的（训练时学到的，量大但固定、可能过时）和上下文里的（当下放进来的，新鲜准确但容量有限）。RAG、Memory、压缩、Skill，本质上都是在管理上下文这块有限的空间。

## 打个比方

上下文窗口像一张工作台：桌面只有这么大，放得下的资料才能用，放不下的只能收进柜子，需要时再拿出来。

## 开发者要注意

- 重要的指令放在开头（System Prompt）或最新的消息里，不要埋在长对话中间。
- 处理长文档时，把问题放在文档后面通常效果更好。

## 相关概念

- [上下文工程](./context-engineering.md)
- [上下文压缩](./compaction.md)
- [迷失在中间](./lost-in-the-middle.md)
- [Memory 记忆](./memory.md)
- [RAG 检索增强生成](./rag.md)
