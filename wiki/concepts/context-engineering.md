---
id: context-engineering
title: "上下文工程"
en: "Context Engineering"
group: app
priority: high
related: [context-window, compaction, memory, agent-skills, subagent, rag]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 上下文工程

> 决定在什么时候、把什么信息、以什么方式放进模型上下文窗口的整套方法。

**分组**：应用开发 · **重要程度**：开发者必知

## 详细讲解

提示词工程关注"一段指令怎么写"。随着应用变得复杂，尤其是 Agent 要运行很多步，问题变成了：上下文这块有限的空间里，每一步应该放什么？这就是上下文工程。

上下文里可能包含：System Prompt、工具说明、Skill、Memory 中的长期信息、RAG 检索结果、对话历史、工具返回结果。每一项都在抢占空间，放太少模型缺信息，放太多模型被干扰、成本上升、中间内容被忽略。

常用策略：按需加载（Skill、工具说明只在需要时放入完整内容）；压缩（对话太长时总结旧内容）；外部化（把进度、笔记写进文件，需要时再读）；隔离（让子 Agent 在独立上下文里处理大量资料，只带回结论）；检索（用 RAG 只拿最相关的部分）。

## 打个比方

给一位顾问准备会议材料：材料太少他无从判断，一次塞给他三百页他又找不到重点，关键是精选和排序。

## 开发者要注意

- Agent 效果不好时，先打印出它每一步实际看到的完整上下文，问题常常一目了然。

## 相关概念

- [上下文窗口](./context-window.md)
- [上下文压缩](./compaction.md)
- [Memory 记忆](./memory.md)
- [Skill 技能](./agent-skills.md)
- [Subagent 子智能体](./subagent.md)
- [RAG 检索增强生成](./rag.md)
