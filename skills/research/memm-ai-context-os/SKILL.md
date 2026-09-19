# MEMM / AI Context OS — Filesystem-Native Agent Memory

## 核心定位

**文件即记忆**：canonical state lives in files（不是向量数据库，不是外部 DB）。本地文件夹 → universal, tool-agnostic memory layer for AI agents。MIT 许可。

## 核心论文论点

> The file, not the vector, is the optimal primitive for human-AI collaborative memory.

论据：透明（人机共读）、可版本控制、可移植、可组合，同时对人和对 AI 都可理解。

## L0 / L1 / L2 分层模型

| 层级 | 内容 | 格式 |
|------|------|------|
| **L0** | 一行摘要 | YAML frontmatter `l0:` 字段 |
| **L1** | 操作摘要 | Markdown body 第一段 |
| **L2** | 完整细节 | Markdown body 剩余部分 |

Token budget 内贪婪分配：L0 全加载 → L1 → L2 只加载 top cluster。

## 存储模型

```
~/AI-Context-OS/
├── inbox/              # 临时捕获区
├── sources/            # 外部引用（只读）
├── User_Folders/       # 用户自定义（物理位置不影响语义分类）
└── .ai/               # 系统基础设施（固定）
    ├── rules/          # AI 行为规则（最高优先级）
    ├── journal/        # 每日日志
    ├── tasks/          # 任务追踪
    ├── scratch/        # 临时 AI 输出（TTL）
    ├── config.yaml     # 工作区配置
    └── index.yaml      # 自动生成 L0 目录
```

**关键不变式**：文件物理位置不影响语义分类，分类来自 YAML frontmatter `type:` 字段。

## SQLite 仅用于可观测性

- 路径：`{workspace}/.cache/observability.db`
- 用途：遥测和优化信号（请求量、使用统计、健康快照）
- **非 canonical**：不替代也不拥有记忆数据模型

## 评分引擎

多信号混合评分：
1. **BM25**（关键词相关性）
2. **语义启发**（非 embedding）
3. **importance**（YAML frontmatter）
4. **access count**（使用频率）
5. **last access**（新鲜度）

每条记忆的 L0/L1/L2 加载由 token budget 控制，超出预算时记录 unloaded-but-available。

## MCP 集成

- MCP stdio server
- MCP HTTP server：`127.0.0.1:3847/mcp`
- 生成的 router 文件：`claude.md`、`.cursorrules`、`.windsurfrules`

## 与其他框架对比

| 维度 | RAG | 手动上下文文件 | MEMM |
|------|-----|--------------|------|
| 透明度 | 低（embedding 不透明）| 高 | **高** |
| 治理机制 | 无 | 无 | **有**（decay/conflict/consolidation）|
| Token 效率 | 中 | 低（全量注入）| **高**（L0/L1/L2 自适应）|
| 基础设施 | 重（向量 DB）| 无 | **轻**（文件系统）|

## 技术栈

React + TypeScript + Rust（Tauri 桌面应用）。也可作为 headless MCP server 独立运行。

## 落地建议

**立即可用**：MEMM 已有 MCP server，workflow 简单。对于已有复杂上下文文件的用户，过渡成本低。

**与 Hermes 技能系统共鸣**：MEMM 的 typed memory files 概念与 Hermes SKILL.md 格式高度对齐，可作为 Hermes 记忆系统的 UI 层参考。

## 来源

- 官网: https://memm.dev
- 论文: https://memm.dev/docs/paper
- GitHub: https://github.com/alexdcd/AI-Context-OS
- 当前 stars: 72（暂不活跃，公开发布快照受限）
