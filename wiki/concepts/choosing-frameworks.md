---
id: choosing-frameworks
title: "框架怎么选"
en: "Choosing a Framework"
group: frame
priority: low
related: [langchain, langgraph, agent, rag]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 框架怎么选

> 除了 LangChain 系列，还有不少框架，各有侧重；也完全可以不用框架。

**分组**：开发框架 · **重要程度**：了解即可

## 详细讲解

原生 SDK：直接用模型厂商的官方 SDK（如 Anthropic、OpenAI 的 Python SDK）。没有额外抽象，最透明，最适合学习原理和做简单项目。工具调用循环自己写也就几十行。

LangChain / LangGraph：集成最多、生态最大，适合需要切换多家模型、需要复杂编排的项目。

LlamaIndex：最初专注于 RAG，在文档加载、索引、检索方面功能丰富，适合以"让 AI 读懂大量文档"为核心的应用。

厂商的 Agent SDK：一些模型厂商提供了自己的 Agent 开发包（例如 Anthropic 的 Claude Agent SDK、OpenAI 的 Agents SDK），和自家模型、工具结合更紧密。

多 Agent 框架：如 CrewAI、AutoGen 等，侧重多个角色 Agent 之间的协作。

这个领域变化很快，框架的功能和流行程度每年都在变，选型前建议看一下最新的官方文档和社区情况。

## 打个比方

就像前端开发：可以用原生 JS，也可以用 React、Vue。先懂原生，再用框架，才知道框架替你做了什么。

## 开发者要注意

- 推荐学习路径：先用原生 SDK 手写一个工具调用循环和一个最小 RAG → 理解原理后再用 LangChain 提速 → 流程复杂时再上 LangGraph。

## 相关概念

- [LangChain](./langchain.md)
- [LangGraph](./langgraph.md)
- [Agent 智能体](./agent.md)
- [RAG 检索增强生成](./rag.md)
