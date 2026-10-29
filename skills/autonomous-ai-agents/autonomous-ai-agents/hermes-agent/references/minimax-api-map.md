# MiniMax API — Full Capability Map for Hermes

## Provider Configuration

| Env var | Base URL | Auth | Purpose |
|---------|----------|------|---------|
| `MINIMAX_API_KEY` | `https://api.minimax.io/v1` | Bearer | Global API |
| `MINIMAX_CN_API_KEY` | `https://api.minimaxi.com/v1` | Bearer | China API |
| `MINIMAX_BASE_URL` | (set in `.env`) | — | Override base URL |

Config in `~/.hermes/config.yaml`:
```yaml
model:
  default: minimax/MiniMax-M2.7
providers:
  minimax:
    api_key_env: MINIMAX_API_KEY
fallback_providers:
  - minimax-cn
```

## API Endpoints & Hermes Integration Status

### Text (Anthropic-compatible)
- **Endpoint:** `POST /v1/messages`
- **Base URL:** `https://api.minimax.io/anthropic/v1` (global), `https://api.minimaxi.com/anthropic/v1` (CN)
- **Hermes status:** ✅ Primary model (`MiniMax-M2.7`, `MiniMax-M2.5`, etc.)
- **Context:** 204,800 tokens
- **Thinking:** Manual `thinking: {type: "enabled", budget_tokens}` — supported
- **Beta headers stripped:** `fine-grained-tool-streaming`, `context-1m` — not sent to MiniMax Bearer endpoints

### TTS — Text-to-Speech
- **Global endpoint:** `https://api.minimax.io/v1/t2a_v2` — ❌ Returns `2049 invalid api key` with both key types
- **CN endpoint:** `https://api.minimaxi.com/v1/t2a_v2` — ✅ Works with CN key (`MINIMAX_CN_API_KEY`)
- **Code default (tts_tool.py:141):** `DEFAULT_MINIMAX_BASE_URL` — **was wrong, patched to CN endpoint**
- **Model:** `speech-02-hd` (2061 tokens/min, always used regardless of config), `speech-2.8-hd` (configurable but endpoint seems to fall back)
- **Max text:** 10,000 chars per request
- **Hermes status:** ✅ Built-in (`tools/tts_tool.py` provider `minimax`)
- **Config keys:** `voice_id`, `speed` (0.5–2.0, tested 0.8–1.5 ✅), `vol`, `pitch` (±5 ✅), `model`, `sample_rate`, `bitrate`, `format`, `channel`
- **Output formats:** MP3 (default), WAV, FLAC, OGG
- **Supported sample rates:** 16000, 24000, 32000, 44100 Hz — **48000 NOT supported**
- **API key fallback:** TTS tries `MINIMAX_API_KEY` first (global), falls back to `MINIMAX_CN_API_KEY`
- **Available voice IDs (verified):**
  - `English_Graceful_Lady` — English female, clear and elegant ✅
  - `male-qn-qingse` — Chinese male voice ✅
  - `female-tianmei` — Chinese female voice ✅
- **Parameters verified working:** speed 0.8/1.5 ✅, pitch ±5 ✅, vol 0.5 ✅, sample rates 44100/32000/24000 ✅, WAV format ✅

### Voice Clone
- **Endpoint:** `POST /v1/voice_clone`
- **Files:** Source audio (mp3/m4a/wav, 10s–5min, ≤20MB) + optional prompt audio
- **Hermes status:** ❌ Not integrated — requires file upload flow
- **Use case:** Clone user's voice for TTS output

### Long TTS Async
- **Endpoint:** `POST /v1/t2a_async` + `GET /v1/t2a_async/query`
- **For:** Text > 10,000 chars (up to 1 hour audio)
- **Hermes status:** ❌ Not integrated

### Voice Design
- **Endpoint:** `POST /v1/voice_design`
- **For:** Generate new synthetic voices from text prompts
- **Hermes status:** ❌ Not integrated

### Video — Text to Video
- **Endpoint:** `POST /v1/video_generation`
- **Models:** `video-01`, `video-01-live2d`
- **Hermes status:** ❌ Not integrated

### Video — Image to Video
- **Endpoint:** `POST /v1/image_to_video`
- **Hermes status:** ❌ Not integrated

### Image Generation
- **Endpoint:** `POST /v1/image_generation`
- **Model:** `image-01`
- **Hermes status:** ❌ Not integrated

### Music Generation
- **Endpoint:** `POST /v1/music_generation`
- **Hermes status:** ❌ Not integrated
- **Related skill:** `heartmula` for Suno-style music prompts

### Embeddings / Rerank
- **Endpoints:** `POST /v1/embeddings`, `POST /v1/rerank`
- **Hermes status:** ❌ Not integrated — would enable local RAG

### MCP Server
- **URL:** `https://api.minimax.io/mcp` (global) or `https://api.minimaxi.com/mcp` (CN)
- **Tools:** Web search, general-purpose tool use
- **Hermes status:** ✅ MCP `minimax` server auto-discovered and registered
- **Tool names:** `mcp_minimax_web_search`, `mcp_minimax_*`

## Key Files

| File | Purpose |
|------|---------|
| `agent/anthropic_adapter.py` | Beta header stripping, max_tokens, Bearer-auth detection |
| `agent/auxiliary_client.py` | Provider fallback chain (MiniMax = #6 for text, #5 for vision) |
| `agent/model_metadata.py` | `DEFAULT_CONTEXT_LENGTHS["minimax"] = 204800` |
| `tools/tts_tool.py` | MiniMax TTS implementation |
| `tools/mcp_tool.py` | MiniMax MCP server registration |

## Adding Missing Integrations

To add Voice Clone, Long TTS Async, Video, or Image APIs as Hermes tools:

1. Create new tool file under `tools/` (e.g. `tools/minimax_video_tool.py`)
2. Use `requests` library for file uploads (`multipart/form-data`)
3. Follow the pattern in `tools/tts_tool.py` — `registry.register()` with `check_fn` and env var check
4. Add to `toolsets.py` or rely on auto-discovery
5. For async endpoints (video, long TTS): implement polling loop with status check

Base URL for new tools:
```python
BASE_URL = "https://api.minimax.io/v1"  # or from config
```
