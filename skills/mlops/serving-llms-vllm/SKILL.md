---
name: serving-llms-vllm
description: vLLM 高吞吐量LLM推理引擎。v0.28+ DFlash2/DSpark/MiniMax-H3支持，PagedAttention+Continuous Batching，OpenAI兼容API，多硬件支持。
trigger: vLLM.*推理|LLM.*部署|serving.*engine|inference.*optim|推理引擎.*选型
version: 1.0.0
author: hermes-auto
created: 2026-09-16
tags: [mlops, inference, llm, vllm, serving, production]
---

# vLLM 高吞吐量 LLM 推理引擎

## 核心定位

vLLM = **通用生产级 LLM 推理引擎**，Apache 2.0，87k+ GitHub stars，2000+ 贡献者。

**2026 最新版本：v0.28.0**（Jul 2026）
- DFlash2：local convolution + candidate selector，speculative decoding 新一代draft
- DSpark：confidence-scheduled verification，异步调度 auto-enabled for draft models
- Model Runner V2：v0.25+ 默认，Python端调度→ZMQ进程分离，高并发下调度开销大幅降低
- v0.25.1（Jul 2026 latest stable）

## 核心技术

### PagedAttention（vLLM 核心创新）
- KV cache 按固定大小页管理（类似OS虚拟内存），消除60-80%内存碎片
- 按需分配/释放，无需为每个序列预分配最大长度
- 与 Continuous Batching 配合：高并发下GPU持续饱和

### v1 架构（v0.25+）
- 统一 token 流：prompt tokens 和 generated tokens 统一表示
- 无 prefill/decode 严格区分，统一调度
- chunked prefill、prefix caching、speculative decoding 全部无缝支持

### Automatic Prefix Caching
- 识别并复用跨请求的相同KV cache块
- **页面级粒度**（vs SGLang的radix tree）
- 适用于：system prompt、tool definitions 重复发送的场景

### Speculative Decoding（v0.28+ 新特性）
- DFlash2：本地卷积draft head，支持MiniMax-H3等MoE模型
- DSpark：置信度调度验证，减少无效draft
- async scheduling auto-enabled for draft models

### 量化支持
- FP8, INT4, AWQ, GPTQ, GGUF（llama.cpp生态）
- multimodal + MoE 全面支持

### 硬件支持（最宽）
- NVIDIA（主要）
- AMD ROCm
- Google TPU
- Intel Gaudi / Ascend

## 选型决策树

```
你的场景：
├── prefix reuse 高（>20%）+ agentic + multi-turn
│   └── → SGLang（RadixAttention 显著优势）
├── 需要最强吞吐量（batch离线任务）
│   └── → TensorRT-LLM（编译后比vLLM高8-13%）
├── 混合流量 + 模型种类多 + 需要多硬件支持
│   └── → vLLM（默认首选）
└── bursty流量 + 不想管理GPU
    └── → 托管端点（DeepInfra等）
```

**实测参考（H100 80GB, Llama 3.3 70B FP8, 50并发）**：
| 引擎 | 吞吐量 | TTFT p50 | 备注 |
|------|--------|----------|------|
| TensorRT-LLM | ~2,700 tok/s | ~800ms | 编译后最高 |
| SGLang | ~1,920 tok/s | ~500ms | prefix reuse高时最优 |
| vLLM | ~1,850 tok/s | ~740ms | 通用场景首选 |

## 快速启动

```bash
# 安装（pip最简路径）
pip install vllm

# 启动推理服务（单命令，零编译）
vllm serve Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 2 \
  --max-model-len 32768 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.85 \
  --port 8000

# 或 HuggingFace 直接
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --tensor-parallel-size 2
```

### Python API

```python
from vllm import LLM, SamplingParam

llm = LLM(
    model="Qwen/Qwen2.5-72B-Instruct",
    tensor_parallel_size=2,
    enable_prefix_caching=True,
    gpu_memory_utilization=0.85,
)

outputs = llm.generate(["What is the capital of France?"])
print(outputs[0].outputs[0].text)
```

### OpenAI 兼容 API

```bash
# 服务自动暴露 /v1/chat/completions, /v1/completions
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2.5-72B-Instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 512
  }'
```

## 性能优化参数

### KV Cache 与 Prefix Caching
```python
LLM(
    enable_prefix_caching=True,  # 启用自动前缀缓存
    gpu_memory_utilization=0.9,  # GPU显存用于KV cache的比例
    max_model_len=131072,         # 最大序列长度
)
```

### Continuous Batching（默认启用）
```python
LLM(
    enforce_eager=False,  # 默认False，用CUDA graph加速
    block_size=16,         # PagedAttention块大小（tokens/块）
)
```

### 多GPU张量并行
```bash
# 2卡
--tensor-parallel-size 2
# 4卡
--tensor-parallel-size 4
# 8卡（多节点）
--tensor-parallel-size 8
```

### Speculative Decoding（v0.28+）
```python
llm = LLM(
    model="...",
    speculative_model="ibm-granite/granite-3.0-2b-instruct",  # draft model
    num_speculative_tokens=5,   # 每次draft的token数
    spec_dec_acceptance_rate=0.3, # 接受率阈值
)
```

## vLLM vs SGLang 深度对比

| 维度 | vLLM | SGLang |
|------|------|--------|
| 核心机制 | PagedAttention | RadixAttention |
| KV cache粒度 | 页面级（固定块） | Radix树（前缀感知） |
| 调度 | Model Runner V2（进程分离） | CPU调度与GPU计算重叠 |
| 前缀复用 | 自动+页面级 | 自动+树结构+请求调度优化 |
| 结构化输出 | guided decoding | xgrammar（更优） |
| 模型覆盖 | 最广（首批支持新架构） | 较广（Grok/DeepSeek优化） |
| 硬件 | NVIDIA+AMD+TPU+Gaudi+Ascend | NVIDIA+AMD+TPU+Ascend |
| 冷启动 | ~62s（无需编译） | ~60s（无需编译） |
| 适用场景 | 通用API服务、batch任务、多模型 | agentic、多轮对话、RAG（prefix重） |

**SGLang 优势场景**（选SGLang）：
- Multi-turn对话，大量重复system prompt
- Coding agent：每步发送相同工具定义+文件上下文（可>80% prefix reuse）
- Few-shot RAG：共享系统提示+少量RAG context
- 结构化JSON输出（JSON Schema enforcement）

**vLLM 优势场景**（选vLLM）：
- 50+模型混跑，需要快速切换
- AMD/TPU/Gaudi 非NVIDIA硬件
- batch离线任务（summarization、embedding backfill）
- 团队没有SGLang专家，不想学SGLang DSL

## 最佳实践

1. **先测量 prefix reuse**：用 streaming client 发送同一 preamble 两次，测 TTFT 差异
2. **GPU 利用率 0.85 起跳**：0.95+ 易 OOM，低并发设 0.8
3. **prefix caching 始终开启**：对有重复的系统prompt工作负载几乎无损
4. **张量并行 > 数据并行**：多卡场景优先 TP 而非 DP
5. **speculative decoding 适合低QPS**：中等流量下TTFT可减半

## 常见问题

**Q: vLLM 和 SGLang 可以混用吗？**
A: 可以。常见模式：Router 前置，根据请求特征路由到不同引擎。

**Q: vLLM 支持 GGUF 吗？**
A: 有限支持，主要为 llama.cpp 生态设计。推荐 HuggingFace safetensors 格式。

**Q: 冷启动太慢？**
A: 预热后保持运行；或使用 vLLM 的 `--gpu-memory-utilization` 和 `--max-num-seqs` 预分配。

## 来源

- https://deepinfra.com/blog/vllm-vs-sglang（2026-08-04，v0.25.1 vs v0.5.15对比）
- https://www.spheron.network/blog/llm-inference-optimization-2026（决策框架）
- https://atomic.chat/blog/llm-updates/sglang-vs-vllm（2026，全面对比）
- https://github.com/vllm-project/vllm/releases（v0.28.0 changelog）
- https://docs.vllm.ai/en/latest（官方文档）
