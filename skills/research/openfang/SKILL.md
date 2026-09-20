# OpenFang — Agent Operating System (Rust)

## Meta
- **Type**: Agent OS / Autonomous Runtime
- **Language**: Rust (137K LOC, MIT)
- **Stars**: 18.2k GitHub
- **License**: MIT + Apache-2.0
- **Latest**: v0.6.9 (May 2026)
- **Links**: https://github.com/RightNow-AI/openfang | https://openfang.sh

## Core Architecture

OpenFang is a full **Agent Operating System**, not a chatbot framework or Python wrapper. It compiles to a single ~32MB binary with zero external runtime dependencies.

### 14 Crates
```
kernel/        # Core agent runtime + scheduler
hands/         # 7 autonomous Hands (pre-built agents)
memory/        # SQLite + vector embeddings + knowledge graphs
channel/       # 40 channel adapters
tools/         # 38 built-in tools + MCP client/server
security/      # 16 security systems
agents/        # 30 pre-built agents (4 performance tiers)
workflow/      # Multi-agent pipelines
```

## Key Differentiators

### 1. Autonomous Hands (vs OpenClaw/Hermes)
7 pre-built Hands that run on **schedules**, build **knowledge graphs**, and report to dashboard — no user prompt required:

| Hand | Capability | Notes |
|------|-----------|-------|
| Clip | Video-to-shorts converter | 8-phase FFmpeg + yt-dlp pipeline |
| Lead | Daily lead generation | ICP scoring 0-100, CSV/JSON/MD export |
| Collector | OSINT monitoring | Sentiment tracking + change detection |
| Predictor | Superforecasting | Brier score calibration + contrarian mode |
| Researcher | CRAAP fact-checking | Multi-language + APA citations |
| Twitter | X account management | 7 content formats + approval queue |
| Browser | Web automation | Playwright + CAPTCHA detection + purchase gate |

### 2. 16 Security Systems (vs OpenClaw 3 / ZeroClaw 6)
- WASM dual-metered sandbox (execution isolation + resource metering)
- Ed25519 manifest signing (agent integrity)
- Merkle hash-chain audit trail (tamper-evident logs)
- Taint tracking (data lineage)
- SSRP protection, secret zeroization, HMAC-SHA256 mutual auth
- GCRA rate limiter, subprocess isolation, prompt injection scanner

### 3. 40 Channel Adapters (vs OpenClaw 8 / ZeroClaw 15)
Telegram, Discord, Slack, WhatsApp, Teams, IRC, Matrix, WeCom, 33+ more.
Cross-channel canonical sessions.

### 4. Performance Benchmarks
| Metric | OpenFang | OpenClaw | ZeroClaw |
|--------|----------|----------|----------|
| Cold start | 180ms | 5,980ms | 10ms |
| Idle memory | 40MB | 394MB | 5MB |
| Install size | 32MB | 500MB | 8.8MB |

### 5. Three-Way Comparison (vs Hermes Agent + OpenClaw)
| Dimension | OpenFang | Hermes Agent | OpenClaw |
|-----------|-----------|--------------|----------|
| Language | Rust | Python | TypeScript |
| Stars | 18.2k | ~199k | 381k |
| Core model | OS-first | Learning loop | Gateway-first |
| Security layers | 16 | ? | 3 |
| Idle memory | 40MB | 15-25MB | 394MB |
| Memory | SQLite+vec | Structured memory | External |
| Audit trail | Merkle chain | ? | Logs |
| Desktop app | Tauri 2.0 | None | None |
| Hands | 7 built-in | Skills system | Skills marketplace |

## Hermes Relevance

### What's New vs Hermes
- **Hands概念**: Pre-packaged autonomous agents that run on schedules — similar to Hermes cron but self-contained
- **16 security layers**: WASM sandbox + Merkle audit trail — strongest security model in the space
- **Knowledge graph built-in**: Agents automatically construct KG from execution history
- **Merkle audit trail**: Tamper-evident execution logging beyond Hermes event system
- **Tauri desktop app**: Hermes lacks native desktop UI, OpenFang ships one

### What Hermes Does Better
- Learning loop (memory across sessions)
- Skill marketplace ecosystem (13k+ skills)
- Daily token processing leadership (458B/day vs OpenFang's much smaller user base)
- 20+ messaging channels (vs OpenFang's different channel set)

### Potential Integration Points
1. **WASM sandbox pattern** → Hermes tool isolation enhancement
2. **Merkle audit trail** → Hermes event log tamper-evidence
3. **Knowledge graph built-in** → Hermes memory system enrichment
4. **Hands CLI** → `openfang hand activate researcher` pattern for Hermes autonomous workflows

## Installation
```bash
curl -fsSL https://openfang.sh/install | sh
openfang --version  # v0.6.9

# Or via cargo
cargo install openfang
```

## Key Commands
```bash
openfang hand list           # List 7 available Hands
openfang hand activate researcher <goal>
openfang hand status <hand>
openfang hand pause <hand>
openfang hand resume <hand>

# Agent management
openfang agent list
openfang agent spawn --template <name>

# Channels
openfang channel add telegram --token <token>
```

## Docs
- https://openfang.sh/docs/getting-started
- https://openfang.sh/docs/architecture (14-crate Rust workspace)
- https://openfang.sh/docs/security (16 security systems)
- https://openfang.sh/docs/hands (Hands system)

## Status
Pre-1.0 (v0.6.9). Pin to specific commit for production. v1.0 target mid-2026.
