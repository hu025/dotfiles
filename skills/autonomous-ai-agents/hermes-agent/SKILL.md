---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `delegation.model` must exist under `providers.<delegation.provider>.models`: `MiniMax-M2.7` only exists under the `minimax` provider, NOT under `siliconflow`. Setting `delegation.provider: siliconflow` + `delegation.model: MiniMax-M2.7` silently fails. Always verify the model ID exists in the target provider's model list before configuring delegation.

| NVIDIA API | **无需 API Key**。`https://integrate.api.nvidia.com/v1` 完全公开，`api_key: NONE` 即可使用。123个模型，含 Llama/Mistral/Gemma/Qwen 等30+厂商。详见 `references/nvidia-api-model-testing-2026-05-15.md`；**fallback 行为**见 `references/model-fallback-chain-2026-06-10.md`
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `hermes-cli` | Built-in CLI tools (default, always on) |
| `web` | Web search and content extraction |
| `search` | Web search only (subset of `web`) |
| `vision` | Image analysis |
| `image_gen` | AI image generation (MiniMax image-01 available) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `todo` | In-session task planning and tracking |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `browser` | Browser automation (requires camofox + playwright — NOT installed) |
| `moa` | Mixture of Agents (off by default) |
| `rl` | Reinforcement learning tools (off by default) |
| `homeassistant` | Smart home control (off by default) |
| `safe` | Safety/approval tools |
| `debugging` | Debugging helpers |
| `hermes-acp` | VS Code / Zed / JetBrains IDE integration |
| `hermes-api-server` | REST API server |
| `hermes-telegram` | Telegram platform adapter |
| `hermes-discord` | Discord platform adapter |
| `hermes-whatsapp` | WhatsApp platform adapter |
| `hermes-slack` | Slack platform adapter |
| `hermes-signal` | Signal platform adapter |
| `hermes-bluebubbles` | iMessage/BlueBubbles adapter |
| `hermes-email` | Email adapter |
| `hermes-mattermost` | Mattermost adapter |
| `hermes-matrix` | Matrix adapter |
| `hermes-dingtalk` | DingTalk adapter |
| `hermes-feishu` | Feishu/Lark adapter |
| `hermes-weixin` | WeChat/Weixin adapter |
| `hermes-qqbot` | QQ bot adapter |
| `hermes-wecom` | WeCom adapter |
| `hermes-webhook` | Webhook trigger adapter |
| `hermes-gateway` | Gateway management |
| `spotify` | Spotify control |
| `video` | Video generation control |
| `kanban` | Multi-agent kanban board |
| `feishu_doc` | Feishu document access |
| `feishu_drive` | Feishu cloud drive access |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Multilayer Memory Plugin (plugins/memory/multilayer/)

Five-layer memory system installed as a plugin provider (`memory.provider: multilayer`).

### Class Names (important)

Classes are named `*MemoryLayer`, NOT `*Memory`:
```python
from plugins.memory.multilayer.flash import FlashMemoryLayer       # NOT FlashMemory
from plugins.memory.multilayer.semantic import SemanticMemoryLayer # NOT SemanticMemory
from plugins.memory.multilayer.procedural import ProceduralMemoryLayer
from plugins.memory.multilayer.episodic import EpisodicMemoryLayer
from plugins.memory.multilayer.working import WorkingMemoryLayer
```

### Smoke Test (verify all 5 layers)

```python
import sys; sys.path.insert(0, '/home/saber/.hermes/hermes-agent')

from plugins.memory.multilayer.flash import FlashMemoryLayer
from plugins.memory.multilayer.semantic import SemanticMemoryLayer
from plugins.memory.multilayer.procedural import ProceduralMemoryLayer
from plugins.memory.multilayer.episodic import EpisodicMemoryLayer
from plugins.memory.multilayer.working import WorkingMemoryLayer

# Flash — sharp/pinned facts
fm = FlashMemoryLayer()
print('flash:', fm.get_all()[0]['content'])

# Semantic — FTS5 entity search (returns list, not dict)
sm = SemanticMemoryLayer()
sm.add_fact('test entity', category='test', tags='test')
r = sm.search('test')
print('semantic:', r[0]['content'])   # r is list[dict], NOT dict with 'facts' key

# Procedural — skill records
pm = ProceduralMemoryLayer()
pm.record_skill('s1', 'desc', ['t1'], True, 5)
procs = pm.get_procedures()   # NOT get_all_preferences()
print('procedural:', procs[0]['name'])

# Episodic — session timeline
em = EpisodicMemoryLayer()
em.start_episode('s1', 'label', 'session')
em.add_event('s1', 'event', 'detail')
ep = em.get_recent_episodes(1)
print('episodic:', ep[0]['label'])

# Working — deque turns
wm = WorkingMemoryLayer()
wm.record_user('hello')
wm.record_assistant('hi')
ctx = wm.get_context()
print('working:', ctx['recent_turns'][0].user)
```

### Layer API Summary

| Layer | Key methods |
|-------|-------------|
| Flash | `add()`, `get_all()`, `get_sharp()`, `get_pinned()`, `pin()`, `promote()` |
| Semantic | `add_fact()`, `search()` → `list[dict]`, `probe_entity()`, `find_contradictions()` |
| Procedural | `record_skill()`, `record_tool_chain()`, `set_preference()`, `get_procedures()`, `get_all_preferences()` |
| Episodic | `start_episode()`, `add_event()`, `get_recent_episodes()`, `get_session_timeline()` |
| Working | `record_user()`, `record_assistant()`, `record_tool()`, `get_context()`, `reset()` |

### Five-Layer Cascade

`MultilayerProvider.prefetch()` executes top-to-bottom: **flash → semantic → procedural → episodic → working**, merging into a single context injection. `memory.provider: multilayer` in `config.yaml`.

> ⚠️ **Common silent failure**: `initialize()` signature mismatch with `MemoryProvider` base class (missing `session_id` arg) causes complete memory system failure with no crash — only a WARNING in logs. See `references/session-2026-05-12-memory-skills-api.md` for the fix (3-patch: `initialize`, `on_turn_start`, `sync_turn`).

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **off by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) passes through unmodified. If the user wants Hermes to auto-mask strings that look like API keys, tokens, and secrets before they enter the conversation context and logs:

```bash
hermes config set security.redact_secrets true       # enable globally
```

### Gateway Crash Loop

Gateway crash loop: reset the failed state:
```bash
systemctl --user reset-failed hermes-gateway.service
```

**Watchdog for Hermes Gateway (Linux/systemd):**

> See `openclaw-gateway-restart-loop-fix` skill for the full watchdog solution. The authoritative version includes:
> - Separate `hermes-gateway-watchdog.service` (systemd) with `Restart=always`
> - Watchdog script at `~/.hermes/gateway-watchdog.sh`
> - `PartOf=` linkage so intentional gateway stops also stop the watchdog
> - All exit codes caught (including clean exit=0 from QQ Bot disconnect)

### Curator (Self-Evolution)

The curator runs skill hygiene, archive, and stale-detection automatically. It is NOT invoked via `from hermes_cli.curator import Curator`. The correct import from inside the repo is:

```python
from agent import curator
state = curator.load_state()
print('enabled:', curator.is_enabled())   # True/False
print('paused:', curator.is_paused())     # True/False
print('last_run:', state.get('last_run_at'))
print('run_count:', state.get('run_count', 0))

# Trigger a manual run:
result = curator.run_curator_review()
# Returns: {'started_at': ..., 'auto_transitions': {...}, 'summary_so_far': '...'}
```

Config (in `config.yaml`):
```yaml
curator:
  enabled: true
  interval_hours: 168        # run once per week
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
```

### Web Dashboard Build

The dashboard (`hermes dashboard`) requires a pre-built `web_dist/` frontend. After `git pull` or a fresh install, `web_dist/` does not exist and the dashboard will fail silently (HTTP 000 on curl, process exits immediately) with no error shown.

**Correct build sequence (one-time after git pull or npm install):**
```bash
cd ~/.hermes/hermes-agent/web
npm install          # populate node_modules (includes sync-assets postinstall)
npm run build       # vite build — the postinstall script copies fonts/assets automatically
```

Then launch (always from the hermes-agent root, NOT from the `web/` subdirectory):
```bash
cd ~/.hermes/hermes-agent
python3 -m hermes_cli.main dashboard --port 18792 --no-open   # local access (127.0.0.1)
python3 -m hermes_cli.main dashboard --port 18792 --no-open --insecure  # bind 0.0.0.0 (network exposure — NOT recommended)
```

The `npm run build` output shows:
```
../hermes_cli/web_dist/index.html       0.47 kB
../hermes_cli/web_dist/assets/index-*.css  ...
../hermes_cli/web_dist/assets/index-*.js   ...
✓ built in 28.50s
```

**Troubleshooting:**
- Dashboard fails silently (curl 000): `web_dist/` missing → re-run `npm run build` from `web/`
- Process running but port unreachable: check `ss -tlnp | grep python` to confirm the port the process actually bound to
- Port already in use: pick a different port or `pkill -f dashboard` first
- Started from wrong directory (web/ subdirectory instead of hermes-agent root): move to parent directory and restart

**Security note:** Dashboard exposes API keys/config without robust auth. The binary refuses `0.0.0.0` unless `--insecure` is passed. Use `--host 127.0.0.1` (default) for local-only access, or SSH port forward for remote: `ssh -L 18792:127.0.0.1:18792 user@host`.

### Web Dashboard Access

URL: `http://127.0.0.1:9119` (local only by default)

Features: Sessions (875 stored), Analytics, Achievements, Models, Logs, Cron, Skills, Config, Keys, Documentation.

Gateway status shown live: platform connections (Qqbot, Weixin), active sessions count.

### Gateway Watchdog (Linux/systemd)

The gateway can exit cleanly (e.g. QQ Bot disconnect = exit 0). systemd's `Restart=on-failure` only catches non-zero exits, so clean exits don't trigger restart. The fix is a separate watchdog service.

**Files:**
- Watchdog script: `~/.hermes/gateway-watchdog.sh`
- systemd unit: `~/.config/systemd/user/hermes-gateway-watchdog.service`

**Setup (already done on this system):**
```ini
# hermes-gateway-watchdog.service
[Unit]
PartOf=hermes-gateway.service

[Service]
ExecStart=/bin/bash /home/saber/.hermes/gateway-watchdog.sh
Restart=always
RestartSec=5
```

Enable and start:
```bash
systemctl --user daemon-reload
systemctl --user enable hermes-gateway-watchdog.service
systemctl --user start hermes-gateway-watchdog.service
```

The `PartOf=` ensures that stopping `hermes-gateway.service` also stops the watchdog. Any gateway exit (zero or non-zero) triggers the watchdog to restart it within 5 seconds.

### hermes-workspace (Web UI App)

Separate Next.js application at `~/hermes-workspace/`. Provides chat UI + terminal + memory visualization + skills manager.

**⚠️ Must use pnpm — npm will fail:**

```bash
# Check if pnpm is available
which pnpm || npm install -g pnpm

# Install dependencies (background)
terminal(background=true, command="cd ~/hermes-workspace && pnpm install 2>&1 | tail -5")

# Monitor progress
ls ~/hermes-workspace/node_modules/.pnpm/ | wc -l

# Start dev server
cd ~/hermes-workspace && pnpm dev
```

### Upgrade Verification (when git fetch fails)

Network issues (GitHub SSL/SSH timeout) can prevent `git pull` but the system may still be running the newer code. **Use multiple signals to verify actual version:**

```bash
./venv/bin/hermes --version     # ← primary: shows exact running version string
pip show hermes-agent | grep Version   # pip metadata (may differ from git)
grep '^version' pyproject.toml  # source tree version
git log --oneline -1             # git commit (may lag behind working tree)
```

**Common discrepancy pattern**: git is at v0.13.0 commit but `hermes --version` shows v0.14.0 — means the code was updated via pip install or manual copy while git was blocked. The running system IS the new version; trust `hermes --version`.

### GitHub CDN for slow networks

When HTTPS git fetch times out, use the CDN tarball URLs (no auth needed for public repos):

```
# API tarball (redirects to CDN storage):
curl -sL "https://api.github.com/repos/NousResearch/hermes-agent/tarball/v2026.5.16" -o /tmp/hermes.tar.gz

# Direct CDN (most reliable on slow connections):
curl -sL "https://codeload.github.com/NousResearch/hermes-agent/tar.gz/v2026.5.16" -o /tmp/hermes.tar.gz
```

Expected size: ~14.6MB for hermes-agent v0.14. Verify with `tar -tzf /tmp/hermes.tar.gz | wc -l` (should show ~2236 entries). If gzip EOF error, the download was incomplete — use `curl -C -` for resumable downloads.

### Git Detached HEAD State

When installed via `git clone` without explicit branch checkout, `~/.hermes/hermes-agent` may be in **detached HEAD** state. This causes `git pull` to fail with "not currently on a branch". Fix:

```bash
cd ~/.hermes/hermes-agent
git checkout main   # or: git checkout <tag>
```

GitHub SSL failures (`SSL_read: unexpected eof while reading`) in slow networks are network/ISP-level, not a git config problem. Use CDN tarball approach above.

### Platform-specific issues

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not appearing after install
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Installing Skills from GitHub Manually

When `hermes skills install` is unavailable or the skill isn't in the hub, install from GitHub tarballs. Full workflow: see `references/github-skill-install-workflow.md` — covers tarball download, repo structure detection (standard/clawhub/monolithic), and installation to `installed/`.

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |
| **Skill references** | `~/.hermes/skills/autonomous-ai-agents/hermes-agent/references/` — session-specific detail, provider configs, API quirks |

## Skill References

- `references/hermes-upgrade-verification-2026-05-16.md` — v0.13→v0.14 升级：hermes --version 版本判断优先顺序、git fetch 失败时确认升级成功的多信号验证方法、网络隔离升级路径（CDN tarball + curl）、v0.14.0 重大更新清单
- `references/hermes-upgrade-workflow-2026-05-16.md` — hermes-agent v0.13→v0.14 upgrade: codeload CDN, SSH auth vs git protocol (git-upload-pack), partial download recovery, verified download URLs, upgrade verification checklist
- `references/version-check-workflow-2026-07-27.md` — 版本检查正确流程：PyPI 可能因 Python 版本兼容性不显示最新版本，需同时查 GitHub API；hermes-agent 0.19.0 vs 0.15.2 实际案例
- `references/github-network-isolation.md` — GitHub network isolation: codeload CDN, SSH vs git protocol, gitconfig url.rewrite trap, PAT tarball auth, upgrade workflow
- `references/siliconflow-multi-model-setup.md` — SiliconFlow 5模型配置、验证命令、API端点、OpenClaw配置对比
- `references/siliconflow-free-models-2026.md` — SiliconFlow 免费模型列表、API Key 脱敏问题修复、验证命令
- `references/nvidia-api-model-testing-2026-05-15.md` — NVIDIA API 128模型全面测试记录：实测可用模型列表、免费额度限制、批量测试方法、当前最优8模型配置
- `references/openclaw-gateway-env-vars-2026-06-07.md` — OpenClaw Gateway 环境变量加载：systemd service 缺少 EnvironmentFile 导致 QQ Bot "Cannot read properties of undefined (reading 'run')" 的诊断与修复
- `references/ssh-port-and-config-set-workflow.md` — SSH 端口迁移（非标准端口→22）、`hermes config set` 是修改 config.yaml 的唯一方式（patch 直接拒绝）、NVIDIA 模型切换命令、OpenClaw 健康检查序列

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### SiliconFlow 多模型 + Multi-Agent 备份路由

**问题场景**：在 `providers` 下配置了 siliconflow 多个模型（DeepSeek-V3、Qwen3-14B 等），但 `delegation.model` 仍然指向一个 provider 上不存在的模型，导致 subagent 全部失败。

**正确配置结构**：

```yaml
# 1. providers 区 — 声明可用的模型
providers:
  siliconflow:
    api_key: sk-xxx...
    base_url: https://api.siliconflow.cn/v1
    enabled: true
    models:
      - id: deepseek-ai/DeepSeek-V3
        name: DeepSeek V3
        context_window: 64000
      - id: Qwen/Qwen3-14B
        name: Qwen3 14B
        context_window: 32000
      # ... 更多模型

# 2. delegation 区 — 指定默认 subagent 模型（必须在 providers 中存在）
delegation:
  provider: siliconflow
  model: deepseek-ai/DeepSeek-V3   # ← 必须是 providers 里有的模型 ID
  base_url: https://api.siliconflow.cn/v1
  orchestrator_enabled: true
  max_concurrent_children: 5

# 3. model_overrides（可选）— 给特定模型路由到不同 backend
model_overrides:
  "siliconflow/deepseek-ai/DeepSeek-V3":
    provider: siliconflow
    base_url: https://api.siliconflow.cn/v1
```

**常见错误**：`delegation.model: MiniMax-M2.7` + `delegation.provider: siliconflow` → subagent 调用时会报模型不存在，因为 siliconflow 上没有 MiniMax-M2.7。

**验证方法**：
```bash
# 确认 provider 有哪些模型
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/saber/.hermes/config.yaml'))
for name, p in cfg.get('providers', {}).items():
    models = p.get('models', [])
    print(f'{name}: {len(models)} models')
    for m in models:
        print(f'  {m.get(\"id\") if isinstance(m, dict) else m}')
"
```

**Pitfall**: `model_overrides` 的 key 格式必须是 `provider_id/model_id`（斜杠分隔），如 `siliconflow/deepseek-ai/DeepSeek-V3`。

### API Key 被脱敏成占位符

**症状**：API key 在 config.yaml 中显示为 `sk-hwp...vluw`（以 `...` 内嵌或 `***` 模式），调用任何 provider API 都返回 HTTP 401 `Invalid token`。

**原因**：`security.redact_secrets: true` 开启后，Hermes 会将疑似密钥的字符串脱敏。如果配置写入流程触发了脱敏逻辑，真实的 key 会被替换成字面量占位符。

**验证方法**：
```bash
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/saber/.hermes/config.yaml'))
for provider, data in cfg.get('providers', {}).items():
    key = data.get('api_key', '')
    if '...' in key or len(key) < 30:
        print(f'PROBLEM: {provider} api_key appears masked: {key}')
"
```

**解决方案**：重新从 provider 控制台获取 key，直接编辑 `~/.hermes/config.yaml` 中的 `api_key:` 字段，或使用 `~/.hermes/.env`（不会被脱敏）。确认 `security.redact_secrets: false` 或删除该配置行。

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
