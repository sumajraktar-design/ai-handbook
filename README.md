# AI 概念手册

一个从零开始学 AI 的个人知识库：64 个概念，从机器学习原理一直讲到 Agent、MCP、LangGraph 和工程化落地。

同一批 Markdown 有三种用法：

| 用法 | 怎么做 | 状态 |
| --- | --- | --- |
| 阅读学习 | 直接在 GitHub 上看，之后用 VitePress 生成网站，带交互动画 | 内容已就绪，网站待搭建 |
| LLM Wiki | 用 Claude Code 打开仓库提问，模型先读目录再读相关页面 | 可用 |
| RAG 检索 | 按二级标题切块，存入 PostgreSQL + pgvector | 待实现 |

## 从哪里开始读

打开 [wiki/index.md](wiki/index.md)，按分组顺序读：

1. 基础原理：机器怎么"学"
2. 大模型结构：Transformer 和它的零件
3. 训练与对齐：一个模型怎么造出来
4. 使用模型：推理、成本、部署
5. 应用开发：提示词、RAG、上下文工程
6. Agent 智能体：让模型动手干活
7. 开发框架：LangChain、LangGraph
8. 安全与风险

## 目录结构

```
CLAUDE.md               给模型的规则：页面模板、写作规范、修改规则
raw/                    原始资料，只增不改
  handbook/             第一版交互式手册（HTML，含 26 个动画）
  notes/                学习笔记和对话整理
wiki/
  index.md              目录
  concepts/*.md         概念页，唯一的内容源
evals/questions.yaml    测试问题，用来比较不同回答方式的质量
.claude/skills/
  ingest/               把新资料整理进 wiki
  lint/                 体检：断链、矛盾、过时内容
```

## 计划

- [x] 第 1 步：导出概念页，建立目录和规则
- [ ] 第 2 步：VitePress 网站 + 把 26 个动画改写成 Vue 组件，部署到 GitHub Pages
- [ ] 第 3 步：用 ingest / lint 两个 Skill 维护 wiki
- [ ] 第 4 步：`rag/ingest.py` 和 `rag/query.py`，接入 pgvector
- [ ] 第 5 步：用 `evals/` 对比 LLM Wiki 和 RAG 的回答质量

## 说明

内容由 AI 辅助编写，用于个人学习。产品功能、框架版本等会变化的信息以官方文档为准。
