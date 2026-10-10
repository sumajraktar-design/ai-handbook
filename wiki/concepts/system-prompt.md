---
id: system-prompt
title: "System Prompt 系统提示词"
en: "System Prompt"
group: app
priority: high
related: [prompt-engineering, compaction, prompt-injection, cost-and-latency]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# System Prompt 系统提示词

> 开发者在对话最前面设定的指令，定义 AI 的身份、规则、风格和边界。

**分组**：应用开发 · **重要程度**：开发者必知

## 详细讲解

调用 API 时，消息分为几种角色：system（系统指令）、user（用户）、assistant（模型回答）。System Prompt 放在最前面，通常用户看不到，用来设定整个对话的基调。

典型内容包括：角色和任务（"你是某某公司的客服助手"）、背景知识（产品信息、用户信息）、行为规则（能做什么、不能做什么、遇到某类问题怎么处理）、输出风格（语气、长度、格式）、工具使用说明。

模型会比较认真地遵守 System Prompt，但它不是绝对的安全边界：用户可能通过越狱或提示注入试图绕过。关键的权限控制不能只靠提示词，要在代码层面实现。

## 打个比方

System Prompt 像员工入职时拿到的岗位说明书：你是谁、负责什么、有哪些规矩。

## 开发者要注意

- 你做的 AI 产品"性格"如何，主要靠 System Prompt 决定。
- 长而固定的 System Prompt 适合配合提示缓存，降低成本。
- 不要在 System Prompt 里放密钥等敏感信息，它有可能被套出来。

## 相关概念

- [提示词工程](./prompt-engineering.md)
- [上下文压缩](./compaction.md)
- [提示注入](./prompt-injection.md)
- [Token 成本与延迟](./cost-and-latency.md)
