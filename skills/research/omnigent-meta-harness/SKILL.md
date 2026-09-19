---
name: omnigent-meta-harness
description: Omnigent — open-source meta-harness for all AI agents (9.7k stars, Hermes native, Apache 2.0)
trigger: Use when evaluating multi-harness orchestration, agent governance, or cross-agent collaboration.
updated: 2026-09-27
---

# Omnigent — Meta-Harness for All AI Agents

## 核心定位

Omnigent 是**元 harness（meta-harness）**：在已有 harness（Claude Code、Codex、Cursor、Pi、Hermes 等）之上建立统一编排层，实现**零重写切换**和**统一治理**。

- **9.7k GitHub stars** | Apache 2.0 | Python 3.12+
- Built by **Databricks AI team** + open contributors
- **Hermes 被列为原生支持的 harness**（`hermes` / `hermes-native`）

---

## 核心能力

### 1. 统一编排层
- 同一会话中混合使用 Claude Code / Codex / Cursor / OpenCode / **Hermes** / Pi / 自定义 agent
- 一个 agent 可以审查另一个 agent 的工作
- 一个任务可跨不同专长的 agent 分配
- **YAML 声明式**：每个 agent = 一个 YAML 文件（prompt + tools + sub-agents）

### 2. 内置 Agent：Polly & Debby
- **Polly**：多 AI 编程协调器（自己不写代码，只协调）
- **Debby**：模型辩论 agent（多头/空头辩论）
- 均可用 `omnigent run examples/polly/` 运行

### 3. 策略治理（Policies）
策略栈三层：**server-wide**（admin）→ **per-agent**（developer）→ **per-session**（user），严格者优先。
- `ask_on_os_tools`：shell/文件写入前请求审批
- `max_tool_calls_per_session`：每会话工具调用上限
- `cost_budget`：美元花费上限（硬限制 + 软警告阈值）
- 模型路由策略：按规则路由到不同模型
- 风险升级策略：按风险级别触发不同动作
- 零 prompt 注入——策略在 harness 层生效，非 LLM 判断

### 4. 云沙箱支持
10+ 供应商：Modal / Daytona / Blaxel / E2B / Kubernetes / CoreWeave / OpenShell / Boxlite / microsandbox / Databricks

### 5. 跨设备协作
- Terminal / Web / macOS桌面 app / iOS / Android 全平台同步
- **Live session 分享**：通过 URL 分享，队友实时观看 + 聊天
- **Co-drive**：队友直接在你的机器上接管输入
- **Fork**：克隆会话到自己的机器独立继续

### 6. Omnibox（Secure OS Sandbox）
- 限制文件系统 + 网络访问
- 对 agent 隐藏凭据，通过 broker 代理访问
- Linux: bubblewrap (bwrap) | macOS: seatbelt
- Windows: Job Object
- YOLO 模式可安全运行

---

## 与 Hermes 的关系

- **Omnigent 原生支持 Hermes**（`hermes` / `hermes-native` harness）
- Omnigent 是 Hermes 的**上层编排框架**而非竞品
- 潜在场景：用 Omnigent 统一管理 Hermes + Claude Code 等多个 agent
- 技能系统参考：Omnigent 的 YAML agent 声明 + 内置 Polly/Debby 协调模式

---

## 安装

```bash
# 方式1: bootstrap (推荐)
curl -fsSL https://omnigent.ai/install.sh | sh

# 方式2: uv
uv tool install -q --python 3.12 "omnigent"

# 方式3: pip
pip install omnigent

# 方式4: Homebrew
brew install omnigent-ai/tap/omnigent
```

**依赖**：Python 3.12+ / git / Node.js 22 LTS + pnpm / tmux

---

## 快速使用

```bash
# 启动本地 server（默认 http://localhost:6767）
omnigent server

# 用 Hermes 运行 agent
omnigent run --harness hermes path/to/agent.yaml

# 用 Claude Code 运行 agent
omnigent run --harness claude-sdk path/to/agent.yaml

# 协作：分享 live session
# Web UI 中点击 "Share"，发送 URL 给队友

# Co-drive：队友接管你的终端
omnigent attach <session_id>
```

---

## Agent YAML 示例

```yaml
name: my_agent
prompt: You are a helpful data analyst.
executor:
  harness: hermes-native  # 或 claude-sdk / codex / cursor / opencode / hermes / pi

tools:
  # 本地 Python 函数（签名自动生成 schema）
  word_count:
    type: function
    callable: mypackage.mymodule.word_count

  # MCP server
  docs:
    type: mcp
    url: https://example.com/mcp

  # 子 agent（由 supervisor 委托）
  researcher:
    type: agent
    prompt: Search for relevant information and summarize it.
    tools:
      word_count: inherit
```

---

## 关键文件

- `docs/AGENT_YAML_SPEC.md` — Agent YAML 完整 schema
- `docs/POLICIES.md` — 策略完整目录和信任模型
- `examples/polly/` — Polly 协调 agent 完整示例
- `tests/harness_bench/` — Harness 测试工作台（添加新 harness 支持时用）
- `deploy/README.md` — 完整部署指南（服务器/Web/云沙箱/品牌白标）

---

## 落地建议

- **研究价值**：⭐⭐⭐⭐⭐（Hermes 被列为原生支持，意义重大）
- **短期落地**：⭐⭐（alpha 状态，Databricks 内部生产）
- **监控关注**：后续版本稳定性和 Hermes harness 质量
- **技能系统中记录**：作为 multi-harness 编排的对比参考
