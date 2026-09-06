#!/usr/bin/env python3
"""
China A-share ETF Full Technical Analysis
Runs a complete panel: MA, MACD, KDJ, Bollinger Bands, ATR, RSI, volume ratio.
Produces actionable signals and operation suggestions.
Verified keys: fetch_realtime() returns 'price' and 'chg_pct' (NOT 'current_price'/'change_pct').
"""
import urllib.request
import json
import math
import re

ETFS = [
    {'name': '芯片ETF国泰', 'secid': '1.512760', 'code': '512760', 'cost': 0.872},
    {'name': '科创50ETF易方达', 'secid': '1.588080', 'code': '588080', 'cost': 1.437},
    {'name': '通信ETF华夏', 'secid': '1.515050', 'code': '515050', 'cost': 1.125},
]

def fetch_realtime(secid):
    """Fetch real-time quote. Returns: price, prev_close, open, volume, chg, chg_pct, day_high, day_low."""
    code = secid.split('.')[-1]
    url = f"https://qt.gtimg.cn/q=sh{code}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as r:
        raw = r.read().decode('gbk', errors='replace')
    m = re.search(r'"([^"]+)"', raw)
    if not m:
        return None
    fields = m.group(1).split('~')
    return {
        'name': fields[1],
        'price': float(fields[3]),
        'prev_close': float(fields[4]),
        'open': float(fields[5]),
        'volume': int(fields[6]),
        'chg': float(fields[31]),
        'chg_pct': float(fields[32]),
        'day_high': float(fields[33]),
        'day_low': float(fields[34]),
    }
