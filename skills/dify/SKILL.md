---
name: dify
description: Dify 开源 LLM 应用平台 — 无代码工作流 + RAG + Agent + LLMOps。触发词：Dify、no-code LLM builder、视觉化 AI 编排
---

# Dify — 开源 LLM 应用开发平台

## 核心定位

- **定位**：no-code 视觉化工作流 + RAG pipeline + Agent + LLMOps 全栈平台
- **Stars**：154k（2026-09，最大开源 LLM 应用平台）
- **License**：Modified Apache-2.0（Commons Clause 限制 SaaS 再销售）
- **融资**：2026-03 融资 $30M（Pre-A）
- **部署**：Docker Compose / K8s / 云 / VPC / 本地

## vs 主要竞品

| 维度 | Dify | Flowise | Langflow |
|------|------|---------|---------|
| 语言栈 | Python+Go+TS | Node.js/LangChain.js | Python/LangChain |
| 侧重 | 完整生命周期 | LangChain 可视化 | LangChain 可视化 |
| 多用户协作 | ✅ 实时协作画布 | 有限 | 有限 |
| 模板市场 | ✅ Creator Center | ❌ | ❌ |
| MCP | ✅ | ✅ | ✅ |
| 观测性 | Opik/Langfuse/Arize | LangSmith | LangSmith |
| E2B 沙箱 | ✅ v1.17 | ❌ | ❌ |

**选型**：Python 团队 + 完整生命周期 → Dify；Node 团队 + LangChain 熟悉 → Flowise

## 核心能力

### 1. 工作流（Workflow）
- 拖拽式画布，支持 20+ 节点类型
- 多用户实时协作（v1.14.1）
- 画布评论 + @提及通知（v1.14.1）
- Loop / Iteration 内嵌 Human Input（v1.14.1）
- 节点配置跨工作流复制（v1.14.1）

### 2. RAG Pipeline
- 多模态知识库（文本 + 图片统一语义空间，v1.13）
- Summary Index（chunk 附带摘要，相关内容一同返回，v1.12）
- 支持 PDF/PPT/DOCX/TXT 等格式
- 100+ 模型 + 30+ 向量库

### 3. Agent
- LLM Function Calling / ReAct 双模式
- **E2B 云沙箱后端**（v1.17）：Shell/代码执行可走 E2B 而非本地
- **Build-time Home Snapshots**（v1.17）：Agent 发布时捕获 home 目录状态，后续运行恢复精确文件系统
- **Workspace-level Skill 管理**（v1.17）：可复用技能包（含代码 + 工具定义），draft→publish→version 生命周期
- **Context-aware History Compaction**（v1.17）：自动 tiered compaction，防止上下文窗口爆炸

### 4. LLMOps
- 应用日志 + 性能分析
- 生产数据持续优化 prompt/dataset/model
- Unified Tracing（v1.17）：workflow/chatflow/message/nodes/loops/iterations 统一父子 span 树
- Provider-neutral tracing：Phoenix + LangSmith 适配器

### 5. 部署 + 生态
- **difyctl CLI**（Jul 2026）：Agent 单命令调用 Dify app
- Creator Center + Template Marketplace（May 2026）
- 50+ 内置工具（搜索/生图/计算）
- MongoDB Atlas / Voyage AI 原生集成
- Qubrid AI（DeepSeek/Kimi/Qwen/MiniMax/GLM 统一接入）
- 多租户 RBAC + SSO（企业版）

## 快速启动

```bash
# Docker 一键启动
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
# 访问 http://localhost/install 完成初始化

# CLI 调用（difyctl）
npx difyctl invoke --app-id <id> --input "你的问题"

# 从源码部署（开发）
cd dify
uv sync
flask db upgrade
python -m flask run --worker
```

## 关键版本演进

- **v1.17**（2026-08）：E2B 沙箱、Home Snapshots、Workspace Skills、Context Compaction、Unified Tracing
- **v1.14.1**（2026-05）：画布协作、模板市场、Human Input API
- **v1.14.0**（2026-05）：Workflow 成为团队资产
- **v1.13.0**（2026-03）：Human Input Node（人机审批节点）
- **v1.12.0**（2026-02）：Summary Index、RAG 摘要
- **v1.11.0**（2026-01）：多模态知识库

## Hermes 集成场景

1. **快速原型验证**：Dify 画布搭建 RAG pipeline → 验证效果 → 用 Hermes skill 实现生产版
2. **E2B 安全沙箱**：Hermes 危险代码走 E2B 而非本地 terminal
3. **模板市场**：复用社区 RAG/Agent 模板到 Hermes 工作流
4. **difyctl**：Agent 直接调用 Dify workflow 作为工具

## 参考

- https://dify.ai/
- https://github.com/langgenius/dify
- https://docs.dify.ai/
- https://dify.ai/blog
