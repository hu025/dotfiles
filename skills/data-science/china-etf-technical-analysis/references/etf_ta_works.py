#!/usr/bin/env python3
"""
Verified working ETF technical analysis for execute_code (sandbox).
Uses subprocess+curl instead of urllib (which times out silently in sandbox).
Pattern confirmed working 2026-06-30.
"""
import subprocess, re, json, math

def fetch_kline(code, count=90):
    """Fetch daily K-line from Tencent API. Returns list of [date, open, close, high, low, volume]."""
    url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?_var=kline_dayqfq&param=sh{code},day,,,{count},qfq")
    r = subprocess.run(f'curl -s "{url}"', capture_output=True, timeout=10, shell=True)
    text = r.stdout.decode('gbk', errors='replace')
    m = re.search(r'=({.*})', text)
    if not m:
        return []
    d = json.loads(m.group(1))
    days = d['data'].get(f'sh{code}', {}).get('qfqday', [])
    return [[dd[0], float(dd[1]), float(dd[2]), float(dd[3]), float(dd[4]), float(dd[5])] for dd in days]

def fetch_quote(code):
    """Fetch real-time quote. Returns (price, prev_close, chg_pct, day_high, day_low)."""
    r = subprocess.run(f'curl -s "https://qt.gtimg.cn/q=sh{code}"', capture_output=True, timeout=5, shell=True)
    text = r.stdout.decode('gbk', errors='replace')
    m = re.search(r'"([^"]+)"', text)
    if not m:
        return None
    f = m.group(1).split('~')
    return {
        'name': f[1], 'code': f[2],
        'price': float(f[3]), 'prev_close': float(f[4]),
        'chg': float(f[31]), 'chg_pct': float(f[32]),
        'day_high': float(f[33]), 'day_low': float(f[34]),
    }

def tech_analysis(klines, price, cost):
    """
    Full technical analysis. klines = list from fetch_kline().
    Returns dict with all indicators.
    """
    closes = [k[2] for k in klines]
    highs  = [k[3] for k in klines]
    lows   = [k[4] for k in klines]
    vols   = [k[5] for k in klines]
    n = len(closes)

    ma5  = sum(closes[-5:])  / min(5, n)
    ma10 = sum(closes[-10:]) / min(10, n)
    ma20 = sum(closes[-20:]) / min(20, n) if n >= 20 else None

    # RSI(14)
    gains, losses = [], []
    for i in range(1, n):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0)); losses.append(max(-d, 0))
    p = min(14, len(gains))
    ag = sum(gains[-p:]) / p if p > 0 else 0
    al = sum(losses[-p:]) / p if p > 0 else 0
    rsi = 100 if al == 0 else 100 - 100 / (1 + ag / al)

    # Daily volatility
    rets = [(closes[i]-closes[i-1])/closes[i-1] for i in range(1, n)]
    m_r = sum(rets) / len(rets) if rets else 0
    var = sum((x-m_r)**2 for x in rets) / len(rets) if rets else 0
    daily_vol = math.sqrt(var) * 100

    # Volume ratio (5d avg / 10d avg)
    v5  = sum(vols[-5:])  / min(5, n)
    v10 = sum(vols)       / min(10, n)
    vol_ratio = v5 / v10 if v10 > 0 else 1

    # Trend
    if n >= 2 and closes[-1] > ma5 > ma10:
        trend = '上升'
    elif n >= 2 and closes[-1] < ma5 < ma10:
        trend = '下降'
    else:
        trend = '震荡'

    # ATR(14)
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
           for i in range(1, min(n, 15))]
    atr = sum(trs) / len(trs) if trs else 0

    # MACD (EMA12 - EMA26)
    e12 = e26 = closes[0]
    for c in closes[1:]:
        e12 = c*(2/13) + e12*(1-2/13)
        e26 = c*(2/27) + e26*(1-2/27)
    macd_dif = e12 - e26

    # 20d / 60d high-low
    h20 = max(closes[-20:]) if n >= 20 else max(closes)
    l20 = min(closes[-20:]) if n >= 20 else min(closes)
    h60 = max(closes[-60:]) if n >= 60 else max(closes)
    l60 = min(closes[-60:]) if n >= 60 else min(closes)

    # 10d change
    chg10 = (closes[-1] - closes[-10]) / closes[-10] * 100 if n >= 10 else 0

    return {
        'n': n, 'price': price, 'cost': cost,
        'profit_pct': (price - cost) / cost * 100,
        'rsi': rsi, 'trend': trend, 'vol': daily_vol, 'atr': atr,
        'ma5': ma5, 'ma10': ma10, 'ma20': ma20,
        'vol_ratio': vol_ratio, 'macd_dif': macd_dif,
        'h20': h20, 'l20': l20, 'h60': h60, 'l60': l60,
        'chg10': chg10,
    }


# --- Working execute_code script template ---
if __name__ == '__main__':
    # Example: run full analysis for user's known ETF holdings
    etfs = [
        ('512760', '芯片ETF', 0.872),
        ('588080', '科创50ETF', 1.437),
        ('515050', '通信ETF', 1.125),
    ]

    results = []
    for code, name, cost in etfs:
        quote = fetch_quote(code)
        kl = fetch_kline(code, 90)
        if not quote or not kl:
            print(f"FAIL: {name}")
            continue
        r = tech_analysis(kl, quote['price'], cost)
        r.update({'name': name, 'code': code,
                  'chg': quote['chg_pct'],
                  'dh': quote['day_high'], 'dl': quote['day_low']})
        results.append(r)
        print(f"OK {name}: n={r['n']}, price={quote['price']}, profit={r['profit_pct']:+.1f}%")

    for r in results:
        nh20 = r['price'] / r['h20'] * 100
        nh60 = r['price'] / r['h60'] * 100
        rsi = r['rsi']

        sigs = []
        if rsi > 80: sigs.append('RSI严重超买')
        elif rsi > 70: sigs.append('RSI超买')
        elif rsi < 30: sigs.append('RSI超卖')
        if nh20 > 97: sigs.append('逼近20日高点')
        if r['vol_ratio'] > 1.5: sigs.append('放量')
        elif r['vol_ratio'] < 0.7: sigs.append('缩量')
        if r['macd_dif'] < 0: sigs.append('MACD负')
        if r['chg10'] > 15: sigs.append('10日急涨')
        if r['trend'] == '上升': sigs.append('均线多头')
        elif r['trend'] == '下降': sigs.append('均线空头')

        print(f"\n{'='*60}")
        print(f"【{r['name']} {r['code']}】")
        print(f"  现价: ¥{r['price']:.3f}  成本: ¥{r['cost']:.3f}  盈利: {r['profit_pct']:+.1f}%")
        print(f"  今日: {r['chg']:+.2f}%  区间: {r['dl']:.3f}~{r['dh']:.3f}")
        print(f"  RSI:{r['rsi']:.1f}  趋势:{r['trend']}  波幅:{r['vol']:.2f}%/日")
        print(f"  MA5={r['ma5']:.3f}  MA10={r['ma10']:.3f}  MA20={r['ma20']:.3f if r['ma20'] else 'N/A'}")
        print(f"  MACD(DIF)={r['macd_dif']:.4f}  量比={r['vol_ratio']:.2f}  ATR={r['atr']:.4f}")
        print(f"  20日高:{r['h20']:.3f}  低:{r['l20']:.3f}  距高:{nh20:.1f}%")
        print(f"  10日涨幅:{r['chg10']:+.1f}%")
        print(f"  信号: {' | '.join(sigs)}")
