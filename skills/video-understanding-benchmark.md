---
name: video-understanding-benchmark
description: 视频理解 benchmark 全景：LVBench/LongVideoBench/VBench 对比，选型决策树。触发词：视频benchmark/长视频理解/LVBench
---

# 视频理解 Benchmark 全景 2026

## 三大主流 Benchmark

### 1. LVBench（Zhipu AI, 2025 IEEE ICCV）
- **论文**: arxiv:2406.08035, IEEE ICCV 2025
- **特点**: 平均视频时长 4101 秒（约 68 分钟），是现有 benchmark 的 4 倍
- **规模**: 公开来源长视频 + 多样化问答任务
- **核心能力**: 6 大时间理解能力（感知/关系/推理/记忆/检索/推理）
- **关键洞察**: 当前 MLLM 在长视频理解仍显著落后，专有模型（GPT-4o/Gemini）优于开源模型
- **维护**: 半年更新一次，GitHub + Hugging Face

### 2. LongVideoBench（Salesforce, NeurIPS 2024）
- **论文**: arxiv:2407.15754, NeurIPS 2024 Poster
- **特点**: 6,678 道人类标注多选题，17 个细粒度分类，1 小时字幕视频
- **创新**: "referring reasoning" 范式 — 问题含引用查询（referred context），测试跨帧检索+推理
- **关键洞察**: 
  - 专有模型随帧数增加性能提升，开源模型无法 scale
  - 最佳专有模型仍需更多帧处理才能提升
- **作者**: Haoning Wu, Dongxu Li, Bei Chen, Junnan Li
- **维护**: 半年更新，GitHub + HuggingFace

### 3. VBench（上海 AI Lab/交大/港中文, 2023）
- **聚焦**: 视频**生成**质量评估（非理解）
- **维度**: 16 个维度（主体一致性/运动平滑/时序闪烁/空间关系等）
- **适用**: 视频生成模型评估

## 选型决策树

```
需求类型?
├── 评估视频生成质量 → VBench
├── 长视频理解能力评估
│   ├── 超长视频（>1小时），需时间推理 → LVBench（平均68分钟）
│   └── 中等长度（分钟级），需跨帧引用推理 → LongVideoBench（referring reasoning）
└── 对话式视频理解 → YouComm/QCAV-1K
```

## 核心发现

1. **长上下文是瓶颈**: LVBench 和 LongVideoBench 均揭示当前开源 LMM 无法 scale 到长视频
2. **referring reasoning 范式**: 新任务类型，要求模型精确定位+推理
3. **帧数 vs 质量权衡**: 专有模型随帧数增加提升，开源模型受限于 context window
4. **评估指标**: 多为多选题（MCQ），降低标注成本，提高可比性

## 来源

- LVBench: https://arxiv.org/html/2406.08035v3
- LongVideoBench: https://arxiv.org/html/2407.15754
- VBench: https://arxiv.org/abs/2311.17982
