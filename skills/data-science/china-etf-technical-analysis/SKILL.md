---
name: china-etf-technical-analysis
description: Fetch real-time quotes and K-line data for Chinese A-share ETFs, then perform technical analysis (RSI, MA, volatility, volume).
category: data-science
---

# China ETF Technical Analysis

Fetch real-time quotes and K-line data for Chinese A-share ETFs, then perform technical analysis.

## Data Sources

### 0. EastMoney Push2 ETF Market Scanner (recommended — all ETFs, sorted)
**Best for: finding top gainers/losers across entire ETF market in one API call.**

```
https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=50&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid={FID}&fs=b:MK0021+f:MK0022+f:MK0023&fields=f12,f14,f3,f2,f6
```
- `fid=f3` → sort by today's % change (desc = gainers, asc = losers)
- `fid=f6` → sort by YTD % change
- `pz=50` → 50 results per page; increase for more
- Fields: `f12`=code, `f14`=name, `f3`=chg%, `f2`=price, `f6`=YTD chg%
- Works in `execute_code` reliably with `subprocess.run(shell=True)` or `urllib`
- **Python parse pattern:**
```python
import subprocess, json
r = subprocess.run('curl -s "URL"', capture_output=True, text=True, timeout=10, shell=True)
d = json.loads(r.stdout)
sorted_etfs = sorted(d['data']['diff'], key=lambda a: a['f3'], reverse=True)
# top 10 gainers: sorted_etfs[:10]
# top 10 losers: sorted(sorted_etfs, key=lambda a: a['f3'])[:10]
```

### 1. Tencent QT API (real-time quote)

### 2. Tencent K-line API (recommended — more reliable)
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sh{SECID},day,,,{COUNT},qfq
```
- Returns JSONP: `kline_dayqfq={...}` — extract with regex `=(\{.*\})`
- Fields: `date, open, close, high, low, volume` (indices 0–5)
- Works reliably from mainland China; EastMoney API may timeout
- Example parsing:
```python
import re, json, urllib.request
url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sh{secid},day,,,{count},qfq"
    with urllib.request.urlopen(req, timeout=8) as r:
        raw = r.read()
    # Tencent QT API returns GB2312/GBK encoded data — use errors='replace' to handle gracefully
    try:
        text = raw.decode('gbk')
    except Exception:
        text = raw.decode('utf-8', errors='replace')
    
    m = re.search(r'"([^"]+)"', text)
klines = [{'date': d[0], 'open': float(d[1]), 'close': float(d[2]),
           'high': float(d[3]), 'low': float(d[4]), 'volume': float(d[5])} for d in days]
```

### 3. EastMoney K-line API (fallback — may timeout)
```
https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={MARKET}.{SECID}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=1&beg=0&end=20500101&lmt={COUNT}
```
- `klt=101` = daily K-line
- `fqt=1` = forward-adjusted
- Returns JSON with `data.klines` array of: `date,open,close,high,low,volume`
- Market: `1`=Shanghai, `0`=Shenzhen
- ⚠️ **Pitfall**: often times out from mainland China; use Tencent K-line API instead

### Known ETF secids
- 芯片ETF国泰: `1.512760` — 历史最高¥1.38（2026-07）
- 科创50ETF易方达: `1.588080`
- 酒ETF华夏: `1.512690` — 成本¥0.403，持仓中（2026-07-03）
- 军工ETF: `1.515220` — RSI 22.7超卖，关注
- 科创50ETF广发: `1.588060`
- 通信ETF华夏: `1.515050`

## Technical Analysis (Python)

Use the **full analysis** from `references/full_analysis.py` — it includes MA, RSI, KDJ, Bollinger Bands, ATR, proper MACD, and volume ratio in one pass. The simple version below is for quick probes only.

### Quick probe (minimal)
```python
import math

def simple_tech_analysis(klines, current_price, cost_price):
    closes = [k['close'] for k in klines]
    highs  = [k['high']  for k in klines]
    lows   = [k['low']   for k in klines]
    vols   = [k['volume'] for k in klines]
    n = len(closes)

    ma5  = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20 if n >= 20 else None

    # RSI(14)
    gains, losses = [], []
    for i in range(1, n):
        delta = closes[i] - closes[i-1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    period = min(14, len(gains))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    rsi = 100 if avg_loss == 0 else 100 - (100 / (1 + avg_gain/avg_loss))

    # Volatility
    returns = [(closes[i]-closes[i-1])/closes[i-1] for i in range(1,n)]
    mean_r = sum(returns) / len(returns)
    var = sum((r-mean_r)**2 for r in returns) / len(returns)
    daily_vol = math.sqrt(var) * 100

    # Volume ratio
    vol_5d  = sum(vols[-5:])  / 5
    vol_10d = sum(vols)       / 10
    vol_ratio = vol_5d / vol_10d if vol_10d > 0 else 1

    # Trend
    if closes[-1] > ma5 > ma10:
        trend = '上升'
    elif closes[-1] < ma5 < ma10:
        trend = '下降'
    else:
        trend = '震荡'

    # ATR(14)
    trs = []
    for i in range(1, min(n, 15)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    atr14 = sum(trs) / len(trs) if trs else 0

    print(f"RSI(14): {rsi:.1f} | 趋势:{trend} | 量能:{'放量' if vol_ratio>1.2 else '缩量' if vol_ratio<0.8 else '持平'} | 日波动:{daily_vol:.2f}% | ATR:{atr14:.4f}")
```

## Key Findings / Pitfalls

- **Principal calculation must exclude cashed-out positions**: When calculating total principal for multiple ETF positions, only sum the CURRENT holdings. Do NOT include already-liquidated positions (e.g., medical ETF that was sold). Wrong: `512760 cost + 588080 cost + already-cashed-out medical ETF`. Correct: `512760 cost + 588080 cost + 515050 cost = actual principal`. Always verify each position is still active before including in the principal sum.

- **Web search is the primary research method**: For investment analysis, web search with titles/descriptions provides sufficient information. Use browser navigation (EastMoney pages) as a supplementary verification step only — the page often returns a compact snapshot, not full data. The key data (current price, NAV, period returns) is often visible in the first snapshot.

- **Tencent QT API `fetch_realtime` return keys** (verified 2026-06-28): returns `price` (not `current_price`) and `chg_pct` (not `change_pct`). Also returns `prev_close`, `open`, `volume`, `chg`, `day_high`, `day_low`. Do NOT use EastMoney-style `current_price`/`change_pct` keys against this API — it silently returns `None`. Quick probe pattern:

```python
import urllib.request, re
url = f"https://qt.gtimg.cn/q=sh{code}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as r:
    raw = r.read().decode('gbk', errors='replace')
m = re.search(r'"([^"]+)"', raw)
if m:
    f = m.group(1).split('~')
    price = float(f[3]); chg_pct = float(f[32])
```

- **EastMoney K-line API (`push2his.eastmoney.com`) unreliability in sandbox/execute_code**: The EastMoney K-line endpoint frequently fails in `execute_code` sandbox with `RemoteDisconnected: Remote end closed connection without response`. Workaround: use **Tencent K-line API** instead — `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sh{SECID},day,,,{COUNT},qfq`. Returns JSON embedded as `kline_dayqfq={...}`. Parse with `re.search(r'=({.*})', raw)` then `json.loads(m.group(1))`. Works reliably in sandbox environments.
- Tencent QT API returns GB2312/GBK encoded data; wrap decode in `errors='replace'` fallback. Raw curl output may show garbled Chinese — use Python to parse.
- Tencent QT response format: `v_sh{SECID}="..."` — extract with regex `"([^"]+)"`. Fields split by `~`: index 1=name, 3=price, 4=prev_close, 5=open, 6=volume, 31=chg, 32=chg_pct, 33=day_high, 34=day_low.
- RSI calculation: ensure `n >= period+1` before accessing `closes[-period-1]`
- `volatility > 2%/day` = high volatility; `> 1%` = medium
- The `full_analysis.py` reference script uses EastMoney K-line and will fail in sandbox — prefer the Tencent K-line approach in `execute_code` for reliability
- **Python f-string pitfall**: `f"{value:.3f if value else 'N/A'}"` is invalid — must use ternary inside the format spec is not allowed. Use a separate variable or helper: `s = f"{value:.3f}" if value else "N/A"` then `f"{s}"`
- **`full_analysis.py` ETFS list is incomplete**: only had 512760 and 588080; user also holds 515050 (通信ETF, cost=1.125). **FIXED** — `references/full_analysis.py` now includes all three ETFs.
- **Sandbox `urllib.request` vs `subprocess+curl`**: The `execute_code` sandbox's `urllib.request` (used in `tencent_kline.py` and `full_analysis.py`) can silently timeout or return empty data for Tencent APIs. Use `subprocess.run('curl -s ...', capture_output=True, shell=True)` + `decode('gbk', errors='replace')` instead — confirmed working in sandbox. The `urllib.request` approach is fine in a normal Python environment but unreliable in `execute_code`. Reference scripts under `references/` use urllib; the verified `execute_code` pattern uses subprocess+curl as shown in the working script this session.

## Real-time Monitoring & Alert System

### Monitoring Script (`~/.hermes/scripts/etf_monitor.py`)

A fully working ETF anomaly monitor with **dynamic session high tracking** and **moving stop-loss**.

**Key features:**
- Tracks per-session high and auto-raises stop-loss (5% trailing from session high)
- Detects: stop-loss breach, >3% single-day drop, breakout of previous high
- Persists state across runs via `~/.hermes/scripts/.etf_monitor_state.json`
- Resets cleanly at 9:25 new trading day (avoids stale alert flags)
- Writes alerts to `~/.hermes/cron/output/etf_alert.txt` when triggered

**Alert conditions:**
| Condition | Action |
|---|---|
| Price ≤ session_high × 0.95 | 🚨 Stop-loss breach → notify |
| Single-day drop > 3% | ⚠️ Anomaly → notify |
| Session high > init_high | 🚀 Breakout → notify |

**Cron job setup (deliver=origin, no skill needed):**
```
schedule: */5 9-11,13-15 * * 1-5
prompt: Run ~/.hermes/scripts/etf_monitor.py. If ~/.hermes/cron/output/etf_alert.txt
exists, read it and output the content. Otherwise output nothing.
```

**State file format (actual — verified 2026-05-13):**
```json
{
  "date": "20260513",
  "alerts": {"sh512760_rsi": "overbought"},
  "init_high": {
    "sh512760": 1.109,
    "sh588080": 1.785,
    "sh512010": 0.38
  }
}
```
- `date`: trading day string (YYYYMMDD)
- `alerts`: flags set by monitor (e.g. RSI overbought), cleared on new day
- `init_high`: per-ticker session opening high, used for trailing stop at ×0.95

### Pitfalls Discovered

- **Delivery channel**: User is on QQ (not WeChat). Cron `deliver=origin` works for QQ. WeChat requires the `openclaw-wechat-file-send` skill separately.
- **Stale state across days**: Always reset `alerts_sent` at 9:25 on new trading day, otherwise alerts fire immediately on re-run.
- **Static stop-loss is wrong**: Use `session_high × 0.95` as dynamic trailing stop, not a hardcoded absolute price.
- **Pre-market data**: Tencent QT price at 18:35 is closing/after-hours data. Intraday highs are from the actual trading session (9:30-15:00).

## Use Cases
- ETF持仓技术分析
- A股指数/ETF择时参考
- 量价配合判断
- **持仓异动实时监控（通过cron+告警文件机制）**

## Support Files

| File | Purpose |
|------|---------|
| `references/tencent_kline.py` | Reliable Tencent K-line fetcher — drop-in replacement for EastMoney API (fails in sandbox). Use `fetch_tencent_kline(secid, count)` and `fetch_tencent_quote(secid)`. |
| `references/etf_market_scanner.py` | EastMoney push2 ETF scanner — fetches all A-share ETFs sorted by gainers/losers. `subprocess.run` + `json.loads`. Drop into execute_code directly. |
| `references/etf_ta_works.py` | **Verified working execute_code script** — full ETFS analysis using `subprocess+curl` (not urllib). Includes `fetch_kline`, `fetch_quote`, `tech_analysis`, and the working `__main__` template. Use this directly in `execute_code` rather than the urllib-based reference files above. |
| `references/full_analysis.py` | Full panel analysis: MA + MACD + KDJ + Bollinger + ATR + RSI + volume. Run directly or import functions. |
| `references/trading_signals.md` | Decision framework: 3-tier stop-loss levels, action triggers, and per-signal response playbook. |

## References

- `references/etf_research_workflow.md` — ETF 横向对比与选品分析框架：搜索维度、本金计算原则、输出结构、推荐 ETF 快速参考
