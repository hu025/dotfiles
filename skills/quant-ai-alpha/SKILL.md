---
name: quant-ai-alpha
description: AI量化因子挖掘与ETF监控。RD-Agent(Q)+QLib+QuantaAlpha工作流，A股高弹性ETF筛选，-10%止损策略
---

# AI量化因子挖掘与ETF监控系统

## 核心工具链

| 工具 | 用途 | 状态 |
|------|------|------|
| QLib（微软）| A股数据+回测引擎 | pip install qlib |
| RD-Agent(Q)（NeurIPS 2025）| 因子自动挖掘 | pip install rdagent |
| QuantMuse | 全栈量化系统(C++后端+实时WebSocket+LLM分析) | GitHub 2.9K stars |
| QuantaAlpha（清华/北大）| LLM+进化策略因子挖掘 | GitHub 1.5K stars |
| AkShare | 免费开源财经数据 | pip install akshare |
| RD-Agent fin_factor | 从研报/财报提取因子 | rdagent fin_factor |
| Goldman AlphaAI | 跨行业AI选股（Sector内AI渗透率识别）| 2026新平台 |

## 高弹性ETF筛选流程

```
1. 获取全市场ETF列表（AkShare）
2. 过滤低价高弹性标的：
   - 价格位于52W低点附近（< 52W high × 0.85）
   - 历史波动率高
   - 成交额活跃（> 5000万/日）
3. 技术面确认（均线多头排列、MACD金叉）
4. RD-Agent因子回测验证
5. -10%止损线
```

## RD-Agent 快速上手

```bash
pip install rdagent
rdagent fin_factor              # 自动因子挖掘
rdagent fin_factor_report --report-folder=./reports  # 从研报提取
rdagent fin_quant               # 因子-模型联合进化
```

## QLib + RD-Agent(Q) 集成

```python
import qlib
qlib.init(provider_path="./data")
# RD-Agent 会自动调度QLib数据接口进行回测
```

## QuantaAlpha（下一代）

```
QuantaAlpha-claw：蜂群式Agent协同
Lead / Reviewer / Miner 多角色并行
Skill化算子 + 血统追踪 + Walk-Forward验证
→ 关注 https://github.com/QuantaAlpha/QuantaAlpha-claw
```

## QuantMuse 全栈量化系统

```
GitHub: https://github.com/0xemmkty/QuantMuse
Stars: 2.9K | MIT License

架构特点：
- C++ 后端核心引擎（低延迟订单执行）
- Python AI层（LLM集成+NLP情绪分析+XGBoost/LSTM）
- WebSocket 实时市场数据（多交易所）
- Streamlit 可视化仪表盘
- 8+ 内置量化策略

安装：
pip install quant-muse  # 或 git clone
cd QuantMuse && pip install -e .[ai,visualization,realtime]

特色：因子分析 + LLM市场解读 + 实时数据一站式
```

## RD-Agent(Q) 2026年新发现

```
关键突破：
- 因子-模型联合进化（而非单独优化）
- 因子数量减少70%+，但IC和ARR提升
- 端到端成本 < $10（实验条件）
- IC ~0.0532, ARR ~14.21%, IR ~1.74

五大功能单元：
规范单元 → 构思单元 → 实现单元 → 验证单元 → 分析单元
       ↑                                          ↓
       ← ← ← ← ← ← 反馈循环 ← ← ← ← ← ← ← ← ← ←

数据源：QLib（已内置A股沪深300数据格式）
```

## Goldman AlphaAI（2026新平台）

```
核心思路：AI主题ETF（$405亿）系统性遗漏了行业内部真正在做AI转型的公司
创新点：识别"AI渗透率"而非"AI标签"
官网：Goldman Sachs Asset Management AlphaAI
```

## 已知限制

- RD-Agent 仅支持 Linux
- A股数据需要 AkShare 或 QLib 内置数据
- QLib 数据存储需要足够磁盘空间
- QuantMuse WebSocket 实时数据需配置 API key
