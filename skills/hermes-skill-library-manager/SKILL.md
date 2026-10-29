---
name: hermes-skill-library-manager
trigger_words: ['skills-library', 'skill-management', 'skill-manager', 'skill-library', 'library-manager']
category: productivity
description: "A comprehensive system for managing Hermes Agent skills: discovery, installation, categorization, integrity validation, and lifecycle maintenance across repositories."
---

# Hermes Skills Library Manager

A consolidated skills library management system for Hermes Agent that handles discovery, installation, category organization, integrity validation, and lifecycle maintenance across multiple skill repositories and sources.

## Overview

This skill serves as a unified interface for managing the entire Hermes Agent skills ecosystem including:
- Discovery from git repositories (Hermes, user profiles, external curators)
- Installation, update, and removal workflows
- Category-based organization (maintaining the taxonomy-driven default_category system)
- Integrity validation and lock-file management
- Cross-session consistency checking
- Debt-driven repackaging of narrow skills into broader class-level skills


## Core Features

### Skill Discovery & Indexing
- Crawl local and remote repositories for skills
- Intelligent indexing with category inference
- Dependency resolution across skills
- Change detection via file monitoring (SHA-based)

### Installation Pipeline
- One-command install from git URL or remote source
- Git clone with depth=1 for speed
- VCS lock file generation (skills.lock) for reproducibility
- Automatic category assignment
- Dependency tree validation

### Category Management
- Maintains the default taxonomy-driven system categories
- Auto-categorization based on directory path and skill tags
- User-configurable category mappings
- Bulk re-categorization workflows

### Repository Integration
- Multi-profile support (default, user profiles)
- Cross-profile skill access
- Consistency checking between profiles
- Remote repository override handling

### Integrity & Validation
- SHA-256 verification of critical files
- Cross-session consistency checking
- Lock file auditing
- Repository signature verification

### Maintenance Operations
- Automated consolidation workflows (umbrella-ification)
- Dead skill pruning via archiving
- Skill renaming and redirect establishment
- Cross-references and redirects migration


## Usage Patterns

```bash
# Refresh skills index from all sources
hermes skills refresh

# Install skill from repository
hermes skills install https://github.com/user/example-skill

# List skills with optional category filter
hermes skills list --category=productivity

# Validate integrity of all installed skills
hermes skills validate --full
```

## Deduplicating same-named skills

Nested installs produce the same skill at several paths
(`foo`, `foo/foo`, `software-development/foo`, …). Hermes resolves by **basename**,
so every extra copy is a load-time ambiguity. Clear it with content hashing —
never by path shape alone, because two same-named skills can be genuinely
different versions.

**1. Back up the whole directory first.** Dedup deletes; there is no undo.
```bash
tar czf ~/.hermes/cache/scratch/skills-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  -C ~/.hermes/skills .
```
Check the archive is non-trivial in size — a near-empty tarball means the
source path was wrong, and you just backed up nothing.

**2. Group by basename, then split each group by SKILL.md content hash.**

```python
import os, hashlib
from collections import defaultdict
root = os.path.expanduser('~/.hermes/skills')
groups = defaultdict(list)
for dp, _, fs in os.walk(root):
    if 'SKILL.md' in fs:
        rel = os.path.relpath(dp, root)
        groups[rel.split('/')[-1]].append(os.path.join(dp, 'SKILL.md'))
```

**3. Act on the split, not the raw group size.** Two outcomes, and only one is
safe to touch:

| Split | Verdict | Action |
|---|---|---|
| one hash — every copy byte-identical | **pure redundancy** | delete all but one |
| multiple hashes | **real conflict** — different versions | delete nothing; a human decides which survives |

A session that reported "148 duplicate groups" and then deleted 148 groups
would have destroyed 51 distinct skill versions. Report both numbers
separately: how many groups were redundant vs. conflicting.

**4. Keep the shallowest copy.** Prefer the shortest path (top-level wins), so
`skill_view` hits it without a long qualifier. Note that "shallowest" can tie —
two copies at the same depth are interchangeable, so pick one deterministically
(e.g. lexicographic) rather than treating the tie as an error.

**5. Re-verify the hash immediately before each delete.** Recompute it against
the keeper and skip the file if it changed — a concurrent `hermes skills
update` can rewrite a copy between your scan and your delete. Walk the target
directory to sum its size before `rmtree` so the freed-space report is real.

**6. Re-scan and report the delta.** Unique names, remaining duplicate groups,
and space freed. The remaining group count should equal the conflict count from
step 3; if it doesn't, something was classified wrong.
