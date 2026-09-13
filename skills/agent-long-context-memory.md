---
description: AI Agent长期记忆技术：Memory vs Context二分法、MCP向量数据库、记忆压缩/选择性遗忘、三大基准(LoCoMo/LongMemEval/BEAM)、2026年新框架。触发词：记忆/上下文/长期记忆/多会话
trigger: 记忆|上下文|长期记忆|多会话|context|memory|recall|persistence
updated: 2026-09-13
---

# Agent Long-Context Memory 技术

## 核心范式转变

**Memory ≠ Context**

| 层 | 回答问题 | 典型内容 |
|---|---|---|
| **Memory** | 什么需要持久化？ | 偏好、事实、事件、决策、流程、摘要 |
| **Retrieval** | 什么需要被找到？ | 文档块、实体、关系、图路径、旧对话 |
| **Context** | 模型现在该看到什么？ | 指令+证据+状态+工具的最小有用集合 |

> **核心洞见**：Memory是被持久化的信息；Context是模型实际使用的工作集。Memory→必须经过检索→排序→过滤→转换→才能成为Context。
> 来源：[Graphlit Memory vs Context](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)

## 三大基准体系

### LoCoMo
- 1,540题，4类：单跳/多跳/开放域/时序记忆
- Mem0新算法得分：**92.5**，平均6,956 tokens/查询
- 论文：https://github.com/snap-research/locomo

### LongMemEval
- 500题，6类：单会话用户/助手/偏好回忆、知识更新、时序推理、多会话回忆
- Mem0得分：**94.4**，平均6,787 tokens/查询
- 论文：https://github.com/xiaowu0162/longmemeval

### BEAM
- 1M和10M token规模测试，10个类别
- Mem0：1M规模**64.1**，10M规模**48.6**
- 核心发现：长上下文模型在长对话中仍显著衰退
- 论文：https://github.com/mohammadtavakoli78/BEAM

## 记忆架构分类（2026）

### 记忆API层
- **Mem0**：管理型长期记忆+个性化，多跳推理+29.6分，时序推理+23.1分
  - 新算法：单次ADD-only提取（Agent生成事实与用户陈述同等权重）+多信号检索（语义+关键词+实体三路并行）
  - 对比：LoCoMo 92.5 vs Zep 80.32 vs Letta 74.0
- **Supermemory**：用户上下文学习+RAG，图记忆+用户画像
- **Membase**：记忆为episode，实体提取，知识图链接
- **Memory Store**：跨AI工具通用记忆

### 时序知识图谱层
- **Zep**：时序知识图+实体+关系+事实+episode+有效期
  - LoCoMo 80.32%，延迟189ms，可配置到83%
- **Graphiti**（Zep出品）：动态对话和业务数据的时序感知图引擎
- **Graphlit**：操作上下文层，关注来源+权限+引用

### 框架原生记忆
- **LangMem**：热路径记忆工具+后台记忆管理器（提取/合并/搜索）
- **CrewAI**：统一记忆API，LLM辅助scope/category/importance推理
- **LlamaIndex Memory**：静态记忆块+事实提取记忆+向量记忆

### 上下文平台（企业级）
- **Atlan**：上下文层，Enterprise Data Graph，AI文本到SQL准确率+38%
- **Graphlit**：跨Slack/GitHub/Gmail/Jira/Linear/Notion/PDF/会议/工单/代码/Web推理，来源可追溯+权限

### 特殊用途
- **Hindsight**：编码agent记忆
- **mem9**：轻量级持久记忆
- **Kumiho**：图原生溯源
- **Memora**：轻量级
- **Redis Agent Memory**：工作内存(Redis内存)+长期内存(Redis向量搜索)
- **mem0-integration**（Hermes现有）：SQLite+TF-IDF轻量方案，官方Mem0为升级路径

## 关键新发现

### 1. Self-Editing Memory成标配
- 高端记忆系统：Agent或后台进程可写入/合并/修正/剪枝记忆
- 不再是append-only日志
- 新问题：**谁有权更新记忆？记忆冲突时哪个来源胜出？如何审计？**

### 2. Temporal Memory成核心
- "Alice拥有账户"：若Alice上月已转团队，信息过时危险
- 解决方案：事件时钟（event clock）— 记录事实如何变成真、何时变、哪个来源主张

### 3. 上下文超过10M token时性能骤降
- BEAM 10M规模得分48.6 vs 1M规模64.1
- 长上下文模型不是银弹

### 4. Context Engineering成为产品
- 上下文组装 > 记忆存储
- 基准：Anthropic Context Management，OpenAI Agents SDK sandbox memory

## Hermes现状分析

现有方案：`mem0-integration`（SQLite+TF-IDF）已存在
- 需评估：是否升级到官方Mem0（需OpenAI API Key）
- 新发现：Mem0的多信号检索架构值得参考
- 时序推理缺口：当前方案无时序知识图能力

## 落地建议

1. **短期**：更新mem0-integration技能文档，补充多信号检索+时序记忆架构
2. **中期**：若需要跨工具记忆共享，研究Membase或Memory Store
3. **企业场景**：关注Graphlit/Atlan的Context Layer方案

## 来源

- [Graphlit: Memory vs Context](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)
- [Mem0: State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Atlan: Best AI Agent Memory Frameworks 2026](https://atlan.com/know/best-ai-agent-memory-frameworks-2026)
- [Agent Memory Paper List (1k stars)](https://github.com/Shichun-Liu/Agent-Memory-Paper-List)
- [LoCoMo Benchmark](https://github.com/snap-research/locomo)
- [BEAM Benchmark](https://github.com/mohammadtavakoli78/BEAM)
- [LongMemEval](https://github.com/xiaowu0162/longmemeval)
