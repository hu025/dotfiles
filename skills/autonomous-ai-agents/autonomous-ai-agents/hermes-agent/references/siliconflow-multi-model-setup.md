# SiliconFlow 多模型配置参考（2026-05-14）

## ⚠️ API Key 失效排障（优先级第一）

**症状**：所有 SiliconFlow API 调用返回 HTTP 401 `{"error":"Invalid token"}`

**确认方法**：
```bash
curl -s "https://api.siliconflow.cn/v1/models" \
  -H "Authorization: Bearer $(grep siliconflow ~/.hermes/config.yaml | grep api_key | awk '{print $2}')"
# 输出 {"error":"Invalid token"} → key 过期或被撤销
```

**解决**：去 https://www.siliconflow.cn/ 登录 → API Key 管理 → 重新生成，替换 `~/.hermes/config.yaml` 中 `providers.siliconflow.api_key` 或 `~/.hermes/.env` 中的对应值。

**在确认 API Key 有效之前，不要尝试测试任何模型。**

---

## 调查免费模型的标准流程

**第一步：确认 Key 有效**（上面完成）

**第二步：列出所有模型 + 价格**
```bash
curl -s "https://api.siliconflow.cn/v1/models" \
  -H "Authorization: Bearer YOUR_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
free_models = []
paid_models = []
for m in data.get('data', []):
    p = m.get('pricing', {})
    ppi = float(p.get('prompt_price_per_1k_tokens', 1))
    cpi = float(p.get('completion_price_per_1k_tokens', 1))
    ctx = m.get('context_window', 0)
    entry = f'{m[\"id\"]} | ctx={ctx} | prompt={ppi} compl={cpi}'
    if ppi == 0.0 and cpi == 0.0:
        free_models.append(entry)
    else:
        paid_models.append(entry)
print('=== FREE ===')
for x in free_models: print(x)
print('=== PAID ===')
for x in paid_models[:20]: print(x)
"
```

**第三步：如果 Key 无效，从网站 UI 获取免费模型信息**
- 访问 https://www.siliconflow.cn/model
- 使用筛选条件或搜索"免费"
- 记录：模型 ID、context_window、价格（¥/M Tokens）

---

## 已知的免费/便宜模型（2026-05-14，基于网站 UI 实时价格）

| 模型 ID | 价格 (¥/M Tokens) | Context | 备注 |
|---------|-------------------|---------|------|
| `deepseek-ai/DeepSeek-V4-Flash` | 输入¥1 / 输出¥2 | 128k | 最新 DeepSeek |
| `deepseek-ai/DeepSeek-V3.2` | 输入¥2 / 输出¥3 | 128k | 便宜大杯 |
| `Qwen/Qwen3-14B` | 输入¥1.6 / 输出¥? | 32k | 开源强模型 |
| `Qwen/Qwen3.6-35B-A3B` | 输入¥1.6 / 输出¥? | 128k | 长上下文 |
| `THUDM/GLM-4.1` | 价格待查 | - | 智谱 |

> **注意**：以上价格来自网站 UI，随时可能变化。用 `curl /v1/models` 获取实时列表最准确。

---

## 模型配置检查命令

```bash
# 检查 providers 中的模型列表
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/saber/.hermes/config.yaml'))
providers = cfg.get('providers', {})
for name, p in providers.items():
    models = p.get('models', [])
    print(f'{name}: {len(models)} models')
    for m in models:
        mid = m.get('id') if isinstance(m, dict) else m
        ctx = m.get('context_window') if isinstance(m, dict) else ''
        print(f'  {mid} (ctx:{ctx})')
"

# 检查 delegation 当前使用的 model 是否在 providers 中存在
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/saber/.hermes/config.yaml'))
delegation = cfg.get('delegation', {})
d_model = delegation.get('model','')
d_provider = delegation.get('provider','')
providers = cfg.get('providers', {})
if d_provider in providers:
    model_ids = [m.get('id') if isinstance(m, dict) else m for m in providers[d_provider].get('models',[])]
    if d_model in model_ids:
        print(f'✅ delegation model {d_provider}/{d_model} exists')
    else:
        print(f'❌ delegation model NOT in provider: {model_ids}')
else:
    print(f'❌ delegation provider {d_provider} not in providers')
"
```

---

## OpenClaw 侧配置格式（对比参考）

```json
{
  "providers": {
    "siliconflow": {
      "CN": true,
      "enabled": true,
      "models": [
        {"id": "deepseek-ai/DeepSeek-V4-Flash", "name": "DeepSeek V4 Flash", "contextWindow": 128000},
        {"id": "deepseek-ai/DeepSeek-V3.2", "name": "DeepSeek V3.2", "contextWindow": 128000},
        {"id": "Qwen/Qwen3-14B", "name": "Qwen3 14B", "contextWindow": 32000},
        {"id": "Qwen/Qwen3.6-35B-A3B", "name": "Qwen3 35B", "contextWindow": 128000}
      ]
    }
  }
}
```

注意：OpenClaw 用 camelCase (`contextWindow`)，Hermes 用 snake_case (`context_window`)。
