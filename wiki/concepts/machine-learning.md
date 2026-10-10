---
id: machine-learning
title: "机器学习"
en: "Machine Learning, ML"
group: base
priority: high
related: [learning-paradigms, loss-function, gradient-descent, overfitting, deep-learning]
demo: LinearFit
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 机器学习

> 不写规则，而是给机器大量例子，让它自己总结出规律。

**分组**：基础原理 · **重要程度**：开发者必知

## 动画演示

> 原手册中有可交互的动画（组件名 `LinearFit`），待迁移为 Vue 组件。

## 详细讲解

传统编程是"人写规则 + 输入数据 → 得到答案"。机器学习反过来："输入数据 + 已知答案 → 机器自己得出规则"。学到的这套规则就叫"模型"。

具体过程是：模型内部有很多可调节的数字（参数/权重），一开始是随机的，所以乱猜。每次猜完和正确答案比较，算出错了多少（损失），再把参数往"错得少一点"的方向微调（梯度下降）。重复几百万次后，参数停在一个好位置，模型就"学会"了。

机器学习能解决的典型问题：分类（这封邮件是不是垃圾邮件）、回归（这套房子值多少钱）、聚类（把用户分成几群）、生成（写一段文字、画一张图）。

## 打个比方

小孩认猫：没人给他规则手册，只是见过很多猫、被告诉"这是猫"，慢慢就会了。机器学习就是让电脑用同样的方式学习。

## 开发者要注意

- 机器学习的效果首先取决于数据：数据少、数据脏、数据有偏差，模型就学不好。业内常说"垃圾进，垃圾出"。
- 做 AI 应用开发一般不用自己训练模型，但理解训练过程能帮你判断模型为什么会犯某类错误。

## 相关概念

- [监督 / 无监督 / 自监督](./learning-paradigms.md)
- [损失函数](./loss-function.md)
- [梯度下降](./gradient-descent.md)
- [过拟合 / 泛化](./overfitting.md)
- [深度学习](./deep-learning.md)
