#!/usr/bin/env python3
"""
Tencent K-line fetcher — reliable alternative to EastMoney K-line API.
EastMoney push2his.eastmoney.com fails in sandbox/execute_code with RemoteDisconnected.
This uses web.ifzq.gtimg.cn which is stable.
"""
import urllib.request
import json
import re

def fetch_tencent_kline(secid, count=60):
    """
    Fetch daily K-line data from Tencent Finance API.
    secid: e.g. '512760' (will prepend 'sh' for Shanghai)
    returns: list of dicts with keys: date, open, close, high, low, volume
    """
    code = secid.lstrip('sh').lstrip('sz').lstrip('1.').lstrip('0.')
    # Determine market prefix: 5/6/8xxx = Shanghai, 000/001/002/003xxx = Shenzhen
    if code.startswith(('5', '6', '8', '9')):
        prefix = 'sh'
    else:
        prefix = 'sz'
    
    url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
           f"?_var=kline_dayqfq&param={prefix}{code},day,,,{count},qfq")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as r:
        raw = r.read().decode('utf-8')
    
    # Response format: kline_dayqfq={...json...}
    m = re.search(r'=(\{.*\})', raw)
    if not m:
        return []
    
    data = json.loads(m.group(1))
    # Nested dict: data -> sh512760 -> qfqday
    key = f"{prefix}{code}"
    days = data.get('data', {}).get(key, {}).get('qfqday', [])
    
    klines = []
    for d in days:
        klines.append({
            'date': d[0],
            'open': float(d[1]),
            'close': float(d[2]),
            'high': float(d[3]),
            'low': float(d[4]),
            'volume': float(d[5])
        })
    return klines


def fetch_tencent_quote(secid):
    """
    Fetch real-time quote from Tencent QT API.
    secid: e.g. 'sh512760' or '512760'
    returns: dict with price, prev_close, open, high, low, chg, chg_pct
    """
    code = secid.lstrip('sh').lstrip('sz')
    if not code.startswith(('sh', 'sz')):
        code = 'sh' + code
    url = f"https://qt.gtimg.cn/q={code}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as r:
        raw = r.read().decode('gbk', errors='replace')
    
    m = re.search(r'"([^"]+)"', raw)
    if not m:
        return None
    fields = m.group(1).split('~')
    return {
        'name': fields[1],
        'code': fields[2],
        'price': float(fields[3]),
        'prev_close': float(fields[4]),
        'open': float(fields[5]),
        'volume': int(fields[6]),
        'chg': float(fields[31]),
        'chg_pct': float(fields[32]),
        'day_high': float(fields[33]),
        'day_low': float(fields[34]),
    }


if __name__ == '__main__':
    # Test
    k = fetch_tencent_kline('512760', 5)
    print("K-line (last 5 days):", k[-5:] if len(k) >= 5 else k)
    q = fetch_tencent_quote('512760')
    print("Quote:", q)
