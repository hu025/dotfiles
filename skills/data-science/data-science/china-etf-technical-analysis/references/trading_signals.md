---
name: ETF Trading Signals
description: Trading signals and decision framework for saber's ETF holdings
category: data-science
---

# ETF Trading Signals & Decision Framework

## User's Holdings (saber, updated 2026-07-03)

| ETF | Code | Cost | Qty | 止损 | 目标 | 盈亏% | RSI | MACD |
|-----|------|------|-----|------|------|-------|-----|------|
| 酒ETF华夏 | 512690 | 0.403 | 1000 | 0.385 | 0.438 | -1.2% | 32.5🟢 | 红柱✅ |
| 芯片ETF国泰 | 512760 | 0.872 | — | — | — | **已止盈** | — | — |
| 科创50ETF易方达 | 588080 | 1.437 | — | — | — | **已止盈** | — | — |

**酒ETF操作逻辑（2026-07-03买入）：**
- RSI 32.5 超卖，MACD刚金叉（红柱+0.001），布林带位置30.7%低位
- 目标1布林上轨¥0.438（+8.7%），目标2近60日高¥0.498（+23.6%）
- 风险收益比2.27，止损幅度4.5%，最大亏损¥18

芯片/科创50已于2026-06-30止盈卖出（盈利约+25%/+22%）。

---

## Stop-Loss Tiers

### Tier 2 — Standard (cost + margin)
Hard floor — **trigger sell if hit**.

| ETF | Cost | +18% | Stop trigger |
|-----|------|------|-------------|
| 芯片ETF | 0.872 | 1.025 | **1.025** |
| 科创50ETF | 1.437 | 1.668 | **1.668** |

### Tier 3 — Dynamic trailing (session high × 0.95)
Active management while trend holds. Moves UP as price rises, never down.

| ETF | Session High | Stop (×0.95) | Margin from Current |
|-----|-------------|-------------|-------------------|
| 芯片ETF | 1.100 | **1.045** | -4.3% from high |
| 科创50ETF | 1.770 | **1.682** | -4.1% from high |

> ⚠️ As of 2026-05-11: 芯片ETF trailing stop is **1.045** (price 1.092, margin 4.3%), 科创50ETF trailing stop is **1.682** (price 1.754, margin 4.1%). Stops are getting close — monitor closely.

---

## Signal Triggers

### 🚨 SELL IMMEDIATELY (any one)
- [ ] Price hits Tier 2 stop-loss
- [ ] Single-day drop > 5% with volume surge
- [ ] Limit-down (跌停) or near-lock

### 🟡 REVIEW & POSSIBLE REDUCE (any one)
- [ ] RSI > 85 AND KDJ K > 80 simultaneously
- [ ] Price pulls back > 5% from session high
- [ ] Volume surges 2x+ on a down day
- [ ] Long red candle (>4%) on extremely overbought reading

### 🟢 HOLD (all must be true)
- [ ] Price above all MAs (MA5 > MA10 > MA20 > MA60)
- [ ] MACD still，红柱
- [ ] RSI < 80 (or < 85 with strong momentum)
- [ ] No volume-price divergence (price rises WITH volume)

---

## Current Status (2026-05-11 EOD)

Both ETFs are in **EXTREME OVERBOUGHT** territory:

| ETF | RSI(14) | MACD | 趋势 | 量能 |
|-----|---------|------|------|------|
| 芯片ETF | **81.1** ⚠️ | 死叉(-0.048) | 📈 上升 | 今日暴涨+6.43% |
| 科创50ETF | **79.1** ⚠️ | 死叉(-0.071) | 📈 上升 | 今日暴涨+4.59% |

⚠️ **RSI > 79 on both ETFs** — overbought but can persist in strong trends. Consider partial profit-taking (e.g., sell 1/3) rather than selling all.

---

## Volatility Context (2026-05-11)

| ETF | Day Range | Day Vol% | ATR(14) | Status |
|-----|-----------|----------|---------|--------|
| 芯片ETF | 1.053–1.100 | ~4.5% | 0.0271 | HIGH |
| 科创50ETF | 1.705–1.770 | ~3.8% | 0.0393 | HIGH |

⚠️ **On high-volatility days**: ATR-based stops are wider. Don't tighten stops mechanically — use the Tier 2/Tier 3 framework above.

---

## RSI Thresholds Used

| RSI | Chinese Markets (A-shares) |
|-----|---------------------------|
| > 85 | Extreme overbought — distribution zone |
| 70–85 | Overbought — caution, watch for reversal |
| 30–70 | Normal range |
| < 30 | Oversold — potential bounce |

⚠️ A-share ETFs can stay in RSI > 80 for extended periods during strong trends (e.g., 2024 tech/chip rallies). Do NOT sell on RSI alone — use the tier framework.
