---
id: neural-network
title: "神经网络"
en: "Neural Network"
group: base
priority: high
related: [neuron, deep-learning, transformer, backpropagation]
demo: NeuralNetwork
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 神经网络

> 把大量神经元分层连接起来的结构，每根连线上的权重就是它学到的知识。

**分组**：基础原理 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `NeuralNetwork`），待迁移为 Vue 组件。

## 详细讲解

神经网络通常分成三部分：输入层（接收原始数据，比如像素或词向量）、若干隐藏层（逐层加工信息）、输出层（给出结果，比如"猫 90%、狗 10%"）。

信息从输入层一层层往后传，叫"前向传播"。每一层都在前一层的基础上提取更抽象的特征。以识图为例：前几层学会识别边缘和线条，中间层把它们组合成眼睛、耳朵，后面的层判断出"这是猫"。这种分工不是人设计的，而是训练中自己形成的。

神经网络有很多种结构：处理图像的卷积神经网络（CNN）、早期处理序列的循环神经网络（RNN），以及现在统治语言领域的 Transformer。结构决定了神经元之间"怎么连"。

## 打个比方

一个工厂流水线：每个车间（层）都对半成品做一点加工，原材料（像素）一路加工到最后变成成品（判断结果）。

## 开发者要注意

- 你不需要会手写神经网络也能做 AI 应用，但要知道：模型的所有"知识"都是这些权重数字，它们没法像数据库那样直接查询或修改某一条。

## 相关概念

- [神经元](./neuron.md)
- [深度学习](./deep-learning.md)
- [Transformer](./transformer.md)
- [反向传播](./backpropagation.md)
