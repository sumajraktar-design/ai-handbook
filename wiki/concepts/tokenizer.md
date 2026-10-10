---
id: tokenizer
title: "分词器"
en: "Tokenizer"
group: arch
priority: medium
related: [token, embedding]
demo: Tokenizer
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 分词器

> 负责把文字切成 Token、并给每个 Token 编号的程序。

**分组**：大模型结构 · **重要程度**：很常见，要懂

## 动画演示

> 原手册中有可交互的动画（组件名 `Tokenizer`），待迁移为 Vue 组件。

## 详细讲解

分词器在模型训练之前就要先准备好。常用的算法叫 BPE（字节对编码）：从单个字符开始，统计哪两个片段最常一起出现，就把它们合并成一个新 Token，反复合并直到词表达到设定大小（通常几万到十几万个 Token）。

分词器决定了模型"看世界的方式"。如果训练数据里中文较少，中文就会被切得比较碎，同样的内容要用更多 Token，既占上下文又更贵。这也是不同模型处理中文效率不同的原因之一。

分词器和模型是绑定的：模型只认识它自己分词器的编号，不能混用。

## 打个比方

分词器像一本"切菜手册"，规定了每种食材切成什么形状，厨师（模型）只认识按这本手册切出来的东西。

## 开发者要注意

- 很多模型提供商有 Token 计数工具或接口，可以在发请求前算出确切 Token 数。

## 相关概念

- [Token（词元）](./token.md)
- [词向量 / 嵌入](./embedding.md)
