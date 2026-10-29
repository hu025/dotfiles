---
name: gh-aw
description: GitHub Agentic Workflows — Markdown→GitHub Actions AI agent workflow compiler
triggers:
  - GitHub Agentic Workflows
  - gh aw
  - agentic DevOps
  - AI agent GitHub Actions
  - Continuous AI
source: https://github.com/github/gh-aw
stars: 5.2k
license: MIT
status: production-ready
updated: 2026-10-22
---

# GitHub Agentic Workflows (gh-aw)

## 核心定位

GitHub 官方 + Microsoft Research + Azure Core Upstream 联合出品。将 Markdown 工作流描述文件编译为安全强化的 GitHub Actions YAML，通过 AI coding agent 在 Actions 内执行自然语言指令。

```
.md (自然语言描述)  →  gh aw compile  →  .lock.yml (安全强化工作流)
```

## 核心架构

### 两文件模型

| 文件 | 作用 | 信任级别 |
|------|------|---------|
| `.github/workflows/foo.md` | 可编辑的自然语言工作流定义 | 低（用户编辑） |
| `.github/workflows/foo.lock.yml` | 编译后安全强化工作流 | 高（自动生成，禁止手动编辑） |

`.lock.yml` 包含 SHA pinning、schema validation、action 版本锁定。`gh aw compile --strict` 强制额外约束（禁止写权限、要求显式网络配置）。

### Frontmatter 结构

```yaml
---
on:                    # 触发器: schedule, workflow_dispatch, push, issue_comment, etc.
permissions:           # GitHub 令牌权限
  contents: read
  issues: read
  pull-requests: write
network: defaults      # 或 custom（配合 AWF）
engine:                # copilot / anthropic / codex / gemini
  id: copilot
  model: gpt-5.2-codex
safe-outputs:          # 允许的写操作白名单
  create-issue:
    title-prefix: "[Status] "
    labels: [report]
    expires: 7         # 7天后自动关闭
tools:
  github:
    toolsets: [default, pull_requests]  # MCP 工具集
---
# Markdown 自然语言指令
```

### 五阶段执行管道

```
1. Pre-activation   → 角色权限检查 + lock 文件校验
2. Input sanitization → @mention 中和 / bot loop 防护 / HTML→安全格式 / HTTPS only
3. Agent execution  → read-only 运行，写操作缓冲为 artifact
4. Threat detection → 独立 AI 分析 job，检查 artifact 的 secret leak / 恶意代码 / 策略违规
5. Safe output execution → 单独 scoped job 执行写操作
```

**关键：agent 本身永远没有写权限**，即使被完全攻陷也无法直接修改仓库。

### 三层安全模型

**Substrate-level trust**
- 容器化环境运行（GitHub Actions runner）
- AWF (Agent Workflow Firewall)：Squid 代理 + domain allowlist
- 每个 MCP server 运行在独立隔离容器
- 支持 HTTPS 深度包检测

**Configuration-level trust**
- 编译时 schema 验证
- Action SHA pinning（防止 tag 劫持供应链攻击）
- 安全扫描：actionlint + zizmor + shellcheck + poutine
- `gh aw compile --strict` 强制额外约束
- Token 作为导入 capability 精确控制分发

**Plan-level trust**
- 工作流分解为 stage，每 stage 有定义好的权限和数据输出
- AI-powered threat detection 在写操作前执行
- blast radius 限制在发生问题的 stage 内

### Safe Outputs 模式

```yaml
safe-outputs:
  create-issue:
    labels: [agent-report]
    expires: 7          # 自动关闭
  missing-data:         # 特殊 safe output：鼓励诚实而非幻觉
    # agent 缺少数据时显式报告而非编造
```

### MCP Gateway

`gh-aw-mcpg` — 统一 HTTP 网关路由 MCP server 调用，支持集中化访问管理。

### Agent Workflow Firewall (AWF)

`gh-aw-firewall` — 网络出口控制，domain-based 访问控制和活动日志记录。

## 配套工具

- `gh aw compile` — Markdown → .lock.yml 编译
- `gh aw run <workflow>` — 手动触发工作流
- `gh aw logs` — 查看运行日志（含 token 使用量、AIC 估算）
- `gh aw audit <run-id>` — 详细运行审计（token 数、推理成本估算、改进建议）

## 成本

- 1 AIC = $0.01 USD
- 默认每运行上限 1000 AIC
- 默认引擎 Copilot：每次运行约 2 premium requests（agent 工作 + threat detection）
- 第三方引擎按提供商计费

## 工作流模式

- **ChatOps** — AI 响应 issue/PR 评论
- **DailyOps** — 每日状态报告（自动创建 issue）
- **IssueOps** — AI issue 分类、标签、优先级
- **Orchestration** — 多 agent 协调

## 与 Hermes 的关系

**非竞争·互补**：gh-aw 是 GitHub 仓库内的 agent DevOps 工具，Hermes 是本地 agent 编排框架。gh-aw 可作为 Hermes 的外部工具被调用（通过 MCP）。

**可借鉴点**：
1. 两文件模型（源 .md + 编译 .lock）→ Hermes 可区分可编辑 skill 与已验证 skill 版本
2. missing-data safe output → Hermes 可在工具调用结果不足时显式报告而非填充
3. 三层安全模型 → Hermes skill hook 安全边界设计的参考架构

## 落地动作

**无立即落地**：gh-aw 是 GitHub 专有工具，Hermes 无法直接集成其执行层。
**记录价值**：三文件安全模型（source/compiled/trusted）和 missing-data 模式是后续 Hermes 架构演进的参考。

## 来源

- https://github.com/github/gh-aw
- https://docs.github.com/en/copilot/concepts/agents/about-github-agentic-workflows
- https://www.kenmuse.com/blog/github-agentic-workflows-bring-ai-agents-to-actions
- https://github.com/github/gh-aw-firewall
- https://github.com/github/gh-aw-mcpg
