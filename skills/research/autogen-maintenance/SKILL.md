---
name: autogen-maintenance
description: AutoGen维护模式与Microsoft Agent Framework (MAF)迁移指南。触发词：AutoGen/MAF/多智能体框架/Magentic-One/CodeAct。
triggers: [autogen, microsoft agent framework, maf, magentic-one, codeact, autogen migration]
version: 1.0
updated: 2026-09-25
---

# AutoGen 维护模式 / Microsoft Agent Framework 迁移

## 状态变更（2025年10月）

Microsoft将AutoGen与Semantic Kernel合并为**Microsoft Agent Framework (MAF)**，AutoGen自此进入**维护模式**：
- ✅ 继续接收Bug修复和安全补丁
- ❌ 不再接收新功能或增强
- ❌ 新项目不再推荐使用AutoGen

**迁移路径**：AutoGen → Microsoft Agent Framework（非可选，是必由之路）

## Microsoft Agent Framework (MAF) 核心信息

| 项目 | 信息 |
|------|------|
| GA时间 | 2026年4月2日 |
| 语言 | Python + .NET |
| 状态 | 生产就绪，稳定API，长期支持承诺 |
| 前身 | AutoGen + Semantic Kernel |
| 协议支持 | A2A + MCP |

## 核心架构对比

### AutoGen v0.4 三层架构
```
Extensions API → Code执行/LLM客户端/工具
AgentChat API → 快速原型，熟悉的对话模式
Core API → 事件驱动，消息传递，跨语言(.NET/Python)
```

### MAF 架构升级
- **Graph-based Workflows**：数据沿定义边流动，executor在输入到达时触发
- **Agent Harness**（Build 2026）：为模型包装工具/记忆/计划/审批/遥测/搜索
- **Hosted Agents**：Azure Foundry托管，沙箱session，持久状态，可观测性，版本控制
- **CodeAct**：多工具调用合并为单次Python执行

### CodeAct 性能提升（来自Microsoft测试）
| 指标 | 标准模式 | CodeAct |
|------|---------|---------|
| 执行时间 | 27.81s | 13.23s |
| Token消耗 | 6,890 | 2,489 |
| **Token节省** | — | **64%** |

## AutoGen → MAF 迁移指南

### 核心概念映射
| AutoGen概念 | MAF对应 |
|-------------|---------|
| AgentChat API | Agent Messaging Model（直接映射） |
| Group Chat | Graph-based Workflow |
| Team | Orchestration Layer |
| 模型客户端 | Model Client（同接口） |
| 工具 | AgentTool |

### 迁移注意事项
1. **API差异**：AgentChat API → Workflow Engine，not 1:1替换
2. **Azure依赖**：AutoGen Azure连接器 → MAF原生Azure AI Foundry集成
3. **多语言**：Python/C#/Java一致性是MAF核心价值
4. **第三方集成**：需审计AutoGen特定插件是否在MAF中有对应

### 何时迁移
- **立即迁移**：新项目从MAF开始
- **暂缓迁移**：现有AutoGen生产系统，评估迁移成本
- **不迁移**：仅需简单LLM调用（重试逻辑），无复杂多智能体对话

### 迁移成本评估
预期为**部分重写**，而非自动化迁移：
- 核心概念可迁移
- 工具集成需重新测试
- 对话流程需重测（非简单重导入）

## AutoGen 生产架构模式

来源：[Markaicode Production Architecture Guide](https://markaicode.com/architecture/autogen-agent-architecture/)

### 分层模块化架构
```
Gateway → Orchestrator → Redis Stream → Worker Agents
                              ↓
                        Observability
                        (Prometheus)
```

### 关键设计原则
1. **Orchestrator/Worker分离**：orchestrator路由+turn-taking，workers执行任务
2. **Redis Streams持久化**：crashed worker → 可重试任务，而非丢失
3. **max_consecutive_auto_reply限制**：防止一个卡住的agent阻塞整个对话
4. **Liveness Probe**：监控agent是否在预期间隔内处理消息
5. **每Worker独立超时**：一个慢LLM调用不能阻塞整个worker slot

### 生产选型对照
| 维度 | 单进程Group Chat | 分层模块化 |
|------|-----------------|-----------|
| 进程模型 | 全部agent同进程 | Orchestrator + Workers分离服务 |
| 消息传递 | 内存列表 | Redis Stream（持久） |
| 故障影响范围 | 整个对话 | 单agent/单任务 |
| 扩缩容 | 垂直（整进程） | Worker水平扩缩 |
| 运维成本 | 低 | 高（Redis+K8s+指标栈） |
| 适用场景 | 原型，≤5 agents，低并发 | 持续多agent流量，高可用需求 |

## Magentic-One（SOTA多智能体案例）

Magentic-One是AutoGen/MAF构建的SOTA多智能体团队：
- 使用AgentChat API + Extensions API
- 支持web browsing + code execution + file handling
- 展示AutoGen架构的实际应用上限

## 与Hermes的相关性

**不直接适用**：Hermes subagent是进程内协作，不匹配MAF client-server模型
**有参考价值**：
1. AutoGen生产架构（Redis+K8s）对未来Hermes分布式扩展有参考
2. MAF的CodeAct多工具批量执行思想可用于Hermes工具调用优化
3. MAF监控指标设计（Redis stream length/Worker CPU/Orchestrator p95 latency）

**行动**：保持监控，不主动迁移；3-6月后重新评估MAF生态成熟度

## 资源链接

- [AutoGen GitHub (维护模式)](https://github.com/microsoft/autogen)
- [MAF官方文档](https://learn.microsoft.com/agent-framework)
- [AutoGen→MAF迁移指南(Azure AI Foundry)](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/agent-framework/migration-guide/from-autogen/index.md)
- [AutoGen生产架构指南](https://markaicode.com/architecture/autogen-agent-architecture/)
- [Mixture of Agents模式](https://microsoft.github.io/autogen/0.4.8/user-guide/core-user-guide/design-patterns/mixture-of-agents.html)
- [CodeAct性能数据](https://www.analyticsinsight.net/artificial-intelligence/microsoft-autogen-explained-building-multi-agent-ai-systems)
