---
name: portable-windows-python-deploy
description: Deploy Python apps to USB as portable Windows executables with no installation required
triggers:
  - portable python windows usb
  - python embeddable windows deployment
  - hermes openclaw portable usb
---

# Portable Python Windows Deployment

Deploy Python applications to USB drives for true portable Windows use — no installation required, no system registry writes, all data on USB.

## Approach: Python Embeddable + Batch Scripts

### Why Embeddable vs Full Installer
- **Embeddable**: ~11MB zip, truly portable, no registry writes
- **Full installer**: ~30MB+, writes to registry, requires uninstaller

### Key Files Needed on USB

```
/YourApp/
├── python-win/              # Python 3.11.x embeddable (unzip zip)
│   ├── python.exe
│   ├── python311._pth       # MODIFY THIS (see below)
│   ├── python311.zip        # stdlib archive
│   ├── python3.dll
│   ├── python311.dll
│   ├── vcruntime140*.dll    # C runtime deps
│   ├── libssl-3.dll
│   ├── libcrypto-3.dll
│   ├── sqlite3.dll
│   ├── get-pip.py           # download from bootstrap.pypa.io
│   └── Scripts/             # created after pip install
├── app/                     # your Python source
├── 启动.bat                  # launcher batch script
└── 数据/                    # data dir
```

### Critical: Enable Site-Packages in Embeddable Python

Embeddable Python disables `site-packages` by default. Modify `python311._pth`:

```
# original (commented lines may vary):
# import site

# replace with:
import site
site
```

The `site` line (without `import`) tells Python to add the site-packages directory to sys.path.

### Critical: Embeddable Python Has NO venv Module

**Embeddable Python is NOT the same as a full Python installer.**

| Feature | Embeddable | Full Installer |
|---------|-----------|----------------|
| `python -m venv` | ❌ FAILS (no venv module) | ✅ Works |
| pip.exe in Scripts/ | ❌ Missing | ✅ Available |
| pre-installed packages | ✅ Often includes some | ❌ None |
| hermes.pth support | ✅ Yes | ✅ Yes |

The `python -m venv` command will fail silently or error on embeddable Python. Use `get-pip.py` instead.

### First-Run: Bootstrap pip via get-pip.py

Embeddable Python doesn't include pip. Download `get-pip.py`:

```bash
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
```

Then install pip and packages:

```batch
@echo off
cd /d "%~dp0python-win"
set PY_HOME=%~dp0python-win

:: Install pip if not present (embeddable has no pip.exe)
if not exist "%~dp0python-win\Scripts\pip.exe" (
    echo [FIRST RUN] Installing pip...
    python.exe get-pip.py
)

:: Upgrade pip
python.exe -m pip install --upgrade pip

:: Install dependencies (use --target for embeddable, or use pip with proper paths)
python.exe -m pip install -r "%~dp0app\requirements.txt" --target "%~dp0python-win\Lib\site-packages"

:: Run your app
python.exe "%~dp0app\your_script.py" %*
pause
```

### Hermes-Specific: Skip venv Entirely

Hermes uses `hermes.pth` in site-packages to auto-add the source directory to `sys.path`. With embeddable Python that has pre-installed dependencies, you can **skip venv creation entirely**:

```batch
@echo off
cd /d "%~dp0"

set "PYTHON=%~dp0Python312\python.exe"
set "HERMES=%~dp0hermes-agent"

REM Verify Python exists
if not exist "%PYTHON%" (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

set "PYTHONPATH=%HERMES%"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "HERMES_HOME=%~dp0"

REM Launch directly — hermes.pth handles source discovery
"%PYTHON%" -m hermes_cli.main chat

pause
```

For offline install of missing packages (firecrawl, websockets, etc.), use `get-pip.py` + pre-cached wheels:

```batch
:: Install pip
python.exe get-pip.py

:: Install missing wheels (--no-deps for speed, --force-reinstall to ensure)
for %%w in (firecrawl exa-py fal_client cryptography websockets) do (
    for %%f in ("%~dp0wheels\%%~w*.whl") do (
        if exist "%%f" python.exe -m pip install "%%f" --no-deps --force-reinstall --quiet
    )
)
```

### Reliable Extraction: Use Python zipfile

`unzip` and `7z` commands timeout on large zips. Use Python instead:

```python
import zipfile, os
zip_path = "/tmp/python-win.zip"
dest = "/mnt/usb/App/python-win"
with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall(dest)
```

### Linux Python vs Windows Python

**Don't copy Linux Python directories to a Windows USB.** Python standalone distributions (like `python-standalone-full` from various sources) are Linux ELF binaries and **will not run on Windows**.

If you accidentally copy Linux Python to a Windows USB, manually delete the directory — it can be ~77MB wasted space.

#### PowerShell Bootstrap: When Linux Network is Blocked

If building the USB from Linux and network to python.org/GitHub is blocked, defer Python download to Windows PowerShell. This approach was used successfully for hermes-agent-windows deployment:

**Key URLs (verified working from Windows PowerShell):**
```batch
# Python 3.12 Embeddable (~8MB, much smaller than 110MB standalone)
https://www.python.org/ftp/python/3.12.13/python-3.12.13-embed-amd64.zip

# pip bootstrap
https://bootstrap.pypa.io/get-pip.py
```

**All-in-one launcher pattern (01启动hermes.bat):**
```batch
@echo off
setlocal
set PY_DIR=%~dp0hermes-agent-windows\python-win
set VENV_DIR=%~dp0hermes-agent-windows\.venv

:: Step 1: Download Python if not present
if not exist "%PY_DIR%\python.exe" (
    echo [1/4] Downloading Python 3.12.13 Embeddable...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.13/python-3.12.13-embed-amd64.zip' -OutFile '%TEMP%\python-embed.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '%PY_DIR%' -Force"
    echo [1/4] Done.
)

:: Step 2: Enable site-packages in embeddable Python
if exist "%PY_DIR%\python312._pth" (
    powershell -Command "(Get-Content '%PY_DIR%\python312._pth') -replace '#import site', 'import site' -replace '^site$', 'site' | Set-Content '%PY_DIR%\python312._pth'"
)

:: Step 3: Install pip
if not exist "%PY_DIR%\Scripts\pip.exe" (
    echo [2/4] Installing pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PY_DIR%\get-pip.py'"
    cd /d "%PY_DIR%" && python.exe get-pip.py
)

:: Step 4: Create venv and install hermes-agent
if not exist "%VENV_DIR%" (
    echo [3/4] Creating virtual environment...
    "%PY_DIR%\python.exe" -m venv "%VENV_DIR%"
)
echo [4/4] Installing hermes-agent...
"%VENV_DIR%\Scripts\pip.exe" install -e "%~dp0hermes-agent-windows"

:: Launch
echo Starting hermes-agent...
"%VENV_DIR%\Scripts\python.exe" -m hermes_cli.main chat
pause
```

**setvar.bat — central environment configuration (sourced by all other scripts):**
```batch
@echo off
set PY_HOME=%~dp0hermes-agent-windows\python-win
set VENV_HOME=%~dp0hermes-agent-windows\.venv
set HERMES_HOME=%~dp0hermes-agent-windows
set GIT_HOME=%~dp0Git
set NODE_HOME=%~dp0node
set RG_HOME=%~dp0ripgrep
set TERM_HOME=%~dp0terminal
set PATH=%PY_HOME%;%VENV_HOME%\Scripts;%GIT_HOME%\bin;%NODE_HOME%;%RG_HOME%;%TERM_HOME%;%PATH%
set PYTHONIOENCODING=utf-8
set HOME=%USERPROFILE%
```

**Source integrity check:** `uv.lock` in hermes-agent-windows confirms source is complete (should be ~990KB). If missing or 0 bytes, the source is corrupted/incomplete.

---

## Hermes-specific Notes

Hermes uses hermes-agent with these key entry points:
- `cli.py` — CLI mode (main agent loop)
- `mcp_serve.py` — MCP server mode (stdio, for OpenClaw integration)
- `run_agent.py` — core agent logic

Dependencies: `minimax` API, `requests`, `subprocess`, standard library modules.

### 5. Hermes + OpenClaw USB Portable Deployment (full stack)

Complete USB structure:
```
/USB/
├── OpenClaw/                 # OpenClaw (Node.js)
│   ├── node-win/              # Node.js Windows binary
│   ├── .openclaw/             # openclaw-app + node_modules
│   │   └── openclaw-app/
│   │       ├── openclaw.mjs   # Main entry
│   │       └── node_modules/  # 702 npm packages
│   ├── 启动.bat                # Gateway launcher
│   ├── Setup.bat              # Interactive config (configure)
│   └── 依赖.bat               # npm install check
├── Hermes/                    # Hermes Agent (Python)
│   ├── python-win/            # Python 3.11 embeddable
│   │   ├── Scripts/pip.exe
│   │   └── Lib/site-packages/ # all pip deps
│   ├── node-win/              # Node.js (for MCP)
│   └── hermes-agent/          # Source + .env
│       └── .env               # API keys — DO NOT RE-RUN WIZARD
└── 离线打包.bat                 # One-click dependency installer
```

**Critical warning**: Running Hermes setup wizard after initial configuration may ERASE credentials from `.env`. The wizard's "clear credentials" action overwrites the file. Keep a backup of `.env` with API keys before running `hermes setup`.

**Setup wizard behavior**:
- `openclaw configure` — modular, per-step skip ✅ Use this
- `openclaw onboard` — full mandatory flow, no skip ❌ Avoid for USB
- Hermes `setup` — curses TUI, requires Windows Terminal (see section above)

**Environment variables for USB batch scripts**:
```batch
set HOME=%~dp0                  :: Keep all data on USB
set OPENCLAW_HOME=%~dp0.openclaw :: OpenClaw config on USB
set HERMES_HOME=%~dp0Hermes      :: Hermes config on USB
set PYTHON_HOME=%~dp0python-win
set PATH=%~dp0node-win;%PATH%   :: Node.js on USB
```

## Hermes + OpenClaw USB Portable Deployment (absorbed from usb-portable-update)

### Full USB Directory Structure

```
openclaw-portable/
├── .openclaw/              # Config + plugins + workspace
│   ├── openclaw.json       # Main config (paths must be relative!)
│   ├── extensions/         # qqbot, weixin plugins
│   ├── workspace/
│   ├── node_modules/        # Pre-copied (saves first-run time)
│   └── openclaw-app/       # OpenClaw source
├── hermes-agent/            # Python MCP agent
│   └── mcp_serve.py        # MCP server entry
├── python-standalone-full/  # uv's standalone Python 3.11 (truly portable, no symlinks)
├── node-linux/              # Linux Node.js binary
├── node-win/               # Windows Node.js binary
├── data/                    # Working data
├── .home/                   # HOME directory simulation
├── scripts/                 # Utility scripts
├── start.bat                # Windows launcher
├── start.sh                 # Linux launcher
└── README.md
```

**Total size reference**: ~1.1 GB (node-linux ~189MB, hermes-agent ~251MB, python-standalone-full ~96MB, .openclaw ~303MB)

### USB Update Workflow (NTFS)

**Problem**: NTFS USB write speed is very slow. Direct extract/copy to `/mnt/usb/` timeout.

**Solution**: Extract locally to `/tmp` first, then copy to USB.

```python
import subprocess, shutil, os

# Download package to /tmp
subprocess.run(["npm", "pack", "openclaw@VERSION", "--pack-destination=/tmp"], check=True)

# Extract locally
os.makedirs("/tmp/oc-new", exist_ok=True)
subprocess.run(["tar", "-xzf", f"/tmp/openclaw-{VERSION}.tgz", "-C", "/tmp/oc-new", "--strip-components=1"])

# Copy to USB (slow but works)
shutil.copytree("/tmp/oc-new", "/mnt/usb/OpenClaw/.openclaw/openclaw-app", dirs_exist_ok=True)
```

**Hermes update (preserve user data)**:
```python
preserve_set = {
    ".env", "config.yaml", "auth.json", "auth.lock",
    "state.db", "state.db-shm", "state.db-wal",
    "skills", "memories", "sessions", "logs",
    "interrupt_debug.log", "models_dev_cache.json",
    "dependencies_installed.flag", "venv",
    "SOUL.md",
}

for item in os.listdir(hermes_new_src):
    if item in preserve_set:
        continue  # skip user data
    src, dst = f"{hermes_new_src}/{item}", f"{hermes_usb}/{item}"
    if os.path.isdir(src):
        shutil.rmtree(dst, ignore_ok=True)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
```

### Check Latest Versions

```bash
# OpenClaw
npm show openclaw version

# Hermes
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | grep tag_name
```

### USB NTFS Remount as Read-Write

USB NTFS drives often auto-mount RO. Remount rw:

```bash
# Find device
lsblk | grep sdb

# Unmount if needed
sudo umount /dev/sdb1

# Remount with write permissions
sudo mount -t ntfs-3g -o rw,uid=1000,gid=1000,umask=0000 /dev/sdb1 /mnt/usb
```

Verify: `touch /mnt/usb/.test && rm /mnt/usb/.test && echo "rw OK"`

### Critical: Windows vs Linux venv Incompatibility

**Do NOT copy a Linux-created venv to a Windows USB deployment.**

Symptoms:
```
Could not import tool module tools.browser_dialog_tool: No module named 'websockets'
Could not import tool module tools.web_tools: No module named 'firecrawl'
Could not import tool module tools.image_generation_tool: No module named 'fal_client'
```

**Fix**: Reinstall dependencies on Windows using embeddable Python + get-pip.py:
```batch
cd /d %~dp0hermes-agent
Python312\python.exe get-pip.py
Python312\python.exe -m pip install -e . --no-cache-dir --find-links ../wheels_win --no-index
```

### Portable Hermes Batch Script Bug

**Symptom:** Hermes won't start, python.exe not found.

**Root cause:** Script at `X:\Hermes\启动-Hermes(Windows).bat` sets `HERMES_HOME=%~dp0Hermes`, resolving to `X:\Hermes\Hermes` instead of `X:\Hermes`.

**Fix:** Change to `set "HERMES_HOME=%~dp0"` (the batch file's own directory).

---

### Verifying Windows PE Executables

You cannot test `.exe` files on Linux. Verify presence of Windows PE headers:

```bash
file /mnt/usb/App/python-win/python.exe
# should contain: PE32+ executable (GUI) x86-64
```

### Space Estimation

| Component | Approximate Size |
|-----------|-----------------|
| Python 3.11 embeddable | ~11MB zip, ~40MB extracted |
| Node.js 25.x Windows | ~37MB zip, ~170MB extracted |
| hermes-agent source | ~461MB |
| npm node_modules | ~200MB+ |
| pip packages (varies) | 10-100MB+ |

Total for Hermes + OpenClaw on USB: ~1.2GB (before user data)

## USB Cleanup Checklist

When auditing or preparing a USB deployment, delete these safely:

| Path Pattern | Why Safe to Delete |
|---|---|
| `**/*.7z` in media/ (e.g. hermes-agent-windows installer) | Already extracted; package is redundant |
| `hermes-agent/wheels/hermes_agent-X.XX.X-py3-none-any.whl` | Keep only latest version |
| `plugins/hermes-achievements/docs/` | Static docs/images, not runtime |
| `openclaw/logs/*.jsonl` | Audit/trajectory logs, safe to purge |
| `openclaw/agents/main/sessions/**/*.jsonl` | Old session trajectories, not runtime data |
| `skills/*/.git/objects/` | Git objects useless after install |
| `skills/*/.git/pack/` | Git pack files, not needed post-install |
| `hermes-agent/web/` | Unbuilt source; `hermes_cli/web_dist/` is the actual artifact |
| `lcm.db-{wal,shm}` | SQLite WAL/SHM journal files |
| `node_modules/node-pty/prebuilds/win32-arm64/` | Windows ARM rarely used, saves ~28MB |
| `node_modules/**/node_modules/**/node-pty-linux-*/` | Nested Linux ELF packages in adapters |

### ELF Binary Scanner (Linux detection for Windows USB)

Run on Linux before shipping USB to Windows:

```python
import glob, os

USB = "/mnt/usb"  # adjust mount point

def is_linux_elf(path):
    with open(path, 'rb') as f:
        return f.read(4) == b'\x7fELF'

# Scan all .node and .so files
linux_elfs = []
for pattern in [f"{USB}/hermes-agent/**/*.node",
                f"{USB}/openclaw/**/*.node",
                f"{USB}/openclaw/**/*.so"]:
    for f in glob.glob(pattern, recursive=True):
        if is_linux_elf(f):
            rel = os.path.relpath(f, USB)
            size = os.path.getsize(f) // 1024
            linux_elfs.append((rel, size))

if linux_elfs:
    print(f"⚠️  Found {len(linux_elfs)} Linux ELF files:")
    for path, kb in linux_elfs[:10]:
        print(f"  {path} ({kb}KB)")
else:
    print("✅ No Linux ELF binaries found")
```

### Nested Linux Package Cleaner

Adapters (`@tencent-weixin/openclaw-weixin`, `@openclaw/discord`, etc.) often bundle their own nested copies of `openclaw/node_modules` which contain Linux ELF binaries. Delete the entire nested `node_modules` tree:

```python
import shutil, os

def remove_nested_linux_pkgs(root_nm, depth=0, max_depth=8):
    """Recursively remove nested node_modules containing Linux ELF binaries."""
    removed = []
    if not os.path.isdir(root_nm) or depth > max_depth:
        return removed

    for pkg in sorted(os.listdir(root_nm)):
        pkg_path = os.path.join(root_nm, pkg)
        if not os.path.isdir(pkg_path):
            continue

        inner_nm = os.path.join(pkg_path, 'node_modules')
        if os.path.isdir(inner_nm):
            removed.extend(remove_nested_linux_pkgs(inner_nm, depth+1, max_depth))

        # Delete this package if it's a nested install with Linux ELF binaries
        if depth > 0:
            has_elf = False
            for dirpath, _, filenames in os.walk(pkg_path):
                for fname in filenames:
                    if fname.endswith('.node') or fname.endswith('.so'):
                        fpath = os.path.join(dirpath, fname)
                        with open(fpath, 'rb') as f:
                            if f.read(4) == b'\x7fELF':
                                has_elf = True
                                break
                if has_elf:
                    break
            if has_elf:
                size = sum(
                    os.path.getsize(os.path.join(r, f))
                    for r, _, files in os.walk(pkg_path)
                    for f in files
                )
                shutil.rmtree(pkg_path)
                removed.append((os.path.relpath(pkg_path, USB), size))

    return removed

nm = f"{USB}/openclaw/node_modules"
removed = remove_nested_linux_pkgs(nm)
print(f"Deleted {len(removed)} nested Linux packages")
```

### USB Disk Usage Audit

```python
import os

def get_size(path):
    if os.path.isfile(path): return os.path.getsize(path)
    return sum(get_size(os.path.join(r, f)) for r, di, fi in os.walk(path) for f in fi)

def show_tree(path, depth=0, min_mb=1.0, max_depth=3):
    try:
        items = [(i, get_size(os.path.join(path, i)), os.path.isdir(os.path.join(path, i)))
                 for i in sorted(os.listdir(path)) if 'System Volume Information' not in i]
        items.sort(key=lambda x: -x[1])
        for name, sz, is_dir in items:
            mb = sz / 1024 / 1024
            prefix = "  " * depth
            icon = "📁" if is_dir else "📄"
            if mb >= min_mb or depth == 0:
                print(f"{prefix}{icon} {name:<38} {mb:>7.1f} MB")
            if is_dir and depth < max_depth and mb >= 5:
                show_tree(os.path.join(path, name), depth+1, min_mb, max_depth)
    except PermissionError:
        pass

show_tree("/mnt/usb", min_mb=5, max_depth=2)
```

### python311._pth — No PYTHONPATH Needed

Python embeddable finds site-packages automatically via `_pth` file. **Do not set PYTHONPATH manually** — the `_pth` mechanism handles it:

```
# python311._pth (correct)
import site
site
lib
lib/site-packages
```

With `import site` present, Python automatically adds `lib/site-packages` to `sys.path`. `hermes_cli` will be found without any PYTHONPATH setting.

### Windows Path Convention on USB

All USB batch scripts must auto-detect drive letter (not hardcode `K:` or `D:`):

```batch
REM Auto-detect drive letter
for %%i in (d e f g h i j k l m n o p q r s t u v w x y z) do (
    if exist "%%i:\hermes-agent\.env" (
        set "USB=%%i"
        goto :found
    )
)
:found
set "HERMES_HOME=!USB!:\hermes-agent"
set "PATH=!USB!:\hermes-agent\python-win;!PATH!"
```

### What NOT to Clean from a USB Deployment

| Item | Reason to Keep |
|---|---|
| `chrome-portable/` | Hermes Browser Tool falls back to it when no system Chrome found |
| `sessions/` JSONL | Hermes conversational history (~400MB, user data) |
| `skills/` | 1000+ skills, reinstall would be slow |
| `openclaw/node_modules/` | Runtime dependencies |
| `python-win/lib/site-packages/hermes_cli/` | Site-packages copy needed at runtime; root copy is for development |
