---
name: etf-high-elasticity-screening
description: 筛选 A 股低价高弹性 ETF——价格低位 + 距52W高点空间大 + 爆发力强，用于追求最大盈利的目标
---

# ETF 高弹性低位筛选

## 核心方法

**目标**：找「价格低 + 向上空间大」的 ETF，追求最大收益。

**筛选标准**：
1. 现价距 52W 高点 ≥50%（向上弹性大）
2. 现价距 52W 低点 ≥30%（已脱离底部，不是继续创新低的弱势）
3. 价格低于 ¥2（便于灵活配置仓位）

**维度优先级**：
- 距 52W 高点空间越大 → 潜在收益越高
- 现价越接近 52W 低点 → 风险越高（可能是下跌中继）
- 已脱离低点 30%+ → 有资金介入，相对安全

## 数据获取（verified 2026-08-06）

### 实时价格（EastMoney push2）
```python
import urllib.request, json

def get_quote(code):
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=1.{code}&fields=f43,f44,f45,f46,f47,f57,f58,f60,f169,f170&ut=fa1fd4627ccbd31434f689c4ce41ac99"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode())
    d = data.get("data", {})
    price = d.get("f43", 0) / 100
    prev_close = d.get("f60", 0) / 100
    pct = d.get("f169", 0) / 100
    chg = price - prev_close
    name = d.get("f58", code)
    return name, price, chg, pct, prev_close
```

### 52W 高低点（EastMoney K-line，250日线）
```python
def get_52w_data(code):
    url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&lmt=250&klt=101&fqt=1&beg=0&end=20500101&ut=fa1fd4627ccbd31434f689c4ce41ac99"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read().decode())
    klines = data.get("data", {}).get("klines", [])
    closes = [float(k.split(",")[2]) for k in klines]  # index 2 = close
    current = closes[-1]
    low_52w = min(closes)
    high_52w = max(closes)
    return current, low_52w, high_52w
```

**K-line 字段索引**：`date,open,close,high,low,volume`（indices 0-5）

## 已知高弹性 ETF 代码

| ETF | 代码 | 现价(2026-08-06) | 52W低 | 52W高 | 距高点空间 |
|------|------|------|--------|--------|----------|
| 光伏ETF华泰柏瑞 | 515790 | ¥0.841 | ¥0.626 | ¥1.901 | **+55.8%** |
| 中概互联ETF易方达 | 513050 | ¥1.163 | ¥0.816 | ¥2.570 | **+54.7%** |
| 科创50ETF易方达 | 588080 | ¥1.723 | ¥0.646 | ¥2.273 | +24.2% |
| 证券ETF国泰 | 512880 | ¥1.096 | ¥0.623 | ¥1.364 | +19.6% |
| 中证2000ETF | 562280 | — | — | — | 微盘股高弹性 |
| 新能源车ETF | 515030 | — | — | — | 锂价触底 |
| 创业板ETF易方达 | 159915 | — | — | — | 科技成长 |
| 中药ETF | 159647 | — | — | — | 政策+防守 |
| 机器人ETF | 159770 | — | — | — | AI主题 |
| 电力ETF | 159611 | — | — | — | 高股息+用电需求 |
| 军工ETF | 515220 | — | — | — | 地缘催化 |
| 酒ETF华夏 | 512690 | — | — | — | 低位震荡 |

## 推荐配置模板

**最大盈利组合**（高弹性）：
```
光伏ETF 515790    50%   目标¥1.3+
中概互联ETF 513050  50%  目标¥1.7+

止损：-8%（光伏 ¥0.774，中概 ¥1.070）
```

**稳健进攻组合**：
```
光伏ETF 515790    40%
科创50ETF 588080  30%
证券ETF 512880    30%
```

## 操作时机判断

- **可以直接入场**：价格已在低位（距高点空间 ≥50%），等最低点意义不大
- **不要等**：等跌到最低点的收益最多 10%，但可能直接拉起踏空
- **止损要严**：-8% 坚决出，不恋战

## 参考资料
- `references/etf-high-elasticity-screening-2026-08-06.md` — 2026-08-06 实测数据记录
