---
id: vector-database
title: "向量数据库"
en: "Vector Database"
group: app
priority: medium
related: [rag, embedding, chunking]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 向量数据库

> 专门存储向量、并能按相似度快速查找"最接近的向量"的数据库。

**分组**：应用开发 · **重要程度**：很常见，要懂

## 详细讲解

普通数据库擅长精确查询（WHERE id = 5）。向量数据库擅长的是近似查询："找出和这个向量最相似的 10 个"。当数据量达到百万级时，逐个比较太慢，向量数据库会使用专门的索引算法（如 HNSW）实现快速的近似搜索。

选择大致有三类：专用向量数据库（Milvus、Qdrant、Weaviate、Pinecone 等）；轻量嵌入式方案（Chroma、FAISS，适合原型和本地实验）；传统数据库加向量扩展（PostgreSQL 的 pgvector、以及 Elasticsearch、Redis 等产品的向量功能）。

向量通常和原文、元数据（来源、日期、权限）一起存储，这样检索时可以加过滤条件，比如"只搜这个用户有权限看的文档"。

## 打个比方

一个按"意思"排列的图书馆，你拿着一个问题进去，管理员直接把意思最接近的几本书递给你。

## 开发者要注意

- 你在学 PostgreSQL，pgvector 是最顺手的入门方式：建一个 vector 类型的列，用  运算符按余弦距离排序即可。

## 代码示例

```sql
-- PostgreSQL + pgvector 示意
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunks (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(1024)   -- 维度取决于你用的嵌入模型
);
-- 查询最相似的 4 段（<=> 为余弦距离）
SELECT content FROM chunks
ORDER BY embedding <=> $1
LIMIT 4;
```

## 相关概念

- [RAG 检索增强生成](./rag.md)
- [词向量 / 嵌入](./embedding.md)
- [切块](./chunking.md)
