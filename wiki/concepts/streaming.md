---
id: streaming
title: "流式输出"
en: "Streaming"
group: deploy
priority: medium
related: [token, cost-and-latency, structured-output]
demo: Streaming
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 流式输出

> 模型一边生成一边把内容推送给前端，而不是等全部写完再返回。

**分组**：使用模型 · **重要程度**：很常见，要懂

## 动画演示

> 原手册中有可交互的动画（组件名 `Streaming`），待迁移为 Vue 组件。

## 详细讲解

因为模型是逐个 Token 生成的，一个长回答可能要十几秒甚至更久。如果等全部生成完再显示，用户会盯着空白页面等很久。流式输出让第一个字在一两秒内就出现，体验好得多。

技术上，大多数 LLM API 使用 SSE（Server-Sent Events）协议：一个 HTTP 请求保持连接，服务器持续推送小块数据，每块包含新生成的几个 Token，最后发送结束标志。

前端处理时要注意：逐块拼接文本、处理 Markdown 渲染（未闭合的代码块等）、支持中途取消、处理网络中断。工具调用、结构化输出在流式模式下也会分块到达，需要拼接完整后再解析。

## 打个比方

看直播而不是等录像：内容一边产生一边播放，不用等整场结束。

## 开发者要注意

- 前端实现可以用 fetch + ReadableStream 读取 SSE 流，或者直接用官方 SDK 提供的流式接口。
- 后端做代理转发时，注意关闭缓冲，否则流式效果会失效。

## 相关概念

- [Token（词元）](./token.md)
- [Token 成本与延迟](./cost-and-latency.md)
- [结构化输出](./structured-output.md)
