---
name: mem0-integration
description: 轻量级向量记忆层（SQLite+TF-IDF），零成本；官方Mem0(需OpenAI key)作为升级路径。add_memory/search_memory/get_all，同步现有MEMORY.md
triggers:
  - 记忆系统
  - 向量搜索
  - 语义记忆
  - mem0升级
---

# Mem0-Integration 技能

## 架构：两级记忆

### L1 — 现有方案（零成本，立即可用）
| 组件 | 方案 | 说明 |
|------|------|------|
| 向量库 | SQLite + TF-IDF | 无GPU/CUDA，~50MB |
| 嵌入 | sklearn TfidfVectorizer | 512特征，1-2 gram |
| 相似度 | Cosine Similarity | 阈值0.05 |
| 持久化 | JSON + NumPy | 向量存.npy |

### L2 — 官方Mem0（需OpenAI API key，升级路径）
| 组件 | 方案 | 说明 |
|------|------|------|
| 嵌入 | OpenAI text-embedding-3-small | $0.02/1M tokens |
| 记忆层级 | User+Session+Agent三层 | 自编辑去重 |
| 检索 | 向量+图谱混合 | 92.5%准确率 |

## 核心函数（L1当前方案）

```python
# 添加记忆（同时写SQLite向量库）
add_memory(content: str, tags: str = "", source: str = "manual") -> dict

# 语义搜索
search_memory(query: str, top_k: int = 5) -> list[dict]

# 获取全部
get_all_memories(limit: int = 50) -> list[dict]
```

## 文件路径
- 脚本：`~/.hermes/self-improvement/mem0_manager.py`
- 数据库：`~/.hermes/self-improvement/memory_mem0.db`
- 向量索引：`~/.hermes/self-improvement/memory_vectorizer.npy`

## 升级到官方Mem0（OPENAI_API_KEY可用时）

```bash
uv pip install mem0ai
```

```python
from mem0 import Memory

client = Memory(api_key="your-openai-key")
client.add("用户偏好: 中文极简风格")
results = client.search("用户喜欢什么风格?")
```

## 双写策略
1. `add_memory()` → 同时写 SQLite 向量库（L1）
2. `search_memory()` → 语义搜索向量库（L1）
3. fact_store → 精确事实查询（不变）
4. MEMORY.md → 结构化长期事实（不变）

## 安装依赖
```bash
uv pip install scikit-learn scipy numpy
```
