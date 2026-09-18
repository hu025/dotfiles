---
name: ecc-agent-harness
description: ECC (Everything Claude Code) — Agent harness performance optimization system. 触发词：ECC/affaan/claude code配置/coding agent优化
triggers: [ecc, everything claude code, affaan, agent harness, claude code优化]
version: 1.0
updated: 2026-09-27
---

# ECC — Agent Harness Performance Optimization System

## 基本信息
- **Stars**: 257k (全球最大 Claude Code 配置仓库)
- **Forks**: 37k
- **License**: MIT（永久开源）
- **URL**: https://github.com/affaan-m/ECC | https://ecc.tools
- **创始人**: Affaan Mustafa
- **GitHub App**: 6,184 安装
- **安装量**: 805.5K skill installs on skills.sh
- **用户**: Tesla / xAI / ByteDance / Amazon / DigitalOcean 等

## 核心定位
ECC 是**agent harness 性能优化系统**，为 Claude Code、Codex、Cursor、OpenCode 等提供 skills、memory、security、planning 能力。不是框架，而是现有 harness 的增强层。

## v2.0 (2026-06) 核心组件

### 1. Control Pane
本地操作界面，跨会话检查 agent sessions、worktrees 和重叠工作。

### 2. Worktree Lifecycle Service
每个 agent 独立 Git 分支，无碰撞并行工作。

### 3. Orchestrator Family (`orch-*`)
多 agent 编排引擎，NanoClaw v2 是核心。

### 4. Plan Canvas
浏览器端 plan 可视化编辑器 + 标注 + 反馈循环。

### 5. Unified Memory Vault (`ecc memory`)
```bash
ecc memory init --scope project
ecc memory handoff --from codex --target claude --title "Continue rollout"
ecc memory search "rollout" --target-harness claude
```
跨 harness 记忆共享，下一个 agent 可接续工作。

### 6. Itô Compute
GPU 资源发现与运行时状态检查（与 Itô Markets 合作）。

### 7. AgentShield
安全扫描：MCP 连接检查、权限审计、prompt injection 检测。
```bash
npx ecc-agentshield
```

### 8. Skills (261个)
跨 harness 可复用技能体系，skills.sh 市场分发。

## 核心产品对比

| 产品 | 价格 | 说明 |
|------|------|------|
| Open Source 工具箱 | 免费 | skills/agents/hooks/Plan Canvas/Memory |
| GitHub App Pro | $19/seat/月 | 私有仓库覆盖 + 深度 GitHub 引导 |
| Enterprise | 定制 | 部署培训 + 安全支持 |

## AgentShield MCP 政策
2026-06 审计后，ECC 只默认打包 `chrome-devtools` 一个 connector，所有其他 MCP 需手动 opt-in。政策文档：`docs/MCP-CONNECTOR-POLICY.md`。

## v2.2.1 (2026-08-31) 新特性
- Guided manifest-driven setup（跨 Claude Code/Codex/Kimi Code）
- Native Antigravity install
- Plan Canvas 浏览器审查
- `ecc memory` 统一记忆库
- Itô compute skill family

## ECC vs Hermes
| 维度 | ECC | Hermes |
|------|-----|--------|
| 定位 | Claude Code 增强层 | 通用 agent 框架 |
| Skills | 261个，跨 harness | 50+ 技能目录 |
| Memory | 统一 vault，跨 agent | fact_store + holographic |
| Security | AgentShield MCP 扫描 | 基础 tool safety |
| Orchestration | NanoClaw orchestrator | 内置编排 |

## Hermes 参考价值
1. **Skills 市场设计**: skills.sh 是 ECC 分发模式，Hermes 可参考类似目录
2. **Unified Memory Vault**: `ecc memory` 跨 agent 记忆设计是 Hermes fact_store 互补方案
3. **AgentShield**: MCP 连接安全扫描可集成到 Hermes MCP 工具链
4. **Plan Canvas**: 浏览器端 plan 可视化是 Hermes planning skill 增强方向

## 新知识
ECC 257k stars 证明 agent harness 增强层有巨大市场。Skills 跨 harness 分发（skills.sh）和 unified memory 是当前最佳实践。AgentShield MCP 安全扫描填补了 Hermes 安全工具链空白。

## 来源
- https://github.com/affaan-m/ECC
- https://ecc.tools
