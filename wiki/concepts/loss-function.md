---
id: loss-function
title: "损失函数"
en: "Loss Function"
group: base
priority: low
related: [gradient-descent, backpropagation, machine-learning]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 损失函数

> 给模型的"错得有多离谱"打分的公式，训练的目标就是让这个分数越来越低。

**分组**：基础原理 · **重要程度**：了解即可

## 详细讲解

模型每做一次预测，损失函数就会把预测值和正确答案比较，算出一个数字。数字越大表示错得越多。

不同任务用不同的损失函数。预测数值（比如房价）常用均方误差：预测值和真实值的差，平方后取平均。分类任务和大模型常用交叉熵：如果正确答案是"猫"，模型给"猫"的概率越低，损失越大。

大模型预训练时的损失，就是"模型对真实的下一个词给出的概率有多低"。损失下降，意味着模型越来越擅长预测下一个词。

## 打个比方

损失函数就像考试的扣分规则。梯度下降则是根据扣分情况，决定下次怎么改进。

## 开发者要注意

- 训练过程中看"损失曲线"是判断训练是否正常的第一手段：持续下降是好事，突然飙升往往说明出了问题。

## 相关概念

- [梯度下降](./gradient-descent.md)
- [反向传播](./backpropagation.md)
- [机器学习](./machine-learning.md)
