---
name: dotfiles-evolution
version: "1.0"
author: self
description: dotfiles 进化仓库管理，技能/脚本同步，GitHub 推送
---

# dotfiles 进化仓库

## 当前状态（2026-09-07）
- 路径：~/dotfiles/，git 管理，已推送 GitHub（hu025/dotfiles）
- 内容：46 个技能分类 + 自主进化核心
- 自主进化核心：`~/.hermes/self-improvement/agent_core.py`
- 同步脚本：`~/dotfiles/bin/sync-skills` + `deploy-dotfiles`
- GitHub 远程：git@github.com:hu025/dotfiles.git（SSH，已配置推送）
- 注意：skills/ 目录下如有嵌入式 .git 目录（嵌入式子仓库），commit 前需删除，否则 git add 无法识别

## 目录结构
```
~/dotfiles/
├── bin/               # sync-skills, deploy-dotfiles
├── skills/            # 46个技能分类（从 hermes 复制）
├── self-improvement/  # agent_core.py + reports/
└── README.md
```

## 每次修改后的工作流
```bash
# 1. 同步到 hermes
cp -r ~/dotfiles/skills/<category> ~/.hermes/skills/
# 或
~/dotfiles/bin/sync-skills

# 2. commit
cd ~/dotfiles && git add -A && git commit -m "描述"

# 3. push（需 Classic PAT）
cd ~/dotfiles && git push origin main
```

## 新增技能到 dotfiles
1. 写到 `~/dotfiles/skills/<category>/SKILL.md`
2. `cp -r ~/dotfiles/skills/<category> ~/.hermes/skills/` 同步到 hermes
3. `cd ~/dotfiles && git add -A && git commit`

## deploy-dotfiles 用法
```bash
~/dotfiles/bin/deploy-dotfiles push   # commit + 可选 push
~/dotfiles/bin/deploy-dotfiles sync  # 只同步不 commit
```

## 当 dotfiles 推送到新机器
```bash
git clone https://github.com/hu025/dotfiles.git ~/dotfiles
~/dotfiles/bin/sync-skills  # 同步到 ~/.hermes/skills/
```
