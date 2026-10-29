---
name: pi-agent-harness
description: pi coding agent 多智能体团队工厂。触发词：构建智能体团队/多智能体协作/pi agent harness。6种架构模式从一句话生成完整智能体团队。
trigger: pi-agent-harness multi-agent team factory
triggers:
  - 构建多智能体团队
  - pi agent 多智能体
  - pi-agent-harness
  - 团队架构设计
  - multi-agent team pi
---

# pi-agent-harness — 多智能体团队工厂

## 核心定位

pi-agent-harness 是 pi coding agent（minimal terminal coding agent）的插件，将**一句话描述**自动转换为**完整的多智能体团队**：专家智能体定义、技能定义、编排提示词。

**不是**单智能体profile管理器，而是设计和编排整个团队的框架。

## 核心能力

### 6 种架构模式

| 模式 | 适用场景 | pi delegation 映射 |
|------|---------|-------------------|
| Pipeline | 顺序依赖任务（生成→审查→测试→部署） | chain |
| Fan-out/Fan-in | 并行独立任务（多角度调研→汇总） | parallel |
| Expert Pool | 上下文相关专家选择 | single |
| Producer-Reviewer | 生成后验证（写作→校对→发布） | chain |
| Supervisor | 中心动态调度（主管分配子任务） | single/parallel |
| Hierarchical Delegation | 递归分解（顶层→子层→子子层） | chain + parallel |

### 6 阶段工作流

1. **Domain Analysis** — 分析代码库/任务类型，检测用户专业度，防止智能体冲突
2. **Team Architecture Design** — 选择 delegation 模式和架构模式
3. **Agent Definition Generation** — 生成 `.pi/agents/*.md`（角色、原则、I/O协议）
4. **Skill Generation** — 创建 YAML frontmatter + Progressive Disclosure 技能
5. **Integration & Orchestration** — 连接智能体，设计数据传递、错误处理、团队规模
6. **Validation & Testing** — 触发验证、干运行测试、skill对比实验

### 核心设计理念

- **零额外依赖**：bundles subagent 扩展，无需安装 companion packages
- **跨域通用**：不仅限于软件开发，可用于研究/小说/营销/数据管道
- **Progressive Disclosure**：技能分 metadata → body → references 三层，按需加载
- **数据传递**：支持 message-based / task-based / file-based 三种方式
- **文件输出**：`.pi/agents/`（智能体定义）+ `.pi/skills/`（技能）+ `.pi/prompts/`（编排提示词）

## 安装

```bash
# 安装 pi package
pi install npm:@baryonlabs/pi-agent-harness

# 触发 harness 生成
> build a harness for this project
```

## 研究价值

### 适用场景

- **复杂多步骤研究任务**：Fan-out/Fan-in 模式并行调研多角度 → 交叉验证 → 综合报告
- **小说创作**：Producer-Reviewer 模式（写作→校对→风格一致性检查）
- **代码审查**：Fan-out/Fan-in 模式并行检查架构/安全/性能/代码风格
- **数据管道设计**：Hierarchical Delegation 模式递归分解 schema/ETL/验证/监控

### Hermes 集成参考

pi-agent-harness 的**架构模式库**和**团队生成工作流**是 Hermes subagent 编排的重要参考：
- 6 种 delegation 模式对应不同的任务分解策略
- Progressive Disclosure 技能设计可用于优化 Hermes 技能系统
- 6 阶段工作流是完整的"从需求到团队"的最佳实践

## 与现有技能区别

- **vs subagent-driven-development**：subagent-driven 是 Hermes 内置的子智能体执行模式；pi-agent-harness 是完整的"团队架构工厂"，从一句话自动生成团队定义
- **vs agent-orchestration 技能**：现有技能关注 orchestration 模式；pi-agent-harness 关注"如何从零构建团队架构"

## 关键链接

- GitHub: https://github.com/baryonlabs/pi-agent-harness
- 文档: https://baryonlabs.github.io/pi-agent-harness
- npm: https://www.npmjs.com/package/@baryonlabs/pi-agent-harness
- 基准论文: https://github.com/revfactory/claude-code-harness（+60% 质量提升，100% win rate）
