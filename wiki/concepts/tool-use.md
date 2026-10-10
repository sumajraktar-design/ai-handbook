---
id: tool-use
title: "Tool 工具调用"
en: "Tool Use / Function Calling"
group: agent
priority: high
related: [agent, mcp, structured-output, prompt-injection]
demo: ToolUseSequence
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# Tool 工具调用

> 模型输出"要调用哪个函数、传什么参数"，由外部程序真正执行，再把结果返回给模型。

**分组**：Agent 智能体 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `ToolUseSequence`），待迁移为 Vue 组件。

## 详细讲解

模型本身不能执行任何代码。工具调用的机制是：开发者先告诉模型有哪些工具可用，每个工具包括名称、用途描述、参数格式（JSON Schema）。模型在回答过程中如果判断需要某个工具，就输出一段结构化的调用请求，比如 get_weather(city="东京")。

你的程序收到这个请求后，真正去执行这个函数（调用天气 API），再把结果作为一条新消息发回给模型。模型读到结果后，继续回答或者决定调用下一个工具。

工具描述写得好不好直接影响效果：模型完全依靠描述来判断什么时候用、怎么用这个工具。描述要说清楚用途、什么时候该用、什么时候不该用、每个参数的含义和格式。

## 打个比方

模型像一个只能打电话下指令的经理：他说"帮我查一下明天的天气"，助理（你的代码）去查，查完把结果报告给他。

## 开发者要注意

- 工具就是你写的普通函数加一段描述，Python 开发者上手很快。
- 工具返回的内容会进入上下文，返回太长会浪费 Token，必要时先截断或总结。
- 把工具的执行结果当作不可信数据，它可能包含提示注入。

## 代码示例

```python
# 工具定义（发给模型的描述）
tools = [{
  "name": "get_weather",
  "description": "查询指定城市未来几天的天气。用户问到天气时使用。",
  "input_schema": {
    "type": "object",
    "properties": {"city": {"type": "string", "description": "城市名，如 东京"}},
    "required": ["city"]
  }
}]

# 循环：模型要求调用工具 → 你执行 → 把结果发回去
while True:
    resp = call_model(messages, tools)
    if resp.wants_tool:
        result = get_weather(**resp.tool_args)   # 你的代码真正执行
        messages += [resp.message, tool_result(result)]
    else:
        print(resp.text); break
```

## 相关概念

- [Agent 智能体](./agent.md)
- [MCP 模型上下文协议](./mcp.md)
- [结构化输出](./structured-output.md)
- [提示注入](./prompt-injection.md)
