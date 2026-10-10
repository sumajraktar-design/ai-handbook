---
id: rag
title: "RAG 检索增强生成"
en: "Retrieval-Augmented Generation"
group: app
priority: high
related: [chunking, embedding, vector-database, rerank, hallucination, prompt-vs-rag-vs-finetune]
demo: RAGPipeline
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# RAG 检索增强生成

> 先从资料库里检索相关内容，再把它和问题一起交给模型回答，相当于"开卷考试"。

**分组**：应用开发 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `RAGPipeline`），待迁移为 Vue 组件。

## 详细讲解

模型的知识固定在权重里，不知道你的私有文档，也不知道最新信息。RAG 的思路是：用户提问时，先去资料库搜出最相关的几段内容，拼进提示词，让模型"根据以下资料回答"。

完整流程分两个阶段。准备阶段（离线）：把文档切成小段（切块）→ 用嵌入模型把每段变成向量 → 存进向量数据库。查询阶段（在线）：把用户问题也变成向量 → 在向量库里找最相似的几段 → （可选）重排序 → 拼进提示词 → 模型生成回答，最好附上引用来源。

为什么用向量检索而不是关键词搜索？因为向量比较的是"意思"：用户问"能休几天假"，也能找到写着"年假 10 天"的段落，即使字面上没有重合的词。实践中常把关键词检索（BM25）和向量检索结合使用，叫混合检索。

RAG 的优点：减少幻觉、知识可以随时更新（改文档就行，不用重新训练）、可以给出处、可以按用户权限控制能检索的资料。它的效果上限主要取决于检索质量：检索不到正确的段落，模型再强也答不对。

## 打个比方

开卷考试：先翻书找到相关的那几页，再照着书写答案，而不是全凭记忆。

## 开发者要注意

- 入门可以用 PostgreSQL + pgvector 扩展，不用额外部署新的数据库。
- RAG 出问题时，先检查检索到的段落对不对，大多数问题出在检索而不是生成。
- Agent 时代也常让模型自己决定何时调用"搜索资料"工具，叫 Agentic RAG。

## 代码示例

```python
# 最小 RAG 流程（伪代码）
chunks = split(documents, size=500)              # 1. 切块
vectors = embed(chunks)                          # 2. 向量化
db.insert(chunks, vectors)                       # 3. 存入向量库

q_vec = embed(question)                          # 4. 问题向量化
top = db.search(q_vec, k=4)                      # 5. 相似度检索
prompt = f"根据以下资料回答，资料中没有就说不知道：\n{top}\n\n问题：{question}"
answer = llm(prompt)                             # 6. 生成回答
```

## 相关概念

- [切块](./chunking.md)
- [词向量 / 嵌入](./embedding.md)
- [向量数据库](./vector-database.md)
- [Rerank 重排序](./rerank.md)
- [幻觉](./hallucination.md)
- [提示词 vs RAG vs 微调](./prompt-vs-rag-vs-finetune.md)
