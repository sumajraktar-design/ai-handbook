---
id: langchain
title: "LangChain"
en: "LangChain"
group: frame
priority: medium
related: [langgraph, choosing-frameworks, agent, tool-use, rag]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# LangChain

> 最流行的开源大模型应用框架之一，提供统一的模型接口、大量集成，以及快速搭建 Agent 的高层 API。

**分组**：开发框架 · **重要程度**：很常见，要懂

## 详细讲解

LangChain 由 LangChain 公司开发，有 Python 和 JavaScript 两个版本。它要解决的问题是：不同模型厂商的 API 各不相同，而 RAG、工具调用、Agent 这些常见模式每次都要从头写。LangChain 把它们封装成统一的接口和现成组件。

它最核心的价值有两块。一是集成：提供上千种对接，包括各家模型（Anthropic、OpenAI、Google 等）、嵌入模型、向量数据库、文档加载器，换模型往往只需要改一行配置。二是 Agent 抽象：2025 年 10 月发布的 LangChain 1.0 把重心放在 create_agent 这个函数上，几行代码就能创建一个带工具的 Agent，底层运行在 LangGraph 之上；还引入了中间件（Middleware）机制，可以在 Agent 循环的各个环节插入自定义逻辑，比如压缩对话、人工审批、限制调用次数。

历史上 LangChain 以"链"（Chain）著称，用 LCEL 语法把提示词、模型、解析器串起来。早期版本因为抽象层次太多、学习成本高、调试困难而受到不少批评，1.0 大幅精简了核心包，旧的接口被移到 langchain-classic 包中。

和它配套的还有 LangSmith：一个用于追踪每次调用细节、调试和做评测的平台（商业服务，有免费额度）。

## 打个比方

LangChain 像一个装满标准零件的工具箱：螺丝、接头、转换器都是现成的，想组装一个 Agent 不用自己从头造每个零件。

## 开发者要注意

- 适合：需要频繁切换模型、需要大量现成集成、想快速做出原型。
- 也可以不用框架：直接调用官方 SDK 自己写循环，代码更透明，对简单项目来说往往更清晰。建议先用原生 SDK 理解原理，再决定是否引入框架。
- 框架版本变化较快，网上很多教程是旧版本写法，以官方最新文档为准。

## 代码示例

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city}：晴，22°C"

agent = create_agent(
    model="anthropic:<模型名>",      # 按官方文档填写，换厂商只改这里
    tools=[get_weather],
    system_prompt="你是一个简洁的天气助手",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "东京天气怎么样？"}]}
)
```

## 相关概念

- [LangGraph](./langgraph.md)
- [框架怎么选](./choosing-frameworks.md)
- [Agent 智能体](./agent.md)
- [Tool 工具调用](./tool-use.md)
- [RAG 检索增强生成](./rag.md)
