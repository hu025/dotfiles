# Hermes Agent Web Build & Dashboard Reference

## Web UI Build Assets (hermes-agent/web/)

`npm run build` in the `web/` directory fails if `public/fonts` and `public/ds-assets` are missing. These are copied from `node_modules/@nous-research/ui/dist/` during `npm run sync-assets` (the `prebuild` step).

### Symptom
### ⚠️ Legacy — these steps may no longer be needed

> As of May 2026, `npm install` now runs `sync-assets` correctly as a postinstall hook and the build succeeds with just `npm install && npm run build`. The manual asset-copying workaround below is kept here for reference on older versions or if the postinstall hook fails.

**Manual asset sync (if build produces missing-font warnings):**
```bash
cd ~/.hermes/hermes-agent/web
mkdir -p public/fonts public/ds-assets
cp -r node_modules/@nous-research/ui/dist/fonts/* public/fonts/
cp -r node_modules/@nous-research/ui/dist/assets/* public/ds-assets/
npm run build
```

## Dashboard Startup

### Default binding: 127.0.0.1 only
```bash
hermes dashboard --port 9119 --host 0.0.0.0 --no-open
# Refuses: "Refusing to bind to 0.0.0.0 — the dashboard exposes API keys and config without robust authentication."
#          "Use --insecure to override (NOT recommended on untrusted networks)."
```

**Correct startup for local-only access:**
```bash
hermes dashboard --port 9119 --host 127.0.0.1 --no-open
# Listens on 127.0.0.1:9119 ✓
```

**For remote access**, either:
- SSH port forward: `ssh -L 9119:127.0.0.1:9119 saber@192.168.31.50` → open `http://localhost:9119`
- Or use `--insecure` only on trusted networks (not recommended)

### Current state (2026-05-08)
- Dashboard: running on `127.0.0.1:18792`
- Gateway: `hermes-gateway.service` active, `hermes-gateway-watchdog.service` monitoring
- Ports: 18789 (OpenClaw WeChat), 18799 (Hermes Gateway), 18792 (Dashboard)
