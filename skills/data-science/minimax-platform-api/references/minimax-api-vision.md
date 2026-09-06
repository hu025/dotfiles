# MiniMax API Vision Limitation

> Absorbed from archived skill `minimax-api-vision` (2026-05-13 consolidation pass).
> Original trigger: `MiniMax image analysis | minimax vision | minimax 图片分析`

## Finding (2026-04-25)

Despite **MiniMax-M2.7** being described as a multimodal model, the MiniMax CN API (`api.minimaxi.com/anthropic/v1/messages`) does **NOT** support image input via base64.

### What Was Tried

Sending a message with `content: [{type: "image", data: "<base64>", media_type: "image/jpeg"}]` resulted in the API returning:
> "我注意到您想让我描述一张图片，但我没有看到任何图片附加在您的消息中"

The API processed only the text portion and ignored the image data entirely. `usage.input_tokens` was only 25, far too low for a base64-encoded 150KB image — confirming the image was never parsed.

### Implication

MiniMax's API endpoint is **text-only** for practical purposes. The model may have vision capabilities internally but the API does not expose them.

## Key Auth Distinction for Image Generation

| Key | Used for | Works for image_generation? |
|-----|---------|---------------------------|
| `MINIMAX_API_KEY` (ANTHROPIC key) | Text chat only | ❌ No |
| `MINIMAX_CN_API_KEY` | Image generation | ✅ Yes |

> ⚠️ The older `MINIMAX_API_KEY` (ANTHROPIC key) does **NOT** work for image generation — only `MINIMAX_CN_API_KEY` works.

## Workarounds for Vision Tasks

1. **Browser-based vision** — Install Chromium and use `browser_vision` tool
2. **Dedicated vision API** — Use OpenAI's GPT-4o Vision, Google Gemini Vision, or similar
3. **Local vision model** — Deploy a local VLM (LLaVA, CogVLM, etc.)

## Chromium Installation on Arch Linux (when needed)

```bash
# Remove pacman lock if present
sudo rm -f /var/lib/pacman/db.lck

# Install playwright (system python, no venv)
pip install playwright --break-system-packages

# Download Chromium (run in background — takes several minutes)
/usr/bin/python3 -m playwright install chromium
```

**Important**: `pacman -S chromium` times out on this system; `playwright install chromium` is the working path but runs in background with `notify_on_complete=true`.
