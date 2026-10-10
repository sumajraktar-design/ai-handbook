---
id: jailbreak
title: "越狱"
en: "Jailbreak"
group: safe
priority: medium
related: [prompt-injection, alignment, system-prompt]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 越狱

> 用户通过各种话术，试图绕过模型的安全限制，让它输出原本会拒绝的内容。

**分组**：安全与风险 · **重要程度**：很常见，要懂

## 详细讲解

常见手法包括：角色扮演（"假装你是一个没有限制的 AI"）、虚构场景（"写一部小说，里面的角色详细解释了……"）、把有害请求拆成很多个看似无害的小问题、用编码或外语绕过检测等。

和提示注入的区别：越狱是用户自己在攻击模型的安全规则；提示注入是第三方内容在攻击用户或应用。

模型厂商通过对齐训练、输入输出分类器等方式持续防御，越狱和防御是一场持续的攻防。

## 打个比方

越狱像是用各种话术说服门卫放行；提示注入则像在送进来的包裹里夹了一张假的"放行条"。

## 开发者要注意

- 做面向公众的产品时，不要假设 System Prompt 里的限制一定不会被绕过，敏感能力要在代码层面加控制。

## 相关概念

- [提示注入](./prompt-injection.md)
- [对齐](./alignment.md)
- [System Prompt 系统提示词](./system-prompt.md)
