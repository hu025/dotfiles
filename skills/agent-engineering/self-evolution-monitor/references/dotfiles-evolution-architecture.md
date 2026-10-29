# dotfiles 进化仓库架构

## 模式

将 `~/dotfiles/` 作为 agent 进化仓库，所有技能/脚本/报告 git 管理。

```
~/dotfiles/           ← 进化仓库（git）
├── bin/               ← 可执行脚本
│   ├── sync-skills   ← 同步到 ~/.hermes/skills/
│   └── deploy-dotfiles
├── skills/           ← 所有技能（46+ 分类）
├── self-improvement/ ← 自主进化核心
│   └── agent_core.py
├── logs/             ← 日志
└── benchmarks/       ← 基准

~/.hermes/             ← 生效目录（从 dotfiles 同步）
└── skills/
```

## 工作流

每次会话结束时：
```bash
~/dotfiles/bin/sync-skills              # 同步到 hermes
~/dotfiles/bin/deploy-dotfiles push     # commit dotfiles
```

## agent_core.py 命令

| 命令 | 用途 |
|------|------|
| `success <action> [detail]` | 记录成就 |
| `failure <action> <error>` | 记录失败 |
| `learning <what> <source> <outcome>` | 记录学习 |
| `improve <area> <what> <result>` | 记录改进 |
| `daily` | 生成日报 |
| `weekly` | 生成周报 |
| `status` | 系统状态采样 |

## cron jobs（自动）

- 每日 23:00 → 生成日报 → 发 QQ
- 每周日 23:00 → 生成周报 → 发 QQ

## 关键陷阱

- agent_core.py 位于 `~/.hermes/self-improvement/`，不在 dotfiles 里（dotfiles 里的 agent_core.py 是副本，仅用于参考）
- dotfiles 里 skills 目录下可能有嵌入式 .git（inkos/pharaoh-write/story-foundry），需要 `.gitignore` 排除
- ESP32 等项目完全清理后，相关技能也要同步删除（skills/devops/ 下 esp32-* 全部删除）

## 进化目标

让 agent 越来越少依赖指令，自己提出可行方案，用户只需说「我要什么」而非「怎么做」。
