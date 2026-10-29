# LLM Provider Model Comparison (OpenRouter)

## Context

User (saber) is looking for MiniMax-M2.7 alternatives as their API key is expiring.
MiniMax-M2.7 specs: context 196k, input $0.30/1M, output $1.20/1M.

## OpenRouter Model Comparison (2026-05-11)

### Budget/Flash Tier (~$0.14-0.40/1M input)

| Model | Context | Input $/1M | Output $/1M | Notes |
|-------|---------|-----------|-------------|-------|
| **deepseek/deepseek-v4-flash** | **1,048,576** | **$0.14** | **$0.28** | 🏆 Best value — 5x context, 1/7 price |
| qwen/qwen3.6-flash | 1,000,000 | $0.25 | $1.50 | Good budget option |
| qwen/qwen3.5-plus-20260420 | 1,000,000 | $0.40 | $2.40 | Good for long context tasks |
| **qwen/qwen3.6-plus** | **1,000,000** | **$0.325** | **$1.95** | 🥈 Best qwen value |

### Premium Tier (~$0.40-0.75/1M input)

| Model | Context | Input $/1M | Output $/1M | Notes |
|-------|---------|-----------|-------------|-------|
| **moonshotai/kimi-k2.6** | 262,144 | $0.75 | $3.50 | Direct MiniMax competitor, Chinese ecosystem |
| moonshotai/kimi-latest | 262,144 | $0.75 | $3.50 | Similar to k2.6 |
| **deepseek/deepseek-v4-pro** | **1,048,576** | **$0.44** | **$0.87** | 🥈 Premium DeepSeek |
| minimax/minimax-m2.7 | 196,608 | $0.30 | $1.20 | Current model (baseline) |

## Recommendations

- **Switch for cost savings**: `deepseek/deepseek-v4-flash` — 5x context, 1/7 the price
- **Switch for similar experience**: `moonshotai/kimi-k2.6` — same Chinese LLM ecosystem
- **For largest context**: both DeepSeek V4 and Qwen 3.6 support 1M token context

## Switching Model in Hermes

```bash
hermes model
# OR
hermes config set model.default deepseek/deepseek-v4-flash
```

OpenRouter API key required. Check:
```bash
grep -i openrouter ~/.hermes/.env
```

## Monthly Plan Reality Check (2026-05-11)

**Key finding: No major AI API provider offers true fixed-monthly plans at the ¥49 level.**

| Provider | Plan Type | Fixed Monthly? | Notes |
|----------|-----------|----------------|-------|
| OpenRouter | Pay-per-use + spend cap | ✅ Yes (set $7 limit) | Best control — stops at budget |
| MiniMax | Fixed ¥49/month | ✅ Yes | Current provider |
| Kimi/Moonshot | Quota packages | ⚠️ Semi-fixed | Buy credits up front, no overages |
| 硅基流动 (SiliconFlow) | Quota packages | ⚠️ Semi-fixed | Domestic, multi-model |
| 阿里云百炼 | Quota packages | ⚠️ Semi-fixed | Alibaba ecosystem |
| DeepSeek direct | Pay-per-use | ❌ No | Cheapest per-token but no cap |
| Groq | Pay-per-use | ❌ No | No monthly plans |

**For users who want fixed monthly budgets:**
- **Best approach**: OpenRouter pay-per-use + monthly spend limit (set $7 ≈ ¥49 cap)
- **Alternative**: MiniMax ¥49/month (already using)
- **Domestic**: Kimi/硅基流动 quota packages (buy credits monthly, no overages)

**OpenRouter monthly limit**: Account dashboard → Billing → Monthly Spend Limit

**Kimi ban risk**: Domestic AI API providers (Kimi, 硅基流动, 阿里云百炼) have account suspension risk — content moderation triggers vary. OpenRouter avoids this since it's a middle layer. Factor this into the decision alongside price.

> **User preference (saber)**: When user asks short questions like "有没有套餐" or "kimi不会封号吗", give compressed direct answers — no markdown tables unless necessary. User communicates in short voice messages and expects concise text responses. Do not load multiple skills for simple questions.

## Direct API Alternatives (no OpenRouter)

| Provider | Website | Notes |
|----------|---------|-------|
| DeepSeek | platform.deepseek.com | Direct API, cheapest |
| Kimi/Moonshot | platform.moonshot.cn | Chinese ecosystem |
| Qwen/Ali | dashscope.console.aliyun.com | Alibaba |
| Zhipu/GLM | open.bigmodel.cn | Chinese GLM models |

## Discovery

`https://openrouter.ai/api/v1/models` is publicly accessible — returns full model list with pricing for programmatic discovery.
