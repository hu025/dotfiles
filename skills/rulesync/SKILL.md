---
name: rulesync
description: "rulesync (agentsync) — One source of truth for all AI coding agent rule files. Sync CLAUDE.md/.cursorrules/AGENTS.md/.windsurfrules/copilot/GEMINI.md from a single canonical Markdown. Use when setting up or maintaining project-level AI coding rules across multiple tools (Cursor, Claude Code, Codex, Windsurf, etc.)."
triggers:
  - rulesync
  - agentsync
  - unified AI coding rules
  - CLAUDE.md .cursorrules sync
  - multi-agent rules management
  - project rules consistency
category: coding-agent-cli
version: 1.0.0
license: MIT
---

# rulesync — AI Coding Agent Rules Sync

## What It Is

**rulesync** (formerly agentsync) is a zero-dependency Python CLI tool that solves the fragmentation problem: every AI coding tool uses a different rule file format, yet the content is almost identical.

```
your-project/
├── .agentsync/rules.md    ← EDIT THIS (canonical source)
├── .cursorrules            ← auto-generated
├── CLAUDE.md               ← auto-generated
├── AGENTS.md               ← auto-generated
├── GEMINI.md               ← auto-generated
├── .windsurfrules          ← auto-generated
└── .github/copilot-instructions.md  ← auto-generated
```

**One edit → all tools updated automatically.**

## Installation

```bash
pip install rulesync
# or
uvx --from agentsync rulesync
```

Zero dependencies. Pure Python 3.10+.

## Quick Start

```bash
cd my-project

# 1. Initialize (creates .agentsync/rules.md)
rulesync init

# 2. Edit the canonical rules
nano .agentsync/rules.md

# 3. Sync all tool files
rulesync sync

# Preview changes without writing
rulesync diff

# Check which files are out of sync
rulesync status
```

## Supported Tool → File Mapping

| Tool | File Generated | Notes |
|------|--------------|-------|
| Claude Code | `CLAUDE.md` | Native format |
| Codex / OpenCode | `AGENTS.md` | Cross-tool standard |
| Cursor (legacy) | `.cursorrules` | Plain text / markdown |
| Cursor (modern) | `.cursor/rules/main.mdc` | YAML frontmatter |
| GitHub Copilot | `.github/copilot-instructions.md` | Enterprise |
| Gemini CLI | `GEMINI.md` | Google native |
| Windsurf | `.windsurfrules` | Codeium |
| Aider | `.aider.conf.yml` | YAML format |

## Key Commands

```bash
rulesync init          # Initialize in current project
rulesync sync          # Generate all rule files from canonical source
rulesync diff          # Preview what would change (dry-run)
rulesync status        # Show which files are out of sync
rulesync add gemini_md # Add a new tool format
rulesync remove cursorrules  # Remove a tool format
rulesync list          # List all 9 supported tools
rulesync adopt         # Import existing rules as canonical source
```

## Canonical Rules File Format

`.agentsync/rules.md` uses structured markdown sections:

```markdown
# Project Rules

## Stack
- Python 3.11+, FastAPI, PostgreSQL

## Testing
- Run: pytest tests/ -v
- Coverage > 80%
- All new features need tests

## Important constraints
- Never commit secrets to the repository
- All PRs require at least one review approval
```

rulesync transforms these sections into each tool's native format.

## Example: Unified Cursor + Claude Code Rules

Canonical source (`.agentsync/rules.md`):

```markdown
## Coding Standards
- Use type hints on all function signatures
- Prefer async/await over callbacks
- Maximum function length: 50 lines

## Git Workflow
- Branch naming: feat/, fix/, chore/
- Commit messages: conventional commits format
- All changes require tests
```

This generates:
- `CLAUDE.md` — Claude Code reads it directly
- `.cursorrules` — Cursor prepends it to every prompt
- `.cursor/rules/main.mdc` — Cursor modern format with YAML frontmatter
- `AGENTS.md` — Codex/OpenCode uses it
- `.windsurfrules` — Windsurf reads it
- `GEMINI.md` — Gemini CLI reads it
- `.github/copilot-instructions.md` — GitHub Copilot Enterprise

## Why Not Just Symlinks?

> Symlinks break on Windows, don't survive git clones cleanly, and can't handle format differences between tools. Cursor's `.mdc` format needs YAML frontmatter, `.aider.conf.yml` is YAML not markdown. rulesync handles all of that.

## Best Practice: CI Enforcement

```yaml
# .github/workflows/ai-rules-check.yml
name: AI Rules Sync Check
on: [push, pull_request]

jobs:
  rulesync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install rulesync
      - run: rulesync diff && rulesync status
        # Fail if any rules are out of sync
```

## Comparison: rulesync vs Alternatives

| Tool | Approach | Supported Tools | Format Handling |
|------|---------|---------------|----------------|
| **rulesync** | Canonical source → multi-format | 9 tools | Smart transformation |
| **Symlinks** | Single file shared | 0 (breaks on Windows) | None |
| **Manual copy** | Copy-paste | Any | None |
| **AI Dev Stack** | Comprehensive rule sets | Cursor + Claude Code | Drop-in templates |

## Integration with AI Dev Stack

AI Dev Stack (2.7k stars) provides production-grade rule sets that work with rulesync:

```bash
# Install AI Dev Stack rules
git clone https://github.com/aiagentwithdhruv/ai-dev-stack.git /tmp/ai-dev-stack

# Use rulesync to deploy across all tools
cp /tmp/ai-dev-stack/foundations/rules/*.md .agentsync/rules.md
rulesync sync
```

## Pitfalls

- **No conflict resolution**: If two tools have incompatible formats, rulesync picks a compromise. Review output files.
- **Windows line endings**: Ensure `.agentsync/rules.md` uses Unix line endings (LF).
- **Large teams**: rulesync doesn't handle concurrent editing of the canonical source — use standard git conflict resolution.

## Sources

- GitHub: https://github.com/obielin/agentsync
- PyPI: `pip install rulesync`
- License: MIT
- Python 3.10+
