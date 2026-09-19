# FluctlightDB — Brain-Native Agent Memory Engine

## 核心定位

**第三数据模型**：Relational ≠ Vector ≠ Brain-native。FluctlightDB 提出 agent 记忆作为独立数据模型，有自己的写入语义（encoding / separation / consolidation / provenance）和读取语义（cue-driven activation across linked memory graph）。

## 核心概念

| 概念 | 角色 |
|------|------|
| **Engram** | 记忆单元：content + context + salience + provenance + edges |
| **experience()** | 写入：分离 → 编码 → 索引 → 连线共激活边 |
| **activate(cue)** | 读取：lexical + semantic seed → graph spread → fusion → trust boost |
| **Consolidation** | 离线重放压缩（checkpoint()），类睡眠记忆整合 |

## 性能数据

- **LongMemEval-S**: 97.6% session_recall@8 (488/500), E2E QA 97.4%
- **LoCoMo evidence recall**: 96.8% (MiniLM-384), 97.0% (mpnet-768)
- **BEIR SciFact**: nDCG@10 0.646 vs Chroma 0.645，Recall@10 0.792 vs 0.783
- **Provenance conflict**: shared-brain 18% top-1 vs isolated 100%（n=50）

## 双模式

| 模式 | 适用场景 | 行为 |
|------|---------|------|
| **Episodic** | Live agent，会话记忆 | 完整 graph wiring，dentate separation 近重复过滤 |
| **Fast Ingest** | 批量导入，向量索引 | 跳过 graph wiring，O(1) 插入 |

## API 快速上手

```python
from fluctlightdb import connect_embedded

brain = connect_embedded("/tmp/my-agent-brain")
brain.turn_begin()
brain.experience(
    content="用户偏好中文回复",
    context={"task": "coding", "project": "hermes"},
    salience=0.9,
    provenance="verified",  # verified > unverified > chat
)
result = brain.activate("用户喜欢什么语言")
```

## Provenance 信任系统

- **verified**: 文档/代码 > 官方来源
- **unverified**: 一般陈述
- **chat**: 最低优先级

来源验证的信息在 recall 时压制未验证的 chat 说法。

## 存储格式

- 每个 agent brain = 一个目录（类似 SQLite）
- `manifest.json` + 12 个命名段（`*.seg`）
- WAL 追加（64 MiB 轮转）
- 原子 rename 保证不 torn write
- `connect_index()` 模式可附加 FTS5 + HNSW sidecar

## 安装

```bash
pip install "fluctlightdb[native]>=0.5.21"  # Linux/macOS/Windows x64+arm64
```

## 与现有技能的关系

- 与 agentmemory (95.2% R@5) 互补：FluctlightDB 更底层（engine），强调 provenance 和 graph
- 与 OpenViking L0/L1/L2 类似：FluctlightDB 的 L0/L1 由 consolidate 自动生成
- 可作为 Hermes 记忆系统的底层引擎候选

## 落地建议

**优先级：观察**。8 GitHub stars，较新项目（2026-07 论文）。存储模型和 provenance 设计有长期价值，生产落地需等生态成熟。

## 来源

- Paper: https://arxiv.org/abs/2608.12365
- GitHub: https://github.com/voxmastery/FluctlightDB
- PyPI: https://pypi.org/project/fluctlightdb/
- DOI: https://doi.org/10.5281/zenodo.20949890
