# BeeAI Framework (IBM Research)

**分类**: Agent Framework / Multi-Agent / ACP Protocol
**触发词**: beeai, ibm agent, acp protocol
**Stars**: ~2K | **License**: Apache-2.0 | **Gov**: Linux Foundation / IBM Research

## 核心定位

IBM Research 出品的生产级多 Agent 框架，核心特色：**Python + TypeScript 双语言完全对等实现**，基于 ACP（Agent Communication Protocol）实现跨框架 Agent 互操作。

## 核心创新

### 1. ACP (Agent Communication Protocol) = A2A 的前身
ACP 是 IBM 主导的 Agent 间通信协议，2025-08 已迁入 **A2A（Agentic AI Foundation）**，成为 Linux Foundation 下的正式标准。BeeAI Framework 是 ACP 的首个生产级实现。

```
BeeAI ACP → A2A (Linux Foundation, 2025-08)
```
协议层核心：Agent 身份注册、任务委托、结果返回、生命周期管理。与 MCP（工具层）+ A2A（路由层）构成完整协议栈。

### 2. 四种 Memory 策略
```
Short-term / Long-term / Session / Custom
```
不同于 Mastra 的纯文本时间戳记忆， BeeAI 提供多种记忆策略按场景切换。

### 3. Dual Language Parity
Python 和 TypeScript 实现完全对等，同一功能在两侧同步发布。这是业界罕见的工程承诺。

### 4. Model Provider 生态
```
Ollama / Grow / OpenAI / Watsonx.ai / Bedrock / LiteLLM
```

### 5. MCP 原生集成
内置 MCP tool 支持，可直接使用 270+ MCP servers。

### 6. BeeAI Platform = Agent 发现/运行平台
基于 ACP 的 Agent Store，支持跨框架 Agent 发现和即插即用：
```
发现 → 安装 → 配置 LLM → 运行
```
类似 npm for agents。

## 与 Hermes 的互补点

| 方面 | BeeAI | Hermes |
|------|-------|--------|
| 协议层 | ACP→A2A 先行者 | 无专属协议 |
| 双语言 | Python/TS 完全对等 | 主要 Python |
| Memory | 多策略（4种） | 文本时间戳 |
| 生态 | IBM/LF 背书 | Nous Research |
| 落地 | 企业级 IBM 客户 | 个人/自托管 |

## 落地建议

**ACP 协议层研究价值**：BeeAI 的 ACP 实现比官方 A2A 早，是协议演进的重要参考。已合并至 A2A，学习成本低。

**不值得全量采用**：BeeAI 仍处于 alpha（Python 2025-02 才发布），生态不如 LangGraph/Mastra 成熟。

## 参考

- Framework: https://github.com/i-am-bee/beeai-framework
- Platform: https://research.ibm.com/projects/bee-ai-platform
- ACP Protocol: https://research.ibm.com/projects/agent-communication-protocol
- IBM Think: https://research.ibm.com/blog/beeai-open-source-multiagent
