---
name: autonomous-self-improvement
description: 自主进化核心系统。状态监控/成就记录/每日日报/每周架构审查，替代人工汇报循环。
trigger: 自主进化 / 自我改进 / 每日回顾 / 周报 / 架构审查 / 系统状态
version: "1.0"
author: saber
tags: []
related_skills: []
---

# 自主进化核心系统

## When to Use

- 每次会话结束前自动调用记录流程
- 收到"每日回顾"/"架构审查"时触发
- 主动侦察：每3天检查一次系统状态和记忆库

## When NOT to Use

- 正在执行用户任务时不要停下来做回顾
- 磁盘 < 500MB 时停止非必要侦察操作
- 不要在单次会话中反复检查同一服务

## 系统架构

```
~/.hermes/self-improvement/
├── agent_core.py          # 核心引擎（状态采样/记录/报告）
├── reports/
│   ├── daily/            # 日报 ~23:00 自动生成
│   └── weekly/           # 周报 周日 23:00 自动生成
└── logs/
    ├── heartbeat.json
    ├── success_YYYY-MM-DD.json
    ├── failure_YYYY-MM-DD.json
    ├── learning_YYYY-MM-DD.json
    └── improvements_YYYY-MM-DD.json
```

## 核心引擎用法

```bash
# 状态采样
python3 ~/.hermes/self-improvement/agent_core.py status

# 记录成就（会话结束时调用）
python3 ~/.hermes/self-improvement/agent_core.py success "<主要成就>" "<详情>"

# 记录失败
python3 ~/.hermes/self-improvement/agent_core.py failure "<动作>" "<错误摘要>" "<详情>"

# 记录学习
python3 ~/.hermes/self-improvement/agent_core.py learning "<学到什么>" "<来源>" "<效果>"

# 记录改进
python3 ~/.hermes/self-improvement/agent_core.py improve "<领域>" "<做了什么>" "<结果>"

# 生成日报（cron自动调用）
python3 ~/.hermes/self-improvement/agent_core.py daily

# 生成周报（cron自动调用）
python3 ~/.hermes/self-improvement/agent_core.py weekly
```

## 会话结束流程

每次会话结束前，执行以下记录（由 agent 自动完成）：

1. **记录成就**：`success "<主要成就>" "<关键结果>"`
2. **记录失败**（如有）：`failure "<动作>" "<错误>"`
3. **记录学习**（如有新知）：`learning "<内容>" "<来源>" "<效果>"`
4. **记录改进**（如有）：`improve "<领域>" "<内容>" "<结果>"`

## 主动侦察规则

每 3 天检查一次：
- [ ] 记忆库陈旧条目（30天+未更新的 fact → 清理或更新）
- [ ] 技能库过时/错误（发现即修，不等用户指令）
- [ ] 系统依赖安全更新（pip list / pacman -Qu）

**禁止**：无意义的循环检查、不经验证的安装、资源耗尽前继续操作（磁盘 < 500MB 时停止非必要操作）

## 用户偏好：自主≠选 SOTA

**关键纠错（2026-09-07）**：用户在系统自主升级到 MiniMax M3（80.5% SWE-bench）后主动切回 M2.7。

**教训**：
- "自主无限制进化"不等于"必须选最贵/最强模型"
- 用户有成本/性能/中文质量/响应速度等多维权衡，模型是其中一维
- 模型升级必须问自己：**这个升级用户感知得到吗？愿意为额外能力多付费吗？**
- 默认倾向：成熟稳定的中价位模型；SOTA 仅在用户明确要求或任务硬性需要时切换

**完整案例数据**：见 `references/model-upgrade-vs-user-cost.md`（含 M3 vs M2.7 维度对比、回退原因推测、验证清单）

**自主选择模型前要做**：
1. 列出当前 vs 候选模型的差异（benchmark/单价/中文质量/速度）
2. 评估任务是否需要该差异（"用不用得上"）
3. 如果不需要 → 不升级
4. 如果需要 → 询问用户或给用户选项
5. 升级后让用户实际跑一段时间，**主动询问是否回退**

## 每日日报要点

自动生成，内容含：
- 系统状态（磁盘/进程/服务）
- 今日成就 Top10
- 今日失败 Top5
- 今日学习
- 今日改进
- 明日改进计划

## 每周架构审查六大维度

1. **模型层**：当前模型表现、切换需求
2. **记忆层**：陈旧条目、矛盾信息、用户偏好更新
3. **技能层**：过时/可合并/新工具封装
4. **工具层**：依赖过时、安全漏洞、可封装重复操作
5. **浏览器自动化**：脚本稳定性、新页面适配
6. **自主改进**：成功率/失败率趋势、系统性解决方向

## 部署记录

- 首次部署：2026-09-07
- Cron Job：日报 `0 23 * * *` / 周报 `0 23 * * 0`
- 投递：QQ Home Channel（qq:1373E0D0CA6C325E0DFFADF44B7BFA55）
