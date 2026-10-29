# GitHub Skill Installation Workflow

How to download and install a skill from a GitHub repository. Covers: tarball download, repo structure detection, and installation to `$HERMES_HOME/skills/installed/`.

---

## Standard Workflow

### Step 1: Download tarball

```bash
curl -sL "https://api.github.com/repos/<owner>/<repo>/tarball" -o package.tgz
```

Use `api.github.com/repos/<owner>/<repo>/tarball` — returns a tar.gz archive without requiring authentication. This is faster and more reliable than `https://github.com/<owner>/<repo>/archive/` redirects.

### Step 2: Extract and find SKILL.md

```bash
tar -xzf package.tgz
find . -name "SKILL.md"          # find all SKILL.md files
ls */SKILL.md                    # check for skills/ dir pattern
```

### Step 3: Detect repo structure

Repos follow one of three patterns:

| Pattern | Structure | Action |
|---------|-----------|--------|
| **Standard** | `skills/<name>/SKILL.md` | `cp -r skills/<name> $HERMES_HOME/skills/installed/` |
| **Clawhub** | `clawhub/<name>/SKILL.md` | `cp -r clawhub/<name> $HERMES_HOME/skills/installed/` |
| **Monolithic** | `<repo>/SKILL.md` at root | `mkdir installed/<name> && cp SKILL.md installed/<name>/` |

### Step 4: Install

```bash
DEST="$HERMES_HOME/skills/installed"
# Standard
cp -r extracted/skills/<name> "$DEST/"
# Clawhub
cp -r extracted/clawhub/<name> "$DEST/"
# Monolithic (single skill at root)
mkdir -p "$DEST/<name>"
cp extracted/SKILL.md "$DEST/<name>/"
```

### Step 5: Cleanup

```bash
rm -rf extracted/* package.tgz
```

---

## Common Repos and Their Structures

```
Agents365-ai/drawio-skill          → skills/drawio-skill/SKILL.md        (Standard)
ZeroPointRepo/youtube-skills       → skills/youtube-*/SKILL.md + clawhub/  (Both)
conorbronsdon/avoid-ai-writing     → SKILL.md at root                     (Monolithic)
HuangYuChuh/ComfyUI_Skills_OpenClaw → SKILL.md at root                    (Monolithic)
codejunkie99/agentic-stack         → .agent/ (not SKILL.md, special format)
```

---

## Shell Background Operator Warning

**Do NOT use `&` for parallel downloads in a foreground terminal command.** The terminal tool does not support `&` backgrounding in foreground calls. Use sequential downloads:

```bash
# ❌ Wrong — background operator in foreground command
curl -sL "url1" -o f1.tgz &
curl -sL "url2" -o f2.tgz &
wait

# ✅ Correct — sequential
curl -sL "url1" -o f1.tgz
curl -sL "url2" -o f2.tgz
```

If parallel background is needed, use `terminal(background=true)`.

---

## Skills Hub CLI (Preferred When Available)

The Hermes CLI has a built-in skill installer — prefer it over manual tarball extraction:

```bash
hermes skills install https://github.com/<owner>/<repo>/raw/main/SKILL.md
hermes skills install https://github.com/<owner>/<repo>/raw/main/skills/<name>/SKILL.md
hermes skills browse   # browse available skills
```

The CLI handles structure detection automatically.

---

## Troubleshooting

- **tar "cannot open" error**: file not in current directory — `cd` to where the `.tgz` is first
- **"No such file or directory" on cp**: check actual extracted dir name with `ls` (often includes commit hash: `owner-repo-COMMITHASH/`)
- **Skills not appearing after install**: run `hermes skills list` to verify; check `hermes skills config` for platform enablement
- **SKILL.md not found via `find`**: repo may use a different filename or no SKILL.md at all (e.g., `.agent/` format for agentic-stack)
