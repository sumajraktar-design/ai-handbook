---
id: agent-skills
title: "Skill 技能"
en: "Agent Skills"
group: agent
priority: medium
related: [mcp, context-engineering, agent, memory]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Skill 技能

> 一个装着"做某类事情的方法说明"和相关脚本的文件夹，Agent 遇到相关任务时才去读取。

**分组**：Agent 智能体 · **重要程度**：很常见，要懂

## 详细讲解

Skill 通常是一个文件夹，核心是一份 SKILL.md：开头有名称和简短描述，正文写着具体做法、注意事项、示例；文件夹里还可以放脚本、模板、参考资料。

它的关键设计是"渐进加载"：平时上下文里只放每个 Skill 的名称和一句话描述，占用很少空间。当任务和某个 Skill 相关时，Agent 才读取完整的 SKILL.md，必要时再运行里面的脚本。这样可以给 Agent 装上很多 Skill，而不会把上下文塞满。

和 MCP 的区别：MCP 提供的是"能力"，让 Agent 能连接到某个系统；Skill 提供的是"方法"，告诉 Agent 怎么把一件事做好。比如接上 PostgreSQL 的 MCP，Agent 就能查数据库；再加一个"我们团队的 SQL 规范"Skill，它查询时就会遵循你们的规范。两者经常配合使用。

## 打个比方

MCP 是给员工配的工具和权限，Skill 是部门的操作手册，员工遇到对应任务时才翻开那一章。

## 开发者要注意

- 团队里反复解释的流程、规范、模板，都适合写成 Skill。
- Skill 的描述决定了 Agent 什么时候会想起它，要写清楚适用场景。

## 相关概念

- [MCP 模型上下文协议](./mcp.md)
- [上下文工程](./context-engineering.md)
- [Agent 智能体](./agent.md)
- [Memory 记忆](./memory.md)
