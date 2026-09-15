---
name: skill-evolution
description: MUSE-Autoskill — AI agents that write, evaluate, and retire their own skills autonomously. 5-stage lifecycle (Create/Memory/Manage/Evaluate/Refine) with skill-level memory. Self-generated skills beat human-authored (87.94% vs 68.40% on SkillsBench).
triggers:
  - MUSE-Autoskill self-writing skills
  - skill lifecycle management autonomous
  - agent skill self-evolution
  - skill evaluation retirement loop
  - skill-level memory cross-task
category: agent-engineering
---

# Skill Evolution Engine — MUSE-Autoskill (ByteDance, May 2026)

## What It Is

MUSE-Autoskill (arXiv:2605.27366) by ByteDance's ByteBrain team is a framework where **AI agents write their own skills, evaluate them, and retire the bad ones** — autonomously. Self-generated skills achieve **87.94% accuracy** vs 68.40% for human-written skills on SkillsBench.

> **Key insight**: AI doesn't just use skills — it writes better ones than humans.

## Core 5-Stage Lifecycle

```
Create → Memory → Manage → Evaluate → Refine
    ↑__________________________________|
         (retirement loop)
```

| Stage | What Happens |
|-------|-------------|
| **Create** | Agent generates `SKILL.md` + scripts + tests + `.memory.md` on demand via `skill_create` tool |
| **Memory** | Each skill carries `.memory.md` — cross-task experience (edge cases, successful adaptations) |
| **Manage** | Skills organized in registry; overlap detection + retrieval by relevance |
| **Evaluate** | Unit tests run automatically; fail = block from registry |
| **Refine** | Rewrites skill descriptions with new successful examples |
| **Retire** | Skills below quality threshold removed (retirement loop prevents registry bloat) |

## Skill Package Structure

```
skill_name/
├── SKILL.md        # Usage instructions (name/triggers/category/steps)
├── scripts/        # Executable code
├── tests/          # Unit tests ← Key: blocks bad skills from registry
├── resources/      # Helper data
└── .memory.md      # Cross-task experience ← Key innovation
```

## Hermes Integration Pattern

**Directly applicable to Herme's skill system**:

1. **Skill-level memory**: Each Hermes skill could carry a `.memory.md` tracking edge cases, failure patterns, and successful adaptations across uses — the existing `skill_manage` tool already supports skill directories.

2. **Evaluation loop**: Before accepting a new skill suggestion, run it through test scenarios and only promote to the library if it passes.

3. **Retirement loop**: Skills that consistently fail or get superseded should be marked as deprecated rather than accumulate in the library.

## Benchmark Results

| Agent | No Skills | Human Skills | MUSE Skills | Gain |
|-------|-----------|--------------|-------------|------|
| Codex | 52.1% | 67.3% | — | +15.2pp |
| Hermes | 53.2% | 61.2% | **68.4%** | +15.2pp |
| MUSE | 53.2% | 68.4% | — | +15.2pp |

**Hermes with MUSE skills**: 48.02% → 51.90% (+3.88pp) on cross-agent transfer

## Key Numbers

| Metric | Value |
|--------|-------|
| Self-generated accuracy | **87.94%** vs 68.40% human |
| Cross-agent transfer gap | ~21% (skills survive runtime change) |
| Token cost per skill | ~383K tokens |
| Break-even point | **3 uses** (reuse savings > creation cost) |
| SkillsBench tasks | 75 tasks, 4 domains, 5 runs each |

## MUSE vs Existing Hermes Patterns

| Pattern | Mechanism | MUSE Addition |
|---------|-----------|---------------|
| Reflexion | Verbal self-critique | Skill-level memory accumulation |
| SWE-RL Loop | Code generate → test → fix | Automated skill creation from task solutions |
| Skill Lifecycle | skill_manage CRUD | Built-in evaluation + retirement loop |
| AutoSkill | Skill retrieval | Self-writing skills that beat human-authored |

## Practical Implementation for Hermes

```python
# Pseudo-code for skill self-evolution in Hermes
def on_task_success(task, solution):
    skill_name = extract_skill_pattern(solution)
    if skill_name not in existing_skills:
        create_skill(
            name=skill_name,
            triggers=[task.type],
            scripts=solution.code,
            memory=f"Edge cases from {task.id}",
        )

def evaluate_skill(skill_name):
    score = run_skill_tests(skill_name)
    if score < threshold:
        retire_skill(skill_name)
    return score
```

## Sources

- Paper: https://arxiv.org/abs/2605.27366
- SkillFed analysis: https://skillfed.io/research/muse-autoskill-s-self-written-skills-beat-human-authored-ones-85-24-vs-81-17
- Dev.to breakdown: https://dev.to/tenglongai2026/muse-autoskill-bytedances-ai-that-writes-its-own-skills-and-beats-humans-at-it-63i
- Survey hub: https://selfimproving-agent.github.io/
