---
name: mem0-integration
description: Mem0 长期记忆层与 Hermes 集成。使用向量语义记忆补充结构化 MEMORY.md，适合对话上下文沉淀、偏好学习、跨会话状态跟踪。触发词：记忆、记得、搜索记忆。
trigger: 记忆 记得 搜索记忆 mem0
category: agent-engineering
---

# Mem0 长期记忆层集成

## 概述

Mem0 是 AI Agent 的长期记忆层，提供语义向量搜索能力。与 Hermes 的关系：

| 维度 | MEMORY.md | Mem0 |
|------|-----------|------|
| 类型 | 结构化事实（YAML） | 向量语义记忆 |
| 格式 | 键值对、分类 | 自然语言段落 |
| 用途 | 系统配置、凭证、偏好 | 对话上下文、临时状态 |
| 持久化 | 手动/双写 | 自动向量存储 |
| 搜索 | 精确匹配 | 语义相似度 |

两者**互补**，MEMORY.md 存结构化事实，Mem0 存对话中自然产生的上下文。

## 安装

```bash
# mem0ai 已通过 uv 安装在 hermes-agent venv 中
# 如需重新安装：
cd /home/saber && uv pip install mem0ai

# 本地 embedding 模型（可选，免费）
uv pip install sentence-transformers
```

## 配置方案

### 方案 A：免费本地 Embedding（推荐）

使用 HuggingFace 本地模型 `all-MiniLM-L6-v2`（384维，无 API key）：

```python
from mem0 import Memory

config = {
    "vector_store": {"provider": "qdrant", "config": {"host": "localhost", "port": 6333}},
    "embedder": {"provider": "huggingface", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
    "llm": {"provider": "ollama", "config": {"model": "qwen2.5", "ollama_base_url": "http://localhost:11434"}},
}
m = Memory.from_config(config)
```

### 方案 B：OpenAI（需 API Key）

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from mem0 import Memory
m = Memory()  # 默认使用 OpenAI gpt-5-mini + text-embedding-3-small
```

### 方案 C：Ollama 本地 LLM + 本地 Embedding

```python
config = {
    "vector_store": {"provider": "qdrant", "config": {"host": "localhost", "port": 6333}},
    "embedder": {"provider": "huggingface", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}},
    "llm": {"provider": "ollama", "config": {"model": "qwen2.5", "ollama_base_url": "http://localhost:11434"}},
}
m = Memory.from_config(config)
```

## 与 Hermes 集成

### 核心接口（mem0_manager.py）

```python
from mem0_manager import add_memory, search_memory, sync_from_memories

# 添加记忆（自动双写到 MEMORY.md）
add_memory("用户喜欢高弹性 ETF", user_id="hermes", metadata={"source": "conversation"})

# 语义搜索记忆
results = search_memory("用户偏好什么", user_id="hermes")
# [{'id': 'mem_xxx', 'memory': '用户喜欢高弹性 ETF', 'score': 0.89, ...}]

# 从 MEMORY.md 同步到 Mem0
sync_from_memories()
```

### 双写策略

`add_memory()` 同时：
1. 调用 `m.add()` 存入 Mem0 向量库
2. 追加到 `~/.hermes/memories/MEMORY.md`

`sync_from_memories()` 从 MEMORY.md 读取结构化事实，转换为向量记忆存入 Mem0。

## 使用场景

| 场景 | 方法 |
|------|------|
| 记住用户偏好 | `add_memory("用户喜欢...", user_id="hermes")` |
| 跨会话恢复上下文 | `search_memory("上次讨论的", user_id="hermes")` |
| ETF 策略学习 | `add_memory("用户选择512880，成本低弹性高", user_id="hermes")` |
| 同步 MEMORY.md | `sync_from_memories()` |

## Qdrant 启动（如使用向量存储）

```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

数据默认存在 `/tmp/qdrant`（内存模式）。

## 验证

```python
from mem0_manager import add_memory, search_memory

add_memory("测试记忆：用户今天学习了 ETF 策略", user_id="hermes")
results = search_memory("用户学了什么", user_id="hermes")
print(results[0]['memory'])  # 应输出相关记忆
```

## 注意事项

1. **API Key**：优先使用本地模型（Ollama + HuggingFace）避免 API 费用
2. **向量维度**：all-MiniLM-L6-v2 输出 384 维，与 Mem0 默认兼容
3. **Qdrant**：如不使用 docker，可改用 Chroma（纯 Python，无需服务）
4. **同步**：定期执行 `sync_from_memories()` 保持两边一致
