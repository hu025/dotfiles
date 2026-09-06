# MiniMax Music Generation — Implementation Reference

## Overview

MiniMax music-2.6 API converts text prompts to MP3 audio. It was integrated into Hermes Agent on 2026-05-15.

**Key constraint**: ¥49/month plan supports 100 generations/day. Generation takes 30-60 seconds.

## Files Created

| File | Purpose |
|------|---------|
| `tools/music_generation_tool.py` | Tool module — schema, registry, handler |
| `plugins/music_gen/minimax/__init__.py` | Backend — API call, hex→MP3 decode, cache |
| `toolsets.py` | Added `music` toolset (1 tool: `music_generation`) |
| `config.yaml` | Added `music_gen.minimax.model: music-2.6` |

## API Details

**Endpoint**: `POST https://api.minimaxi.com/v1/music_generation`

**Request**:
```json
{
  "model": "music-2.6",
  "prompt": "peaceful piano in C major",
  "lyrics": "la la la"
}
```

**Response** (success):
```json
{
  "data": {
    "audio": "<hex string of MP3 bytes>"
  }
}
```

**Response** (failure):
```json
{"base_resp": {"status_msg": "invalid params", "status_code": 2013}}
```

## Known Issues

- **`invalid params`**: usually means `model` field is missing or the API key doesn't support this endpoint. Verify the key is `MINIMAX_API_KEY` (CN key, not the ANTHROPIC global key). Test with the older API key format if `MINIMAX_CN_API_KEY` is available.
- **Timeout**: Set `timeout=120` in the requests call. Generation takes 30-60s.
- **Empty `audio` field**: API returned success but no audio data — try again or check if the key has exhausted daily quota.

## Testing

```python
import sys
sys.path.insert(0, "/home/saber/.hermes/hermes-agent")
from plugins.music_gen.minimax import _generate
result = _generate(prompt="peaceful piano", lyrics="la la la")
print(result)  # {'audio_path': '/home/saber/.hermes/cache/music/minimax_music_xxx.mp3', 'model': 'music-2.6'}
```

## Return Format

The tool returns `MEDIA:/path/to/file.mp3` — the `MEDIA:` prefix tells the platform to deliver the file as native audio to WeChat/QQ.