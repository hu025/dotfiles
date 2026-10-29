---
name: group-sim
description: Use when the agent participates in group chats (QQ群/飞书群) and needs to decide whether to speak, how long to reply, and when to disengage. Provides a 4-state social simulator (watching/active/probing/withdrawing) with relevance gating, cooldown, daily quota, topic-round limit, auto-closing, sentence splitting, and safety blocks. Trigger on 群聊/群消息/仿真/潜水/接话策略.
---

# 群聊仿真引擎（轻量版）

从 <https://github.com/Derpyu520/qq-bridge>（QQ ↔ DeepSeek Harness 桥接，MIT）的「一代仿真 / 二代仿真」机制提炼的自实现。**不依赖 SnowLuma，不依赖 DeepSeek Harness**，纯 Python 标准库，可直接嵌入 Hermes。

上游那套要额外跑一个 Node 桥接进程 + DSH + SnowLuma（等于把 QQ 账号交出去），与 Hermes 已有的 qqbot 适配器功能重叠。本模块只保留「决策」部分：**该不该说、说多长、什么时候闭嘴**。

## 状态机

| 状态 | 含义 | 最大字数 | 主动发起 | 最小间隔 | 接话倾向 |
|---|---|---|---|---|---|
| `watching` 观望 | 只看，不主动 | 60 | 否 | 30 min | 0.15 |
| `active` 活跃 | 正常参与 | 180 | 是 | 2 min | 0.75 |
| `probing` 试探 | 谨慎发言 | 90 | 是 | 10 min | 0.45 |
| `withdrawing` 退场 | 收尾后沉默 | 0 | 否 | 60 min | 0.0 |

## 核心规则

1. **选择性参与**：不是每条消息都接。相关度 = 被@（0.45）+ 提到话题（每个 0.18，上限 0.35）+ 问句（0.12）+ 提到自己名字。
   - 相关度 < 0.15 → 直接沉默，**不调用 LLM**
   - 相关度 ≥ 0.8 且处于 active → 必回
2. **主动收尾**：同一话题聊够 `max_rounds_per_topic` 轮后，允许说**一句** ≤60 字的收尾语，然后转入 `withdrawing` 彻底沉默。话题切换时重置。
3. **硬边界**：消息含密码/验证码/密钥/身份证/银行卡，或要求转人工/退款/投诉 → 一律不接（`blocked_by_safety`）。
4. **群白名单**：`allowed_groups` 非空时只响应名单内的群；`deny_groups` 优先。
5. **额度护栏**：`daily_quota` 每日发言上限，超出即静默。
6. **冷却**：两次发言最小间隔按状态区分。
7. **分句发送**：长回复按句末标点拆成多条短消息，符合群聊节奏。

## 用法

```python
import sys
sys.path.insert(0, "/home/saber/.hermes/skills/group-sim")
from chat_sim import GroupSimulator, GroupConfig, SILENT

cfg = GroupConfig(
    topics=["基金", "ETF", "行情"],
    bot_name="小月",
    max_chars=180,
    max_rounds_per_topic=6,
    cooldown=60,
    daily_quota=40,
    allowed_groups=["123456789"],   # 建议填，别留空
)
sim = GroupSimulator(cfg, "/home/saber/.hermes/state/group_sim_123456789.json")

# 每条群消息先 observe
sim.observe(msg, group_id="123456789")

# 需要 LLM 出稿时，先问"该不该说"（省 token）
pre = sim.decide(msg, "", group_id="123456789")
if not pre.speak:
    return   # 别调 LLM

# 出稿后再决策一次（拿分句结果）
d = sim.decide(msg, llm_reply, group_id="123456789")
if d.speak:
    for m in d.messages:
        send(m)
```

命令行自测：

```sh
python3 ~/.hermes/skills/group-sim/chat_sim.py \
  --message "@小月 ETF今天怎么样" \
  --reply "医疗ETF今天跌了不少，可以先别急着加仓" \
  --group 123456789 --topics "基金,ETF,行情" \
  --state ~/.hermes/state/group_sim_123456789.json
```

## Decision 返回

```json
{"speak": true, "reason": "speak", "state": "active",
 "text": "...", "messages": ["...", "..."]}
```

`reason` 取值：`speak` / `closing` / `below_threshold` / `low_relevance` / `cooldown` /
`daily_quota_exhausted` / `max_rounds_reached` / `withdrawn` / `group_not_allowed` / `blocked_by_safety` / `empty_reply`

## 与上游的差异

- 上游是「桥接 + 运行时」两层，本模块是**纯决策层**，由 Hermes 自己调 LLM、自己发消息
- 上游的 `reserved` 模式靠 LLM 输出 `[SILENT]` 表示潜水；本模块在**决策层**就拦掉，不需要浪费一次 LLM 调用
- 上游的额度/白名单/SSRF 防护在传输层；本模块把额度与白名单放在决策层，语义相同但更早生效
- 上游有黑话词库、表情包 CDN、引用解析；这些属于传输层能力，Hermes 侧可另行实现

## 已知局限

- 状态是 per-instance 的，需要调用方按群号各自 new 一个实例并给独立 state 文件
- 概率门槛用了 `random`，测试时可能不稳定；用 `--force-state` 或 `state=` 参数可固定
- 没有做「别人回复我之后」的连续对话追踪，轮次计数按话题近似
