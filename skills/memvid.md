---
description: Memvid — 单文件记忆层。Rust核心，16.5k stars，append-only Smart Frames时序记忆，时间旅行调试，sub-5ms检索，无数据库无服务器。触发词：memvid/便携记忆/离线记忆/单文件记忆
trigger: memvid|便携记忆|离线记忆|单文件记忆|embedded memory|serverless memory
updated: 2026-09-16
---

# Memvid — 单文件AI记忆层

## 核心定位

**替代复杂RAG管道和服务器向量数据库**，用单个`.mv2`文件提供持久化、可版本控制、可移植的记忆。

- Stars: **16.5k**（2026-07）
- License: **Apache 2.0**
- 核心语言: **Rust**
- GitHub: https://github.com/memvid/memvid

## 核心概念

### Smart Frames（智能帧）
受视频编码启发，每个Frame是**不可变单元**，存储内容+时间戳+校验和+元数据。
- Append-only写入，不会修改或损坏已有数据
- 可查询历史记忆状态
- 时间线风格检视知识演化
- 崩溃安全（已提交immutable frames）

### .mv2 格式（Memory Capsule）
自包含、可分享的记忆胶囊，含规则和过期时间。
- 可以`scp`/`git commit`/邮件发送
- 在不同agent间共享
- 单文件 = 整个记忆状态

## 关键特性

| 特性 | 说明 |
|------|------|
| Living Memory Engine | 跨session持续追加、分支、演化记忆 |
| Capsule Context | 可分享的`.mv2`记忆胶囊，含规则和过期 |
| Time-Travel Debugging | 回滚、重放、分支任意记忆状态 |
| Smart Recall | Sub-5ms本地记忆访问+预测缓存 |
| Frame-level ACL | 帧级访问控制 |
| Portable | 一个文件走天下，无数据库依赖 |

## 功能模块（Feature Flags）

```toml
memvid-core = "2.0"

# 按需启用
lex           # BM25全文搜索(Tantivy)
vec           # 向量相似搜索(HNSW + 本地ONNX嵌入)
temporal_track # 时序追踪
pdf_extract   # 纯Rust PDF文本提取
clip          # CLIP视觉嵌入（图搜图）
whisper       # Whisper音频转录
api_embed     # OpenAI云端嵌入
```

## 性能基准

- 检索延迟: **< 5ms**（P50）
- 吞吐量: **1,372×** 高于标准RAG
- LoCoMo得分: **+35%** 优于行业平均
- 嵌入式存储: **无服务器** 零运维

## 与Mem0/Supermemory对比

| 维度 | Memvid | Mem0 | Supermemory |
|------|--------|------|-------------|
| 存储形态 | 单文件`.mv2` | 云服务/SaaS | 云服务/SaaS |
| 部署 | 无服务器 | 需配置 | 需Cloudflare |
| 便携性 | **极高** | 低 | 低 |
| 离线支持 | **完全离线** | 需API | 需网络 |
| 向量搜索 | HNSW+本地ONNX | 云嵌入 | 云嵌入 |
| 时序记忆 | ✅ Smart Frames | ✅ 多信号 | ✅ 图记忆 |
| 适用场景 | **边缘/离线/便携Agent** | 企业托管 | 企业托管 |

## 使用场景

- **边缘/离线Agent**: 嵌入式设备、无网络环境
- **便携记忆**: git commit记忆文件、跨机器携带
- **隐私敏感**: 数据不出本地
- **跨Agent共享**: 分享`.mv2`文件而非数据库访问
- **Claude Code记忆**: `memvid/claude-brain` — 一个`.mv2`文件给Claude Code照片级记忆

## 快速开始

```python
# Python SDK
from memvid import Memvid

# 创建记忆文件
mem = Memvid.create("knowledge.mv2")

# 添加记忆
mem.add("用户偏好Python而非JavaScript", metadata={"pref": "python"})

# 语义搜索
results = mem.search("编程语言偏好")
```

```rust
// Rust SDK
use memvid_core::{Memvid, PutOptions, SearchRequest};

let mut mem = Memvid::create("knowledge.mv2")?;
mem.add("context here", &PutOptions::default())?;
let results = mem.search("query", &SearchRequest::default())?;
```

## Claude Brain（重点关注）

`memvid/claude-brain` — 给Claude Code零数据库记忆：
- 一个`.mv2`文件替代SQLite/ChromaDB
- 可git commit、scp、分享
- Rust核心，sub-ms操作
- 完美契合Hermes coding agent场景

## 落地建议

**适合Hermes场景**:
1. **coding agent记忆**: `claude-brain`模式，git式记忆管理
2. **跨session便携**: 单一`.mv2`文件，Hermes dotfiles直接管理
3. **隐私/离线**: 完全本地，无外部依赖

**安装**:
```bash
# Rust (推荐)
cargo add memvid-core
# 或预编译安装脚本
curl -fsSL https://get.memvid.com | sh

# Python
pip install memvid
```

## 来源

- https://github.com/memvid/memvid
- https://www.memvid.com
- https://blog.devgenius.io/ai-agent-memory-systems-in-2026
