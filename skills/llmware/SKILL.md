---
name: llmware
description: 企业级RAG+小型专用模型统一框架，300+模型目录（GGUF/ONNX/OpenVINO），纯本地部署，SLIM/Bling/Dragon专业模型，AI PC优化。触发词：本地RAG/小模型/GGUF/企业知识管理/AI PC
triggers:
  - llmware
  - 本地RAG
  - 小型专用模型
  - GGUF量化
  - 企业知识库
  - AI PC
---

# llmware — 本地优先企业RAG框架

## 核心定位
- **本地+私有**: 优化AI PC和边缘部署，支持Windows/Mac/Linux
- **300+模型目录**: 50+微调专用模型（SLIM/Bling/Dragon/Industry-Bert）
- **GGUF + OpenVINO + ONNX原生**: 硬件NPU/GPU优化
- **GitHub**: 14,860 stars，Apache-2.0

## 两大组件

### 1. Model Catalog（模型目录）
```python
from llmware.models import ModelCatalog

models = ModelCatalog().list_all_models()
my_model = ModelCatalog().load_model("llmware/bling-phi-3-gguf")
output = my_model.inference("what is the future of AI?", add_context="...")
```

### 2. RAG Pipeline（检索增强生成）
```python
from llmware.library import Library
from llmware.retrieval import Query
from llmware.prompts import Prompt

# 创建知识库
lib = Library().create_new_library("my_library")
lib.add_files("/folder/path/to/files")

# 查询
q = Query(lib)
results = q.semantic_query("semantic query", result_count=10)

# 带来源的Prompt
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")
source = prompter.add_source_new_query(lib, query="my query")
responses = prompter.prompt_with_source("my query")
```

## 专业模型系列

| 模型系列 | 用途 | 参数量 |
|---------|------|--------|
| BLING | 通用对话/工具 | 1-7B |
| SLIM | 专用任务（extract/summary/qa）| tiny |
| DRAGON | 企业文档理解 | 7-9B |
| Industry-Bert | 金融/法律/合规 | base |

## 企业级特点

### 文档解析
支持: pdf, pptx, docx, xlsx, txt, csv, md, json/jsonl, wav, png, jpg, html

### 多向量库支持
Milvus / ChromaDB / PGVector / Qdrant / Pinecone

### 混合查询
text + semantic + metadata + custom filters

### LLMfx Agent（函数调用Agent）
```python
from llmware.agents import LLMfx

agent = LLMfx()
```

## 与现有技能差异化
- **vs Haystack**: llmware更偏本地+小型专用模型，Haystack偏云端+灵活管道
- **vs RAG系统**: llmware的300+小模型目录是独特资产
- **Hermes场景**: 本地RAG能力可增强Hermes知识管理

## 安装
```bash
pip install llmware  # 最小安装
# 或
pip install llmware[all]  # 完整安装
```

## 关键优势
1. **纯本地**: 不依赖云API，适合隐私敏感场景
2. **小型专用模型**: 1-7B参数，RAG优化，边缘可运行
3. **多格式文档**: 企业文档全支持
4. **量化支持**: GGUF原生，AI PC NPU优化

## 参考
- https://github.com/llmware-ai/llmware
- https://llmware.ai
