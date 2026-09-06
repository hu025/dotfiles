---
name: mem0-integration
description: 轻量级向量记忆层：SQLite+TF-IDF替代Mem0重型依赖，5分钟安装，add_memory/search_memory/get_all，同步现有MEMORY.md
---

# Mem0-Integration 技能

## 架构

| 组件 | 方案 | 说明 |
|------|------|------|
| 向量库 | SQLite + TF-IDF | 无需 GPU/CUDA，~50MB |
| 嵌入 | sklearn TfidfVectorizer | 512 特征，1-2 gram |
| 相似度 | Cosine Similarity | 阈值 0.05 |
| 持久化 | JSON + NumPy | 向量存在 .npy 文件 |

## 核心函数

```python
# 添加记忆
add_memory(content: str, tags: str = "", source: str = "manual") -> dict

# 搜索记忆
search_memory(query: str, top_k: int = 5) -> list[dict]

# 获取全部
get_all_memories(limit: int = 50) -> list[dict]
```

## 文件路径

- 脚本：`~/.hermes/self-improvement/mem0_manager.py`
- 数据库：`~/.hermes/self-improvement/memory_mem0.db`
- 向量索引：`~/.hermes/self-improvement/memory_vectorizer.npy`

## 双写策略

现有架构（fact_store + MEMORY.md）保留，新增向量层做语义搜索：

1. `add_memory()` → 同时写 SQLite 向量库
2. `search_memory()` → 语义搜索向量库
3. fact_store → 精确事实查询（不变）
4. MEMORY.md → 结构化长期事实（不变）

## 安装依赖

```bash
uv pip install scikit-learn scipy numpy
```

无 CUDA、无 GPU 需求，CPU 即可运行。
