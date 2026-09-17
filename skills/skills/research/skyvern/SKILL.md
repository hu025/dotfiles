---
name: skyvern
description: Vision-LLM browser automation. Use when automating multi-step web workflows, form filling, login flows, or replacing brittle XPath/Playwright scripts.
trigger: skyvern | vision-LLM browser | automate web | form automation | login automation | web workflow
category: research
tags: [browser-automation, vision-llm, mcp, web-workflow, ai-agent]
version: 2026-09-18
---

# Skyvern — Vision-LLM Browser Automation

## 核心定位

Skyvern 是基于 Vision-LLM 的浏览器自动化平台，核心差异：**用视觉理解替代 XPath/CSS 选择器**，自动化随网站布局变化自动适应，无需维护。

**与现有工具的分工**：
- `browser-use` — DOM-free 纯 LLM 决策，适合通用网页任务
- `Crawl4AI` — LLM 友好爬虫，专注内容抓取和 Markdown 输出
- `Playwright MCP` — 标准浏览器控制，无 AI 增强
- `Skyvern` — Vision-LLM + 多智能体架构 + Playwright 增强，擅长多步工作流、表单填写、登录

## 核心能力

### 1. Vision-LLM 视觉理解

不再依赖 XPath/CSS 选择器，Skyvern 用 Vision-LLM 实时理解页面视觉元素，映射到操作意图。

- 网站布局变化后自动化仍然有效
- 可处理从未见过的网站
- 跨网站通用工作流成为可能

### 2. 多智能体编排架构

```
用户指令 → 理解智能体(Reasoning LLM) → 规划智能体(Instruction LLM) → 视觉智能体(Vision LLM) → 执行层
```

三个 LLM 各司其职，协同完成复杂多步工作流。

### 3. Playwright SDK AI 扩展

`pip install "skyvern[all]"` 后，在 Playwright page 对象上获得 4 个 AI 命令：

| 命令 | 作用 |
|------|------|
| `page.act(prompt)` | 自然语言执行操作（"点击登录按钮"） |
| `page.extract(prompt, schema)` | 用 JSON schema 提取结构化数据 |
| `page.validate(prompt)` | 自然语言验证页面状态（返回 bool） |
| `page.prompt(prompt, schema)` | 发送任意 LLM 提示 |

高层 `page.agent` 命令：
- `page.agent.run_task(prompt)` — 多步复杂任务
- `page.agent.login(credential_type, credential_id)` — 认证（支持 Bitwarden/1Password/Skyvern vault）
- `page.agent.download_files(prompt)` — 文件下载导航

### 4. MCP Server（75+ 工具）

内置 MCP Server，支持 Claude Code/Codex/Cursor/Hermes/OpenClaw。

**关键 MCP 工具（75+）**：

| 类别 | 工具 | 功能 |
|------|------|------|
| 会话管理 | `skyvern_browser_session_create/close/list/get` | 浏览器会话生命周期 |
| 基础操作 | `skyvern_navigate/click/type/hover/scroll/select_option/press_key` | 自然语言+选择器混合操作 |
| 数据提取 | `skyvern_extract/screenshot/evaluate` | 结构化 JSON / 截图 / JS 执行 |
| 验证 | `skyvern_validate` | 自然语言断言（返回 true/false+推理） |
| 认证 | `skyvern_login/credential_list/get/delete` | TOTP/2FA 自动处理 |
| 工作流 | `skyvern_workflow_create/run/status/get/update/delete/cancel` | 23 种块类型的可视化工作流 |
| 高级 | tab 管理、iframe 切换、拖放、文件上传、网络/控制台检查、HAR 录制 | |

### 5. No-Code 工作流构建器

支持 23 种块类型，可视化构建多步自动化，无需代码。

### 6. 支持的 LLM 提供商

OpenAI (GPT-5.5/5.4/5/o3/o4-mini)、Anthropic (Claude 4.7/4.6/4.5)、Azure OpenAI、AWS Bedrock、Gemini 3.1/3/2.5、Ollama（本地）、OpenRouter、OpenAI 兼容端点。

## 安装与配置

### 本地安装

```bash
pip install "skyvern[all]"
skyvern quickstart          # SQLite 默认，启动本地 UI (localhost:8080)
# 或使用 Postgres:
skyvern quickstart --database-string=postgresql+psycopg://user:pass@host:5432/dbname
```

### Docker 部署

```bash
git clone https://github.com/skyvern-ai/skyvern.git && cd skyvern
cp .env.example .env
# 编辑 .env 添加 LLM API key
docker compose up -d
# 打开 http://localhost:8080
```

### MCP Server 配置（Hermes）

```bash
# API key 方式（Hermes 兼容）
claude mcp add-json skyvern '{"type":"http","url":"https://api.skyvern.com/mcp/","headers":{"x-api-key":"YOUR_SKYVERN_API_KEY"}}' --scope user
```

或在 config.yaml 中配置（Hermes 特有）：

```yaml
mcp:
  servers:
    skyvern:
      type: http
      url: https://api.skyvern.com/mcp/
      headers:
        x-api-key: "${SKYVERN_API_KEY}"
```

获取 API key: https://app.skyvern.com

## Skyvern Cloud vs 自托管

| | Cloud | Self-hosted |
|--|-------|-------------|
| 反爬绕过 | 内置代理网络 | 需自行配置 |
| CAPTCHA | 自动解决 | 需自行处理 |
| 维护 | 零维护 | 你负责 |
| 费用 | 按用量 | 免费（需 GPU） |
| 许可证 | AGPL-3.0 + 云服务 | AGPL-3.0 |

## 应用场景

- **表单填写自动化**：政府表格、申请流程（招聘/移民/贷款）
- **采购工作流**：跨多供应商门户自动下载发票
- **数据采集**：竞品情报、价格监控（无 API 的网站）
- **登录流程**：TOTP/2FA 自动处理
- **前端 QA**：结合 `/qa` skill 自动回归测试

## 与 browser-use 的关键区别

browser-use 用纯 DOM-free LLM 决策，Skyvern 的差异化在于：
1. **视觉优先**：Vision-LLM 实时视觉理解 > DOM 解析
2. **多智能体架构**：理解+规划+视觉三层协同
3. **Playwright 基础**：兼容现有 Playwright 脚本，逐步增强
4. **工作流持久化**：JSON-RPC + Task 状态机，可中断/恢复
5. **MCP 原生集成**：75+ 工具，生态更完整

## 已知限制

- AGPL-3.0 许可证（自托管版本）
- 反爬绕过功能仅在 Cloud 版提供
- 需要可靠的 LLM API key
- 复杂工作流仍需人工设计 prompt

## 参考资料

- GitHub: https://github.com/skyvern-ai/skyvern
- 官网: https://www.skyvern.com
- MCP 文档: https://www.skyvern.com/docs/integrations/mcp
- 技术报告: https://www.skyvern.com/blog/skyvern-2-0-state-of-the-art-web-navigation-with-85-8-on-webvoyager-eval/
