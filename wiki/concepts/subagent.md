---
id: subagent
title: "Subagent 子智能体"
en: "Subagent / Multi-agent"
group: agent
priority: low
related: [agent, context-engineering, langgraph]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Subagent 子智能体

> 主 Agent 把一部分任务交给另一个拥有独立上下文的 Agent 完成，只把结果拿回来。

**分组**：Agent 智能体 · **重要程度**：了解即可

## 详细讲解

有些任务会产生大量中间信息，比如翻阅一百个文件寻找某个线索。如果主 Agent 亲自做，这些文件内容会塞满它的上下文。交给子 Agent 去做，子 Agent 在自己的上下文里完成翻找，最后只把"在第几个文件找到了什么"这个结论交回来。

子 Agent 的另一个用途是并行：同时派出几个子 Agent 分别调研不同方向，再由主 Agent 汇总。

更广义的"多智能体系统"会让多个不同角色的 Agent 协作，比如一个负责规划、一个负责写代码、一个负责审查。多 Agent 更强大，但也更难调试、成本更高、Agent 之间的信息传递可能出现偏差。

## 打个比方

项目经理把"查遍所有历史合同"这件事派给实习生，实习生翻完后只汇报一页结论，经理的办公桌不会被堆满。

## 开发者要注意

- 先用单个 Agent，确实遇到上下文不够或需要并行时再引入子 Agent。

## 相关概念

- [Agent 智能体](./agent.md)
- [上下文工程](./context-engineering.md)
- [LangGraph](./langgraph.md)
