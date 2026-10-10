---
id: mcp
title: "MCP 模型上下文协议"
en: "Model Context Protocol"
group: agent
priority: high
related: [tool-use, agent-skills, agent, prompt-injection]
demo: MCPConnections
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# MCP 模型上下文协议

> Anthropic 在 2024 年发布的开放协议，统一规定 AI 应用如何连接外部工具和数据。

**分组**：Agent 智能体 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `MCPConnections`），待迁移为 Vue 组件。

## 详细讲解

没有 MCP 之前，每个 AI 应用要接入 GitHub、数据库、Slack 等服务，都得各自写一遍对接代码。N 个 AI 应用乘以 M 个服务，就要写 N×M 份集成。

MCP 定义了一套标准的对接方式：服务方写一个 MCP Server，按协议暴露自己的能力；任何支持 MCP 的 AI 应用（MCP Client）都能直接连接使用。这样只需要 N+M 份工作。

一个 MCP Server 主要可以提供三类东西：Tools（可调用的函数，如"创建 Issue"）、Resources（可读取的数据，如文件、数据库记录）、Prompts（预设的提示词模板）。通信基于 JSON-RPC，可以在本地运行（通过标准输入输出），也可以作为远程服务（通过 HTTP）。

MCP 发布后被众多 AI 产品和开发工具采纳，已经成为连接 AI 和外部系统事实上的通用标准之一。

## 打个比方

AI 世界的 USB-C 接口：以前每种设备一种充电线，现在一个统一接口，什么设备都能插。

## 开发者要注意

- 写 MCP Server 门槛很低，Python 有官方 SDK，几十行就能把你的一组函数暴露出去。
- 接入第三方 MCP Server 要注意安全：它能看到 Agent 传过去的数据，返回的内容也可能包含提示注入。

## 代码示例

```python
# Python 官方 SDK 写一个最小 MCP Server（示意）
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("menu-tools")

@mcp.tool()
def count_menus(env: str) -> int:
    """统计指定环境（dev/test/prod）的菜单数量"""
    return query_db(env)

if __name__ == "__main__":
    mcp.run()
```

## 相关概念

- [Tool 工具调用](./tool-use.md)
- [Skill 技能](./agent-skills.md)
- [Agent 智能体](./agent.md)
- [提示注入](./prompt-injection.md)
