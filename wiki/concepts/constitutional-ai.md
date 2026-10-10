---
id: constitutional-ai
title: "宪法 AI"
en: "Constitutional AI / RLAIF"
group: train
priority: low
related: [rlhf, alignment, system-prompt]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 宪法 AI

> Anthropic 提出的方法：写下明确的原则，让 AI 依据原则去评判和改进回答。

**分组**：训练与对齐 · **重要程度**：了解即可

## 详细讲解

传统 RLHF 高度依赖人工标注，成本高，而且标注员的判断不一定一致。宪法 AI 的思路是：先写一份明确的原则清单（"宪法"），比如"选择更诚实、更无害的回答"，然后让模型自己根据这些原则批评和修改回答，或者比较两个回答哪个更符合原则。

这些由 AI 生成的偏好数据再用于训练，所以这类方法也叫 RLAIF（基于 AI 反馈的强化学习）。

它的好处是：原则写在纸面上，行为依据更透明；减少了对大量人工标注的依赖；也减少了人类标注员接触有害内容的需要。Anthropic 用这类方法训练 Claude，其他机构也有类似的做法。

## 打个比方

不再靠领导一份份审批，而是写一本公司章程，让员工对照章程自查自改。

## 开发者要注意

- 写 System Prompt 时，给出清晰的原则和理由，往往比堆一长串禁止事项效果更好，思路相通。

## 相关概念

- [RLHF 人类反馈强化学习](./rlhf.md)
- [对齐](./alignment.md)
- [System Prompt 系统提示词](./system-prompt.md)
