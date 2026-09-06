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