---
description: GNAP — Git-Native Agent Protocol。用 git 作为多 Agent 协作消息总线，无需服务器/数据库。适合分布式 swarm 研究、离线协作、零基础设施 Agent 协调。
trigger: GNAP git-native agent protocol coordination
---
# GNAP — Git-Native Agent Protocol

## 核心概念

**用 git 本身作为 Agent 协调层**。无需服务器、无需数据库——任何能 `git push` 的 Agent 都能参与协作。

4 个 JSON 文件 = 整个协议：

```
.gnap/
  version              → 协议版本 (如 "4")
  agents.json          → 团队成员（人 + AI Agent）
  tasks/FA-1.json      → 任务
  runs/                → 执行历史
  messages/            → Agent 间通信
```

## 心跳循环

每个 Agent 运行心跳循环：
```
1. git pull
2. Read agents.json     → 我是否活跃？
3. Read tasks/          → 有分配给我的任务吗？
4. Read messages/       → 有新消息吗？
5. Do the work → commit → git push
6. Sleep until next heartbeat
```

Git 历史 = 审计日志，无需独立数据库。

## 4 个协议实体

| 实体 | 文件 | 作用 |
|------|------|------|
| Agent | `agents.json` | 谁在团队里 |
| Task | `tasks/*.json` | 需要完成什么 |
| Run | `runs/*.json` | 一次执行尝试 |
| Message | `messages/*.json` | Agent 间通信 |

## agents.json 示例

```json
{
  "agents": [
    {
      "id": "carl",
      "name": "Carl",
      "role": "CRO",
      "type": "ai",
      "status": "active"
    },
    {
      "id": "leo",
      "name": "Leonid",
      "role": "CTO",
      "type": "human",
      "status": "active"
    }
  ]
}
```

## 关键优势

- **零基础设施** — 不需要部署服务器，不需要维护数据库
- **任何 Agent，任何运行时** — 只要能 git push 就能参与
- **默认可审计** — `git log` 就是审计轨迹
- **人类参与** — 人和 AI Agent 都是一等公民
- **离线可用** — Agent 可断开连接后同步
- **可组合** — 可以在上面构建预算/仪表盘/工作流

## 适用场景

- SETI@home 风格分布式 Agent swarm 研究
- 跨框架 Agent 协作（OpenClaw + Claude Code + Codex 共同工作）
- 零服务器的长期多 Agent 任务
- 需要完整审计轨迹的合规环境
- 离线分布式计算任务

## 与 Hermes 对比

| | GNAP | Hermes |
|---|---|---|
| 协调机制 | git push/pull | HTTP/WebSocket |
| 实时性 | 低（轮询心跳）| 高 |
| 基础设施 | 零 | 需要 |
| 适用场景 | 分布式 swarm | 集中式任务 |

## 链接

- GitHub: https://github.com/farol-team/gnap
- Stars: 81 | MIT License
- 创建时间: 2026-03-12
