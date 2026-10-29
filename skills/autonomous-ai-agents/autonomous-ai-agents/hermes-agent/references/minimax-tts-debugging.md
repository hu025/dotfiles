# MiniMax TTS — Configuration Session Notes (2026-04-26)

## Critical Finding: Endpoint Confusion

**MiniMax has TWO separate API infrastructures that do NOT互通:**

| Base URL | Used for | TTS works? |
|----------|----------|------------|
| `https://api.minimax.io/v1` | Global API (text, embeddings, etc.) | ❌ TTS returns `2049 invalid api key` |
| `https://api.minimaxi.com/v1` | China API | ✅ TTS works |

**Root cause:** `tts_tool.py` had `DEFAULT_MINIMAX_BASE_URL = "https://api.minimax.io/v1/t2a_v2"` hardcoded. This endpoint does NOT support TTS. The correct endpoint is `https://api.minimaxi.com/v1/t2a_v2`.

**File patched:** `hermes-agent/tools/tts_tool.py` line 141 — `DEFAULT_MINIMAX_BASE_URL` changed to CN endpoint.

## Verification Commands

```python
# Test global endpoint (FAILS)
import requests
headers = {"Authorization": f"Bearer {cn_key}"}
data = {"model": "speech-02-hd", "text": "test", "voice_id": "English_Graceful_Lady"}
requests.post("https://api.minimax.io/v1/t2a_v2", json=data, headers=headers)
# → 2049 invalid api key

# Test CN endpoint (WORKS)
requests.post("https://api.minimaxi.com/v1/t2a_v2", json=data, headers=headers)
# → 200, returns MP3 audio
```

## Verified Working Configuration

**config.yaml:**
```yaml
tts:
  provider: minimax
  minimax:
    model: speech-2.8-hd
    voice_id: English_Graceful_Lady
    speed: 1.0
    vol: 1.0
    pitch: 0
    sample_rate: 44100    # 44.1kHz — does NOT support 48000
    bitrate: 128000
    format: mp3
    channel: 1
    base_url: https://api.minimaxi.com/v1/t2a_v2
```

## Tested Voice IDs

| voice_id | Language | Status | Notes |
|----------|----------|--------|-------|
| `English_Graceful_Lady` | English F | ✅ | Default, clear elegant |
| `male-qn-qingse` | Chinese M | ✅ | |
| `female-tianmei` | Chinese F | ✅ | |

## Tested Parameters

| Parameter | Range tested | Status |
|-----------|---------------|--------|
| `speed` | 0.8, 1.0, 1.5 | ✅ |
| `pitch` | -5, 0, +5 | ✅ |
| `vol` | 0.5, 1.0 | ✅ |
| `sample_rate` | 16000, 24000, 32000, 44100 | ✅ |
| `sample_rate` | 48000 | ❌ NOT supported |
| `format` | mp3, wav | ✅ |

## Voice Clone — CN Endpoint Returns 404

```bash
# Voice Clone endpoint test
curl -X POST "https://api.minimaxi.com/v1/voice_clone" \
  -H "Authorization: Bearer $MINIMAX_CN_API_KEY" \
  -F "audio=@sample.mp3"
# → 404 Not Found

# Voice Management endpoint test
curl "https://api.minimaxi.com/v1/voice_management/get" \
  -H "Authorization: Bearer $MINIMAX_CN_API_KEY"
# → 404 Not Found
```

**Hypothesis:** Voice Clone may require a `GroupId` parameter or different endpoint path for CN API. Not yet resolved.

## Code Changes Made

1. **`tts_tool.py:141`** — `DEFAULT_MINIMAX_BASE_URL` patched to `https://api.minimaxi.com/v1/t2a_v2`
2. **`tts_tool.py:943-978`** (`_generate_minimax_tts`):
   - API key: tries `MINIMAX_API_KEY` first, falls back to `MINIMAX_CN_API_KEY`
   - `sample_rate`: reads from config (was hardcoded 32000)
   - `bitrate`: reads from config
   - `channel`: reads from config
   - `audio_setting` block: uses config variables instead of hardcoded values
3. **`config.yaml`**: `tts.provider: edge` → `tts.provider: minimax` + full minimax config block
