---
name: osworld-benchmarks
description: OSWorld 2026-09 SOTA 数据：GPT-6 Astra 72.6% / Claude Opus 5 68.3% / MiniMax M3 22.3% (性价比SOTA $258/任务)
---

# OSWorld 基准测试 (2026-09 数据)

## OSWorld 2.0 (108 长程任务, 1.6小时/任务, 平均318步)

### SOTA 排名 (partial score)
| 排名 | 模型 | 二进制 | 部分完成 | 成本 |
|------|------|--------|---------|------|
| 1 | GPT-6 Astra (OpenAI) | - | **72.6%** | n/a |
| 2 | Claude Opus 5 (Anthropic) | 31.43% | 68.31% | n/a |
| 3 | Muse Spark 1.3 (Meta) | - | 66.9% | n/a |
| 4 | GPT-5.6 Sol (OpenAI) | 27.34% | 62.72% | n/a |
| ... | ... | ... | ... | ... |
| 19 | **MiniMax M3** | 4.6% | **22.3%** | **$258** |

**关键观察**：
- M3 22.3% partial, 4.6% binary, $258/任务
- Claude Opus 5 68.3% partial, $2.4K/任务
- **M3 性价比 SOTA**: 9x 便宜 vs Claude

### 长程任务的核心能力
- State tracking（多步状态保持）
- Cross-source reasoning（跨应用推理）
- Visual-spatial precision（视觉空间精度）
- Dynamic interaction（动态交互）
- Verification（结果验证）

## OSWorld-Verified (369 短任务, 30步/任务)

### SOTA 排名
| 排名 | 模型 | 通过率 | 公司 |
|------|------|--------|------|
| 1 | Qwen3.8 Max | 86.1% | Alibaba |
| 2 | Claude Fable 5 | 85% | Anthropic |
| 2 | Claude Mythos 5 | 85% | Anthropic |
| 4 | Qwen3.8-27B | 84.3% | Alibaba |
| 5 | Claude Opus 4.8 | 83.4% | Anthropic |
| 6 | Gemini 3.6 Flash | 83% | Google |
| 7 | Holo3-35B-A3B | 82.6% | H Company |
| 8 | Claude Sonnet 5 | 81.2% | Anthropic |
| 9 | Muse Spark 1.1 | 80.8% | Meta |
| ... | ... | ... | ... |
| 21 | **MiniMax M3** | **70.1%** | MiniMax |

## Hermes 部署策略

| 任务类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 短任务 (<30步) | M3 (本地/云) | 70.1% OSWorld-V, 性价比最优 |
| 长程 (>250步) | Claude Opus 5 / GPT-6 | partial >60%，多步推理强 |
| 极致质量 | Mythos 5 / Opus 5 | 短任务 85%+ |
| 成本敏感 | M3 (默认) | $258 vs $2.4K = 9x |

## 升级路径

```
当前: MiniMax M3 (70.1% OSWorld-V, 22.3% OSWorld 2.0)
↓
备选 1: Claude Sonnet 5 (81.2%, +16%)
↓
备选 2: Mythos 5 (85.0%, +21%)
↓
极限: GPT-6 Astra (72.6% OSWorld 2.0 partial, 长程SOTA)
```

## 数据来源
- https://leaderboard.steel.dev/leaderboards/osworld-2/
- https://benchlm.ai/benchmarks/osworld-verified
- https://snorkel.ai/leaderboard/os-world-2-0/
- 更新日期: 2026-09-04
