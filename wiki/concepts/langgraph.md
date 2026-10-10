---
id: langgraph
title: "LangGraph"
en: "LangGraph"
group: frame
priority: medium
related: [langchain, agent, subagent, choosing-frameworks]
demo: LangGraphRun
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# LangGraph

> LangChain 团队开发的底层 Agent 编排框架，用"图"来定义 Agent 的流程，强调可控和可靠。

**分组**：开发框架 · **重要程度**：很常见，要懂

## 动画演示

> 原手册中有可交互的动画（组件名 `LangGraphRun`），待迁移为 Vue 组件。

## 详细讲解

LangGraph 把一个 AI 应用描述成一张图，由三样东西组成。State（状态）：一个在整个流程中传递的共享数据，比如对话消息、检索到的文档、当前步骤。Node（节点）：一个个处理步骤，本质是普通的 Python 函数，读取状态、返回对状态的更新，可以是调用模型、调用工具、或任何代码。Edge（边）：决定执行完一个节点后去哪里，可以是固定的，也可以是条件边，根据状态决定走向，并且允许形成循环。

"能形成循环"是关键。普通的链（Chain）只能从头走到尾；Agent 需要"思考 → 调工具 → 观察 → 再思考"的循环，还可能需要"写完代码 → 测试失败 → 回去修改"这种回退。用图来表达这些流程非常自然。

LangGraph 面向生产环境提供了几项重要能力：检查点与持久化（每一步的状态都可以保存，程序崩溃后能从断点恢复，长任务可以运行数小时甚至数天）；人在回路（Human-in-the-loop，流程可以在某个节点暂停，等人审批或修改后再继续）；流式输出（实时推送每一步的进展）；以及基于持久化状态的记忆。

LangGraph 1.0 和 LangChain 1.0 同时在 2025 年 10 月发布。两者的关系是：LangChain 的 create_agent 就运行在 LangGraph 之上。所以可以先用 LangChain 快速起步，遇到需要精细控制流程的场景，再下沉到 LangGraph 自己画图。

## 打个比方

LangChain 的 create_agent 像一辆自动挡汽车，上手快；LangGraph 像手动挡加可编程的导航，每个路口怎么走都能自己定，适合复杂路线。

## 开发者要注意

- 适合：流程复杂、有分支和循环、需要中途人工审批、需要长时间运行并能断点恢复的 Agent。
- 简单的"问答 + 几个工具"场景，用 create_agent 或原生 SDK 就够了，不必一开始就画图。
- 节点就是普通函数，你熟悉 Python 的话会觉得很直观。

## 代码示例

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    docs: list[str]
    answer: str
    retries: int

def retrieve(s: State):  return {"docs": search(s["question"]), "retries": s["retries"] + 1}
def generate(s: State):  return {"answer": llm(s["question"], s["docs"])}
def check(s: State):     return "ok" if good(s["answer"]) or s["retries"] >= 3 else "retry"

g = StateGraph(State)
g.add_node("retrieve", retrieve)
g.add_node("generate", generate)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "generate")
g.add_conditional_edges("generate", check, {"ok": END, "retry": "retrieve"})

app = g.compile()          # 传入 checkpointer 即可获得持久化和断点恢复
app.invoke({"question": "年假几天？", "docs": [], "answer": "", "retries": 0})
```

## 相关概念

- [LangChain](./langchain.md)
- [Agent 智能体](./agent.md)
- [Subagent 子智能体](./subagent.md)
- [框架怎么选](./choosing-frameworks.md)
