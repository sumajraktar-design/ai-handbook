---
id: cost-and-latency
title: "Token 成本与延迟"
en: "Cost & Latency"
group: deploy
priority: high
related: [token, context-window, streaming, parameters]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Token 成本与延迟

> API 按 Token 收费，输出比输入贵；上下文越长、模型越大，就越贵越慢。

**分组**：使用模型 · **重要程度**：开发者必知

## 详细讲解

API 价格通常按"每百万 Token"计算，输入和输出分开定价，输出一般比输入贵好几倍，因为输出要一个个 Token 生成。

延迟分两部分：首个 Token 的等待时间（模型读完全部输入的时间，上下文越长越久），以及之后每秒生成多少 Token。

降低成本的常用手段：选够用的最小模型；精简上下文，别把无关内容塞进去；使用提示缓存（Prompt Caching），重复的前缀（如长 System Prompt、固定文档）只需第一次全价处理，后续调用便宜很多、也更快；非实时任务用批处理接口，通常有折扣。

一个真实产品里，多轮对话、Agent 循环、RAG 检索结果都会让 Token 数快速膨胀，上线前一定要估算。

## 打个比方

打出租车：按里程（Token）计价，豪华车（大模型）每公里更贵，绕远路（冗长上下文）多花钱又多花时间。

## 开发者要注意

- 记录每次调用的输入输出 Token 数，是做成本优化的第一步。
- Agent 每循环一次都会重新发送整个上下文，成本随步骤数快速增长。

## 相关概念

- [Token（词元）](./token.md)
- [上下文窗口](./context-window.md)
- [流式输出](./streaming.md)
- [参数量（7B、70B）](./parameters.md)
