# Blocked-Endpoint Signatures — Concrete Reference

Provider-specific observed signatures, reusable across incidents. Read this
when the SKILL.md ladder lands you on a specific layer and you need to know
what that provider's failure actually looks like.

---

## OpenAI (`api.openai.com`)

### Known-good baseline
```bash
curl -sS -m 25 https://api.openai.com/v1/models -H "Authorization: Bearer $KEY"
```
Success shape: `{"object":"list","data":[{"id":"gpt-4o-mini",...}]}`.
Any `{"error":{...}}` JSON body means you reached the app layer.

### Endpoint shape
`api.openai.com` is Cloudflare-fronted. A `403` that carries a `CF-RAY`
header and `Server: cloudflare` means **the request arrived** — the refusal
is the app layer, not the network.

### Geo-block signature
```json
{"error":{"code":"unsupported_country_region_territory",
          "message":"Country, region, or territory not supported",
          "type":"request_forbidden"}}
```
This is emitted **before** authentication is evaluated. The proof: send the
real key, a bogus key, and no `Authorization` header at all — all three
return byte-identical 403 bodies. Therefore this response contains **zero
information about key validity**.

A request that reaches OpenAI will carry `cf-ray` and `set-cookie:
__cf_bm=...`. If you see neither, you never reached the edge.

### Key-shape sanity
Newer project-scoped keys look like `sk-proj-<~160 chars>`. Legacy keys are
`sk-<48 chars>`. Format sanity is **not** validity proof — a perfectly
well-formed key can be revoked. Never report "the key looks right, so it's
fine."

### Relay caveat
OpenRouter, Groq, and similar OpenAI-compatible relays are reachable from
CN networks and will happily serve models. But they authenticate with **their
own** key. A relay can prove "the model is available and the endpoint shape
works"; it can **never** prove the user's own OpenAI key is valid. Say so
when a relay is the only available path.

---

## Cloudflare-fronted services generally

| Signal | Meaning |
|---|---|
| `Server: cloudflare` + `CF-RAY: <id>-<colo>` | Reached the edge. Colo tells you which PoP served you. |
| `__cf_bm` cookie in `set-cookie` | Bot-management cookie issued — normal for a real request. |
| `cf-ray` absent but HTTP status present | A middlebox fabricated the response, not the origin. |
| `cf-mitigated: challenge` | Bot challenge, not a geo or auth issue. |

---

## DNS poisoning — observed examples

A poisoned answer usually belongs to a **different vendor entirely**:

| Domain asked | Poisoned answer | Tell |
|---|---|---|
| `api.openai.com` | `2a03:2880:f10d:183:face:b00c:0:25de` | Meta/Facebook IPv6 space |
| `api.openai.com` | `108.160.165.141` | Dropbox-owned IP |
| `api.openai.com` | `174.37.54.20` / `104.244.43.35` | Telecom-owned, not OpenAI |
| `www.youtube.com` | `2001::1` | RFC 6666 placeholder — nothing listens there |
| `r.jina.ai` | `2a03:2880:...face:b00c` | Meta IPv6 space |

Legitimate answers for the same names come from different resolvers and land
in the right vendor's netblock (e.g. `104.18.x.x` / `172.64.x.x` = Cloudflare
for genuinely Cloudflare-fronted hosts).

### DoH reachability from CN networks

| Resolver | Typical result |
|---|---|
| `https://223.5.5.5/resolve?name=H&type=A` | Works, returns JSON |
| `https://doh.pub/dns-query?name=H&type=A` | Works, returns JSON |
| `https://cloudflare-dns.com/dns-query` | Connection reset |
| `https://dns.google/resolve` | Timeout |
| `https://1.1.1.1/dns-query` | Timeout |

Always send `-H 'accept: application/dns-json'`. Compare **at least two**
resolvers — a single DoH answer can itself be poisoned.

---

## SNI filtering — observed examples

Blocked SNI strings on a CN network include `api.openai.com` and
`chatgpt.com`. The filter matched the **exact string**; `www.openai.com` on
the same IP passed, and so did `api.openai.com.` with a trailing dot.

The signature is always the same shape:

```
CONNECTED(00000003)
write:errno=104          <- peer sent RST right after ClientHello
---
New, (NONE), Cipher is (NONE)
```

`openssl` reports `write:errno=104` because the RST arrived during the write;
`curl` surfaces it as `curl: (35) Recv failure: 连接被对方重置` or
`curl: (7) Failed to connect`.

### Decisive control test
Run the *same* blocked SNI against an unrelated host's IP that normally
works. If it also dies there, the block is SNI-based, not IP-based:

```bash
# openrouter.ai's own IP, but with the blocked SNI:
openssl s_client -connect 104.18.3.115:443 -servername api.openai.com  # → errno=104
# same IP, its own SNI:
openssl s_client -connect 104.18.3.115:443 -servername openrouter.ai  # → CN=openrouter.ai
```

This is the single cleanest proof that filtering is on the hostname string.

---

## Cloudflare WARP — observed behaviour

```bash
warp-cli --accept-tos status
warp-cli --accept-tos tunnel stats     # shows protocol, endpoints, colo
curl -sS -m 12 https://www.cloudflare.com/cdn-cgi/trace | grep -E '^(loc|colo|warp|ip)='
```

`cdn-cgi/trace` fields that matter:
- `warp=on` → tunnel is live.
- `colo=LAX` → the PoP serving you (moves freely between endpoints).
- `loc=CN` → **your apparent country**, and it does NOT move with `colo`.

Observed across MASQUE and WireGuard protocols and four forced endpoints
(`162.159.192.1:2408`, `188.114.96.1:2408`, `162.159.193.10:500`,
`188.114.97.1:2408`): colo varied LAX → SJC → AMS, `loc` stayed `CN` every
time. WARP preserves the user's country on purpose so domestic services keep
working.

**Consequence:** WARP fixes DNS poisoning and SNI filtering (it fixes
YouTube and V2EX), but it does **not** fix services that geolocate by
Cloudflare's `loc` — OpenAI being the canonical example. For those you need
an exit whose country is actually different: a self-hosted VPS, a
non-CN relay, or the user's own phone hotspot.

### `warp-cli` operational notes
- `warp-cli status` → "Unable to connect to the CloudflareWARP daemon" means
  `warp-svc` isn't running. `sudo systemctl start warp-svc`.
- First invocation needs `--accept-tos`, otherwise it refuses with a ToS
  prompt even in a non-TTY.
- "Old registration is still around" → do **not** `registration delete`;
  the device is already enrolled. Just `warp-cli --accept-tos connect`.
- `sudo systemctl start` can fail with an auth prompt even when
  `sudo -n true` succeeds (the prompt comes from systemd, not sudo). Use
  `sudo -n systemctl ...`.
- `mode proxy` puts a SOCKS5 listener on port 40000 in the default config;
  if the port isn't listening, the daemon didn't come up.

---

## Probing the local box for an existing egress path

Do this before telling a user "there's no VPN here". A headless box often
already has the CLI installed but not running.

```bash
ps aux | grep -iE 'vpn|proxy|tun2socks|clash|sing-box|xray|v2ray|shadowsocks|trojan|wireguard|openvpn|tailscale|mihomo'
pacman -Q | grep -iE 'clash|mihomo|sing|xray|v2ray|shadow|trojan|hysteria|wireguard|openvpn|tailscale|cloudflare'
command -v clash mihomo sing-box singbox xray v2ray ss-local trojan wg openvpn tailscale zerotier-cli
ls /usr/share/applications ~/.local/share/applications 2>/dev/null | grep -iE 'vpn|clash|sing|xray|outline|wireguard|tailscale'
ss -tlnp | grep -E ':(7890|1080|1087|10808|10809|8118|8888|40000)'
ip link show | grep -E 'tun|tap|utun|wg'
```

Notes:
- `libproxy` is KDE's proxy *settings page*, not a proxy client.
- The `shadow` package is the passwd password-hash tool, not shadowsocks.
- `kcm_proxy.desktop` is a settings UI, not a client.
- A GUI client is useless on a headless box (no `$DISPLAY`, no Xvfb) —
  look for the CLI + systemd path instead.

---

## Installer-file triage

A user may hand you a Windows binary for a Linux host. Check before acting:

```bash
file <path>                 # "Composite Document File V2 ... MSI Installer" → Windows
uname -a; cat /etc/os-release | head -3
```

Even better, check whether the **Linux equivalent is already installed**
before downloading anything — package managers often have it:

```bash
pacman -Qo /usr/sbin/warp-cli     # "owned by cloudflare-warp-minimal-bin ..."
```

The MSI's own version string does not have to match the installed Linux
package version; what matters is whether a usable client exists locally.
