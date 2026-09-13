---
name: agent-orchestration
description: 多Agent编排模式：fan-out/pipeline/debate/supervisor/swarm五种2026生产级模式，supervisor是默认起点
---

# Agent Orchestration 多智能体编排

## 5 种核心模式 (2026 production)

### 1. **Fan-out** (并行 scatter-gather)
- 一个 orchestrator 分解任务 → N 个子 agent 并行 → 合并结果
- **Wall-clock** 由最慢的子 agent 决定，不是总和
- **适合**: 独立只读任务（代码搜索、多文件审查、研究扫描）
- **Hermes**: `delegate_task tasks=[...]`

### 2. **Pipeline** (顺序链)
- 多阶段：generate → review → refine → finalize
- 每阶段转换独立
- **适合**: 已知的多阶段处理

### 3. **Debate** (辩论)
- 2-N 个 agent 给出独立答案 → judge agent 仲裁
- **成本 ~2.5x** 单模型（多 agent + judge）
- **适合**: 高风险决策、多视角验证
- **不推荐**用于日常任务（性价比低）

### 4. **Supervisor** (2026 默认)
- top-level supervisor agent 接收请求 → 分解为子任务 → 分发给 specialized sub-agents → 聚合
- 子 agent **互不可见**（独立 context）
- **最广泛支持**: Claude Agent SDK / LangGraph / OpenAI Agents SDK / CrewAI
- **失败模式**: over-delegation（用 iteration ceiling 限制）

### 5. **Swarm** (动态 peer agents)
- agent 从共享队列发现工作 → 互相协调
- Claude Code Agent Teams 实现
- **失败模式**: context-drift（agent 重复工作）
- **仅当**: 任务数 > 50 且运行时增长

### 6. **Conversational** (AutoGen / Microsoft Agent Framework)
- agents 通过结构化对话协作，AI 自身决定下一个 speaker
- **Group Chat Manager**: 另一个 AI agent 决定谁在什么时刻发言
- **适用**: 代码生成+review、辩论、研究多专家会诊
- **成本**: ~2.5x 单 agent（非确定性对话可能消耗更多 token）
- **注意**: AutoGen 已进入维护模式（2026-04），新项目用 Microsoft Agent Framework 1.0

### 7. **Typed Handoff** (Mastra / Pydantic AI)
- TypeScript 类型系统跨 agent 边界流动，确保 handoff 时数据 schema 不丢失
- Mastra: `.network()` + LLM router 动态决定哪个 agent 处理输入
- Pydantic AI: `result_type` Pydantic 模型保证输出结构
- **适用**: TypeScript 生产系统、需要编译时类型安全的 Python 系统

## 决策矩阵

| 情况 | 模式 | 工具 |
|------|------|------|
| 独立并行读 | Fan-out | Subagents |
| 有序多阶段 | Pipeline | Workflow script |
| 两个方案需裁决 | Debate | Subagents + judge |
| 已知任务树+专业化 | Supervisor | Subagents with agentType |
| 未知任务列表+运行时增长 | Swarm | Agent Teams |
| agents 需要讨论/辩论/迭代改进 | Conversational | AutoGen / MAF |
| TypeScript 生产系统需类型安全 | Typed Handoff | Mastra / Pydantic AI |

## 跨模式通用规则

1. **不要用 barrier 用 pipeline**：`parallel().map().parallel()` 中间 transform 几乎不需要同步点
2. **Native subagents 覆盖 ~80% 需求**：LangGraph/CrewAI/AutoGen 仅当 workflow 超出原生时再用

## Hermes 当前实践

| 任务 | 模式 | 实例 |
|------|------|------|
| ETF 筛选 + Mem0 + 小说去AI化 + Reflexion + SWE-RL | Fan-out | delegate_task batch 5 |
| M3 优化 + 浏览器升级 + 学习沉淀 | Supervisor (me) | delegate_task 3 parallel |
| 每日研究 cron | Pipeline | research_loop → research_executor |

## 选型经验

- **不要默认 swarm** —— 80% 任务 supervisor 足够
- **用 subagent** 而不是 LangGraph，除非有显式限制
- **记录每个 agent 的成本** —— 避免 token 浪费
- **所有 agent 必须有 fallback** —— LLM 调用失败时降级
