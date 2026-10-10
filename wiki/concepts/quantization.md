---
id: quantization
title: "量化 / 本地部署"
en: "Quantization / Local Deployment"
group: deploy
priority: low
related: [parameters, open-weights, cost-and-latency]
sources: [raw/handbook/ai-handbook-v2.html]
updated: 2026-10-11
---

# 量化 / 本地部署

> 把权重从高精度压缩成低精度，让大模型能在普通电脑上运行。

**分组**：使用模型 · **重要程度**：了解即可

## 详细讲解

模型权重默认通常是 16 位浮点数。量化就是把它们压缩成 8 位、4 位甚至更低。4 位量化后，模型体积大约只剩原来的四分之一，一个原本需要 140GB 的 70B 模型，可以压到 40GB 左右。

代价是精度损失，模型会变笨一点。一般 8 位几乎看不出差别，4 位在多数任务上仍然可用，再低就明显下降了。

常用的本地运行工具有 Ollama、llama.cpp、LM Studio 等，常见的量化文件格式有 GGUF。服务器端的高性能推理框架有 vLLM 等。

## 打个比方

把高清照片压缩成较小的 JPG：文件小了很多，肉眼看差别不大，但放大细看能发现损失。

## 开发者要注意

- 想在自己电脑上体验，可以先装 Ollama 跑一个几 B 参数的小模型。
- 苹果芯片的统一内存对本地跑模型比较友好。

## 相关概念

- [参数量（7B、70B）](./parameters.md)
- [开源权重 vs 闭源](./open-weights.md)
- [Token 成本与延迟](./cost-and-latency.md)
