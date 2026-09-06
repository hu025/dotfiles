# USB Portable OpenCode — Session Reference (2026-08-28)

## Finding Version on USB

OpenCode.exe is buried in node_modules — no top-level binary. Run the exe directly:

```bash
find /mnt/usb/opencode -name "opencode.exe" -exec {} --version \;
```

Current USB: **1.18.23** | GitHub latest: **1.18.25**

## GitHub API

Repo migrated to `anomalyco/opencode` (was `sst/opencode`). API redirects:

```
GET https://api.github.com/repos/anomalyco/opencode/releases/latest
→ tag: v1.18.25, name: "OpenCode v1.18.25", published: 2026-08-28
```

## USB Directory Structure

```
/mnt/usb/opencode/              ← main (Windows exe + Linux shell shim)
/mnt/usb/opencode-portable/     ← minimal (cache dir only)
/mnt/usb/Hermes/               ← Hermes portable (node/python/hermes-agent v0.20.6)
/mnt/usb/openclaw/             ← OpenClaw QQ bot
/mnt/usb/opencode/opencode/node_modules/opencode-ai/
    opencode.exe                ← actual binary (find to run)
```

## Update Procedure

1. Backup: `cp -r /mnt/usb/opencode/opencode/node_modules /mnt/usb/opencode/opencode/node_modules.bak`
2. Windows: run `update.bat` inside USB opencode dir
3. Linux (from USB node env): USB has no Linux-native opencode binary — update must be done on Windows
4. Verify: `find /mnt/usb/opencode -name "opencode.exe" -exec {} --version \;`
