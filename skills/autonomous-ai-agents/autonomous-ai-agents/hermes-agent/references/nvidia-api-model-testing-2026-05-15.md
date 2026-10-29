# NVIDIA API 模型测试记录

## ⚠️ 关键发现（2026-05-22 更新）

**NVIDIA API 完全公开，无需 API Key。**

- 端点：`https://integrate.api.nvidia.com/v1`
- 无需 Authorization header 即可访问目录：`curl https://integrate.api.nvidia.com/v1/models`
- chat/completions 端点同样无需 key 即可调用（免费额度限流）
- 模型总数：**123 个**（2026-05-22）

## 模型目录（2026-05-22，123个）

完整列表见 `models/nvidia-all-123.md`。

主要分类：

| 分类 | 代表模型 |
|------|---------|
| Llama | `meta/llama-3.3-70b-instruct`, `meta/llama-3.1-70b-instruct` |
| Llama Vision | `meta/llama-3.2-90b-vision-instruct`, `meta/llama-3.2-11b-vision-instruct` |
| Gemma | `google/gemma-3-12b-it`, `google/gemma-4-31b-it` |
| Mistral | `mistralai/mistral-large-3-675b-instruct`, `mistralai/mixtral-8x22b-v0.1` |
| DeepSeek | `deepseek-ai/deepseek-v4-pro`, `deepseek-ai/deepseek-v4-flash` |
| Qwen | `qwen/qwen3.5-397b-a17b`, `qwen/qwen3.5-122b-a10b` |
| NVIDIA Nemotron | `nvidia/nemotron-4-340b-instruct`, `nvidia/nemotron-4-340b-reward` |
| NVIDIA 安全 | `nvidia/llama-3.1-nemoguard-8b-content-safety` |
| NVIDIA 嵌入 | `nvidia/nv-embed-v1`, `nvidia/llama-nemotron-embed-1b-v2` |

## 实测可用模型（2026-05-15，28个，供参考）

> 以下为 2026-05-15 测试结果。部分大模型在免费额度下有超时限制。

| 模型ID | 分类 | 备注 |
|--------|------|------|
| `meta/llama-3.3-70b-instruct` | 通用 | 主力 |
| `meta/llama-3.1-70b-instruct` | 通用 | 备选旗舰 |
| `mistralai/mistral-medium-3.5-128b` | 通用 | 128K上下文 |
| `meta/llama-4-maverick-17b-128e-instruct` | 通用 | 轻量快速 |
| `nvidia/nemotron-3-super-120b-a12b` | 通用 | 120B MoE |
| `mistralai/mixtral-8x22b-v0.1` | MoE | 主力MoE |
| `mistralai/mixtral-8x7b-instruct-v0.1` | MoE | 轻量MoE |
| `mistralai/mistral-small-4-119b-2603` | MoE | 快速MoE |
| `nvidia/llama-3.3-nemotron-super-49b-v1` | MoE | NVIDIA优化 |
| `mistralai/ministral-14b-instruct-2512` | 中量 | |
| `upstage/solar-10.7b-instruct` | 中量 | |
| `meta/llama-3.1-8b-instruct` | 中量 | |
| `qwen/qwen3-coder-480b-a35b-instruct` | 代码 | ~35s超慢 |
| `meta/llama-3.2-90b-vision-instruct` | 视觉 | |
| `meta/llama-3.2-11b-vision-instruct` | 视觉 | |
| `meta/llama-3.2-3b-instruct` | 小模型 | |
| `meta/llama-3.2-1b-instruct` | 小模型 | |
| `google/gemma-2-2b-it` | 小模型 | |
| `nvidia/nvidia-nemotron-nano-9b-v2` | 小模型 | |
| `meta/llama-guard-4-12b` | 安全 | |
| `nvidia/llama-3.1-nemoguard-8b-content-safety` | 安全 | |

## 已知不可用（供参考）

- **代码系**: `bigcode/starcoder2-*` / `google/codegemma-*` / `mistralai/codestral-*` — 404
- **Embedding**: `nvidia/nv-embed-*` / `snowflake/arctic-embed-*` — 专用端点，非 chat 接口
- **大模型超时**: `nvidia/nemotron-4-340b-*` / `qwen/qwen3.5-122b-a10b` — 免费额度限流

## USB Hermes 配置

U盘 Hermes 路径：`/mnt/usb/hermes-agent/config.yaml`

```yaml
providers:
  nvidia:
    api_key: NONE
    base_url: https://integrate.api.nvidia.com/v1
    enabled: true
    models:
      # 123 models (完整列表见 models/nvidia-all-123.md)
```
