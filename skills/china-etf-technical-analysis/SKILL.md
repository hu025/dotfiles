---
name: china-etf-technical-analysis
description: A股/ETF 高弹性量化筛选。触发词：ETF筛选、A股弹性、高弹性ETF、低价ETF
triggers:
  - ETF筛选
  - A股弹性
  - 高弹性ETF
  - 低价ETF
  - ETF弹性筛选
---

# A股/ETF 高弹性量化筛选技能

## 核心接口（AkShare）

### ETF 实时行情
```python
import akshare as ak
df = ak.fund_etf_spot_em()
```
返回字段：`代码`, `名称`, `最新价`, `最高价`, `最低价`, `涨跌幅`, `成交量`, `成交额`, `主力净流入-净额`, `数据日期`, `更新时间`

### ETF 历史行情（用于计算 52 周高点）
```python
df = ak.fund_etf_hist_em(symbol="159865", period="daily", start_date="20240101", end_date="20260907", adjust="qfq")
```
返回字段：`日期`, `开盘`, `收盘`, `最高`, `最低`, `成交量`, `成交额`, `涨跌幅`, `涨跌额`, `换手率`

### A股 全局行情
```python
df = ak.stock_zh_a_spot()
```
返回字段：`代码`, `名称`, `最新价`, `涨跌幅`, `最高`, `最低`, `成交量`, `成交额`, `市盈率`, `市净率`, `总市值`, `流通市值`

## 筛选逻辑

### 高弹性 ETF 策略
1. **价格低位**：最新价距历史低点 ≤ 10%
2. **向上空间大**：当前价距 52 周高点空间 ≥ 15%
3. **流动性过滤**：日成交额 > 5000 万
4. **止损提示**：若最新价较买入参考价下跌 ≥ 10%，输出 ⚠️ 止损警告

### 指标计算
- `52WHigh`: 过去 252 个交易日最高价
- `DistTo52WHigh`: (当前价 - 52WHigh) / 52WHigh × 100%
- `LowPrice52W`: 过去 252 个交易日最低价
- `DistToLow`: (当前价 - LowPrice52W) / LowPrice52W × 100%
- `Score`: 综合弹性评分 = |DistTo52WHigh| × 流动性加权

## 脚本
- `~/.hermes/scripts/etf_screener.py` — 主筛选脚本，使用 AkShare

## 备选方案
- baostock：A股数据备选，`ak.stock_zh_a_daily()` → `baostock.bs.query_history_k_data_plus()`
- 依赖：`~/.hermes/venv`（uv venv 创建，已安装 akshare）

## 使用方法
```bash
~/.hermes/venv/bin/python ~/.hermes/scripts/etf_screener.py
```
