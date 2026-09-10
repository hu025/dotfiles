---
name: deer-flow
description: DeerFlow 2.0 — ByteDance Super Agent Harness. 触发词：DeerFlow/字节跳动agent/深度研究agent/SOUL.md自更新/Skill Evolution
triggers: [DeerFlow, ByteDance, super agent harness, skill evolution, SOUL.md, 自定义agent]
version: 1.0.0
category: agent-engineering
tags: [multi-agent, skills-system, sandbox, langgraph, langchain, deep-research, self-modifying]
sources:
  - https://github.com/bytedance/deer-flow (81k stars, MIT)
  - https://deerflow.tech/en/docs/harness/skills
  - https://deerflow.tech/en/docs/introduction
created: 2026-09-14
updated: 2026-09-14
---

# DeerFlow 2.0 — Super Agent Harness

## 核心定位

ByteDance 开源的全功能 Super Agent 运行平台（81k ⭐，GitHub Trending #1 Feb 2026）。从内部深度研究工具演化为完整运行时，基于 LangGraph + LangChain，内置所有 agent 需要的组件。

**与现有框架的差异**：
- 不同于 Mastra（TypeScript 全栈）或 Smolagents（极简 Python）：DeerFlow 是开箱即用的完整 harness，配齐 filesystem/memory/skills/sandbox
- 不同于 E2B（纯沙箱）：DeerFlow 整合了沙箱+多智能体编排+技能系统
- 不同于 SWE-agent（单任务 coding）：DeerFlow 面向分钟到小时级别的长时任务

## 架构概览

```
Lead Agent（主控）
  ├── Sub-agents（按需并行派生，作用域隔离）
  ├── Memory（持久化记忆）
  ├── Skills System（按需注入的 Markdown 技能包）
  ├── Sandbox（Docker 隔离执行环境）
  └── Tools（搜索/文件/bash/MCP）
```

后端：Python 3.12+ | 前端：Node.js 22 | 部署：Docker Compose

## 核心创新

### 1. SOUL.md — 自更新 Agent 身份配置

每个 custom agent 有自己的 `SOUL.md` 文件（身份定义）和 `config.yaml`（运行时配置）。

**独特能力**：agent 可以在对话过程中**自己修改自己的 SOUL.md / config.yaml**，实现自我进化，无需重启。

```yaml
# agents/my-researcher/SOUL.md
# Agent 的身份、价值观、行为准则——agent 可自行更新
```

```yaml
# agents/my-researcher/config.yaml
name: my-researcher
skills:
  - deep-research
  - academic-paper-review
```

Agent 通过内部工具触发自我更新，更改后会持久化到磁盘，下次对话生效。

### 2. Skills System — 按需注入的 Markdown 技能包

Skills 不是硬编码能力，而是 Markdown 文件定义的**自包含能力模块**：

```
skills/public/
├── deep-research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── data-analysis/SKILL.md
├── image-generation/SKILL.md
└── video-generation/SKILL.md

skills/custom/
└── your-custom-skill/SKILL.md  ← 用户自定义
```

**SKILL.md 结构**（从 `skills/parser.py` 解析）：
- name / description / category（元数据）
- instructions（分步工作流 + 最佳实践）
- tool_requirements（所需工具）
- resource_references（参考资源）

**按需加载**：只在任务需要时注入系统提示词，不是一次性加载所有技能，保持 context 精简。

**技能演化（Skill Evolution）**：
```yaml
skill_evolution:
  enabled: false  # 开启后 agent 可自主创建/改进 skills/custom/ 下的技能
  moderation_model_name: null  # 安全扫描模型
```

### 3. Sub-agents — 作用域隔离的并行子任务

Lead Agent 分解复杂任务，按需派生 sub-agents：
- 每个 sub-agent 有独立作用域 context、工具集、终止条件
- 支持并行执行（独立任务）或串行链式（需要依赖时）
- Sub-agent 的内部消息不进入父级对话流
- 长时 sub-agent 会压缩历史并注入摘要后继续

### 4. Extension Manager — 运行时可插拔扩展

`config.yaml` 中声明扩展，DeerFlow 自动安装并加载：

```yaml
extensions:
  middlewares:
    - python_package: my_domain_guardrails
    - git_url: https://github.com/org/deerflow-extension
    - local_dir: /opt/extensions/my-tool
```

支持三种来源：Python 包 / Git HTTPS URL / 本地目录。

### 5. 完整 IM 集成

支持 Slack、Telegram、Discord、Feishu/Lark、DingTalk、WeChat、WeCom。用户可以绑定自己的账号（user-owned IM），operator 配置机器人。

### 6. 丰富的内置工具

- **搜索**：DDG、Brave、Tavily、SearXNG（均支持时间范围过滤）
- **执行**：文件操作、bash（沙箱内）
- **MCP**：MCP 服务器连接器
- **生成**：图片、视频、播客、PPT、报告、前端页面

## 部署

```bash
git clone https://github.com/bytedance/deer-flow
cd deer-flow
cp config.example.yaml config.yaml
# 编辑 config.yaml 配置 API keys
docker compose up -d
# 访问 http://localhost:2026
```

**依赖**：Docker + Python 3.12+ + Node.js 22+

**推荐模型**（DeerFlow 官方推荐）：
- Doubao-Seed-2.0-Code（最佳工具调用）
- DeepSeek v3.2（最佳性价比）
- Kimi 2.5（超长上下文）

## 与 Hermes 的关联点

- **Skills 系统**：DeerFlow 的 Markdown SKILL.md 与 Hermes Skill 系统设计思路相似，但 DeerFlow 支持运行时动态加载/禁用（Gateway API，无需重启）
- **Skill Evolution**：DeerFlow agent 可自主创建技能包 → 对应 Hermes 的自主进化能力
- **Sub-agents** → Hermes 的 delegate_task 多智能体编排
- **Sandbox** → Hermes 配合 E2B/code-execution-sandbox 使用场景类似

## 适用场景

✅ 深度研究 + 报告生成（分钟到小时级长时任务）
✅ 自主网页应用构建（从设计到部署）
✅ 数据分析 + 可视化流水线
✅ 多智能体并行探索 + 综合输出
✅ 需要沙箱隔离的代码执行

## 不适合场景

❌ 轻量级单次工具调用（用 Smolagents 更简洁）
❌ TypeScript 优先的项目（用 Mastra）
❌ 纯沙箱隔离执行（用 E2B）
❌ 单任务软件工程（SWE-agent 更专注）

## 参考链接

- GitHub: https://github.com/bytedance/deer-flow
- Docs: https://deerflow.tech/en/docs/introduction
- Skills: https://deerflow.tech/en/docs/harness/skills
- Claude Code 集成: `npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow`
