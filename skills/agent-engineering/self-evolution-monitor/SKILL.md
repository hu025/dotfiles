---
name: self-evolution-monitor
version: 1.0
description: 复杂任务完成后自动沉淀为可复用技能
trigger: complex tasks (>=5 tool calls or 3+ steps)
---

# Self-Evolution Monitor

## Trigger
在任何复杂任务完成后（>=5 tool calls 或 3+ 步骤），自动触发。

## Process

1. **评估**：这个任务的结果是否可复用？是否解决了非平凡的问题？
2. **凝练**：提取关键步骤、命令、判断逻辑，去除临时性细节
3. **创建技能**：
   - 文件名：`~/.hermes/skills/<category>/<skill-name>.md`
   - 使用 `skill_manage(action='create', name='...', content='...', category='...')`
4. **注册**：技能自动出现在 skills_list 中，下次可直接 `skill_view` 调用

## 进化仓库架构

完整模式见 `references/dotfiles-evolution-architecture.md`：
- dotfiles 作为 git 管理的进化仓库
- 每次会话结束 → sync-skills → deploy-dotfiles push
- agent_core.py 采集成功/失败/学习/改进记录
- 每日 23:00 日报 + 每周日 23:00 周报（自动 cron）

## 判断标准

✅ 应该创建技能的情况：
- 错误排查流程（非明显 bug，有探索过程）
- 多步骤配置/部署流程
- 跨工具协作的复杂工作流
- 用户明确说"记住这个"或"下次这样做"
- 解决了非平凡的系统性问题

❌ 不需要创建技能的情况：
- 简单的一次性问答
- 纯信息查询无操作
- 用户已明确不想保存的临时探索

## 技能命名规范
- 使用 kebab-case：`qq-bot-reconnect-sequence`
- 包含领域前缀：`devops/`, `finance/`, `messaging/`, `system/`

## 创建后操作
- 同步更新 `skills/devops/skills-library-management/references/hermes-openclaw-ecosystem-YYYY-MM-DD.md`（如果涉及生态系统）
- 完成后向用户报告："已将 [任务名] 沉淀为技能 [skill-name]"
