---
id: deep-learning
title: "深度学习"
en: "Deep Learning"
group: base
priority: medium
related: [neural-network, transformer, scaling-laws]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 深度学习

> 用层数很多的神经网络做机器学习，"深度"指的就是层数多。

**分组**：基础原理 · **重要程度**：很常见，要懂

## 详细讲解

深度学习是机器学习的一个分支。神经网络的想法几十年前就有，但直到 2012 年前后才大爆发，主要是因为三件事凑齐了：互联网带来的海量数据、GPU 带来的巨大算力、以及训练深层网络的技术改进。

2012 年，一个叫 AlexNet 的深度网络在图像识别比赛中大幅领先，被视为深度学习时代的开端。之后语音识别、机器翻译、围棋（AlphaGo）等领域接连被深度学习突破。

深度学习最大的优势是能自动学习特征。以前做图像识别，要靠专家手工设计"什么样的像素组合算边缘"；深度学习直接从原始数据学，层数越多，能学到的特征越抽象、越复杂。

## 打个比方

浅层网络像只能看懂简单笔画的人，深层网络能从笔画一路理解到字、词、句子的含义。

## 开发者要注意

- 今天的大语言模型都是深度学习模型，几十到上百层的 Transformer。

## 相关概念

- [神经网络](./neural-network.md)
- [Transformer](./transformer.md)
- [Scaling Law 规模定律](./scaling-laws.md)
