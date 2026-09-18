---
name: deer-flow
description: DeerFlow 2.0 — ByteDance open-source super agent harness. 触发词：DeerFlow/鹿Flow/ByteDance agent/长时agent
triggers: [deer-flow, 鹿flow, bytedance super agent, long-horizon agent]
version: 1.0
updated: 2026-09-27
---

# DeerFlow 2.0 — ByteDance Super Agent Harness

## 基本信息
- **Stars**: 82.6k (GitHub Trending #1, 2026-02-28)
- **Forks**: 11.4k
- **License**: MIT
- **URL**: https://github.com/bytedance/deer-flow | https://deerflow.tech
- **语言**: Python 82.1%, TypeScript 14.7%
- **贡献者**: 463人

## 核心定位
DeerFlow (**D**eep **E**xploration and **E**fficient **R**esearch **Flow**) 是 ByteDance 开源的**super agent harness**，通过编排 sub-agents、memory、sandboxes 处理从分钟到小时的复杂任务。

> **v2.0 完全重写**，与 v1 无共享代码。

## 核心架构

### 底层
- **LangGraph + LangChain** 驱动状态机
- **Python + Node.js** 双后端（Python 主逻辑 + Node TUI）
- **Docker Compose** 一键部署（推荐）或本地开发

### 核心组件
1. **Lead Agent**: 主规划 agent，协调 sub-agents
2. **Sub-Agents**: 独立任务执行 agent，可并行
3. **Skills System**: 可扩展技能系统（`.agent/skills/`）
4. **Memory**: 长期记忆持久化
5. **Sandbox**: 隔离执行环境（文件、网络控制）
6. **Message Gateway**: IM 通道集成（Telegram/Slack/飞书/微信/Wecom/钉钉）

### 关键特性
- **Claude Code 集成**: `npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow`
- **MCP Server 内置**: 支持 MCP 工具扩展
- **InfoQuest**: BytePlus 开发的搜索爬虫集成
- **Session Goals**: 会话目标管理与进度追踪
- **Manual Context Compaction**: 手动上下文压缩
- **Terminal Workbench (TUI)**: 终端工作台
- **Scheduled Tasks**: 定时任务
- **LangSmith/Langfuse/Monocle Tracing**: 全链路追踪

## 推荐模型
- **Doubao-Seed-2.0-Code**（字节豆包，官方推荐）
- **DeepSeek v3.2**
- **Kimi 2.5**

## 部署要求
| 场景 | 最低 | 推荐 |
|------|------|------|
| 本地评估 | 4 vCPU / 8GB RAM / 20GB SSD | 8 vCPU / 16GB RAM |
| Docker 开发 | 4 vCPU / 8GB RAM / 25GB SSD | 8 vCPU / 16GB RAM |
| 长期运行服务器 | 8 vCPU / 16GB RAM / 40GB SSD | 16 vCPU / 32GB RAM |

## 快速开始
```bash
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow
make setup          # 交互式配置向导
make doctor         # 验证环境
make up             # 启动生产服务 (http://localhost:2026)
```

## IM 通道支持
Telegram / Slack / 飞书/Lark / 微信 iLink / 企业微信 / 钉钉

## Hermes 参考价值
1. **Sub-agent 架构**: Hermes cron 任务可用类似 sub-agent 模式分解
2. **Skills 系统**: DeerFlow 的 `.agent/skills/` 设计与 Hermes 技能系统高度相似
3. **Sandbox 隔离**: DeerFlow 的 sandbox 网络控制是 Hermes 执行安全参考
4. **Memory 持久化**: 长期记忆设计是 Hermes fact_store 外的补充方案

## 新知识
DeerFlow 2.0 是当前最成熟的 LangGraph-based super agent harness，82.6k stars 验证了其生产可用性。其 skills 系统与 Hermes 技能设计高度共鸣；sandbox 隔离方案比 Hermes 当前实现更精细。

## 来源
- https://github.com/bytedance/deer-flow
- https://deerflow.tech
