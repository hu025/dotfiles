# SiliconFlow 免费模型参考 (2026-05)

## 状态

API key `sk-hwp...vluw` 已失效（HTTP 401），无法实时查询。需重新从控制台获取。

## 已知免费/低成本模型（来自网页快照）

| 模型 ID | 类型 | 输入 | 输出 | 备注 |
|--------|------|------|------|------|
| `deepseek-ai/DeepSeek-V3` | 对话 | ￥1/M | ￥2/M | 免费额度可用 |
| `deepseek-ai/DeepSeek-V3.2` | 对话 | ￥2/M | ￥3/M | 新版 |
| `deepseek-ai/DeepSeek-V3.1-Terminus` | 对话 | ￥4/M | ￥12/M | |
| `Qwen/Qwen2.5-7B-Instruct` | 对话 | ~开源免费 | ~开源免费 | 开源模型，SF 托管 |
| `THUDM/GLM-4-9B-Chat` | 对话 | ~开源免费 | ~开源免费 | 开源模型 |
| `mistralai/Mistral-7B-Instruct-v0.3` | 对话 | ~开源免费 | ~开源免费 | 开源模型 |
| `baichuan-inc/Baichuan2-7B-Chat` | 对话 | ~开源免费 | ~开源免费 | 开源模型 |

## 推荐的免费最强 5 个（待验证）

1. `deepseek-ai/DeepSeek-V3` — 旗舰全能，￥1/M 输入
2. `Qwen/Qwen2.5-7B-Instruct` — 开源免费
3. `THUDM/GLM-4-9B-Chat` — 开源免费
4. `mistralai/Mistral-7B-Instruct-v0.3` — 开源免费
5. `baichuan-inc/Baichuan2-7B-Chat` — 开源免费

## 验证命令（key 恢复后）

```bash
KEY="your-real-key"
for model in "deepseek-ai/DeepSeek-V3" "Qwen/Qwen2.5-7B-Instruct" "THUDM/GLM-4-9B-Chat"; do
  result=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.siliconflow.cn/v1/chat/completions" \
    -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":5}")
  echo "$model: HTTP $result"
done
```

## SiliconFlow API 端点

- 基础: `https://api.siliconflow.cn/v1`
- 模型列表: `GET /v1/models`（需要有效 key）
- 对话: `POST /v1/chat/completions`

## 获取新 API Key

1. 登录 https://www.siliconflow.cn
2. 控制台 → API Keys → 创建新 key
3. 更新 `~/.hermes/config.yaml` 中 `providers.siliconflow.api_key`（直接编辑，不通过 `hermes config set`）
