---
name: api-connectivity-triage
title: api-connectivity-triage
description: Use when an API call fails or a key needs validating.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [Networking, DNS, TLS, SNI, API, Geo-block, Troubleshooting]
    related_skills: [blocked-page-recovery, connectivity-layer]
triggers:
  - '"API 不通"'
  - '"连不上"'
  - '"API key 测一下"'
  - '"验证 api key"'
  - '"curl 超时"'
  - '"连接被重置"'
  - '"unsupported_country"'
  - '"invalid_api_key"'
  - '"DNS 污染"'
  - '"SNI"'
  - '"换个出口"'
categories:
  - networking
author: Hermes Agent
created: "2026-10-25"
---

# API Connectivity Triage

## When to Use

Use this skill whenever a request to a **third-party API** fails, hangs, resets,
or returns an error you cannot explain — and especially whenever the user asks
you to **validate an API key**. Typical triggers:

- "测一下这个 API" / "试试这个 key" / "这个 key 还能用吗"
- A `curl` to an external API returns 403/401/404/timeout, or "connection
  reset by peer"
- A service works on the user's own machine but not from yours
- You need to pick an egress path (WARP, relay, VPS) for a blocked service
- An API key was pasted into chat and needs a verdict

**Not** for: reading page content behind a login/paywall (use
`blocked-page-recovery`), connecting to a serial bus or local device (use
`connectivity-layer`), or red-team/pentest traffic analysis.

When a request to a third-party API fails, the failure lives in exactly **one**
layer, and each layer produces a **different, identifiable signature**. Never
jump to "the key is bad" or "the service is down" — name the layer first.

The whole point of this skill is to produce a **defensible conclusion**:
either the key is verified working, verified broken, or **genuinely
undeterminable from here** — with the reason stated. "Undeterminable" is a
valid, honest deliverable. Never dress a guess as a result.

---

## The layer stack (memorize this order)

```
DNS        →  resolves? right address?          (pollution → wrong IP)
TCP        →  port reachable?                    (reset/refused → middlebox)
TLS/SNI    →  handshake completes? cert for host? (SNI filter → RST)
HTTP layer →  request sent? status? headers?     (Host/path filter)
App layer  →  JSON error from the service itself  (geo-block / auth / quota)
```

**A layer that fails hides every layer below it.** You cannot conclude
anything about the key until the request physically reaches the API's app
layer and returns a JSON error.

---

## Step 1 — Baseline: is general egress working?

Always start here, or you will misread a dead network as a blocked domain.

```bash
curl -sS -m 10 -o /dev/null -w 'github %{http_code}\n' https://api.github.com
curl -sS -m 10 -o /dev/null -w 'baidu %{http_code}\n'  https://www.baidu.com
curl -sS -m 10 https://ipinfo.io/json | head -c 300   # your exit IP + country
```

If a *known-good* host also fails → your network/router/proxy is down. Fix
that first; the target domain is not the story.

---

## Step 2 — DNS: distinguish poisoned from clean

```bash
getent hosts api.example.com          # what the system resolver returns
```

Poisoning signature: the resolved address belongs to a **completely unrelated
operator**. Tells seen in the wild: an IPv6 address inside
`2a03:2880:...face:b00c` (Meta/Facebook space) for a non-Meta domain; a
Cloudflare IP for a domain that is demonstrably not on Cloudflare; a
Dropbox-owned IP for an API host.

Never trust the system resolver alone. Query public DoH resolvers and
**compare**:

```bash
for u in 'https://223.5.5.5/resolve?name=HOST&type=A' \
         'https://doh.pub/dns-query?name=HOST&type=A'; do
  curl -sS -m 12 "$u" -H 'accept: application/dns-json'
done
```

On a poisoned network, `cloudflare-dns.com` and `dns.google` are themselves
often blocked/reset — their failure is a signal, not a dead end. Alibaba
`223.5.5.5` and dnspod `doh.pub` are usually reachable from CN networks.

**DoH answers can also be poisoned.** Cross-check at least two resolvers and
sanity-check the returned IP against the target's real host. An IP that
belongs to a totally different vendor is poisoned even if it came from DoH.

---

## Step 3 — TCP: is the port open?

```bash
timeout 6 bash -c 'exec 3<>/dev/tcp/IP/443 && echo TCP_OK'
```

- `TCP_OK` → routing fine, problem is above (TLS/HTTP/app).
- connection refused → actively rejected (local firewall or RST).
- timeout → packets dropped upstream.

---

## Step 4 — TLS/SNI: is there hostname-based filtering?

This is the layer that most often fools people, because **the handshake dies
before any HTTP is sent** and the error looks like a dead host.

```bash
timeout 12 openssl s_client -connect IP:443 -servername HOST </dev/null 2>&1 \
  | grep -E 'errno|subject=|Cipher is|CONNECTED'
```

Read the signature:

| Signature | Meaning |
|---|---|
| `subject=CN=host` + a real cipher | TLS fine, host not filtered |
| `write:errno=104`, `Cipher is (NONE)`, 0 bytes read | **RST during ClientHello → SNI filter** |
| `no peer certificate available` | MITM or incomplete interception |

**The decisive control test** — same IP, different SNI:

```bash
# blocked SNI on this IP:
openssl s_client -connect IP:443 -servername api.example.com   # → errno=104
# allowed SNI on the SAME IP:
openssl s_client -connect IP:443 -servername www.example.com   # → subject=CN=...
```

If one SNI dies and another on the identical IP succeeds, the middlebox is
matching the **SNI string**, not the IP.

### Trailing-dot bypass

A naive SNI matcher that does exact string comparison will **not** match a
hostname with a trailing dot, and the TLS stack still resolves it normally:

```bash
openssl s_client -connect IP:443 -servername 'api.example.com.'   # → passes
```

The certificate still validates (`CN=api.example.com`), because the trailing
dot is stripped for name matching. Verify with `Verify return code: 0 (ok)`.

**Limitations — know these before you rely on it:**
- Some middleboxes normalize the trailing dot; then it buys nothing. Test it.
- The HTTP `Host:` header is often matched **separately**. A trailing-dot SNI
  with a bare `Host: api.example.com` can still be reset. Try a trailing dot
  on the Host header too, and via `openssl s_client` (raw HTTP) rather than
  curl if curl keeps resetting.
- The block may also key on the **URL path** or on the `Authorization` header.

### Driving raw HTTP over a working TLS session

When curl resets but openssl handshakes, bypass curl's own URL handling:

```bash
printf 'GET /v1/models HTTP/1.1\r\nHost: api.example.com.\r\nAuthorization: Bearer %s\r\nConnection: close\r\n\r\n' "$KEY" \
| timeout 20 openssl s_client -quiet -connect IP:443 -servername 'api.example.com.' 2>/dev/null
```

This is often the only way to get a real response out of a host whose SNI is
filtered but whose certificate and origin are reachable.

---

## Step 5 — The app layer: read the JSON error, don't guess

Once a request finally returns, the service's own JSON error names the
problem. Match on the **error code**, not on prose.

| Error | Layer | Meaning |
|---|---|---|
| `unsupported_country_region_territory` | app | **Geo-block.** Service refuses your exit country. Nothing about your key was evaluated. |
| `invalid_api_key` / `incorrect API key` | app | Key genuinely rejected. |
| `401` + `missing api key` | app | Header never arrived — curl/http-layer strip, not a key problem. |
| `429` | app | Rate/quota, not auth. |
| `model_not_found` | app | Key fine, model name wrong. |
| `403` + CF-RAY header | app | Reached Cloudflare-fronted origin; the app layer decided. |

### HTTP 200 is not proof of health

Some providers report **quota exhaustion as HTTP 200 with a degenerate body**
rather than 429. Observed with MiniMax: the OpenAI-compatible endpoint
`text/chatcompletion_v2` returns `200` plus
`{"choices": null, "usage": {"total_tokens": 0}}` when the Token Plan is
exhausted, while the Anthropic-compatible endpoint on the *same account*
returns a plain `429` carrying the quota code in the message.

Two rules follow:

1. **Judge a health probe by payload, not status.** For a chat endpoint a
   healthy response carries a non-empty `choices`/`content` list and a
   non-zero token count. `choices: null` or `total_tokens: 0` is a failure
   whatever the status code says. This bites hardest in a **circuit breaker
   or monitoring probe**, where a false "healthy" means the guard silently
   never fires while every downstream call fails.
2. **Read the whole body before concluding.** Error markers sit at the *end*
   of the JSON (MiniMax puts `base_resp.status_code` last). Truncating the
   body to the first couple hundred characters hides exactly the field you
   need, so the probe reports "normal" while callers fail.

If two protocol endpoints exist for one account, prefer the one with the
unambiguous signal (a real 429) and use the other only as a fallback — then
still validate its payload shape.

### The control test that proves key validity

Send the **same** request three ways:

```bash
# (a) real key, (b) syntactically bogus key, (c) no Authorization header at all
```

Compare the responses:

- **All three identical** → the rejection happens *before* auth. The response
  carries **zero information about key validity**. Say so explicitly.
- **Real key differs from bogus key** → auth ran, and the difference is your
  verdict: real key → 200, bogus → `invalid_api_key`. Now you have a result.

This is the single most important step for "test this key for me" tasks.
Skipping it produces confident nonsense.

---

## Step 6 — Choosing an egress path

| Path | Fixes | Does NOT fix |
|---|---|---|
| **Cloudflare WARP (free)** | DNS poisoning, SNI filtering, geo-blocks on ordinary sites | **App-level geo-blocks that key off Cloudflare's own `loc`** |
| **Self-hosted VPS + WireGuard/sing-box** | Everything, including app-layer geo-blocks | Needs a non-CN (or otherwise supported) exit IP |
| **Third-party relay** (OpenRouter, groq, …) | Model availability | Uses the **relay's** key — cannot validate the user's own key |
| **User's phone hotspot with VPN** | Everything | Needs the user to turn it on |

### The WARP trap — read before you promise anything

Cloudflare WARP deliberately **preserves your apparent country**. The exit
colo (LAX/SJC/AMS) moves, but the `loc=` field in
`https://www.cloudflare.com/cdn-cgi/trace` stays your real country. Services
that geolocate via Cloudflare (including OpenAI) see that country and refuse.

Verify before promising WARP solves it:

```bash
curl -sS -m 12 https://www.cloudflare.com/cdn-cgi/trace | grep -E '^(loc|colo|warp|ip)='
```

`warp=on` + `colo=LAX` + `loc=CN` → WARP is working **and still geo-blocked
at the app layer**. Switching protocol (MASQUE ↔ WireGuard) or forcing
different endpoints does **not** change `loc`. Say this plainly instead of
letting the user believe the colo is the problem.

WARP *does* fix DNS-poisoned/SNI-filtered ordinary sites (YouTube, V2EX, etc.)
— worth enabling regardless.

### Enabling WARP headless (no GUI)

```bash
sudo systemctl start warp-svc
sudo systemctl enable warp-svc
warp-cli --accept-tos status          # first run needs --accept-tos
warp-cli --accept-tos connect
```

If `warp-cli status` says the daemon isn't running, start `warp-svc` first.
If it says a registration already exists, do **not** delete and re-register —
just `connect`. If `sudo systemctl start` fails with an auth prompt while
`sudo -n true` succeeds, use `sudo -n systemctl ...` — the prompt is
systemd's, not sudo's.

---

## Provider-specific signatures

Concrete observed signatures per provider — OpenAI's geo-block body and how to
prove it is pre-auth, poisoned DNS answers and which DoH resolvers work from
CN networks, SNI-filtered hostname examples, WARP's `loc` vs `colo`
behaviour, and how to probe the local box for an existing egress path — are in
[blocked-endpoint-signatures.md](references/blocked-endpoint-signatures.md).
Read it when the ladder lands on a specific provider or you need to compare
against a known-good baseline.

Run the layer ladder automatically with:

```bash
bash scripts/diagnose_endpoint.sh api.openai.com "$API_KEY"
```

It walks DNS → TCP → TLS/SNI → HTTP → app layer, prints the layer it
stopped at, and runs the three-way auth control test when it can reach the
app layer. It never prints the key.

---

## Pitfalls

- **Do not report "the key is invalid" from a network-layer failure.** If you
  never reached the app layer, you have no result — only a blocked path.
- **Do not treat a 403 as an auth failure.** Read the JSON `code`.
- **Do not let the tool's output leaking the key change your verdict.** If the
  terminal redacts the key in output, that means the *header* was still sent;
  it does not mean the key was rejected.
- **A redacted transcript is not a corrupted file.** If terminal output or a
  Python print shows `***` where a header value or literal should be, the
  masking happened on the way *out* of the tool, not in the file. Confirm the
  on-disk bytes with a raw byte dump (`od -c`, or `read_file` on the exact
  line) before "fixing" anything — rewriting a correct line after reading a
  redacted view is how working code gets broken.
- **Do not write a supplied key into config files, skill files, or memory.**
  Verify, then advise rotation if it was pasted in chat. The rotation
  procedure for this box (sweep all `config.yaml`/`.env` locations, full-token
  replace, independent verification) is in the `hermes-agent` skill →
  "Rotating an API key".
- **`grep PATTERN file | tail` is unreliable for log freshness** — use
  `stat -c '%y'` on the file and read the raw tail.
- **Check the local machine before declaring "no VPN here".** Probe processes,
  installed packages, `.desktop` files, PATH binaries, listening ports, and
  `tun`/`tap`/`wg` interfaces. A GUI VPN client on a headless box is useless
  anyway — look for the **CLI + systemd** path.
- **The user may send a Windows installer for a Linux box.** Check the file
  type and the local package manager *before* trying to install it; the Linux
  equivalent may already be installed and merely not running.
- **A service's geo-block error is not proof the request was well-formed.** It
  proves you reached the server. Both facts matter, separately.
- **Don't stall the user with a plan when a probe would answer.** The layer
  ladder is cheap; run it before proposing solutions.

---

## Reporting shape

State findings in this order, and be explicit about what is *known* vs
*unknown*:

1. **Which layer is blocking** (DNS / TCP / TLS-SNI / HTTP / app).
2. **What you proved** (with the observed signature).
3. **What remains undeterminable and why** (usually: the request never
   reached the auth check).
4. **Concrete next actions**, each with its cost/effort, and which ones
   actually change the outcome.
5. **Credential hygiene** — if a key was pasted in chat, recommend rotating
   it, and confirm you did not persist it.

Do not pad. One table of layer→signature→finding beats a wall of prose.
