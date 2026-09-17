---
description: Agent分层记忆架构：5种生产模式对比（72.9%准确率@17s vs 66.9%@1.4s）、CrewAI/TiMem/LangGraph实现、EU AI Act合规张力。触发词：分层记忆/短期/中期/长期记忆分离
trigger: 分层记忆|hierarchical|三层记忆|global|team|private|scope tree|temporal memory
updated: 2026-09-18
---

# Agent 分层记忆架构 (Hierarchical Memory)

## 核心概念：记忆类型 ≠ 记忆架构

| 概念 | 职责 | 典型实现 |
|------|------|---------|
| **记忆类型** | 认知层：episodic/semantic/procedural/working | 知识分类 |
| **记忆架构** | 系统层：存储/检索/控制逻辑 | 存储引擎 |

> 来源：Atlan agent memory architectures

## 5种生产记忆架构模式

| 模式 | 准确率 | P95延迟 | 适用场景 |
|------|--------|---------|---------|
| Pattern 1: Zero-infrastructure | ~66.9% | 1.44s | 快速原型 |
| Pattern 2: Flat vector | ~72.9% | 17.12s | 成熟生产 |
| Pattern 3: Tiered | ~72.9% | 17.12s | 大规模 |
| Pattern 4: Knowledge graph | ~72.9% | 17.12s | 结构化领域 |
| Pattern 5: Enterprise context layer | ~72.9% | 17.12s | 企业治理 |

> 2026生产组合：Pattern 2/3（体验记忆）+ Pattern 5（组织语义权威）
> 来源：Atlan AI Labs benchmark

## 三层记忆架构（行业共识）

CrewAI、MemOS、Collaborative Memory三方独立收敛到同一设计：

```
Global（全局层）     → 团队级知识，所有agent共享
  ↓
Group/Role（角色层） → 任务级，同角色agent共享
  ↓
Private（私有层）   → agent私有，不可访问
```

### CrewAI scope trees实现

```python
from crewai import Memory, Agent

memory = Memory(recency_weight=0.5, recency_half_life_days=7)

# 私有记忆
researcher = Agent(
    role="Researcher",
    memory=memory.scope("/agent/researcher")
)

# 团队记忆
writer = Agent(
    role="Writer", 
    memory=memory.scope("/crew/writing-project")
)

# 多范围只读视图
view = memory.slice(
    scopes=["/agent/researcher", "/company/knowledge"],
    read_only=True
)
```

检索权重：语义相似度50% + 近因衰减30% + 重要性20%

## TiMem：时序层次记忆树 (ACL 2026)

**论文**：Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents
**精度**：LoCoMo 75.30%，LongMemEval-S 76.88%
**效率**：Recall context减少52.20%

### 架构：5级TMT（Temporal Memory Tree）

```
Level 1: Raw segments（原始对话片段）
Level 2: Event clusters（事件聚类）
Level 3: Summary abstractions（摘要抽象）
Level 4: Entity knowledge（实体知识）
Level 5: Persona profiles（人格画像）
```

### 核心设计原则

1. **时序包含作为一等约束**：TMT强制显式时序边界，防止跨时间窗口记忆混淆
2. **语义引导的层级合并**：LLM指令驱动合并，level-specific prompts，无需微调
3. **复杂度感知的检索**：Query Complexity Classifier决定从哪层检索

### Query复杂度分类

| 类别 | 判断标准 | 例子 |
|------|---------|------|
| **Simple Retrieval** | 单事实查询 | "Alice在哪工作？" |
| **Hybrid Retrieval** | 多事实整合 | "Alice这周参加了哪些会议？" |
| **Deep Retrieval** | 个性化推理 | "Alice适合什么职业方向？" |

> Deep Retrieval需要理解用户偏好/习惯/价值观，不能直接查表

### 与现有方案对比

| 方案 | 组织方式 | 时序 | 合并机制 |
|------|---------|------|---------|
| Mem0 | 语义聚类 | 元数据 | Learned routing |
| RAPTOR | 树形聚类 | 无 | 语义相似度 |
| TiMem | 时序树 | 一等约束 | LLM指令驱动 |

## EU AI Act × GDPR合规张力

> 来源：Oracle developers blog

| 法规 | 要求 | 矛盾点 |
|------|------|--------|
| **GDPR** | 删除权（个人数据） | 须物理删除 |
| **EU AI Act** | 10年审计追溯（高风险AI） | 须保留所有记录 |

**架构要求**：物理删除 + 审计日志分离存储

## 存储后端收敛趋势

"polyglot persistence"反模式（分离式向量DB+图DB+关系DB）正在消亡：

| 新趋势 | 方案 |
|--------|------|
| PostgreSQL系 | pgvector + JSON + audit log |
| MongoDB系 | Atlas Vector Search + 操作日志 |
| 统一平台 | Mem0 / MemOS |

## Hermes落地建议

### 当前状态

现有3个相关skill：
- `agent-long-context-memory`：Benchmark体系+Memory≠Context
- `memory-progressive-disclosure`：Tier 1/2/3注入架构
- `mem0-integration`：SQLite+TF-IDF轻量记忆

### 短期落地（本月）

1. **CrewAI scope trees** → 参考其私有/团队/全局三层隔离思想，优化Hermes subagent记忆隔离
2. **Query复杂度分类** → 引入Simple/Hybrid/Deep三级检索，Tier 2按复杂度决定检索深度
3. **合规张力记录** → fact_store增加deletion_flag字段，支持GDPR删除

### 中期考虑

| 场景 | 方案 |
|------|------|
| 多subagent协作 | MemOS（统一层+ACL+审计） |
| 企业上下文 | Atlan Pattern 5 |
| 长期人格记忆 | TiMem TMT |

## 来源

- [Atlan: Agent Memory Architectures 5 Patterns](https://atlan.com/know/agent-memory-architectures)
- [TiMem ACL 2026](https://aclanthology.org/2026.findings-acl.1091.pdf)
- [Zylos: Multi-Agent Memory Architectures](https://zylos.ai/research/2026-03-09-multi-agent-memory-architectures-shared-isolated-hierarchical)
- [Oracle: Agent Memory GDPR/EU AI Act](https://blogs.oracle.com/developers/agent-memory-why-your-ai-has-amnesia-and-how-to-fix-it)
- [AWS: Persistent Memory S3 Vectors](https://aws.amazon.com/blogs/storage/building-persistent-memory-for-multi-agent-ai-systems-with-amazon-s3-vectors/)
- [CrewAI Memory Documentation](https://docs.crewai.com/en/concepts/memory)
