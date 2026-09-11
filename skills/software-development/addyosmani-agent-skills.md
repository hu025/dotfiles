---
name: addyosmani-agent-skills
description: Addy Osmani 93K stars生产级AI编码Agent技能库。23个SKILL.md工作流(定义→规划→构建→验证→审查→简化→发布)，Google工程文化内置反合理化机制。触发词：/spec /plan /build /review /simplify /ship
---

# Addy Osmani Agent Skills

## 概述

**addyosmani/agent-skills** (93.4K⭐, MIT) 是Google Chrome工程师Addy Osmani维护的生产级AI编码Agent技能库。23个结构化SKILL.md工作流，覆盖完整开发周期：定义→规划→构建→验证→审查→简化→发布。

**与Hermes技能系统的关系：** 格式完全兼容（SKILL.md + YAML frontmatter），可被Claude Code/Cursor/Codex/OpenCode直接使用。已有部分技能（spec-driven-development, test-driven-development, incremental-implementation等）存在重叠，但addyosmani版本的**反合理化表格**和**验证门控**是独特增量。

## 核心技能清单

### 定义阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `spec-driven-development` | PRD规范先于代码，6个核心区域，能力地图(capability map) | /spec |
| `constraint-driven-development` | 面试需求获取质量门槛，写入CONSTRAINTS.md，捕捉Agent跳过检查的倾向 | |

### 规划阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `planning-and-task-breakdown` | 小原子任务分解，任务图谱 | /plan |

### 构建阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `incremental-implementation` | 薄垂直切片—实现→测试→验证→提交→下一步 | /build |
| `frontend-ui-engineering` | 生产级UI，可访问性 | |
| `api-and-interface-design` | 契约优先设计，Hyrum定律，API稳定性 | |
| `context-engineering` | 正确上下文时机注入，规则文件/MCP集成 | |
| `source-driven-development` | 验证实现是否符合官方文档 | |
| `doubt-driven-development` | **独特增量**：对抗性新鲜上下文审查 | |

### 验证阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `test-driven-development` | 红→绿→重构，测试金字塔(80/15/5)，Beyonce规则 | /test |
| `browser-testing-with-devtools` | Chrome DevTools MCP运行时验证 | |
| `debugging-and-error-recovery` | 复现→定位→修复→守卫 | |

### 审查阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `code-review-and-quality` | 五轴审查，~100行变更，Nit/Required/Critical标签 | /review |
| `code-simplification` | Cherton fences，Rule of 500，保持行为减少复杂度 | /simplify |
| `security-and-hardening` | OWASP Top 10，输入验证，最小权限 | |
| `performance-optimization` | 测量优先，Core Web Vitals | |

### 发布阶段
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `git-workflow-and-versioning` | 主干开发，原子提交，~100行变更 | |
| `ci-cd-and-automation` | 左移，质量门，失败反馈循环 | |
| `deprecation-and-migration` | 代码为负债思维，迁移模式 | |
| `documentation-and-adrs` | 架构决策记录，记录"为什么" | |
| `shipping-and-launch` | 发布前检查表，功能标志，灰度回滚 | /ship |

### 元技能
| 技能 | 用途 | 触发词 |
|------|------|--------|
| `using-agent-skills` | 元技能：技能路由，发现正确技能工作流 | |
| `incremental-implementation` | 递进实施 | |

## 独特机制：反合理化表格

每个技能包含**anti-rationalization table**，列出Agent跳过步骤的常见借口及对抗论点：

```
| 合理化借口 | 现实 |
|-----------|------|
| "最后再测试" | Bug会叠加，Slice 1的bug使Slice 2-5都错 |
| "一次搞定更快" | 直到出问题才发现500行中哪行导致 |
| "小改动不用单独提交" | 小提交免费，大提交隐藏bug |
```

**这对Hermes的价值：** 内置反合理化机制，Agent更难自我欺骗跳过关键步骤。

## 独特机制：新鲜上下文对抗审查

`doubt-driven-development`工作流：
1. **CLAIM** — 命名决策（2-3行）
2. **EXTRACT** — 提取最小可审查单元（diff/函数）
3. **DOUBT** — 调用对抗性审查者，不给结论只给合同
4. **RECONCILE** — 按优先级分类发现（contract misread/actionable/trade-off/noise）
5. **STOP** — 满足停止条件

**与现有审查的区别：** `/review`是完成后的判定，doubt-driven是飞行中的姿态，非平凡决策在代价还低时就被审查。

## 验证门控

每个技能有明确的**退出标准和证据要求**：
- 测试通过
- 构建成功
- 运行时数据
- "看起来对"永远不够

## 与Hermes现有技能的差异

| Hermes技能 | addyosmani版本差异 |
|-----------|-------------------|
| `test-driven-development` | 无反合理化表格 |
| `spec-driven-development` | 无能力地图(capability map) |
| `requesting-code-review` | 无五轴审查，标签体系不同 |
| `planning-and-task-breakdown` | 无任务图谱结构 |
| `doubt-driven-development` | **不存在** — 独特新增 |
| `constraint-driven-development` | **不存在** — 独特新增 |

## 来源

- GitHub: https://github.com/addyosmani/agent-skills
- 技能官网: https://skills.addy.ie/
- 视频介绍: Microsoft Dev LIVE150, Jun 2026
- 93.4K stars, 9.9K forks, 66 contributors, v0.6.9 (Sep 2026)
