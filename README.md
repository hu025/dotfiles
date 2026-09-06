# dotfiles

自我进化知识库。包含所有技能、脚本、报告。

## 目录结构

```
dotfiles/
├── bin/                  # 可执行脚本
│   ├── sync-skills       # 同步技能到 hermes
│   └── deploy-dotfiles   # 部署脚本
├── skills/               # 所有技能（46个分类）
├── self-improvement/     # 自主进化核心
│   ├── agent_core.py
│   ├── reports/daily/    # 日报
│   └── reports/weekly/   # 周报
├── logs/                 # 记录
└── benchmarks/           # 基准测试
```

## 工作流

1. 我修改 `~/dotfiles/` 下的文件
2. 自动 commit 到 `~/dotfiles/.git`
3. 可选：推送到远程仓库
4. 用户机器：`git pull` 后用 `bin/sync-skills` 同步到 `~/.hermes/skills/`

## 目标

让强化过程**可追溯、可回滚、可迁移**。
