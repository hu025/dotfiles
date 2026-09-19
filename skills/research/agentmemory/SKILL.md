# agentmemory — 技能文档

## 基本信息

- **名称**: agentmemory
- **类型**: AI 记忆引擎 + MCP 服务器
- **GitHub**: rohitg00/agentmemory (28k stars, Apache 2.0)
- **官网**: agent-memory.dev
- **最新版本**: v0.9.29
- **触发词**: agent记忆、跨会话记忆、MCP记忆工具、coding agent记忆
- **Hermes集成**: 原生支持（`integrations/hermes/`目录 + config.yaml配置）

---

## 核心价值

> 给 coding agent 装上跨会话记忆，95.2% R@5，仅 1,900 tokens/session，费用 $10/年。

**核心定位**: 记忆引擎 + MCP 服务器，不是向量数据库包装器。

---

## 核心架构

### 三层构建

| 层次 | 名称 | 说明 |
|------|------|------|
| 01 | Hooks | 12个自动捕获钩子，session/prompt/tool/stop 全链路 |
| 02 | Recall | BM25+向量+知识图三元组混合检索，重排后返回 |
| 03 | Consolidate | LLM压缩，session结束时自动：观测→语义记忆→去重→衰减→审计 |

### 技术栈

- **底层引擎**: iii engine（每个记忆操作 = worker/function/trigger）
- **存储**: JSON文件 + SQLite（观测性），零外部数据库
- **索引**: BM25 + 向量（Xenova/all-MiniLM-L6-v2本地推理） + 知识图
- **协议**: MCP JSON-RPC (localhost:3111) + 130条 REST API

---

## 关键指标

| 指标 | 数值 | 说明 |
|------|------|------|
| R@5 (LongMemEval-S) | **95.2%** | 超越 Mem0(68.5%)/Letta(83.2%)/Zep(63.8%) |
| Token/会话 | **~1,900** | 比完整上下文重放减少 92% |
| 年成本 | **~$10** | 有本地嵌入时 $0 |
| MCP工具数 | **54个** | 完整记忆操作面 |
| REST端点 | **130个** | HTTP优先设计 |
| 外部依赖 | **0** | 自包含，无需 Qdrant/Postgres/Neo4j |

---

## 核心功能

### 12个自动捕获钩子

- session start/end
- prompt in/out
- tool call（所有工具调用）
- tool result
- stop

每个 hook 自动将观测写入记忆管道，无需胶水代码。

### 54个 MCP 工具（按类别）

**记忆操作**: `memory_save` / `memory_recall` / `memory_smart_search` / `memory_delete`

**会话管理**: `memory_sessions` / `memory_session_get` / `memory_session_export`

**治理**: `memory_governance_*` / `memory_audit` / `memory_snapshot_create`

**图谱**: `memory_graph_*` / `memory_knowledge_graph`

**工作项**: `memory_action_create` / `memory_action_update` / `memory_frontier` / `memory_next` / `memory_lease`

**其他**: `memory_lessons_*` / `memory_mesh_*` (P2P同步) / `memory_export`

### 记忆生命周期

1. **观测（Observation）**: 原始 hook 数据，时间戳+来源+agentId
2. **语义记忆（Semantic Memory）**: LLM 压缩后去重合并
3. **衰减（Decay）**: retention scoring 自动过期低价值记忆
4. **审计（Audit）**: 全链路可追溯

### 竞争差异

| | agentmemory | Mem0 | Letta | Built-in(MEMORY.md) |
|--|-------------|------|-------|---------------------|
| R@5 | **95.2%** | 68.5% | 83.2% | N/A |
| Token/会话 | **~1,900** | varies | varies | 22K+ |
| 实时查看器 | **3113端口** | 云端 | 云端 | 无 |
| 自托管 | ✅ | 可选 | 可选 | ✅ |
| 零外部DB | ✅ | ❌Qdrant/pgvector | ❌Postgres+vector | ✅ |

---

## Hermes 集成方式

### 方式一：MCP JSON（推荐，43工具）

```bash
# 终端1：启动记忆服务器
npx @agentmemory/agentmemory

# ~/.hermes/config.yaml 添加：
mcp:
  servers:
    agentmemory:
      command: npx
      args: ["-y", "@agentmemory/mcp"]
      env:
        AGENTMEMORY_URL: http://localhost:3111
```

### 方式二：深度插件集成（6个hook）

```bash
# 复制插件到 Hermes
cp -r integrations/hermes ~/.hermes/plugins/agentmemory

# 启用：pre-LLM context injection + turn capture + MEMORY.md镜像
```

---

## Token 节省分析

### LongMemEval-S 实测（来自 benchmark/QUALITY.md）

| 观测数 | MEMORY.md tokens | agentmemory tokens | 节省 | MEMORY.md可达 |
|--------|-----------------|-------------------|------|---------------|
| 240 | 12,000 | 3,142 | **74%** | 83% |
| 500 | 25,000 | 3,142 | **87%** | 40% |
| 1,000 | 50,000 | 3,142 | **94%** | 20% |
| 5,000 | 250,000 | 3,142 | **99%** | 4% |

> MEMORY.md 200行上限导致 240 观测时已丢失最近内容；agentmemory 始终检索全部语料。

### 年费用对比

| 方案 | Tokens/年 | 费用/年 |
|------|-----------|--------|
| 完整上下文重放 | 19.5M+ | 不可能（超窗口） |
| LLM摘要 | ~650K | ~$500 |
| agentmemory | ~170K | **~$10** |
| agentmemory + 本地嵌入 | ~170K | **$0** |

---

## 与现有技能的关系

- **补充**: 现有 `agent-memory-frameworks-2026.md` 仅框架对比，无具体工具落地能力
- **升级**: `mem0-integration`/`local-rag` 是存储层，agentmemory 是完整记忆运行时
- **差异**: agentmemory 自带 MCP 服务器，零配置接入，无需外部向量数据库

---

## 安装与使用

```bash
# 一键安装（Node.js 20+）
npx -y @agentmemory/agentmemory@latest

# 首次运行交互式引导（选择 agents + LLM provider）

# 启动服务器（常驻）
agentmemory

# 查看记忆 UI
# http://localhost:3113 (实时查看器)
# http://localhost:3114 (引擎控制台)

# 本地嵌入（免费，零 API key）
# ~/.agentmemory/.env 设置 EMBEDDING_PROVIDER=local
```

---

## 适用场景

✅ **强烈推荐**:
- Coding agent（Claude Code/Cursor/Codex/OpenClaw/Hermes）跨会话记忆
- 需要 $0 成本本地语义检索
- 需要记忆可观测性和实时查看

❌ **不适用**:
- 非 coding 场景（通用 agent）
- 已有 Mem0/Letta 生产环境
- 需要云端协作的记忆同步

---

## 参考资料

- GitHub: https://github.com/rohitg00/agentmemory
- 官网: https://agent-memory.dev
- Benchmark: `benchmark/LONGMEMEVAL.md` / `benchmark/QUALITY.md` / `benchmark/SCALE.md`
- Hermes集成: `integrations/hermes/`
- 竞品对比: `benchmark/COMPARISON.md`
