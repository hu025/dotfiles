---
name: openviking
description: OpenViking — 火山引擎开源 Context Database，viking:// 虚拟文件系统记忆范式，文件树分层加载（L0/L1/L2），VLDB 2026 论文支撑，LoCoMo 基准 80-83% 准确率。与 Hermes 官方合作（Partner Projects）。
triggers:
  - OpenViking
  - viking://
  - context database
  - agent memory filesystem
---

# OpenViking — Context Database for AI Agents

## 核心价值

开源 Context Database（Apache-2.0，AGPLv3 部分），将 AI Agent 的记忆/资源/技能统一管理为虚拟文件系统，用 `viking://` URI 寻址。

**关键创新**：文件系统范式替代向量数据库黑盒；三级分层加载（L0/L1/L2）节省 token；目录递归检索；检索轨迹可观测；会话自动转化为记忆。VLDB 2026 论文支撑。

**Benchmark**：LoCoMo 准确率 24%→82%（原生 Hermes 33%→83%）；token 降低 34-91%；延迟降低 58-66%。

**Partner 项目**：与 Hermes Agent 官方合作（Partner Projects 列表）。

---

## 架构

```
viking://
├── resources/          # 知识/文档/代码库（长期静态）
│   └── {project}/
│       ├── .abstract   # L0: ~256 chars 抽象层
│       ├── .overview   # L1: ~4000 chars 概览层
│       └── docs/
│           └── api.md # L2: 全量，按需加载
├── user/
│   └── {user_id}/
│       ├── memories/   # 记忆：preferences/identity/cases/trajectories
│       ├── resources/  # 私有资源
│       ├── skills/     # 私有技能
│       └── sessions/   # 会话记录
└── agent/
    └── skills/         # 账户级共享技能
```

### 三层加载

| 层 | 名称 | 默认限制 | 用途 |
|----|------|----------|------|
| L0 | Abstract | 256 chars | 向量搜索/快速过滤 |
| L1 | Overview | 4000 chars | Rerank/内容导航 |
| L2 | Detail | 无统一限制 | 全量内容，按需加载 |

### 检索流程

```
Query → Intent Analysis(LLM) → Hierarchical Retrieval → Rerank → Results
                            ↓
              find() 简单查询（无意图分析，低延迟）
              search() 复杂任务（需会话上下文，0-5个TypedQuery）
```

### 内置记忆类型

- **User/Environment**: `profile`, `preferences`, `entities`, `events`
- **Assistant Identity**: `identity`, `soul`
- **Task/Learning**: `cases`, `trajectories`, `experiences`, `tools`, `skills`

---

## 安装

```bash
pip install openviking --upgrade
openviking-server init      # 交互式向导：providers/models/ov.conf
openviking-server doctor    # 验证配置
openviking-server           # 启动（后台：nohup openviking-server > openviking.log 2>&1 &）
```

Python SDK:
```python
from openviking import OpenVikingClient

client = OpenVikingClient(base_url="http://localhost:8080")

# 简单查询
results = await client.find(query="OAuth authentication", target_uri="viking://resources/")

# 复杂任务
session_info = await client.create_session()
results = await client.search(query="Help me create an RFC document", session_id=session_info.id)

# 目录操作
await client.ls(uri="viking://resources/")
await client.read(uri="viking://resources/docs/api.md")
await client.abstract(uri="viking://~/memories/")
```

---

## 与 Hermes 集成思路

1. **记忆层对齐**：OpenViking 的 `viking://user/{user_id}/memories` 与 Hermes 记忆系统概念对齐
2. **Partner 项目**：OpenViking 明确列出 Hermes Agent 为官方 Partner
3. **会话→记忆**：session commit 后异步提取用户偏好和 Agent 经验到长期记忆
4. **分层加载**：L0/L1/L2 机制可用于 Hermes 渐进式上下文披露（memory-progressive-disclosure 技能已存在，可整合）
5. **检索轨迹**：可观测的检索过程可用于调试 Hermes 记忆检索

---

## 局限

- AGPLv3 主许可证（核心）；crates/ov_cli 和 examples 为 Apache 2.0
- 仍处于早期阶段
- 需要 Python 3.10+
- 意图分析依赖 LLM（有额外 token 消耗）

---

## 来源

- GitHub: https://github.com/volcengine/OpenViking
- Docs: https://docs.openviking.ai/
- Paper: https://arxiv.org/abs/2605.29640 (VikingMem, VLDB 2026)
- Studio: https://openviking.ai/studio
