---
name: agent-skills-standard
description: Use when authoring, packaging, porting, or optimizing SKILL.md agent skills. Covers the agentskills.io open standard, progressive disclosure, the npx skills distribution rail, Capability vs Preference skill triage, and text-space skill optimization (SkillOpt / SkillReducer).
---

# Agent Skills Open Standard

SKILL.md is no longer a Claude Code feature — it is an **open, cross-vendor
standard** with a distribution rail. This skill covers the format, the
portability rules that actually break, and the 2026 tooling for *optimizing*
skills rather than hand-tuning them.

Hermes' skill system is already compatible with agentskills.io; this skill is
about authoring to the spec and measuring whether a skill actually helps.

## When to Use

- Writing or restructuring a `SKILL.md` (frontmatter, body, references/, scripts/).
- Debugging why a skill triggers too often / never triggers.
- Publishing skills so other agents (Claude Code, Codex, Cursor, Copilot,
  Gemini CLI, Goose…) can install them.
- Deciding whether a skill is worth building at all, or how to compress it.
- NOT for writing agent code — use `agent-engineering` / framework skills.

## The format

```
my-skill/
├── SKILL.md          # REQUIRED: YAML frontmatter + markdown body
├── scripts/          # optional: executable helpers
├── references/       # optional: long-form docs, loaded on demand
├── assets/           # optional: templates, schemas
└── agents/           # optional: agent-specific config
```

Minimum frontmatter is just two fields:

```yaml
---
name: {product}-best-practices
description: >-
  Best practices for building with {product}. Use when writing, reviewing,
  or debugging code that uses {product} ({key APIs, file patterns, imports}).
---
```

Fields seen in the wild: `license`, `compatibility`, `metadata.author`,
`version`, and the still-**experimental** `allowed-tools`.
Validation: `skills-ref validate ./my-skill`.

## Progressive disclosure — the whole point

Three stages, and each stage has its own budget:

| Stage | Loads | Cost |
|---|---|---|
| Discovery | `name` + `description` only, at startup | ~30–50 tokens **per skill** |
| Activation | full `SKILL.md` body, when a prompt matches the description | the real cost |
| Execution | `scripts/`, `references/`, `assets/` — only when the body points at them | unbounded |

**All matching responsibility lives in `description`.** A vague description
never fires; an over-broad one fires on everything. Write descriptions as
*trigger conditions*, not summaries — "Use when X" not "This skill covers X".

A hundred skills cost a few thousand tokens of listing, not a hundred full
documents. That is why a big skill library is affordable at all.

## Portability rules (the ones that bite)

1. **`context: fork` is Claude Code-only.** Including it silently degrades the
   other ~54 agents that read the same folder. Keep it out of shared repos.
2. **No org-specific values baked into the skill body.** Use placeholders
   (`{owner}/{repo}`) and put the concrete values in `AGENTS.md` or config.
   One canonical `SKILL.md`, no parallel internal copy, no version drift.
3. **Body lean: 100–300 lines that change behavior.** Push depth to
   `references/` and executables to `scripts/`.
4. **Ship the proven three-skill set** if publishing a product:
   `{product}-best-practices`, `{product}-quickstart`,
   `migrate-from-{competitor}`.
5. Add `.claude-plugin/marketplace.json` to the same repo for free Claude Code
   plugin dual-listing.

## Distribution: `npx skills`

Vercel Labs owns the rail; Anthropic owns the spec. As of 2026-06 the CLI was
pulling ~1.38M npm downloads/week and installing into ~55 agents.

```bash
npx skills add {org}/{skills}              # install from GitHub shorthand
npx skills add https://github.com/org/repo # full URL / GitLab / git URL / local path
npx skills add {org}/{repo} --skill NAME -a claude-code
npx skills add -g {org}/{repo} -y          # global + non-interactive (CI)
npx skills list | find | check | update | remove | init
```

- **GitHub is the registry.** No publish command, no submission, no review —
  push a public repo with `SKILL.md` files and it is installable immediately.
  Listing on skills.sh is driven by install telemetry.
- Install scope is `.agents/skills/` or `.claude/skills/`; symlink by default,
  `--copy` as fallback. Per-agent global paths otherwise.
- `.skills.json` + `skills-lock.json` mirror npm's `package.json`/lock pair;
  `npx skills experimental_install` is the CI equivalent of `npm ci`.
- Known agents: amp, antigravity, claude-code, codex, cursor, droid, gemini,
  github-copilot, goose, kilo, kiro-cli, opencode, roo, trae, windsurf.
- Quality on skills.sh varies — audit community skills with the same scrutiny
  as any third-party dependency.

## Triage: is this skill worth building?

Red Hat's ACE team split (from building a production root-cause-analysis
skill for the Red Hat Demo Platform):

- **Capability skills** patch what the base model can't do reliably — tool
  calling patterns, format conversion, a bespoke log fetcher. **These
  deprecate** as models and harnesses improve. Don't over-invest.
- **Preference skills** encode workflows, conventions, institutional knowledge
  — RCA process, deployment checklist, incident playbook. **Durable**, but only
  as valuable as their fidelity to the real workflow. The value is the
  orchestration, not any single step.

Rule of thumb: *defining the process first, then fitting tooling inside it.*
That maps to the business-analysis distinction between tooling and process —
you can swap one log collector, you cannot swap the process knowledge.

## Determinism: put mechanical work in scripts

Use scripts for fetching, formatting, validation; reserve LLM reasoning for
subjective analysis. Red Hat measured a **26% cost cut** from this split in
their experiments. If a step can be expressed as a deterministic function, it
does not belong in the prompt.

## Measured reality: skills are mostly non-actionable

SkillReducer (arXiv 2603.29919, v2 Jun 2026) studied **55,315** public skills:

- **26.4% have no routing description at all** — they can never fire.
- **Over 60% of body content is non-actionable.**
- Reference files can inject tens of thousands of tokens per invocation.

Its two-stage fix (compress descriptions → restructure bodies by taxonomy with
progressive disclosure, faithfulness-checked) reached **48% description and 39%
body compression while *improving* functional quality 2.8%** — a less-is-more
effect: cutting non-essential content reduces distraction. Gains transferred
across five models from four families (mean retention 0.965) and to an
independent agent framework.

**Corollary for auditing an existing skill library:** measure the description
field first. A missing or vague description is the highest-leverage bug, and
it is invisible until you grep for it.

## Skill as a trainable parameter — SkillOpt

Microsoft Research's SkillOpt (arXiv 2605.23904) reframes the question from
"how do we write a better prompt?" to **"how do we train the skill?"** The skill
Markdown is a trainable parameter living *outside* a frozen target model.

| Deep learning | SkillOpt |
|---|---|
| Model weights | the skill document (Markdown) |
| Forward pass | rollout (frozen target executes tasks) |
| Loss / gradient | reflect (optimizer proposes add/delete/replace edits) |
| Gradient clipping | edit selection — `learning_rate` = max edits per step |
| SGD step | patch application to the skill |
| Validation set | gated evaluation on a held-out selection split |
| Epochs | multi-epoch with slow/meta update |

The **validation gate** is the load-bearing part: a candidate skill is adopted
only if it beats the current score on the held-out split; only a new best is
promoted to `best_skill.md`. Rejected edits are *kept* in an epoch-local buffer
as negative feedback, so the optimizer doesn't retry them. Ablations: dropping
the rejected-edit buffer lowered scores on all three benchmarks; dropping the
meta skill plus slow update dropped SpreadsheetBench from 77.5 → 55.0.

Results: best or tied-best across **all 52 evaluation cells** (6 benchmarks ×
7 target models × 3 execution modes) vs. seven baselines including TextGrad,
GEPA, Trace2Skill and EvoSkill. GPT-5.5 direct-chat six-benchmark average went
58.8 → 82.3 (+23.5 points, and +5.4 over an *oracle* that picks the best
competing method per cell). Largest gains on procedural work: SpreadsheetBench
41.8 → 80.7, OfficeQA 33.1 → 72.1.

Two properties worth copying even without running the tool:
- **Compact and auditable.** Final `best_skill.md` medians ~920 tokens
  (379–1,995 range); only **one to four** edits are accepted into the final
  file. OfficeQA's +39.0 came from a *single* accepted edit.
- **Converges instead of drifting.** Bounded edits + validation gating +
  best-version selection are what stop unbounded self-editing.

Corollary: this only works **wherever automatic evaluation or a reliable
verifier exists**. Without a scored task set, "train the skill" degenerates
into taste-based rewriting.

## Tooling

- `microsoft/SkillOpt` — research engine (`skillopt`, `skillopt-train`,
  `skillopt-eval`) plus **SkillOpt-Sleep** (preview), which reviews real coding
  agent sessions and *stages* proposed memory/skill updates for human adoption.
  Distinct configs and safety boundaries; read the Sleep overview before
  pointing it at real session data.
- CodexOpt — wraps the same loop as `codexopt improve --live [--apply]`, with
  `heuristic` / `reflective` / `skillopt` engines over `SKILL.md` globs.
  Its `gepa` engine is deprecated (older `gepa.optimize_anything` API).
- SkillOpt's "Red Hat variant" (`AIMikav/skillopt`) uses GEPA evolutionary
  search to compress SKILL.md — same intent, different search strategy.

## Checklist for a new or revised skill

- [ ] `description` is a **trigger condition** ("Use when…"), not a summary —
      it is the only thing loaded at discovery and it carries all matching
- [ ] Frontmatter has `name` + `description`; run `skills-ref validate`
- [ ] No `context: fork` in anything meant to be shared
- [ ] No hardcoded org/repo/URL values — placeholders + config
- [ ] Body is 100–300 lines of *actionable* rules; depth in `references/`,
      executables in `scripts/`
- [ ] Mechanical steps (fetch/format/validate) are scripts, not prose
- [ ] Classified as capability (will deprecate) or preference (durable)
- [ ] If optimizing: validation gate + rejected-edit buffer, never unconditional
      self-edit

## Sources

- https://agentskills.io/home — the spec
- https://github.com/agentskills/agentskills
- https://github.com/vercel-labs/skills — the `npx skills` CLI
- https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context
- https://next.redhat.com/2026/07/28/building-skills-for-ai-agents-pitfalls-and-best-practices/ — capability vs preference, 26% determinism cut
- https://arxiv.org/abs/2603.29919 — SkillReducer, 55,315-skill empirical study
- https://arxiv.org/abs/2605.23904 — SkillOpt, 52/52 cells
- https://microsoft.github.io/SkillOpt/docs/ — docs incl. SkillOpt-Sleep