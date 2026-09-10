---
name: agent-protocol-stack
description: AI Agent 协议栈 2026 — 6层标准体系：MCP/A2A/WebMCP/OSI/支付/身份。触发词：Agent协议/标准体系/互操作/语义层
triggers:
  - Agent协议标准
  - MCP A2A WebMCP OSI
  - agent互操作标准
  - 语义层 semantic layer
  - auth.md 认证协议
---

# Agent Protocol Stack — AI Agent 协议栈 2026

> 2026年Agent生态正在形成6层协议栈，从工具到人机界面的完整标准体系。

---

## 一、协议栈总览（6层）

```
┌─────────────────────────────────┐
│  6. Human Interface (人机界面) │  ←  Agent向人类展示工作
├─────────────────────────────────┤
│  5. Payments (支付层)           │  ←  机器原生支付/微交易
├─────────────────────────────────┤
│  4. OSI (Open Semantic Inter.) │  ←  语义/业务含义标准化
├─────────────────────────────────┤
│  3. A2A (Agent-to-Agent)       │  ←  独立Agent之间的通信
├─────────────────────────────────┤
│  2. WebMCP (Web MCP)           │  ←  浏览器内Agent工具标准
├─────────────────────────────────┤
│  1. MCP (Model Context Prot.)  │  ←  Agent→工具/数据（已胜出）
└─────────────────────────────────┘
身份 & 安全：贯穿全层
```

---

## 二、各层详解

### Layer 1: MCP — 工具层（已胜出）

**Model Context Protocol** — Anthropic 2024年末发布，已成为事实标准。

- **定位**：Agent连接工具和数据的事实标准
- **架构**：MCP Server（包装能力/数据库/文件系统/API）↔ MCP Client（Agent内部）
- **传输**：JSON-RPC + Streamable HTTP，远端服务器支持OAuth授权
- **生态**：服务器数量垂直增长，所有主要框架和模型提供商均已采用
- **对比**：USB-C — 通用端口，乏味但变革性

**与Hermes关系**：MCP已在Hermes中集成（mcp skill已有）

---

### Layer 2: WebMCP — 浏览器工具标准

**状态**：Chrome Origin Trial（Chrome 149+），W3C Web Machine Learning社区组开发

- **定位**：让网页向AI Agent暴露结构化工具，浏览器内的MCP变体
- **核心能力**：
  - **Discovery**：网页注册工具（`checkout`、`filter_results`等）
  - **JSON Schema**：输入输出显式定义，减少幻觉
  - **State**：共享当前页面上下文，Agent实时感知可用资源
- **API形式**：
  - **Imperative API**：JavaScript定义工具（`document.modelContext`）
  - **Declarative API**：HTML表单注解，添加`mc-tool`属性即可
- **安全**：Origin隔离要求，`Permissions Policy: tools`
- **生态**：Chrome扩展（WebMCP Inspector）、Puppeteer `page.webmcp` API、React框架支持
- **与MCP关系**：MCP处理外部工具，WebMCP处理浏览器内实时页面工具，互为补充

**来源**：
- https://developer.chrome.com/docs/ai/webmcp
- https://github.com/webmachinelearning/webmcp

---

### Layer 3: A2A — Agent间通信协议

**状态**：v1.0 GA（2026年4-6月），托管于 **Agentic AI Foundation**（Linux Foundation分支）

- **定位**：独立Agent之间的通信，与MCP互补（MCP=工具，A2A=对等体）
- **核心概念**：Agent Cards / Tasks / Artifacts
- **架构**：基于HTTP/SSE/JSON-RPC等Web标准
- **生态**：
  - Google Cloud背书
  - IBM竞争协议合并进A2A
  - 150+生产组织
  - 5语言SDK
  - Signed Agent Cards（v1.0特性）
- **治理**：从Linux Foundation迁移至Agentic AI Foundation（专注Agentic AI的中立机构）
- **与MCP关系**：MCP用于工具调用，A2A用于多Agent协作（如HR系统中HR Agent + Payroll Agent）

**来源**：
- https://www.axios.com/2026/08/17/a2a-agentic-ai-foundation-open-ai-standards
- https://developers.googleblog.com/developers-guide-to-ai-agent-protocols

---

### Layer 4: OSI — Open Semantic Interchange（语义层）

**状态**：v1.0 发布（2026年1月），Apache 2.0，已在Snowflake/Apache Polaris中落地

- **定位**：解决"语义歧义"问题——同一指标（如revenue）在不同系统定义不同
- **核心**： vendor-neutral规范，描述业务语义（metrics/dimensions/entities/relationships）
- **架构**：语义定义一次，可跨BI工具/语义层/数据目录/Agent旅行
- **生态**：
  - Snowflake发起（2025年9月），合作伙伴：Salesforce、Tableau、dbt Labs等
  - Apache Polaris社区投票引入OSI对齐语义规范
  - Ataccama、Collibra等数据治理平台支持
- **落地**：Snowflake语义视图 → 一行函数调用 → 导出OSI格式YAML（可Git版本控制）
- **与Agent关系**：数据平台是Agent最大消费者——Agent需要可信、可解释的数据语义

**来源**：
- https://medium.com/@pascalpfffle/open-semantic-interchange-what-the-finalized-spec-means-for-data-teams-0f2f8f744ab6
- https://www.collibra.com/blog/accelerating-data-delivery-using-osi-with-snowflake-and-collibra

---

### Layer 5: 支付层

**状态**：萌芽期，各方提出方案，尚未收敛

- **用例**：机器原生微支付、API按调用付费、Agent服务结算
- **相关项目**：Vellum Natural payments plugin（`vellum-ai/natural`）

---

### Layer 6: Human Interface（人机界面）

**状态**：成熟度不一

- **挑战**：Agent如何向人类展示工作、解释决策、请求确认
- **相关**：Mastra的Human-in-the-loop机制

---

## 三、身份与安全（跨层）

### auth.md 协议
- AI Agent代表用户注册应用
- 解决Agent身份认证问题
- 来源：https://bmdpat.com/blog/a2a-agent-to-agent-protocol-business-2026

### Vellum Trust Engine
- **Fail-closed原则**：Actor身份解析一次（guardian/trusted/unknown），全系统强制
- **隔离设计**：凭证在独立进程中，不到达模型；所有工具沙箱执行

---

## 四、Timeline（18个月标准化加速）

```
2024年末  MCP发布（Anthropic）
2025年初  MCP跨过临界点
2025年4月 A2A发布（Google + 合作伙伴）
2025年中  机构化阶段：A2A→Linux Foundation；OSI启动；支付标准萌芽
2025年末  企业从试点转向部署
2026年1月 OSI v1.0发布（Apache 2.0）
2026年2月 WebMCP Chrome Canary预览（W3C）
2026年4-6月 A2A v1.0 GA；150+生产组织
2026年8月 A2A迁入Agentic AI Foundation
```

---

## 五、对Hermes的启示

1. **短期**：MCP已是核心，继续深化
2. **中期**：A2A多Agent协作是Hermes可探索方向（当前是单Agent）
3. **长期**：语义层OSI对数据富化的Agent系统至关重要
4. **WebMCP**：影响Hermes的browser-use skill方向——未来browser可暴露WebMCP工具

---

## 六、来源链接

| 主题 | 链接 |
|------|------|
| Agent协议栈全景 | https://dev.to/alexmercedcoder/the-state-of-agentic-ai-standards-in-2026-mcp-a2a-webmcp-osi-and-the-protocol-stack-taking-3o2l |
| Vellum Top 11框架 | https://www.vellum.ai/blog/top-ai-agent-frameworks-for-developers |
| WebMCP官方文档 | https://developer.chrome.com/docs/ai/webmcp |
| WebMCP GitHub | https://github.com/webmachinelearning/webmcp |
| A2A Foundation迁移 | https://www.axios.com/2026/08/17/a2a-agentic-ai-foundation-open-ai-standards |
| OSI语义层解析 | https://medium.com/@pascalpfffle/open-semantic-interchange-what-the-finalized-spec-means-for-data-teams-0f2f8f744ab6 |
| Vellum Assistant | https://github.com/vellum-ai/vellum-assistant |
