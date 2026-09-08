---
name: anti-slop-checks
description: "Anti-slop checks for AI code quality gates."
version: 1.0.0
license: MIT
---

# Anti-Slop AI Semantic Checks

AI-powered semantic code quality checks encoded as markdown agent prompts, executed on every PR/commit.

## Core Concept

**The problem:** AI-assisted development generates code fast, but AI-generated code accumulates "slop" — verbose comments, over-abstraction, dead code, boilerplate. Standard linters cannot catch semantic quality issues.

**The solution:** Encode quality standards as markdown files, each running as a full AI agent that reads code, exercises judgment, and reports violations. This scales human quality standards across AI velocity.

> "Chiseling" — the human refinement step after AI code generation — becomes automated and systematic.

## Directory Structure

```
.continue/checks/
├── anti-slop.md       # Core anti-slop rule (10 patterns)
├── security-audit.md  # Prompt injection / local code exec
├── stale-comments.md  # Outdated comments
├── react-best-practices.md
├── setup-scripts.md
├── update-agents-md.md
└── update-continue-docs.md
```

Each file is a **standalone AI agent** with YAML frontmatter:

```yaml
---
name: Anti-slop
description: Fix AI Slop
---
[Markdown body with instructions]
```

## The 10 Anti-Slop Patterns

From Continue.dev's anti-slop.md:

1. **Overly verbose comments** — Comments restating exactly what code does
2. **Excessive defensive programming** — Unnecessary null checks, try-catches
3. **Redundant type annotations** — Already inferred by the compiler
4. **Boilerplate explosion** — Separate classes for trivial operations
5. **Over-abstraction** — Interfaces with single implementations, factories for one thing
6. **Verbose variable names** — `currentUserAuthenticationStatusBoolean` not `isAuthenticated`
7. **Unnecessary intermediate variables** — Used exactly once on the next line
8. **Repetitive error handling** — Copy-pasted try-catch blocks
9. **Filler documentation** — JSDoc adding nothing beyond the function signature
10. **"Just in case" code** — Unused parameters, dead code paths, hypothetical features

## Hermes Integration

For Hermes cron jobs and kanban workers, implement equivalent checks:

```
~/.hermes/checks/
├── anti-slop.md      # Run before any git commit
├── security-audit.md # Run on PR open
├── novel-quality.md  # Check novel-writing output quality
└── skill-audit.md   # Validate skill frontmatter
```

## Key Insights

| Pattern | Human Review | Anti-Slop Check |
|---------|-------------|-----------------|
| Coverage | Sampled | 100% of changes |
| Consistency | Varies by reviewer | Uniform criteria |
| Speed | Minutes/human | Seconds/machine |
| Scalability | Team bottleneck | Infinite scale |

## Comparison: Anti-Slop vs Standard Linters

- **Linters**: Syntax, style, formatting (mechanical)
- **Anti-slop checks**: Semantic quality, design patterns, intent (AI judgment)

The anti-slop check fills the gap where ruff or eslint cannot help — code that compiles but smells.

## Sources

- Continue.dev blog: Chiseling The Art of Polishing Vibe Code (Feb 2026)
- Continue.dev blog: Check on Your Spaghetti Software Factory (Mar 2026)
- Continue.dev GitHub: .continue/checks/anti-slop.md (read-only repo, archived Jul 2026)
