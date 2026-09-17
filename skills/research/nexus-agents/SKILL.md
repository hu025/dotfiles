---
name: nexus-agents
description: nexus-substrate治理控制面——adversarial review + 哈希链审计 + 闭环遥测，监控Claude Code/Codex/Gemini/OpenCode。触发词：agent治理/对抗审查/审计追踪
triggers:
  - agent治理
  - adversarial review
  - 哈希链审计
  - nexus-agents
  - agent control plane
  - 治理控制面
---

# nexus-agents — AI Coding Agent 治理控制面

## 核心定位
- **定位**: agent之上的治理层（control plane），而非另一个coding agent
- **数据面**: Claude Code / Codex / Gemini / OpenCode 做实际工程
- **控制面**: 接管准入审查、对抗PR review、哈希链审计、闭环调优
- **GitHub**: 18 stars，MIT，4,700+ commits，活跃开发（2026-01至今）
- **技术栈**: Node.js 22.x LTS + pnpm 9.x + TypeScript

## 核心能力（四类）

### 1. 准入控制（Admission）
- Charter drift检测：规则变更后强制重新审查
- 路由决策：基于历史成功率分配任务

### 2. 对抗PR审查（Adversarial Review）
- `nexus-agents review <pr-url>` 对PR进行对抗性审查
- 6种投票策略：simple/super-majority/unanimous/Bayesian/opinion-wise/proof-of-learning

### 3. 哈希链审计（Immutable Audit）
- append-only tamper-evident record
- `verify_audit_chain` 验证链完整性
- 每个决策全链路追溯

### 4. 闭环调优（Closed-Loop Tuning）
- autonomous demotion：失败率高的agent降级
- earned promotion：成功率高的agent升级
- MAPE-K loop：Monitor → Analyze → Plan → Execute over shared Knowledge base

## CLI命令
```bash
nexus-agents review <pr-url>    # 审查GitHub PR
nexus-agents expert list         # 列出可用专家agent
nexus-agents workflow list       # 列出工作流模板
nexus-agents config init         # 生成配置文件
nexus-agents init --portable     # 创建workspace本地配置
```

## 三层架构
```
Human / IDE / CLI
      │
      ▼ MCP Protocol
┌─────────────────────────────────────┐
│         GOVERNANCE SUBSTRATE          │
│  Charter (drift-checked)             │
│  Adversarial PR review               │
│  AuditTrail (hash chain)            │
│  Closed-loop tuning (demote/promote)│
└─────────────────────────────────────┘
      │
      ▼
Engineering agents: Claude Code · Codex · Gemini · OpenCode
      │
      ▼
Code: actual edits, tests, PRs, issues
```

## 与现有技能差异化
- **vs pi-agent-harness**: pi-agent-harness生成团队，nexus-agents治理已运行的fleet
- **vs agent-testing-frameworks**: 测试框架评估性能，nexus-agents管理治理流程
- **互补**: 两者可组合——harness生成团队，agents治理团队

## 安装
```bash
git clone https://github.com/nexus-substrate/nexus-agents.git
cd nexus-agents
pnpm install
pnpm build
pnpm test
# 要求: Node.js 22.x LTS, pnpm 9.x
```

## 参考
- https://github.com/nexus-substrate/nexus-agents
- https://github.com/nexus-substrate/nexus-agents/blob/main/docs/architecture/README.md
