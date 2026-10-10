---
id: open-weights
title: "开源权重 vs 闭源"
en: "Open-weight vs Closed"
group: deploy
priority: medium
related: [quantization, data-privacy, parameters]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 开源权重 vs 闭源

> 闭源模型只能通过 API 使用；开源权重模型可以下载下来自己运行。

**分组**：使用模型 · **重要程度**：很常见，要懂

## 详细讲解

闭源模型（如 Claude、GPT、Gemini）的权重不公开，只能通过官方 API 或产品使用。优点是通常能力最强、不用管服务器；缺点是数据要发给服务商、依赖对方的价格和政策。

开源权重模型（如 Llama、Qwen、DeepSeek、Mistral 的部分模型）公开了权重文件，你可以下载到自己的服务器或电脑上运行、微调。优点是可控、数据不出本地、长期成本可能更低；缺点是需要硬件和运维能力，能力通常略逊于最前沿的闭源模型。

严格来说，很多模型只是"开放权重"，并没有公开训练数据和完整训练代码，许可协议也各有限制（比如商用条件），所以"开源"这个说法有争议。

## 打个比方

闭源像去餐厅吃饭，方便但只能点菜单上的；开源权重像拿到了菜谱和食材，可以自己在家做、随意改，但得自己下厨。

## 开发者要注意

- 公司有严格数据合规要求时，开源权重 + 本地部署是常见选择。
- 用开源模型前一定要看许可协议。

## 相关概念

- [量化 / 本地部署](./quantization.md)
- [数据隐私](./data-privacy.md)
- [参数量（7B、70B）](./parameters.md)
