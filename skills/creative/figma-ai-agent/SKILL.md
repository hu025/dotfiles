---
name: figma-ai-agent
description: "Figma AI Agent: Skills系统+MCP连接器+Canvas双向同步。触发词：Figma Agent/MCP/Custom Skills/设计系统自动化。"
triggers:
  - Figma Agent
  - Figma AI
  - 设计系统自动化
  - Figma MCP
  - Claude Code Figma
  - Figma Make
  - Figma 技能
  - Custom Skills Figma
---

# Figma AI Agent — 设计系统×Agentic工作流

> 触发词：Figma Agent / Figma AI / 设计系统自动化 / Figma MCP / Claude Code Figma

Figma 在 Config 2026 将 AI Agent 能力全面开放，形成完整的 Agentic 设计工作流。与传统设计工具不同，Figma Agent 的核心价值在于：
- **技能（Skills）**：Markdown 文件封装设计规范，驱动外部 AI Agent 在 Figma Canvas 上操作
- **MCP 连接器**：Figma 作为 MCP Server，外部 Agent（Claude Code/Codex/Cursor）通过 `use_figma` 工具读写设计文件
- **代码↔画布双向同步**：`generate_figma_design`（HTML→Figma）+ `use_figma`（Figma→代码）

---

## 核心能力（2026年9月现状）

### 1. Figma Agent（内置于 Figma Design）

| 功能 | 状态 | 说明 |
|------|------|------|
| 设计反馈 | ✅ 可用 | 无障碍审查、人物视角批评、转化率建议 |
| 图片编辑 | ✅ 可用 | 抠图、从图片生成变更 |
| 设计系统创作 | ✅ 可用 | 组件/样式/变量操作 |
| 矢量编辑/Draw | 🔜 即将 | 创建/编辑矢量图、图标、布尔运算 |
| 图标生成 | 🔜 即将 | 生成图标、修改几何、创建图标集 |
| Slots | 🔜 即将 | 操作组件 Slot |
| 原型/交互 | 🔜 即将 | 创建原型、添加交互、定义导航 |

**自定义技能系统**：
- 技能 = Markdown 文件（遵循 Agent Skills 规范 agentskills.io/specification）
- 支持 `/slash` 命令调用（如 `/follow-ds-guidelines`、`/design-crit`）
- 可发布到团队/组织，支持版本管理
- 与 MCP 连接器配对：技能可引用连接器，Agent 在同一提示中调用技能+连接器

### 2. Figma MCP Server（外部 Agent 访问 Figma）

**`use_figma` 工具**：让外部 Agent 直接操作 Figma Canvas，基于你的设计系统
**`generate_figma_design` 工具**：将 HTML 页面逆向转为可编辑 Figma 图层

已支持 MCP Client（2026年9月）：Augment、Claude Code、Codex、Copilot CLI、Copilot VS Code、Cursor、Factory、Firebender、Warp

**工作流**：设计师在 Figma 定义设计系统 → Agent 读取组件/变量/MCP → Agent 在代码中实现 → Code Connect 同步回 Figma → 设计师审核

### 3. Figma Make（AI 产品原型构建）

无需 Figma 账号可直接通过 Prompt 构建产品原型和工作流：
- AI PRD 生成器、AI 路线图生成器、MVP 构建器、AI 应用构建器
- **AI Agent Workflow Builder**：PM 描述功能→生成逻辑/流程/边界案例，通过 Linear/Jira 连接器直接创建开发任务

### 4. MCP 连接器生态（Verified Partner）

Figma Make 作为 MCP Client，连接外部工具获取上下文：

| 连接器 | 核心能力 |
|--------|----------|
| Notion | 读取 PRD/文档，创建/更新页面 |
| GitHub | 读取 Repos/Issues/PR，创建 Issue/PR |
| Linear | 读取 Issues/Projects，创建管理工作项 |
| Jira/Confluence/Compass | Atlassian 全家桶 |
| zeroheight | 读取设计系统风格指南，生成符合规范的原型 |
| Marvin | 客户反馈数据，验证原型 |
| Granola | 会议记录，提取行动项 |
| Amplitude | 用户数据，生成有产品上下文的原型 |
| Zapier | 9000+ 应用的集成 |

### 5. Custom Skills 生态（社区技能）

9个官方示例技能（Figma Community）：

| 技能 | 用途 |
|------|------|
| `/figma-generate-library` | 从代码库创建 Figma 组件 |
| `/figma-generate-design` | 用现有组件和变量创建新设计 |
| `/create-voice` | 从 UI Spec 生成无障碍规范（VoiceOver/TalkBack/ARIA） |
| `/cc-figma-component` | 从 JSON Contract 生成 Figma 组件 |
| `/apply-design-system` | 将现有设计连接到系统组件 |
| `/rad-spacing` | 应用层级间距（变量+降级） |
| `/sync-figma-token` | 代码与 Figma 变量之间的设计 Token 同步（漂移检测） |
| `/multi-agent` | 运行并行工作流并在 Augment 中实现设计 |

---

## 落地动作

### 场景1：Hermes Agent 读取 Figma 设计系统

Figma MCP Server 已内置于 native-mcp skill 的 MCP 服务器列表。若需从外部 Agent 访问 Figma 设计文件：

1. 获取 Figma Personal Access Token
2. 配置 Figma MCP Server 连接（参考 native-mcp skill）
3. Agent 通过 `use_figma` 读取组件/变量/样式

### 场景2：设计系统规范技能化

将团队设计规范编写为 Markdown 技能文件，上传到 Figma Agent：
- 命名规范、颜色变量、间距规则、排版系统
- `/follow-ds-guidelines` 技能自动约束 AI 输出

### 场景3：Figma Make 产品原型工作流

PM 在 Figma Make 中用自然语言描述产品需求 → 生成 PRD/原型/用户流程 → 通过 Linear/Jira 连接器直接创建开发任务

---

## 与现有技能的关系

- **mcp-integration**：已列 Figma MCP Server，本技能补充 Agentic 工作流细节
- **popular-web-designs**：已引用 Figma 设计系统示例（字体/颜色），本技能补充 AI Agent 维度
- **claude-design**：聚焦 HTML 原型设计，Figma MCP Server 可将 HTML 同步回 Figma

---

## 来源链接

- Figma Agent 官方博客：https://www.figma.com/blog/the-figma-agent-is-here/
- Agents 开放 Canvas：https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/
- Custom Skills 文档：https://help.figma.com/hc/en-us/articles/40283639496599
- MCP 连接器：https://help.figma.com/hc/en-us/articles/35440096186007
- Config 2026 全览：https://help.figma.com/hc/en-us/articles/39582753756695-What-s-new-from-Config-2026
- Agentic Workflows：https://www.figma.com/resource-library/agentic-framework
- Figma AI 主页：https://www.figma.com/ai/
- Community Skills：https://www.figma.com/community/skills
- Agent Skills 规范：https://agentskills.io/specification
