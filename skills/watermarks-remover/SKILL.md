---
name: watermarks-remover
description: Remove AI text watermarks and C2PA/file metadata from Claude/Gemini/OpenAI content. Aug 2026 watermarks-remover v0.6.0 — multi-vendor provenance stripping (Layer A Unicode hygiene + Layer B statistical rewrite + C2PA/EXIF/XMP/metadata). Complements anti-ai-filter (stylistic tells). Use when stripping AI provenance from owned content, cleaning C2PA manifests, or defeating statistical token-sampling watermarks.
---

# watermarks-remover Skill

> Strip multi-vendor AI provenance marks from text and files — for privacy and hygiene on content **you own**.

---

## When to Use This Skill

Trigger phrases: "strip AI watermark", "remove Claude mark", "clean C2PA", "defeat SynthID", "strip provenance"
Trigger phrases: "remove AI text watermark", "clean Gemini watermark", "defeat OpenAI provenance"

**Not for:** image/visual watermarks (PDF stamps, photo watermarks) → use `pdf` skill.

---

## Two Different Problems

"AI watermark removal" bundles two unrelated mechanisms:

| Layer | What It Is | How to Remove | Verifiable? |
|-------|-----------|---------------|-------------|
| **A** — Invisible Unicode | ZWSP, bidi chars, tag chars, exotic spaces hidden in text | Deterministic strip (trivial, always works) | ✅ Yes — bytes either there or not |
| **B** — Statistical Token Watermark | Delibrate bias in which words model chooses, spread across passage | Best-effort rewrite (degrades writing quality) | ❌ No — no public detector with keys |
| **Files** — C2PA / metadata | Signed certificates, EXIF, XMP, doc properties in files | Deterministic strip | ✅ Yes — bytes either there or not |

**Anthropic's own docs confirm:** SynthID-based watermark adds **no hidden characters**. Unicode cleaning does NOT defeat Claude's real statistical watermark.

---

## Layer A — Invisible Unicode Strip (Text, Deterministic)

Works on: Claude, Gemini, OpenAI, any open-LLM.

```bash
SCRIPTS=skills/watermarks-remover/scripts

# Inspect — show every invisible character
python3 "$SCRIPTS/inspect_text.py" draft.md

# Clean — strip all invisible carriers
python3 "$SCRIPTS/clean_text.py" draft.md -o draft.cleaned.md --stats
```

What gets stripped:
- Zero-width space (U+200B), zero-width joiner, variation selectors
- Bidirectional override characters (change display order — security risk)
- Tag characters
- Homoglyph spaces
- Unusual Unicode spaces → replaced with normal space (words never merge)

Preserved: emoji, Persian/Khmer/Korean text, braille content.

---

## Layer B — Statistical Watermark Rewrite (Text, Best-Effort)

> ⚠️ **Important:** This rewrites text substantially. Only use when Layer A is insufficient AND you own the content.

```bash
# Default: print rewrite prompt only (no model required)
python3 "$SCRIPTS/rewrite_text.py" draft.md --backend print-prompt --strength paraphrase

# With local Ollama (loopback only by default)
WATERMARKS_REWRITE_BACKEND=ollama WATERMARKS_REWRITE_MODEL=llama3.2 \
  python3 "$SCRIPTS/rewrite_text.py" draft.md -o draft.rewritten.md

# Remote API (requires explicit flag)
WATERMARKS_REWRITE_ALLOW_REMOTE=1 WATERMARKS_REWRITE_API_KEY=sk-... \
  WATERMARKS_REWRITE_BACKEND=openai WATERMARKS_REWRITE_MODEL=gpt-4o-mini \
  python3 "$SCRIPTS/rewrite_text.py" draft.md -o draft.rewritten.md
```

**Strength levels:** `light` → `paraphrase` → `aggressive`

**Warning:** Removes watermarks by rewriting, not magic erasure. The writing will change. Short passages (<200 words) have weak signal — rewrites barely help. Long passages (>500 words) show more signal, rewrite more effective.

---

## File Layer — C2PA / Metadata Strip (Deterministic, Verifiable)

Supported formats: PNG, JPEG, WebP, AVIF, HEIC, BMP, GIF, TIFF, SVG, PDF, DOCX, XLSX, PPTX, EPUB, ODT, HTML, Markdown, MP4/MOV/M4A/M4V, WAV, MP3, FLAC

```bash
# Inspect C2PA manifest and metadata
python3 "$SCRIPTS/inspect_file.py" photo.png

# Clean all provenance metadata
python3 "$SCRIPTS/clean_file.py" photo.png -o photo.cleaned.png

# Works on PDFs too (uses exiftool if available, stdlib fallback)
python3 "$SCRIPTS/clean_file.py" document.pdf -o document.cleaned.pdf

# Unified: auto-detect format
python3 "$SCRIPTS/clean_file.py" draft.docx -o draft.cleaned.docx
```

What gets stripped: C2PA manifests, EXIF, XMP provenance, IPTC fields, document properties.

Optional tools (auto-used when present):
- `c2patool` — C2PA manifest inspection
- `exiftool` — residual metadata (especially PDF)

---

## Interaction with anti-ai-filter Skill

These two skills are **complementary**, not redundant:

| Skill | Removes | Method |
|-------|---------|--------|
| `anti-ai-filter` | Stylistic AI tells (vocabulary, structure, rhythm) | Pattern replacement, structural rewrite |
| `watermarks-remover` | Invisible Unicode carriers + C2PA/file metadata | Deterministic char strip |
| `watermarks-remover` Layer B | Statistical token watermarks | Best-effort text rewrite |

**Recommended workflow:**
1. Write with AI assistance
2. Run `anti-ai-filter` → fixes vocabulary + structure
3. Run `watermarks-remover Layer A` → strips invisible Unicode
4. For high-stakes content, add Layer B rewrite
5. Verify with AI detector (Phrasly, Originality.ai, ZeroGPT)

---

## Quick Reference

```bash
SCRIPTS=skills/watermarks-remover/scripts

# Text — Layer A (always do this first)
python3 "$SCRIPTS/inspect_text.py" draft.md
python3 "$SCRIPTS/clean_text.py" draft.md -o draft.cleaned.md --stats

# Text — Layer B (only if Layer A insufficient)
python3 "$SCRIPTS/rewrite_text.py" draft.md --backend print-prompt --strength paraphrase
# then apply the rewrite prompt with your preferred model

# Files — C2PA/metadata
python3 "$SCRIPTS/inspect_file.py" photo.png
python3 "$SCRIPTS/clean_file.py" photo.png -o photo.cleaned.png
```

---

## Vendor Coverage

| Vendor | Layer A Unicode | Layer B Statistical | C2PA/Metadata |
|--------|----------------|--------------------|--------------|
| Claude (Aug 2026+) | ✅ | ✅ (best-effort) | ✅ |
| Gemini / SynthID-Text | ✅ | ✅ (best-effort) | ✅ |
| OpenAI provenance | ✅ | ✅ (if present) | ✅ |
| Open-LLM (Kirchenbauer) | ✅ | ✅ (best-effort) | ✅ |
| Images (SynthID pixel) | N/A | External only (aloshdenny/reverse-SynthID) | ✅ |

---

## Sources

- https://github.com/guillaumemeyer/watermarks-remover (MIT, ~940 stars, v0.6.0)
- https://omidsaffari.com/blog/best-ai-text-watermark-detectors-2026
- https://hackernoon.com/it-took-developers-24-hours-to-build-around-claudes-invisible-watermark
