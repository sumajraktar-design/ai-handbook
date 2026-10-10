---
id: backpropagation
title: "反向传播"
en: "Backpropagation"
group: base
priority: low
related: [gradient-descent, loss-function, neural-network]
demo: NeuralNetwork
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 反向传播

> 计算"每个权重该往哪边调、调多少"的算法，是梯度下降的搭档。

**分组**：基础原理 · **重要程度**：了解即可

## 动画演示

> 原手册中有可交互的动画（组件名 `NeuralNetwork`），待迁移为 Vue 组件。

## 详细讲解

一个大模型有几十亿个权重。损失出来之后，我们需要知道每一个权重对这次错误负多少责任，才能决定怎么调整它。反向传播就是高效计算这个的方法。

它的思路是从输出层开始，把误差一层层往回传：最后一层的权重对错误的贡献最直接，先算出来；再根据它推算前一层的贡献，依此类推。数学上用的是微积分里的链式法则。

所以一次训练步骤是：前向传播（算出预测）→ 计算损失 → 反向传播（算出每个权重的梯度）→ 梯度下降（更新权重）。

## 打个比方

一个项目出了问题，从最终结果开始往回追责：直接负责人担多少，他的上游又各担多少，一层层算到每个人头上。

## 开发者要注意

- 现在的框架（PyTorch 等）会自动完成反向传播，开发者几乎不用手写。

## 相关概念

- [梯度下降](./gradient-descent.md)
- [损失函数](./loss-function.md)
- [神经网络](./neural-network.md)
