# MiniMax 快速调用模板

## 先决条件：key 必须从 shell 展开，不能用 Python 读 .env

`terminal` 工具的输出会把密钥脱敏成 `***`。**在 Python 里读 `.env` 拿到的是脱敏串**，
拼进 Authorization 头就是废串 —— 表现为 `status_code: 1004 login fail`，
看起来像 key 坏了，其实 key 是好的。

正确做法：写 payload 到文件，用 shell `source` 出 key，key 全程不经过工具输出。

```bash
set -a
. ~/.hermes/.env
set +a
curl -s -X POST https://api.minimax.chat/v1/image_generation \
  -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d @/tmp/payload.json -o /tmp/resp.json -w 'HTTP:%{http_code}\n'
```

验证 key 完整性用长度，不用值：`${#MINIMAX_API_KEY}` 应为 125。

## 图片生成 → 下载 → 发送（已验证可用）

payload 字段用 `aspect_ratio` / `response_format` / `n` / `prompt_optimizer`：

```json
{
  "model": "image-01",
  "prompt": "anime style portrait avatar of a 20 year old girl, short fluffy ash-pink bob hair, bright teal-green eyes, ...",
  "aspect_ratio": "1:1",
  "response_format": "url",
  "n": 1,
  "prompt_optimizer": true
}
```

```bash
# 1) 出图（key 在 shell 内展开）
curl -s -X POST https://api.minimax.chat/v1/image_generation \
  -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d @/tmp/payload.json -o /tmp/resp.json

# 2) 校验 base_resp.status_code（HTTP 200 不代表成功）
python3 -c "
import json; d=json.load(open('/tmp/resp.json'))
assert d.get('base_resp',{}).get('status_code')==0, d.get('base_resp')
print(d['data']['image_urls'][0])"

# 3) 下载（签名链接约 1 小时过期，拿到就下）
curl -sL '<image_url>' -o ~/.hermes/image_cache/<name>.jpg
file ~/.hermes/image_cache/<name>.jpg

# 4) vision_analyze 验收画面是否符合人设，再发给用户
```

`aspect_ratio` 取值：`1:1` / `16:9` / `9:16` / `4:3` / `3:4`。
`prompt_optimizer: true` 会扩写 prompt，风格漂移时关掉它再手动写细。

## Embeddings（embo-01，1536维）
```python
resp = requests.post(
    "https://api.minimax.chat/v1/embeddings",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "embo-01", "texts": ["文本"], "type": "db"},
)
vectors = resp.json()["vectors"]  # list of lists
```

## Function Calling
```python
tools = [
    {"type":"function","function":{
        "name": "get_weather",
        "description": "获取天气",
        "parameters": {"type":"object","properties":{"city":{"type":"string"}}}
    }}
]
resp = requests.post(
    "https://api.minimax.chat/v1/text/chatcompletion_v2",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "MiniMax-Text-01",
        "messages": [{"role":"user","content":"北京天气如何？"}],
        "max_tokens": 100,
        "tools": tools,
    },
)
msg = resp.json()["choices"][0]["message"]
tool_call = msg.get("tool_calls", [{}])[0]
fn = tool_call.get("function", {})
print(fn["name"], fn["arguments"])
```

## Vision（base64）
```python
import base64
img_b64 = base64.b64encode(open("/tmp/image.jpg","rb").read()).decode()
resp = requests.post(
    "https://api.minimax.chat/v1/text/chatcompletion_v2",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "MiniMax-Text-01",
        "messages": [{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}},
            {"type":"text","text":"描述这张图"}
        ]}],
        "max_tokens": 200,
    },
    timeout=30,
)
print(resp.json()["choices"][0]["message"]["content"])
```

## TTS（两条路：MiniMax chat 域 / edge_tts）
### A. MiniMax TTS（chat 域，sk-cp- key 直接可用，实测 200）

用 shell 展开 key（Python 读 .env 只会拿到脱敏串）：

```bash
set -a
. ~/.hermes/.env
set +a
curl -s -X POST https://api.minimax.chat/v1/t2a_v2 \
  -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"model":"speech-02-hd","text":"小月在测试语音。","stream":false,
       "voice_setting":{"voice_id":"female-shaonv","speed":1.0,"vol":1.0,"pitch":0,"emotion":"neutral"},
       "audio_setting":{"sample_rate":32000,"bitrate":128000}}' \
  -o /tmp/tts_resp.json
```

```python
import json
d = json.load(open("/tmp/tts_resp.json"))
assert d.get("base_resp", {}).get("status_code") == 0, d.get("base_resp")  # 200 不代表成功
# data.audio 是 hex 字符串，不是 base64
audio = bytes.fromhex(d["data"]["audio"])
open("/tmp/output.mp3", "wb").write(audio)
print(f"Saved {len(audio)} bytes")
```
### B. edge_tts（零依赖备选，必须用 hermes venv 解释器）
```python
import asyncio
from edge_tts import Communicate

async def tts(text, out_path="/tmp/tts.mp3", voice="zh-CN-XiaoxiaoNeural"):
    tts = Communicate(text, voice=voice)
    await tts.save(out_path)

asyncio.run(tts("你好世界", "/tmp/test.mp3"))
# 运行：~/.hermes/hermes-agent/.venv/bin/python your_script.py
# 系统 python 调 edge_tts 会 HTTP 400
# Hermes: text_to_speech 工具读 tts.provider 配置（edge / minimax 均可）
```

## Streaming
```python
import json
r = requests.post(
    "https://api.minimax.chat/v1/text/chatcompletion_v2",
    headers={"Authorization": f"Bearer {key}"},
    json={"model":"MiniMax-Text-01","messages":[{"role":"user","content":"数到5"}],"max_tokens":50,"stream":True},
    stream=True,
)
for line in r.iter_lines():
    if line:
        line = line.decode("utf-8")
        if line.startswith("data: "):
            chunk = json.loads(line[6:])
            delta = chunk.get("choices",[{}])[0].get("delta",{}).get("content","")
            if delta:
                print(delta, end="", flush=True)
```
