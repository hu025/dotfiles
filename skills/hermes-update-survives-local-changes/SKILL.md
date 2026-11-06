---
name: hermes-update-survives-local-changes
description: Use when an update wipes local patches or a platform.
version: 1.0.0
author: luna
license: MIT
metadata:
  hermes:
    tags: [hermes, update, plugins, platforms, diagnostics]
    related_skills: [hermes-deep-inspection]
---

## When to Use

- Hermes 升级/checkout 之后某个平台或功能“自己没了”（config 里有、日志里没有）。
- cron 投递报 `unknown platform '<名字>'`。
- 想往 `gateway/*.py` / `hermes_cli/*.py` 打本地补丁时（先读完这条）。

# Hermes 更新会吃掉本地核心补丁

**规则：任何需要长期存在的改动，一律走插件（`hermes plugins install`）或配置，绝不手改 `gateway/*.py`、`hermes_cli/*.py` 等核心文件。**

**原因（2026-11-06 实锤）：** 自制 NapCat 平台补丁（`gateway/platforms/napcat*.py`、`tools/qq_tool.py`、`gateway/config.py` / `gateway/run.py` / `hermes_cli/platforms.py` / `hermes_cli/toolsets.py` 四处修改）在更新流程里被 autostash 进 `stash@{0}^3` 后**从未 pop**，工作区文件全部消失、`git status` 干净，看起来像“功能自己没了”。结果：`platforms.napcat` 配置仍在却从未被加载，cron 投递 `napcat:…` 每次报 `unknown platform 'napcat'`。

**检查步骤（整体检查时按序）：**
1. `git -C ~/.hermes/hermes-agent stash list` —— 有没有 `hermes-update-autostash-*` 没 pop；`git stash show --include-untracked '<stash>^3'` 能找回未跟踪副本。
2. 对着 config 里的每个 `platforms.<name>`，在 `gateway.log` 里确认有对应 “Connecting to … / ✓ … connected”；只在 config 里、日志零命中的平台就是没加载。
3. cron 侧 `grep "unknown platform" ~/.hermes/logs/errors.log` —— 命中即投递目标指向已消失的平台。
4. 修法：优先装官方目录插件（QQ/OneBot 用 `hermes plugins install --yes-deps onebot-platform`，平台名 `onebot`）→ 改配置 → 改 cron deliver 前缀 → `systemctl --user reload hermes-gateway.service`（SIGUSR1 优雅重启，会等当前 turn 结束）→ 用一次性 no-agent cron 脚本在重启后验收（当场看不到结果）。
5. 改 `config.yaml` 必须文本级替换（`yaml.safe_dump` 会把脱敏占位写成字面量），改完 `diff` 确认只有目标块变化、跑 `hermes config check`。
