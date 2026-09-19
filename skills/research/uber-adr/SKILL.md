---
name: uber-adr
description: Uber ADR — Agentic AI Detection & Response。生产级agent安全框架，含ADR-Bench(304任务)和双层检测器。
trigger: agent安全 / ADR / agent红队 / MCP威胁检测 / prompt injection检测
tags: [agent-security, detection, benchmark, mcp, production]
sources:
  - https://github.com/uber/ADR
  - https://arxiv.org/abs/2605.17380
updated: 2026-09-27
---

# Uber ADR — Agentic AI Detection & Response

## 概述

**ADR** (Agentic AI Detection & Response) 是 Uber 开源的生产级 agent 安全框架，已在 Uber 生产环境部署，配套论文被 MLSys 2026 接收。

核心定位：**四能力覆盖** observability / benchmarking / detection / prevention（ Prevention 未开源）。

## 核心架构

### 四组件（开源三）

| 组件 | 功能 | 状态 |
|------|------|------|
| ADR Sensor | 从 Claude Code/Cursor/Codex/Copilot/DeepSeek Harness/opencode 等收集遥测 | ✅ 开源 |
| ADR Discovery | 端点清单、探测器和指纹目录 | ✅ 开源 |
| ADR-Bench + Detector | 双层检测器：304 任务（43 恶意），134 MCP servers | ✅ 开源 |
| ADR Prevention | 阻止危险行为 | ❌ 未开源 |

### 双层检测架构

```
第一层 Triage（L1）  →  高召回筛选：GPT-4o，判断是否可疑
       ↓ 可疑会话
第二层 Reasoning（L2）→  Claude CLI，深度 agentic 推理确认
```

- **零误报**：302 任务评估集零假正例
- **ADR 检测精度**：100% precision / 67% recall（ADR-Bench）
- **基准对比**：LlamaFirewall 同期运行

## ADR-Bench 数据

| 指标 | 数值 |
|------|------|
| 总任务 | 304（261 良性，43 恶意） |
| MCP servers | 134（78 良性，26 漏洞，12 环境模拟，15 社区，4 官方） |
| 上下文提供器 | 3（源码分析 / 威胁情报 / 策略存储） |
| 威胁技术 | 17 种 ADR + AgentDojo prompt injection |
| AgentDojo 集成 | 完整对话日志 + ground truth 提取 |

### MCP Server 分类（重要）

- **78 良性**：合法业务工具
- **26 漏洞服务器**：模拟 EAS 攻击（含供应链冒名 `location_harvester` 伪装为天气服务）
- **12 环境服务器**：企业系统仿真（安全测试用）
- **15 社区服务器**：含冒名注入测试

## 快速启动

```bash
git clone https://github.com/uber/ADR
cd ADR/Detection
uv sync
export ANTHROPIC_API_KEY="..."   # Claude 推理 agent
export OPENAI_API_KEY="..."      # OpenAI triage LLM
# 安装 Claude CLI（必须，MCP server 集成）
npm install -g @anthropic-ai/claude-code
claude auth login
```

运行 benchmark：
```bash
cd ADR/Detection
python main_benchmark.py
```

运行检测器：
```bash
python main_detector.py
```

## 与 Hermes 相关性

### 现有对比

| 维度 | ADR | StackOne Defender |
|------|-----|-----------------|
| 类型 | 离线 benchmark + 在线检测 | 实时 MCP 流量扫描 |
| 威胁覆盖 | 17 种技术 | prompt injection + 数据泄露 |
| 部署 | 研究/隔离环境 | 生产集成 |
| 与 Hermes 关系 | 互补：ADR 测 Hermes skill 安全上限，Defender 保护生产 |

### Hermes 落地方向

1. **ADR-Bench 用于 Hermes skill 安全评测**：定期用 ADR-Bench 任务集测试 Hermes MCP 工具链安全性
2. **双层检测模式**：借鉴 ADR Triage → Reasoning 二阶段处理 Hermes 敏感操作审批
3. **威胁技术矩阵**：对照 ADR 17 种技术评估 Hermes 当前 skill 边界
4. **Sensor 思路**：未来为 Hermes 补充运行时 agent 遥测收集

## 关键限制

⚠️ **Not for production use**（benchmark 部分）
- 依赖 pinned exact versions，含已知 CVE（隔离环境可接受）
- synthetic credentials / prompt injection payloads 禁止暴露生产网络
- Prevention 组件未开源

⚠️ **仅开源检测，不含预防**：实际阻止能力需自行构建

## 与现有技能的关系

- **补充 StackOne Defender**：Defender 实时防护，ADR 离线评估，两者构成完整 agent 安全覆盖
- **补充 agent-testing-frameworks**：ADR-Bench 是当前最完整的 agent 安全 benchmark

## 来源

- https://github.com/uber/ADR
- https://arxiv.org/abs/2605.17380
- MLSys 2026 Paper + Slides（GitHub 内置）
