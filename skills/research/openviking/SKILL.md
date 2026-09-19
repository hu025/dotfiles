---
name: openviking
description: OpenViking — ByteDance self-evolving context database for AI agents. L0/L1/L2三层上下文分层，viking:// URI文件系统，LoCoMo 80-83%准确率，AGPLv3，~35K stars。
trigger: 上下文数据库 / 记忆系统 / 知识管理 / VikingURI / 分层上下文 / agent memory
trigger_en: context database / memory system / knowledge management / tiered context
trigger_zh: 上下文数据库 / 记忆系统 / 分层上下文加载 / VikingURI
trigger_tags: [memory, context-database, tiered-context, self-evolving]
category: agent-infrastructure
framework: volcengine/openviking
stars: 35000
license: AGPLv3
language: Python
updated: 2026-09-28
---

# OpenViking — Self-Evolving Context Database for AI Agents

## 核心定位

OpenViking 是字节跳动火山引擎 Viking 团队开源的上下文数据库（Context Database），将 Agent 的记忆（Memory）、资源（Resources）和技能（Skills）统一存储为虚拟文件系统，通过 `viking://` 协议让 Agent 以 `ls`、`tree`、`find` 等命令浏览上下文，而非查询黑盒向量数据库。L0/L1/L2 三层上下文分层加载，LoCoMo 基准 80-83% 准确率（相比原生内存 24-57%），AGPLv3 开源，~35K GitHub stars。

**一句话定位**：把上下文当数据管理，而非当 prompt 填充。

## 核心概念

### Viking URI — 统一命名空间

所有上下文（记忆/资源/技能）共享同一个虚拟文件系统：
```
viking://memory/          — Agent 长期记忆
viking://resources/       — 知识资源（RAG 文档等）
viking://skills/          — Agent 技能
viking://memory/sessions/ — 具体会话记录
```

Agent 像操作真实文件系统一样操作上下文，`ov ls`、`ov tree`、`ov find` 替代向量检索。

### L0/L1/L2 三层上下文分层

每个条目写入时自动生成三层：
- **L0（Abstract）**：一句话摘要，用于快速相关性判断
- **L1（Overview）**：核心信息和适用场景，用于规划
- **L2（Details）**：完整原始数据，仅在需要时读取

**效果**：输入 token 减少 34.3-91.0%，查询延迟降低 58.45-66.10%。

### 目录递进检索（Directory Recursive Retrieval）

1. 向量搜索定位最高评分目录
2. 按层级逐层深入
3. 结果附带周围上下文
4. 每步检索轨迹可观测、可调试

### 可观测检索（Observable Retrieval）

每次检索保留目录浏览轨迹，结果可追溯——当结果出错时，可精确回溯哪条路径产生了错误。

### 会话 → 记忆（Session → Memory）

会话提交后，OpenViking 异步提取：
- 用户偏好 → 长期记忆
- Agent 经验 → 技能更新

## 基准数据

### 用户记忆（LoCoMo）
| Agent 集成 | 原生准确率 | OpenViking 准确率 | Token 节省 |
|------------|------------|-------------------|-----------|
| Agent A | 24% | 80% | 34.3-91.0% |
| Agent B | 42% | 82% | 同上 |
| Agent C | 57% | 83% | 同上 |

### Agent 经验（tau2-bench）
| 任务类型 | 无记忆提升 | 有记忆提升 |
|----------|------------|------------|
| Retail | +6.87pp | — |
| Airline | +11.87pp | — |

## 上下文工程公式（OpenViking 定义）

```
Context Engineering = 
  可靠推理约束（Constraints）
  + 完整信息组织（Organization）
  + 有效上下文推荐（Recommendation）
  + 全生命周期记忆（Memory）
  + 可追溯自我进化（Learning）
```

## 上下文数据库 vs 其他范式

| 能力 | OpenViking | 向量数据库 | 真实文件系统 |
|------|------------|-----------|------------|
| 数据操作 | 增删查改 | 增删查改 | 增删改/查依赖外部 |
| 语义检索 | ✓（向量搜索） | ✓（核心能力） | ✗ |
| 关键词检索 | ✓（稀疏向量/grep） | ✓ | ✓（grep） |
| 层级结构 | 保暴露给 Agent | 通常不保留 | 原生支持 |
| 自动解析摘要 | ✓ L0/L1/L2 | 通常无 | ✗ |
| Agent 读取 | ls/tree/find/abstract/overview/read | ✗ | 可遍历但缺语义处理 |
| 原生记忆插件 | ✓ | ✗ | ✗ |

## Agent 集成

官方支持：
- Claude Code ✓
- Codex ✓
- OpenClaw ✓
- **Hermes ✓**
- Cursor ✓
- TRAE / TRAE CN / TraeCode CLI 2.0 ✓
- OpenCode ✓
- pi ✓
- Agent Plugins 1.0 ✓
- MCP clients ✓
- LangChain / LangGraph ✓

## 上下文分层加载 — Agent 操作路径

```
ov add-resource <doc>   # 添加文档，自动分解为三层
ov tree <uri>           # 查看结构
ov find <query>         # 定位入口点
ov abstract <uri>       # 读摘要（L0）
ov overview <uri>       # 读概览（L1）
ov read <uri>           # 仅在证据不足时读原文（L2）
```

**Agent 应遵循路径**：root structure → search → tree → abstract → overview → read（按需深入）

## VikingMem 论文

OpenViking 开源了 VikingMem 论文描述的核心能力子集：

> **VikingMem: A Memory Base Management System for Stateful LLM-based Applications**
> Jiajie Fu, Junwen Chen, Mengzhao Wang, et al.
> arXiv:2605.29640, 2026. Accepted by **VLDB 2026**.

## 部署方式

### 开源版（当前仓库）
- AGPLv3，无功能门控
- 无需账号、无激活密钥
- 完全本地/自托管

### 托管版（路线图）
- 分布式部署
- 官方支持
- BYOC 支持

### 离线/气隙模式
- 完全离线环境可用
- 面向受监管行业

## 与 Mem0 / Letta / Zep 对比

OpenViking 不只是记忆库，而是**上下文数据库**——记忆是内置用例之一，但核心是统一的上下文管理层。

| 维度 | OpenViking | Mem0 | Letta | Zep |
|------|-----------|------|-------|-----|
| 协议/接口 | Viking URI | API | API | API |
| 三层分层 | ✓ L0/L1/L2 | ✗ | ✗ | ✗ |
| Hermite 集成 | ✓ 官方 | ✓ | ✓ | ✓ |
| 知识 RAG | ✓ 统一管理 | 分离 | 分离 | 分离 |
| 可追溯检索 | ✓ | ✗ | 部分 | 部分 |
| 许可 | AGPLv3 | Apache 2.0 | MIT | MIT |

## 对 Hermes 的价值

### 立即可用
1. **记忆系统升级**：OpenViking 的 L0/L1/L2 分层完全替代 Hermes 当前的事实存储方案
2. **知识管理**：ETF 分析结果/财经知识可用 `viking://resources/` 统一管理
3. **会话 → 记忆自动流**：cron 任务会话自动沉淀为长期记忆，减少重复研究

### 长期架构参考
1. **上下文数据库范式**：Hermes 可将 skill/knowledge/memory 统一为上下文数据库设计
2. **可追溯检索**：每个上下文引用附带检索轨迹，Hermes skill 调用可参考
3. **三层分层思想**：L0/L1/L2 可应用于 Hermes 记忆系统的分层读取策略

## 关键引用

- GitHub: https://github.com/volcengine/OpenViking
- 官网: https://openviking.ai/
- 博客: https://blog.openviking.ai/post/openviking-context-database/
- VikingMem 论文: https://arxiv.org/abs/2605.29640
- CLI: `ov`（OpenViking CLI）
