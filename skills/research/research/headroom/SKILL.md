---
name: headroom
description: Headroom — local-first context compression layer for AI agents. 压缩工具输出/RAG/日志，60-95% token节省，CCR可逆缓存，Python+Rust内核，Apache-2.0，~72K stars。
trigger: 上下文压缩 / token节省 / 工具输出优化 / 长上下文窗口 / context window
trigger_en: context compression / token savings / tool output optimization / long context
trigger_zh: 上下文压缩 / token优化 / 工具输出压缩
trigger_tags: [token-optimization, context-window, compression, agent-infrastructure]
category: agent-infrastructure
framework: headroom-ai
stars: 72000
license: Apache-2.0
language: Python, Rust, TypeScript
updated: 2026-09-28
---

# Headroom — Context Compression Layer for AI Agents

## 核心定位

Headroom 是 AI Agent 的上下文压缩中间件层——以透明代理 + SDK + MCP Server 形式，在 Agent 与 LLM API 之间拦截工具输出并进行内容类型感知压缩，使用统计方法（无 LLM 在热路径上），节省 60-95% token，同时通过 CCR（Compress-Cache-Retrieve）保持可逆性。Apache-2.0，~72K GitHub stars。

**一句话定位**：上下文窗口是预算，压缩是解决方案。

## 架构概览

```
Agent (Claude Code/Cursor/Codex/LangChain/Agno/Strands)
        ↓ (tool outputs / RAG results / logs / files)
ContentRouter — 内容类型检测
        ↓
┌─────────────────────────────────────────────┐
│  专家压缩器（按类型路由）                    │
│  • SmartCrusher     — JSON数组专用          │
│  • CodeCompressor   — AST感知代码压缩        │
│  • Kompress-v2-base — ModernBERT prose压缩  │
│  • ImageCompressor  — 图像压缩              │
└─────────────────────────────────────────────┘
        ↓
LLM Provider (Anthropic / OpenAI / Bedrock / ...)
        + CCR Cache — 原文本地TTL缓存
        + headroom_retrieve MCP tool — 按需回取原文
```

## 核心压缩器

### SmartCrusher（JSON — 生产主力）
- **技术栈**：Rust + PyO3（高性能）
- **算法**：Kneedle 膝点检测 + SimHash 去重 + zlib 校验
- **保证**：始终保留 errors / anomalies / schema / statistical distribution
- **适用**：grep 输出、API JSON、测试日志、数据库查询结果

### CodeCompressor（AST感知代码）
- **支持语言**：Python, JavaScript, Go, Rust, Java, C++
- **策略**：AST 解析后保留语义结构，删除冗余空白和注释
- **效果**：代码文件压缩率低（~0-5%），但不影响语义

### Kompress-v2-base（文本/Prose）
- **架构**：ModernBERT-base 双头模型，int8 ONNX 导出
- **适用**：RAG 文档块、文档段落、长文本描述
- **注意**：RAG 场景压缩率低（~3%），生产实测 96% 场景收益微小

### ImageCompressor
- **策略**：ML 路由器 + 40-90% 压缩

## CCR（Compress-Cache-Retrieve）— 可逆保证

**核心问题**：有损压缩会丢失关键细节（如 stack trace 第 847 行、200 行 JSON 的某字段）

**解决**：
1. **Compress**：压缩工具输出后发送
2. **Cache**：原文本地 TTL 缓存（可配置 TTL）
3. **Retrieve**：LLM 通过 `headroom_retrieve` MCP 工具按需回取原文

**意义**：比"更便宜但盲目"多了"更便宜但可审计"的能力。

## CacheAligner（KV 缓存稳定性）

- 检测并警告 volatile 内容（会破坏 provider KV 缓存前缀）
- 不重写 prompts
- **效果**：稳定前缀 → Anthropic/OpenAI KV 缓存命中提升 → 间接降低延迟和成本

## 性能数据

### 实验室数字（ README 标称）
| 场景 | 压缩率 |
|------|--------|
| 代码搜索 | 92% |
| SRE 调试 | 92% |
| GitHub Issue 分类 | 73% |

### 生产实测（250+ 实例，50,000+ 会话）
| 百分位 | 压缩率 |
|--------|--------|
| P25 | 4.8% |
| Median | 4.8% |
| P75 | 6.9% |
| Mean | 11.3% |

**重要洞察**：实验室数字（>70%）与生产中位数（~5%）差距巨大。RAG 场景压缩率仅 3%——这是 README 对自身的隐性修正。JSON-heavy 场景（API 响应、日志、大型数组）是主要受益者。

## 输出 Token 压缩（HEADROOM_OUTPUT_SHAPER=1）

不只是压缩输入，还压缩模型输出：
- 去除 ceremony / restated code
- 跳过简单步骤的深度 "thinking"
- 适合：批量处理、数据管道

## 部署模式

### 模式 1：库（Python/TypeScript SDK）
```python
from headroom import compress
result = compress(messages=[{"role": "user", "content": long_tool_output}], model="claude-opus-4-6")
# result.messages 已压缩，result.tokens_saved 显示节省量
```

### 模式 2：零代码代理
```bash
pip install headroom-ai
headroom proxy --port 8787
# 透明代理，无需修改 agent 代码
```

### 模式 3：Agent Wrapper（一行命令）
```bash
headroom wrap claude   # Claude Code 通过 Headroom 路由
headroom wrap codex    # Codex（与 Claude 共享内存）
headroom wrap cursor   # 打印 base URLs 供手动配置
headroom unwrap claude # 撤销
```

### 模式 4：MCP Server
```bash
headroom deploy  # 一键部署本地 MCP Server
```

## 与 LLMLingua 对比

| 维度 | Headroom | LLMLingua |
|------|----------|-----------|
| 热路径 LLM | 无 | 有（LM-based）|
| 压缩策略 | 统计/结构 | LM 生成 |
| 可逆性 | CCR 原文缓存 | 不可逆 |
| 擅长内容 | JSON/日志/结构化 | prose/自由文本 |
| 延迟 | ~毫秒级 | 有 LLM 延迟 |
| 适用场景 | Agent 工具输出 | Prompt 整体压缩 |

**判断**：两者解决不同问题——LLMLingua 适合 prose，Headroom 适合 JSON-heavy agent 工作流。

## 安装注意

- **主通道**：PyPI（`pip install headroom-ai`），~100k/月下载
- **npm 包**：~3.4k/月，维护次要，不推荐
- **版本固定**：`headroom-ai==0.22.4`，快速迭代中
- **依赖**：Rust 工具链（SmartCrusher PyO3 绑定需要）

## 对 Hermes 的价值

### 立即可用
1. **Cron 任务 token 优化**：对需要读取日志/输出的 cron 任务，通过 headroom wrap 代理减少 token 消耗
2. **ETF 分析工具输出压缩**：对中国 A 股/ETF 数据 API 响应（大量 JSON 数组）压缩效果显著
3. **MCP 工具输出压缩**：Kitsune MCP 动态加载的工具输出可通过 Headroom 压缩

### 长期架构参考
1. **内容类型路由**：ContentRouter 设计可参考用于 Hermes 工具输出分级
2. **可逆缓存模式**：CCR 思想可用于 skill 参数缓存/回取机制
3. **Token 预算控制**：生产实测 ~5% 中位数提醒我们，实际收益远低于宣传

## 关键引用

- GitHub: https://github.com/headroom-ai/headroom
- PyPI: `pip install headroom-ai`
- 官方文档: https://docs.headroom.ai
- AgenticSpark 深度分析: https://agenticspark.github.io/posts/headroom.html
