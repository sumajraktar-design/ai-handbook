---
id: agent
title: "Agent 智能体"
en: "AI Agent"
group: agent
priority: high
related: [tool-use, mcp, agent-skills, memory, subagent, langgraph]
demo: AgentLoop
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Agent 智能体

> 模型 + 工具 + 循环：能接受一个目标，自己规划、调用工具、观察结果，直到完成任务。

**分组**：Agent 智能体 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `AgentLoop`），待迁移为 Vue 组件。

## 详细讲解

大模型本身只能输入文字、输出文字。Agent 给它配上工具（搜索、读写文件、执行代码、调用 API），并让它在一个循环里工作：思考下一步做什么 → 调用工具 → 观察结果 → 再思考，直到任务完成或需要人来决定。

这个循环通常被称为 ReAct（Reasoning + Acting，推理 + 行动）模式。和普通聊天的关键区别是：Agent 自己决定步骤和顺序，而不是每一步都由人或代码规定好。

要区分"工作流"和"Agent"：工作流是开发者预先写好固定步骤（先检索、再总结、再翻译），模型只负责每一步的内容；Agent 是模型自己决定走哪些步骤。工作流更可控、更便宜，Agent 更灵活。很多实际产品是两者的混合。

Claude、ChatGPT 这些名字既指模型也指产品。产品层面它们都配备了工具，执行任务时就是以 Agent 的方式在工作。Claude Code 这类编程助手是典型的 Agent：读代码、改代码、运行测试、根据报错继续修改。

## 打个比方

模型是一个聪明但被关在房间里、只能传纸条的人；Agent 是给他配了电脑、电话和工作手册，让他自己去查、去做、去验证。

## 开发者要注意

- 能用固定工作流解决的问题，先别上 Agent，可控性和成本都更好。
- Agent 的每一步都会重新发送整个上下文，步骤多时成本增长很快。
- 让 Agent 执行有副作用的操作（删除、付款、发送邮件）前，设计人工确认环节。

## 相关概念

- [Tool 工具调用](./tool-use.md)
- [MCP 模型上下文协议](./mcp.md)
- [Skill 技能](./agent-skills.md)
- [Memory 记忆](./memory.md)
- [Subagent 子智能体](./subagent.md)
- [LangGraph](./langgraph.md)
