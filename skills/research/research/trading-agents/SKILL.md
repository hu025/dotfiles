---
name: TradingAgents
description: Multi-agent LLM financial trading framework with structured analyst/researcher/trader/risk roles. Trigger: 需要量化交易agent、bull-bear辩论框架、金融分析多agent协作。
trigger: multi-agent trading framework, financial analysis, bull bear debate, LangGraph finance
owner: saber
updated: 2026-09-27
tags: [research, multi-agent, finance, trading, LangGraph]
---

# TradingAgents — Multi-Agent LLM Financial Trading Framework

## 核心信息

- **Stars**: 开源研究框架（非商业产品）
- **License**: Apache 2.0
- **GitHub**: github.com/TradingAgents-AI（另有 JeffBaumgardt fork 含完整Web UI）
- **论文**: arXiv:2412.20138 (2024-12, UCLA+MIT)
- **v0.3.0** (2026-06): verified data-access contract, FRED + Polymarket data vendors

## 架构亮点

### 七角色协作模型（真实交易所结构）

```
Analyst Team (并行)
  ├─ Market Analyst        技术分析：MA/RSI/波动率
  ├─ Sentiment Analyst    社交媒体情绪
  ├─ News Analyst         新闻事件驱动
  └─ Fundamentals Analyst 基本面财务数据

Researcher Team (辩论)
  ├─ Bull Researcher      多头论点
  └─ Bear Researcher      空头论点

Trader                    交易决策
Risk Management Team      风险评估（激进/保守/中性三档）
Portfolio Manager         仓位管理+执行
```

### 核心创新

1. **Structured Document Communication** — agents间通过结构化文档而非自由对话传递信息，避免"电话效应"（信息失真）
2. **Bull/Bear 辩论机制** — 多空双方辩论后再由 Trader 决策
3. **ReAct Prompting** — 所有agents使用ReAct框架驱动协作
4. **LangGraph Checkpoint** — 支持断点恢复 (`--checkpoint`)
5. **Verified Data Contract** — v0.3.0引入数据访问验证，防止幻觉价格

### 数据源（v0.3.0）

- FRED（美联储经济数据）
- Polymarket（预测市场情绪）
- StockTwits / Reddit（社交）
- 新闻API
- 技术指标（内置）

### 支持模型（v0.3.0）

GPT-5.x / Gemini 3.x / Claude 4.x / Grok 4.x / DeepSeek / Qwen / GLM / MiniMax / NVIDIA / Kimi / Groq / Bedrock + OpenAI兼容端点

## 落地评估

**对Hermes的意义**：
- ** Bull/Bear 辩论结构** → 可迁移到ETF/股票多空判断场景
- ** Polymarket 数据源** → 情绪数据输入，补充现有ETF分析
- ** 三档风险模型** → Hermes quant ETF分析的risk layer参考
- ** Structured Document Communication** → 替代自由对话的agent间通信范式

**不落地原因**：
- 研究框架，非生产级交易系统
- 回测结果不可复现（LLM sampling固有变化）
- 用户偏好低价ETF筛选，无需完整交易框架

**参考价值**：⭐⭐⭐（架构模式值得参考，但用户量化需求已被 china-etf-technical-analysis skill 覆盖）

## 关键命令

```bash
# 安装
pip install tradingagents

# CLI 单股分析
tradingagents run AAPL --date 2024-11-19

# Docker
docker compose up

# 断点恢复
tradingagents run AAPL --checkpoint --resume-from 42

# 配置数据源
TRADINGAGENTS_FRED_API_KEY=xxx
TRADINGAGENTS_POLYMARKET_KEY=xxx
TRADINGAGENTS_LLM_PROVIDER=openai
```

## 来源

- https://github.com/TradingAgents-AI/TradingAgents
- https://github.com/JeffBaumgardt/TradingAgents（fork含Web UI）
- https://arxiv.org/abs/2412.20138
- https://tradingagents-ai.com/
