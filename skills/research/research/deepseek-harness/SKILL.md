---
name: deepseek-harness
description: DeepSeek Harness v0.1 调研技能。触发词：DeepSeek Harness/Cordis/插件化Agent框架。
trigger: DeepSeek Harness Cordis plugin agent framework
owner: hermes-evolution
updated: 2026-09-25
---

# DeepSeek Harness v0.1

## 核心定位
- **定位**: 开发者预览版 Agent Harness（框架）
- **发布**: 2026-08-20，MIT 许可证
- **基础**: Cordis 元框架（时空可组合性范式）
- **Stars**: 未明确（GitHub 未列出，开发者预览阶段）

## 核心创新

### 1. "一切皆插件"架构（Everything is a Plugin）
- **Cordis** (8K+ stars, MIT)：时空可组合性元框架
- Effect 系统驱动（类似 Monadic Effect）
- 插件体系：npx @deepseek-ai/dsh web 启动 Web UI
- 插件发现：GitHub topic `dsh-plugin`

### 2. Cordis 理论基础
- 论文：*A Programming Paradigm for Spatiotemporal Composability* (arXiv:2608.25512)
- 92页学术论文，系统阐述可组合性理论
- 核心概念：时间和空间维度的组合性

### 3. 技术栈
- **运行时**: Node.js（npx @deepseek-ai/dsh）
- **UI**: Web UI 默认 http://127.0.0.1:3080
- **pnpm**: 构建工具（pnpm install && pnpm run build）
- **本地运行**: git clone 后直接运行，无需后端

### 4. 安全状态
- 提供 SAFETY.md 文件（需查看）
- 开发者预览版，存在 Breaking Changes

## 与 Hermes 相关性
- **架构**: "一切皆插件"理念可融入 Hermes skill/plugin 系统
- **Cordis Effect**: 可能是 Hermes 轻量级 effect/hook 系统的参考
- **快速启动**: npx 一行启动的 UX 值得参考

## 限制
- 开发者预览版，API 不稳定
- Node.js 而非 Python（与 Hermes 技术栈差异）
- 生态刚刚起步

## 来源
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/cordiverse/cordis
- https://arxiv.org/abs/2608.25512
