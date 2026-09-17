---
name: qodo-agent-toolbox
description: Qodo Agentic Toolbox — 为 AI coding agent 提供代码质量/规则/审查的技能集。触发词：Claude Code规则/PR审查/代码标准/LLM编程质量。
trigger: Qodo Agentic Toolbox coding agent quality rules review
triggers:
  - Qodo coding agent
  - qodo-get-rules
  - qodo-pr-resolver
  - Claude Code 规则
  - 代码质量 agent
  - agent skill 标准
---

# Qodo Agentic Toolbox — Agent 代码质量技能集

## 核心定位

Qodo Agentic Toolbox 将 Qodo 平台的代码质量、审查、规则管理能力封装为 **Agent Skills**，让 coding agent 在编写代码**之前**就能加载团队规范，在 PR 创建**之前**就能进行独立审查。

核心理念：**Shift-left quality** — 把质量检查左移到编码阶段，而非仅在 PR 环节。

## 核心技能

### qodo-get-rules

在编写/重构代码之前，自动获取当前任务最相关的编码规范。

- 语义搜索匹配相关规则
- 支持 ERROR/WARNING/RECOMMENDATION 严重级别
- 组合 topic-based 和 cross-cutting 规则检索
- 返回格式：`severity + rule text + applicability说明`

### qodo-pr-resolver

获取当前分支 PR 的 Qodo 审查意见，修复问题或回复评论。

- 支持 GitHub/GitLab/Bitbucket/Azure DevOps/Gerrit
- 交互式修复和批量修复模式
- 内联评论处理 + 自动 commit
- 振荡检测（防止修复方案反复撤销）
- 跨审查轮次的自动去重

### qodo-codebase-wisdom

利用 Qodo 关系图谱、PR 历史、实时 Git 状态回答结构性问题。

- 追踪回归
- 映射跨仓库影响
- 回答"这段代码改了什么"

### qodo-review

在 PR 存在之前，对本地已提交和未提交的更改运行 Qodo 审查。

- 利用实时会话上下文增强审查质量
- 主动发现问题而非被动等待 PR

### qodo-manage-standards

从 agent 会话内部管理 Qodo 规则本身（管理员权限）。

- 创建/更新/激活/停用/重设范围/批量编辑规则

## 安装方式

```bash
# 安装全部 Qodo 技能
npx skills add qodo-ai/qodo-skills

# Claude Code
/plugin install qodo-skills@claude-plugins-official

# 手动安装
npx skills add qodo-ai/qodo-skills/skills/qodo-get-rules
npx skills add qodo-ai/qodo-skills/skills/qodo-pr-resolver

# 登录
qodo login
```

## Agent 兼容性

| Agent | 安装目录 | 调用方式 |
|-------|---------|---------|
| Claude Code | `~/.claude/skills/` | `/qodo-get-rules` `/qodo-pr-resolver` |
| OpenAI Codex | `$HOME/.agents/skills/` | `$qodo-get-rules` `$qodo-pr-resolver` |
| Cursor | `~/.cursor/skills/` | Command palette |
| Windsurf | `~/.windsurf/skills/` | Flow menu |
| Cline | `~/.cline/skills/` | Skill invocation |
| 任何 Agent Skills 兼容 agent | — | 通用 |

## 与 Hermes 的关系

### 当前状态
- Qodo Agentic Toolbox 是闭源 SaaS，需要 Qodo API key
- 不适合离线/Hermes 环境直接使用

### 价值参考点

1. **qodo-get-rules 的"规则前置加载"模式**：
   - 在编码前加载适用规则 → 符合 Hermes 技能系统设计方向
   - 现有 `agent-framework-comparison-2026.md` 可补充"编码前规则加载"最佳实践

2. **qodo-pr-resolver 的主动审查模式**：
   - 在 PR 创建前审查本地更改 → 这是 agent coding workflow 的质量门控创新
   - Hermes 可参考此模式：在 commit 前执行本地审查

3. **Agent Skills 标准**：
   - Qodo 遵循 [Agent Skills Standard](https://www.agentskills.com/)（agentskills.io）
   - Hermes SKILL.md 格式已与 Agent Skills 标准对齐
   - 这是行业互操作性的信号，Hermes 技能系统方向正确

## 关键链接

- GitHub: https://github.com/qodo-ai/qodo-skills（52 stars，MIT license）
- 主页: https://www.qodo.ai/features/qodo-agentic-toolbox/
- Claude Code 插件: https://claude.com/plugins/qodo
- Agent Skills 标准: https://www.agentskills.com/
