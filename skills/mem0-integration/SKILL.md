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

## 召回后角色校准（重要，2026-10-25 加入）

`search_memory()` 目前是「相关性排序 → 直接塞进上下文」，**没有一层判断这条记忆该不该影响当前答案**。MemSyco-Bench 的实证：Mem0/A-Mem/LightMem 上 **61–62% 的错误发生在记忆已被正确召回之后**——瓶颈在 post-retrieval 决策，不在检索。

在召回路径**上游**加一层轻量分类（正则起手，成本近零），给注入的记忆定一个角色：

| query 类型 | 记忆角色 | 处理 |
|-----------|---------|------|
| 客观事实题（`^(what\|when\|who\|where\|which\|how many\|how much)` 且无 should/compare/analyze 等主观词） | **不是证据** | 注入时附加"用户偏好是背景不是证据"提示 |
| 明确的记忆检索（remember / remind / my favorite / my deadline） | **个性化信号** | 直接注入，信任个性化 |
| 主观/个性化题 | **偏好** | 注入并标注"此为用户偏好" |

另需给记忆条目加元信息 `role` / `scope` / `updated_at` / `supersedes`，否则模型没有做「新旧偏好仲裁」和「作用域判断」的信号。

**完整方法、四个指标、正则模板、三个可移植过滤模块**：见 `research/memsyco-memory-calibration` 技能。

## 安装依赖
```bash
uv pip install scikit-learn scipy numpy
```
