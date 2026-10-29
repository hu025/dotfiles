# NVIDIA API Key 测试与配置（2026-05-15）

## API Key 格式
NVIDIA NIM API Key 格式：`nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 测试端点

**正确端点**（返回模型目录，HTTP 200）：
```
GET https://integrate.api.nvidia.com/v1/models
Authorization: Bearer <nvapi-KEY>
```

**错误端点**（返回 HTML 404 或 403）：
- `https://api.ngc.nvidia.com/v2/org/-/models` → 403 Forbidden
- `https://catalog.ngc.nvidia.com/api/v1/models` → HTML 404

## 验证流程

```bash
# 测试 key 是否有效
curl -s -H "Authorization: Bearer nvapi-YOUR_KEY" \
  "https://integrate.api.nvidia.com/v1/models" \
  -w "\n%{http_code}" | tail -3
# 200 = 有效，其他 = 无效/权限不足
```

## config.yaml 配置格式

```yaml
providers:
  nvidia:
    provider: custom
    api_key: nvapi-YOUR_KEY
    base_url: https://integrate.api.nvidia.com/v1
    models:
    - id: meta/llama-3.3-70b-instruct
      name: Llama 3.3 70B
      context_window: 131072
    - id: nvidia/llama-3.1-nemotron-70b-instruct
      name: Nemotron 70B
      context_window: 131072
    - id: mistralai/mistral-large-3-675b-instruct-2512
      name: Mistral Large 3
      context_window: 131072
    enabled: true
```

> 注意：`provider: custom` 而非 `provider: nvidia`。`base_url` 必须精确到 `/v1`。

## 已知可用模型（2026-05-15）

| 模型 ID | 名称 |
|---------|------|
| `meta/llama-3.3-70b-instruct` | Llama 3.3 70B |
| `nvidia/llama-3.1-nemotron-70b-instruct` | Nemotron 70B |
| `mistralai/mistral-large-3-675b-instruct-2512` | Mistral Large 3 |
| `nvidia/llama-3.1-nemotron-340b-instruct` | Nemotron 340B |

> 模型目录可能随时变化，以 `GET /v1/models` 返回的实时列表为准。
