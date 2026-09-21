---
name: pi-core-harness
description: Pi 核心 — Armin Ronacher 的 sub-1K token 极简 agent harness，lazy skills 按需加载。2026-10-21 研究新发现。
trigger: pi-core-harness sub-1000 tokens minimal agent
triggers:
  - pi agent 核心
  - pi-core-harness
  - sub-1000 token agent
  - lazy skills 按需加载
---

# Pi Core Harness — 极简 Token 高效 Agent

## 核心定位

Pi（earendil-works/pi）是 Armin Ronacher（Flask/Jinja2 作者）+ Mario Zechner 构建的**极简 agent harness**，核心特性是：

- **系统提示词 < 1,000 tokens**，vs Claude Code ~10,000 / OpenCode ~10,000+ / Cline ~7,000
- **Lazy Skills**：技能只保留一行描述驻留上下文，完整指令在调用时才加载
- **~98K GitHub stars**（2026-10），MIT 许可

## 核心机制

### Lazy Skills（核心创新）

Pi 的 lazy skills 机制与 Hermes SKILL.md 的 Progressive Disclosure 高度共鸣：

```
# 每个技能包只贡献一行描述驻留上下文
# 完整指令和工具 schema 在 /skill:name 或自动检测时才加载
```

| 工具 | Token 开销 | 说明 |
|------|-----------|------|
| Claude Code | ~10,000 tokens | 所有工具 schema 预加载 |
| Pi | < 1,000 tokens（全部） | 仅核心 4 工具 + 按需加载技能 |

**对比 MCP**：MCP 预加载所有工具 schema，而 Pi 的 lazy skills 真正实现了按需加载。

### 4 个核心原语工具

Pi 只内置 4 个工具（vs Claude Code/OpenCode 的几十个）：

1. **read** — 文件读取
2. **write/edit** — 文件写入/编辑
3. **shell** — shell 命令
4. **search** — 代码搜索

### 自我扩展（Self-Extension）

Pi 的独特能力：**让 agent 自己写技能**。告诉 Pi "Build me a skill that runs my Jest tests"，Pi 生成 TypeScript 扩展模块：

```typescript
export default {
  name: "db-migrate",
  description: "Generate and run a database migration from a schema diff.",
  async run(ctx) {
    // 完整指令只在这里，调用时才进入上下文
    await ctx.shell("npm run migrate:generate");
    return "Migration generated; review before applying.";
  },
};
```

### Context Compaction

- **自动压缩**：上下文满时触发，16K tokens 始终保留给 LLM 响应
- **/compact [instructions]**：手动触发，指示优先级
- JSONL 会话历史始终完整，仅内存表示被压缩

### DAG 会话树

会话存储为 JSONL（id + parentId），历史是 DAG 而非线性列表：
- **/fork**：创建分支
- **/tree**：可视化完整图

## 包结构

| 包 | 说明 |
|----|------|
| @earendil-works/pi-coding-agent | 交互式 CLI |
| @earendil-works/pi-agent-core | Agent runtime + tool calling |
| @earendil-works/pi-ai | 统一 LLM API（OpenAI/Anthropic/Google 等）|
| @earendil-works/pi-telemetry | 供应商中立遥测合同 |
| @earendil-works/chord | 应用组合运行时 |

## 与 Hermes 的关系

Pi 内嵌于 OpenClaw（145K stars，RPC 集成）。Pi 维护者 Ronacher 的设计哲学：
> "Do less in the framework, trust the user" — 这与 Hermes 的 skill 驱动设计高度共鸣。

### Hermes 可借鉴点

1. **Lazy Skills 机制**：Hermes 技能目前是全量加载，lazy loading 可减少 token 消耗
2. **DAG 会话历史**：Hermes cron 的会话线性，/fork 分支可用于探索性研究
3. **自我扩展能力**：Hermes 技能由用户/AI 共同创建，Pi 的 self-extension 提供了更激进的自动化方案
4. **Context Compaction 策略**：16K 保留给响应的策略值得参考

## 安装与使用

```bash
# npm 安装
npm install -g @earendil-works/pi-coding-agent

# TUI 交互模式
pi

# Print mode（非交互）
pi -p "query"

# JSON 模式（事件流）
pi -p "query" --mode json

# 添加 MCP 服务器
pi mcp add github --command "npx @modelcontextprotocol/server-github"

# 安装第三方扩展
pi install npm:@foo/pi-tools
pi install git:github.com/badlogic/pi-doom

# 作为 SDK 使用
import { Agent } from "@earendil-works/pi-coding-agent";
const agent = new Agent({ model: "claude-opus-4-8" });
const result = await agent.run("Summarize the failing tests and propose a fix.");
```

## 限制与注意事项

- Pi 尚未在 Terminal-Bench 或任何公开基准上进行正式评估
- 沙箱和审批门是 opt-in 扩展（安全功能默认关闭）
- 极简设计依赖强大模型，对弱模型可能不可靠

## 关键链接

- GitHub: https://github.com/earendil-works/pi
- 文档: https://pi.dev/
- npm: https://www.npmjs.com/package/@earendil-works/pi-coding-agent
- TensorLake 博客: https://tensorlake.ai/blog/pi-coding-agent-efficient-system-prompting
