---
name: webwright-skill-factory
description: Microsoft Webwright Skill Factory — 终端原生浏览器Agent框架，代码即动作，可执行技能库，WebArena 86.7%。与browser-use互补。
tags: [browser, ai-agent, playwright, python, skill-factory, autonomous-improvement]
category: browser-use
---

# Webwright Skill Factory 技能文档

## 核心定位

与 browser-use 的根本区别：

| | browser-use | Webwright Skill Factory |
|---|---|---|
| **范式** | Agent在有状态浏览器中逐步操作 | Agent写Playwright脚本，浏览器是一次性的 |
| **状态** | 浏览器会话 | 本地工作区 = 代码 + 日志 + 截图 |
| **动作空间** | LLM选择step-by-step操作 | Agent直接写Python/Playwright代码 |
| **技能本质** | 模型阅读的文档 | **可执行程序，无需模型** |
| **技能复用** | 无 | 成功解决后自动蒸馏为可复用脚本 |

## 核心数据

- **GitHub**: github.com/microsoft/Webwright
- **Stars**: 5,960+
- **License**: MIT
- **框架**: Python + Playwright
- **发布**: 2026-04-08
- **Benchmark**: WebArena 86.7%，Odysseys 60.1%

## 安装

```bash
pip install webwright  # 或 uv add webwright
playwright install chromium
```

## 核心概念：Skill Factory

### 原理

大多数 Agent 技能是模型阅读的**文档**。Skill Factory 的技能是**可执行程序**——无需模型即可运行。

每次成功解决任务后，留下一个 Playwright 脚本。Skill Factory 将这些脚本蒸馏为：
- **可复用**：相同模板的任务对齐，差异变为参数
- **已验证**：必须复现自身记录的答案才通过
- **零token**：首次后无需再调用模型

### 核心数据

- WebArena held-out accuracy: 55% → 70%（+15pp）
- 可执行技能：~40s，零token
- 训练集准确率：76.7% → 86.7%

### 工作流

```
solve → 留下脚本 → build(蒸馏) → gate(验证) → library(发布)
                                                        ↓
任务来了 → route → recommend → run/adapt/skip → 可直接执行或注入为prior
```

1. **route**: 入口，决定复用策略
2. **recommend**: 检索候选技能，评估fit
3. **build**: 将多个同模板解答蒸馏为一个参数化程序
4. **gate**: 必须复现自身答案才通过（correctness + consistency）
5. **learn**: 整合新技能到library

### 三种复用模式

| 模式 | 行为 |
|---|---|
| `run` | 直接执行，无需模型 |
| `adapt` | 注入为prompt prior，agent阅读后适配 |
| `skip` | 无匹配技能，从头开始 |

## 与 browser-use 的选择

- **browser-use**: 复杂多步、需要规划的交互任务；已有有状态会话管理
- **Webwright**: 重复性任务、脚本化工作流、需要生成可复用技能的场景
- **组合**: Webwright写脚本 + browser-use做规划层

## Skill Factory CLI

```bash
# 推荐技能（决定run/adapt/skip）
python -m webwright.skill_factory route --task "搜索北京到上海的机票"

# 构建新技能（蒸馏成功脚本）
python -m webwright.skill_factory build --run-id <run_id>

# 验证技能（必须复现自身答案）
python -m webwright.skill_factory gate --skill-id <skill_id>

# 列出library中的技能
python -m webwright.skill_factory library list

# 手动创建技能（manual模式）
python -m webwright.skill_factory init --template "flight_search" --params "origin,dest,date"
```

## 集成 Hermes

```bash
mkdir -p ~/.hermes/skills
ln -sfn /path/to/Webwright/skills/webwright ~/.hermes/skills/webwright
```

然后 Hermes 会自动加载 `SKILL.md`。

## 关键文件

- `src/webwright/skill_factory/route.py` — 入口，路由决策
- `src/webwright/skill_factory/build.py` — 蒸馏脚本
- `src/webwright/skill_factory/gate.py` — 验证技能
- `src/webwright/skill_factory/learn.py` — 整合到library
- `docs/skill_factory/manual.md` — 手动模式用法
- `docs/skill_factory/reference.md` — 完整API参考

## 局限

- **蒸馏随机性**: 可能产生脆弱技能，需重试
- **library维护**: 网站变更后技能可能失效，无自动健康检查
- **需Playwright基础**: 代理需能编写Python/Playwright代码

## 核心洞察

Webwright 的核心洞察：**浏览历史 = 代码文件**。browser-use 保留浏览器会话，Webwright 保留脚本。

这意味着：
1. Webwright 的"记忆"是代码，不是状态
2. 可执行技能 = 零token重复执行
3. Skill Factory = 从成功案例中自动提取代码模式
