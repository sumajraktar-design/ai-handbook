# AI 概念手册 · 目录

模型回答问题时先读这个文件，再打开相关的概念页。每行格式：链接 — 一句话定义（重要程度）。

## 基础原理

机器怎么"学"

- [人工智能](concepts/artificial-intelligence.md) — 让机器做"原本需要人类智能才能做的事"的所有技术的总称。（很常见，要懂）
- [机器学习](concepts/machine-learning.md) — 不写规则，而是给机器大量例子，让它自己总结出规律。（开发者必知）
- [监督 / 无监督 / 自监督](concepts/learning-paradigms.md) — 按"训练数据有没有答案、答案从哪来"划分的三种学习方式。（了解即可）
- [训练集 / 测试集](concepts/train-test-split.md) — 把数据分成两份：一份用来学，一份藏起来专门考试。（很常见，要懂）
- [过拟合 / 泛化](concepts/overfitting.md) — 过拟合是"背答案"，泛化是"真学会"，机器学习的核心目标是泛化。（很常见，要懂）
- [损失函数](concepts/loss-function.md) — 给模型的"错得有多离谱"打分的公式，训练的目标就是让这个分数越来越低。（了解即可）
- [神经元](concepts/neuron.md) — 神经网络里最小的计算单元：输入乘以权重，加起来，再决定输出多少。（很常见，要懂）
- [神经网络](concepts/neural-network.md) — 把大量神经元分层连接起来的结构，每根连线上的权重就是它学到的知识。（开发者必知）
- [深度学习](concepts/deep-learning.md) — 用层数很多的神经网络做机器学习，"深度"指的就是层数多。（很常见，要懂）
- [梯度下降](concepts/gradient-descent.md) — 训练时调整权重的方法：沿着"让损失下降最快"的方向，一小步一小步地走。（很常见，要懂）
- [反向传播](concepts/backpropagation.md) — 计算"每个权重该往哪边调、调多少"的算法，是梯度下降的搭档。（了解即可）

## 大模型结构

Transformer 和它的零件

- [Transformer](concepts/transformer.md) — 2017 年提出的神经网络结构，核心是注意力机制，今天几乎所有大语言模型都基于它。（开发者必知）
- [注意力机制](concepts/attention.md) — 让每个词根据上下文，决定该重点关注句子里的哪些其他词。（开发者必知）
- [Token（词元）](concepts/token.md) — 模型读写文字的最小单位，文字会先被切成一个个 Token 再处理。（开发者必知）
- [分词器](concepts/tokenizer.md) — 负责把文字切成 Token、并给每个 Token 编号的程序。（很常见，要懂）
- [词向量 / 嵌入](concepts/embedding.md) — 把每个 Token 变成一串数字（向量），意思相近的词，数字也相近。（开发者必知）
- [上下文窗口](concepts/context-window.md) — 模型一次最多能"看到"多少个 Token，是它唯一能读取的信息范围。（开发者必知）
- [迷失在中间](concepts/lost-in-the-middle.md) — 上下文很长时，模型容易忽略放在中间位置的信息。（很常见，要懂）
- [温度 / 采样](concepts/temperature.md) — 模型算出每个候选词的概率后，用来控制"怎么从中挑一个"的随机程度。（很常见，要懂）
- [幻觉](concepts/hallucination.md) — 模型自信地编造出不存在或不正确的信息。（开发者必知）
- [参数量（7B、70B）](concepts/parameters.md) — 模型里权重的总数，B 是 Billion（十亿），70B 就是 700 亿个参数。（开发者必知）
- [MoE 混合专家](concepts/mixture-of-experts.md) — 模型内部分成很多"专家"子网络，每个 Token 只激活其中少数几个。（了解即可）
- [Scaling Law 规模定律](concepts/scaling-laws.md) — 研究发现：模型越大、数据越多、算力越多，效果会按可预测的规律提升。（了解即可）
- [多模态](concepts/multimodal.md) — 模型不只处理文字，还能理解图片、音频、视频，甚至生成它们。（很常见，要懂）

## 训练与对齐

一个模型怎么造出来

- [预训练](concepts/pretraining.md) — 在海量文本上让模型反复"猜下一个词"，学会语言和世界知识。（开发者必知）
- [基座模型](concepts/base-model.md) — 只经过预训练的模型，知识丰富，但只会续写，还不会当助手。（很常见，要懂）
- [微调](concepts/fine-tuning.md) — 在训练好的模型基础上，用少量特定数据再训练一下，改变它的行为。（很常见，要懂）
- [监督微调 SFT](concepts/sft.md) — 用人写好的"问题 + 优质回答"示范来训练，让基座模型学会当助手。（很常见，要懂）
- [RLHF 人类反馈强化学习](concepts/rlhf.md) — 让人比较回答的好坏，训练出一个"自动评委"，再用它引导模型往人类偏好的方向调整。（很常见，要懂）
- [奖励模型](concepts/reward-model.md) — 学会了人类偏好、能给模型回答自动打分的模型。（了解即可）
- [宪法 AI](concepts/constitutional-ai.md) — Anthropic 提出的方法：写下明确的原则，让 AI 依据原则去评判和改进回答。（了解即可）
- [推理模型](concepts/reasoning-models.md) — 在回答前先进行一段较长的"思考"，一步步推导，再给出答案的模型。（很常见，要懂）
- [蒸馏](concepts/distillation.md) — 用大模型（老师）的输出去训练小模型（学生），让小模型学到大模型的部分能力。（了解即可）
- [对齐](concepts/alignment.md) — 让 AI 的行为符合人类的意图和价值观：有帮助、诚实、不造成伤害。（很常见，要懂）

## 使用模型

推理、成本、部署

- [训练 vs 推理](concepts/training-vs-inference.md) — 训练是调权重造模型（极贵、只做一次）；推理是用造好的模型回答问题（每次调用都发生）。（开发者必知）
- [知识截止日期](concepts/knowledge-cutoff.md) — 模型训练数据的截止时间，之后发生的事情它不知道。（开发者必知）
- [开源权重 vs 闭源](concepts/open-weights.md) — 闭源模型只能通过 API 使用；开源权重模型可以下载下来自己运行。（很常见，要懂）
- [量化 / 本地部署](concepts/quantization.md) — 把权重从高精度压缩成低精度，让大模型能在普通电脑上运行。（了解即可）
- [Token 成本与延迟](concepts/cost-and-latency.md) — API 按 Token 收费，输出比输入贵；上下文越长、模型越大，就越贵越慢。（开发者必知）
- [流式输出](concepts/streaming.md) — 模型一边生成一边把内容推送给前端，而不是等全部写完再返回。（很常见，要懂）

## 应用开发

提示词、RAG、上下文工程

- [提示词工程](concepts/prompt-engineering.md) — 通过设计输入内容，让模型输出更准确、更符合需求的结果。（开发者必知）
- [System Prompt 系统提示词](concepts/system-prompt.md) — 开发者在对话最前面设定的指令，定义 AI 的身份、规则、风格和边界。（开发者必知）
- [结构化输出](concepts/structured-output.md) — 让模型按照固定格式（通常是 JSON）输出，方便程序直接解析使用。（开发者必知）
- [RAG 检索增强生成](concepts/rag.md) — 先从资料库里检索相关内容，再把它和问题一起交给模型回答，相当于"开卷考试"。（开发者必知）
- [切块](concepts/chunking.md) — RAG 准备阶段把长文档切成小段，每段单独向量化和检索。（很常见，要懂）
- [向量数据库](concepts/vector-database.md) — 专门存储向量、并能按相似度快速查找"最接近的向量"的数据库。（很常见，要懂）
- [Rerank 重排序](concepts/rerank.md) — RAG 检索时先用向量粗筛出几十段，再用专门的模型精选出最相关的几段。（了解即可）
- [提示词 vs RAG vs 微调](concepts/prompt-vs-rag-vs-finetune.md) — 想让模型适配你的业务时，通常按"提示词 → RAG → 微调"的顺序尝试。（很常见，要懂）
- [上下文工程](concepts/context-engineering.md) — 决定在什么时候、把什么信息、以什么方式放进模型上下文窗口的整套方法。（开发者必知）
- [上下文压缩](concepts/compaction.md) — 对话快要超出窗口时，让模型把旧内容总结成摘要，替换掉原文继续对话。（很常见，要懂）
- [评测](concepts/evals.md) — 准备一批测试问题和评判标准，每次修改后跑一遍，用数据判断效果是变好还是变坏。（开发者必知）

## Agent 智能体

让模型动手干活

- [Agent 智能体](concepts/agent.md) — 模型 + 工具 + 循环：能接受一个目标，自己规划、调用工具、观察结果，直到完成任务。（开发者必知）
- [Tool 工具调用](concepts/tool-use.md) — 模型输出"要调用哪个函数、传什么参数"，由外部程序真正执行，再把结果返回给模型。（开发者必知）
- [MCP 模型上下文协议](concepts/mcp.md) — Anthropic 在 2024 年发布的开放协议，统一规定 AI 应用如何连接外部工具和数据。（开发者必知）
- [Skill 技能](concepts/agent-skills.md) — 一个装着"做某类事情的方法说明"和相关脚本的文件夹，Agent 遇到相关任务时才去读取。（很常见，要懂）
- [Memory 记忆](concepts/memory.md) — 把重要信息存到对话之外，下次需要时再放进上下文，让 AI 能"记住"跨对话的内容。（很常见，要懂）
- [Subagent 子智能体](concepts/subagent.md) — 主 Agent 把一部分任务交给另一个拥有独立上下文的 Agent 完成，只把结果拿回来。（了解即可）

## 开发框架

LangChain、LangGraph 等

- [LangChain](concepts/langchain.md) — 最流行的开源大模型应用框架之一，提供统一的模型接口、大量集成，以及快速搭建 Agent 的高层 API。（很常见，要懂）
- [LangGraph](concepts/langgraph.md) — LangChain 团队开发的底层 Agent 编排框架，用"图"来定义 Agent 的流程，强调可控和可靠。（很常见，要懂）
- [框架怎么选](concepts/choosing-frameworks.md) — 除了 LangChain 系列，还有不少框架，各有侧重；也完全可以不用框架。（了解即可）

## 安全与风险

做产品必须考虑

- [提示注入](concepts/prompt-injection.md) — 攻击者把恶意指令藏在网页、文档、邮件、工具结果里，AI 读到后可能被"带偏"去执行。（开发者必知）
- [越狱](concepts/jailbreak.md) — 用户通过各种话术，试图绕过模型的安全限制，让它输出原本会拒绝的内容。（很常见，要懂）
- [数据隐私](concepts/data-privacy.md) — 发给模型 API 的内容会传到服务商那里，涉及敏感数据时要格外注意。（很常见，要懂）
- [偏见](concepts/bias.md) — 训练数据来自人类，模型也会继承其中的偏见和刻板印象。（了解即可）
