---
id: rlhf
title: "RLHF 人类反馈强化学习"
en: "Reinforcement Learning from Human Feedback"
group: train
priority: medium
related: [reward-model, sft, constitutional-ai, alignment, reasoning-models]
demo: RLHF
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# RLHF 人类反馈强化学习

> 让人比较回答的好坏，训练出一个"自动评委"，再用它引导模型往人类偏好的方向调整。

**分组**：训练与对齐 · **重要程度**：很常见，要懂

## 动画演示

> 原手册中有可交互的动画（组件名 `RLHF`），待迁移为 Vue 组件。

## 详细讲解

RLHF 分两步。第一步，训练奖励模型：让模型对同一个问题生成多个回答，由人来比较"A 和 B 哪个更好"，收集大量这样的比较数据，训练出一个能给回答打分的奖励模型。

第二步，强化学习：让模型大量生成回答，奖励模型给每个回答打分，模型根据分数调整权重，越来越倾向于写出高分回答。这一步常用的算法叫 PPO，后来也出现了 DPO 等更简单的方法，可以直接从偏好数据学习，不必单独训练奖励模型。

为什么不直接让人打分？因为强化学习需要几十万甚至上百万次评分，人工来不及。所以先用少量人类判断训练出评委，再让评委大规模打分。

RLHF 让模型变得更有帮助、更诚实、更会拒绝有害请求。它的一个已知副作用是：模型可能学会讨好评委，比如过度迎合用户、回答写得很长显得更认真。

## 打个比方

训练小狗：做对了给零食，做错了不给。重复多次后，它就学会了你想要的行为。

## 开发者要注意

- 理解 RLHF 能帮你理解模型为什么有时过于客气、啰嗦或谨慎，这些往往是训练偏好留下的痕迹。

## 相关概念

- [奖励模型](./reward-model.md)
- [监督微调 SFT](./sft.md)
- [宪法 AI](./constitutional-ai.md)
- [对齐](./alignment.md)
- [推理模型](./reasoning-models.md)
