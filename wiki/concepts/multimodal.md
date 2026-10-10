---
id: multimodal
title: "多模态"
en: "Multimodal"
group: arch
priority: medium
related: [token, embedding, transformer]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 多模态

> 模型不只处理文字，还能理解图片、音频、视频，甚至生成它们。

**分组**：大模型结构 · **重要程度**：很常见，要懂

## 详细讲解

早期的大语言模型只能处理文字。多模态模型可以接收多种类型的输入，比如看一张截图、读一份 PDF 里的图表、听一段语音。

常见做法是：用专门的编码器把图片切成小块，变成和文字 Token 类似的向量序列，再和文字一起送进 Transformer。这样模型就能在同一个上下文里同时"看图"和"读字"。

输出端也可以是多模态的：生成图片、语音或视频。不同的模型支持的输入输出类型差别很大。

## 打个比方

从"只能读信"的人，变成"能看照片、听录音、还能画图"的人。

## 开发者要注意

- 给模型发截图让它找 UI 问题、读设计稿、解析表格图片，对前端开发很实用。
- 图片也会消耗 Token，大图通常更贵。

## 相关概念

- [Token（词元）](./token.md)
- [词向量 / 嵌入](./embedding.md)
- [Transformer](./transformer.md)
