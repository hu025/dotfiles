---
name: memu
description: MemU — 轻量跨Agent记忆系统，500行核心记忆逻辑，支持 Hermes 专用适配器（memu-hermes），会话日志→可复用Markdown技能。与Hermes/SOUL.md深度集成。
triggers:
  - MemU
  - memu-hermes
  - cross-agent memory
  - session-to-skill
---

# memU — Personal Memory Across Agents

## 核心价值

轻量级跨 Agent 记忆系统（Apache-2.0）。核心记忆逻辑仅 500 行，可检验、可理解、可适配。

**关键创新**：
- 跨会话/跨 Agent/跨设备统一记忆（Wiki 格式存储）
- Hermes 专用适配器 `memu-hermes`（读取 `~/.hermes/state.db` SQLite，写入 `~/.hermes/SOUL.md`）
- 会话日志自动蒸馏为可复用 Markdown 技能
- 支持 Codex/Claude Code/Cursor/OpenClaw/Hermes 等主流 Agent

**14.3K stars**，社区活跃（Discord/ X）。

---

## 架构

### Host 适配器矩阵

| Host | Binary | Session Log | Instruction File |
|------|--------|-----------|-----------------|
| Hermes Agent | `memu-hermes` | `~/.hermes/state.db` (SQLite) | `~/.hermes/SOUL.md` |
| Claude Code | `memu-claude-code` | `~/.claude/projects/*/.jsonl` | `~/.claude/CLAUDE.md` |
| Codex | `memu-codex` | `~/.codex/sessions/**/*.jsonl` | `~/.codex/AGENTS.md` |
| Cursor | `memu-cursor` | `~/.cursor/projects/*/agent-transcripts/**.jsonl` | `./AGENTS.md` |
| OpenClaw | `memu-openclaw` | `~/.openclaw/agents/*/openclaw-agent.sqlite` | `~/.openclaw/workspace/AGENTS.md` |

### 记忆工作流

1. **Memorize** — 定时后台任务抓取会话日志，切片为独立任务文件，Agent 自行蒸馏为 memory/skill Markdown，`commit` 提交到存储
2. **Retrieve** — Agent 执行任务前，`retrieve`（→ `progressive_retrieve`）拉取相关记忆

### 存储后端

| Provider | DSN | Vector Search | 用途 |
|----------|-----|--------------|------|
| inmemory | — | brute-force | 测试 |
| sqlite | `sqlite:///path.sqlite3` | brute-force | 本地/单写 |
| postgres | `postgresql://...` | pgvector | 并发/大规模 |

Embedding providers: `openai`（默认）/ `jina` / `voyage` / `doubao` / `openrouter`

---

## 安装（Hermes）

```bash
# 方式1：pip
pip install memu-cli

# 方式2：npx（无安装）
npx memu-cli --help
uvx --from memu-cli memu

# 方式3：memu-hermes 专用
# 告诉 Agent：
# > Read https://raw.githubusercontent.com/NevaMind-AI/MemU/main/SKILL.md and follow it
```

### Hermes 集成步骤

1. 安装：`pip install memu-cli`
2. 初始化：`memu-agent detect`（探测会话日志和指令文件）
3. 配置 `~/.memu/config.env`：
   ```
   MEMU_MEMORY_MODE=local
   MEMU_DB=~/.memu/memu.sqlite3
   MEMU_EMBED_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```
4. 注册定时任务：`memu-hermes` 定时切片会话日志
5. Agent 指令文件中注册 retrieve hook（告诉 Agent 每次回答前先 retrieve）

### 配置项

```bash
# 检查配置
<binary> doctor   # 显示解析后的模式和检索路径

# 手动检索
memu-hermes retrieve "上次我让你写的小说项目在哪"
```

---

## 与 Hermes SOUL.md 集成

MemU 与 SOUL.md 的协同方式：
- MemU 的记忆结果以 Markdown 格式存储在 SOUL.md 中
- 每次会话结束时，memu-hermes 从 `~/.hermes/state.db` 提取关键信息
- Agent 通过 `~/.hermes/SOUL.md` 读取长期记忆

---

## 局限

- 意图蒸馏完全由 Agent 自行完成（MemoryService 只存/检索，不做 LLM 调用）
- 依赖定时任务调度
- 跨设备同步需要 MemU Cloud 或手动配置 Postgres

---

## 来源

- GitHub: https://github.com/NevaMind-AI/MemU
- Website: https://memu.so
- SKILL.md: https://raw.githubusercontent.com/NevaMind-AI/MemU/main/SKILL.md
