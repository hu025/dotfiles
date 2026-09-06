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
| QuantaAlpha（清华/北大）| LLM+进化策略因子挖掘 | GitHub 1.5K stars |
| AkShare | 免费开源财经数据 | pip install akshare |
| RD-Agent fin_factor | 从研报/财报提取因子 | rdagent fin_factor |

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

## 已知限制

- RD-Agent 仅支持 Linux
- A股数据需要 AkShare 或 QLib 内置数据
- QLib 数据存储需要足够磁盘空间
