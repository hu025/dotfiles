---
name: memory-progressive-disclosure
description: Hermes三层渐进披露记忆架构。触发词：记忆太多/上下文污染/token优化。用现有skill机制实现Tier1强制注入→Tier2索引→Tier3按需。
---

# 渐进披露记忆架构

## 问题诊断

Hermes 当前 flat injection 模式：
- `MEMORY.md` (2200 chars) + `USER.md` (1375 chars) = 全量注入每轮
- 无论话题是否相关，所有记忆都占用 token
- 随积累时间增长，信噪比下降

## 三层架构（无核心修改，立即可用）

### Tier 1 — 强制注入层（~500-800 chars）
**每轮全量注入，字节稳定（prefix cache 友好）**

注入内容：
- 用户身份核心：name, pronouns, timezone, language
- Agent persona (SOUL.md)
- 全局执行约束（非negotiable规则）
- 平台/环境 essentials

目标大小：500-800 chars，**只增不减原则**

```
~/.hermes/memory/user/SOUL.md   # Tier 1 核心
```

### Tier 2 — 索引注入层
**session start 注入轻量索引，full content 按需获取**

注入方式：`skills_list` → `skill_view` 已经是渐进披露模式
索引 = skill name + description (约 40-60 chars/skill)

Tier 2 内容：
- 项目上下文：active project status, architecture decisions
- 详细用户profile：beyond identity essentials
- 环境知识：tool quirks, pitfalls, network config
- Lessons learned：corrections, debugging discoveries

**核心规则**：`skills_list` 输出即 Tier 2 索引，agent 主动判断加载哪些

### Tier 3 — 技能程序层
**skills 系统本身是 Tier 3**

```
~/.hermes/skills/          # 全部可执行技能
skill_view(name)           # 按需加载完整 SKILL.md
```

## 落地步骤

### 1. SOUL.md Tier 1 压缩
检查 SOUL.md 是否混入 capability catalog → 移除实现细节

### 2. skill description 极简化
每个 skill 的 `description` 字段：
- 必须 ≤ 60 chars
- 必须 self-contained（不看正文也能判断是否相关）
- 必须包含 trigger condition

### 3. skill 分类整理
```
~/.hermes/skills/
├── user-profile/          # Tier 2: 用户偏好类
├── project/               # Tier 2: 项目上下文类
├── environment/           # Tier 2: 环境知识类
└── procedural/            # Tier 3: 可执行技能
```

### 4. 关键洞察（来自 rr5201314）
> `skills_list` 天然返回 name + description 作为轻量索引
> agent 扫描索引后只 `skill_view` 相关 skill
> 这就是 Tier 2 progressive disclosure 的现成实现

## 优化效果

| 层 | 注入方式 | Token 节省 |
|----|----------|-----------|
| Tier 1 | 强制全量 | 不变 |
| Tier 2 | 索引stub → 按需 | ~60-80% on Tier 2 content |
| Tier 3 | skill_view | 零开销（无索引） |

## 参考

- Hermes RFC #64876: Prompt Architecture Optimization
- Hermes issue #59576: Progressive Disclosure Memory Architecture
- Skill-based workaround: github.com/rr5201314/Memory-hygiene-skill
