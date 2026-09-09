---
name: code-execution-sandbox
description: E2B sandboxed code execution for AI agents — secure cloud sandbox with Code Interpreter SDK (Python/JS), multi-language support, MCP integration.
trigger: Use when building AI coding agents, needing safe LLM-generated code execution, or evaluating code interpreter infrastructure.
trigger_tags: [sandbox, code-execution, e2b, ai-agent, code-interpreter]
---

# E2B Sandboxed Code Execution

E2B — open-source secure sandbox for AI-generated code. Firecracker microVM isolation, multi-language, MCP-ready.

## Core Value

| 对比 | exec() 本地 | E2B Sandbox |
|---|---|---|
| 隔离 | ❌ 无 | ✅ Firecracker microVM |
| 超时控制 | ❌ 难 | ✅ 精确控制 |
| 多语言 | ❌ 难 | ✅ Python/JS/R/Java |
| LLM 集成 | ❌ 手动 | ✅ SDK 一行调用 |
| 自托管 | ❌ — | ✅ Terraform 部署 |

## Quick Start

```bash
pip install e2b-code-interpreter
export E2B_API_KEY="e2b_your_key_here"
```

```python
from e2b_code_interpreter import Sandbox

with Sandbox(timeout=120) as sandbox:
    execution = sandbox.run_code("""
import math
print(math.sqrt(144))
df = __import__('pandas').DataFrame({'a': [1,2,3]})
print(df.describe())
""")
    print(execution.text)      # "12.0"
    print(execution.logs.stdout)  # ['12.0\n', ...]
    # Rich results: charts (base64 PNG), dataframes
```

## Key Features (2026年最新)

- **Sandbox Forking** (Jul 2026): In-place sandbox fork，秒级克隆运行状态
- **Multi-language**: Python / JavaScript / R / Java，Jupyter kernel 执行
- **Chart Detection**: Matplotlib 自动检测并返回 base64 PNG + chart data
- **MCP Server**: 49+ servers in catalog，`Template().addMcpServer("postgres")`
- **BYO Proxy**: SOCKS5 egress proxy，完全控制出站流量
- **Wildcard transform rules**: `*.example.com` 一次性匹配所有子域名
- **Snapshot CLI**: `e2b sandbox snapshot create/list/delete`
- **Multi-connection client**: 一个进程连接多个 API keys / domains
- **Self-hosted**: AWS / GCP Terraform 部署，Azure 规划中
- **Artifacts**: Anthropic Code Artifacts 开源实现 (Claude-3.5 Sonnet + Next.js)
- **Desktop** (beta): `e2b-desktop`，沙箱内启动 Chrome 截图

## SDK 版本

- JS SDK: `@e2b/code-interpreter` (npm)
- Python SDK: `e2b-code-interpreter` (pip)
- 当前稳定版 ~2.46.x (2026-08)

## 与 Hermes execute_code 的关系

Hermes `execute_code` 工具是本地执行，E2B 是云端隔离执行。E2B 适合：
- 不可信代码需要强隔离
- 需要多语言 (R/Java)
- 需要 MCP server 集成
- 生产级代码解释器场景

## 落地优先级

**低优先级** — Hermes `execute_code` 已满足本地执行需求。E2B 适合：
- 构建对外 SaaS 产品（需要强隔离）
- 多租户代码执行服务
- 需要 MCP 集成的复杂 agent 编排

## 参考

- Repo: https://github.com/e2b-dev/E2B (13.7k ⭐ Apache-2.0)
- Docs: https://docs.e2b.dev
- Cookbook: https://github.com/e2b-dev/e2b-cookbook
- Self-hosting: https://github.com/e2b-dev/infra
- 比较: Daytona / Modal / Piston — 见上方教程
