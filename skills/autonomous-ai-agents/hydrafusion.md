# Project HydraFusion (GitHub Copilot CLI)

**分类**: Multi-Model Orchestration / Cost Optimization
**触发词**: hydrafusion, multi-model, cost routing, copilot cli
**Status**: Research Preview (2026-09-04) | Copilot CLI only

## 核心定位

GitHub Copilot CLI 的运行时多模型编排系统，核心理念：**不再选单一模型，而是为每个请求构建最优 workflow**。不是框架，是 Copilot 的内置能力。

## 核心创新

### 1. 从 Model Selection → Workflow Optimization
传统 routing：选一个最合适的模型
HydraFusion：选一个执行 pattern（Single / Cascade / Critique）

### 2. 三种执行 Pattern

**Single**: 任务直接路由到最优单模型
**Cascade**: 便宜模型 draft → 质量门失败则升级到强模型
**Critique**: A 模型写代码 → B 模型（不同家族）评审 → A 修订

### 3. 动态 Workflow 构建
```
每次请求 → 读取 capability signals（reasoning/code/debug/tool-use）
→ 评估任务复杂度 → 选择最小代价满足质量门槛的 pattern
→ 执行（可能跨多 provider 多模型）
```
质量门 = 自动化的"这个答案够不够好"判断，无需人工介入。

### 4. Benchmark 结果
```
TerminalBench 2.1:  +4.9 quality points @ -67% cost vs Claude Opus 5
DeepSWE:            -1.5 quality points @ -36% cost
CheckpointBench:    -?? quality points @ -65% cost
```

### 5. Beam Search 决策策略
不是人工调参，是用 beam search 自动学习最优决策策略。训练集：TerminalBench 2.1 / DeepSWE / CheckpointBench。

## 与 Hermes 的互补点

| 方面 | HydraFusion | Hermes |
|------|------------|--------|
| 粒度 | Workflow per request | 任务级模型路由 |
| 决策 | 自动（beam search policy） | 半自动（用户授权） |
| 目标 | 成本/质量平衡 | 任务完成 + 成本控制 |
| 集成 | Copilot CLI only | 全平台 |

**核心洞察**：HydraFusion 证明了"per-request workflow optimization"在 coding 场景可行（+4.9 quality @ -67% cost）。Hermes 可借鉴类似思路：对简单任务（单次搜索）用小模型，对复杂任务（多步骤研究）动态升级模型。

## 落地建议

**不值得建 skill**（Copilot CLI only，无法在 Hermes 中集成），但架构思想值得借鉴：
- 在任务复杂度评估后动态选择模型/wrapper
- 用 quality gate 判断是否需要升级
- 对高频简单任务（代码补全/单行修改）固定用小模型

## 参考

- GitHub Blog: https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/
- MarkTechPost: https://www.marktechpost.com/2026/09/05/github-introduces-project-hydrafusion-runtime-multi-model-orchestration-that-builds-a-workflow-per-coding-task-in-copilot-cli/
- StartupFortune: https://startupfortune.com/github-ships-hydrafusion-a-copilot-tool-that-mixes-ai-models-to-cut-costs/
