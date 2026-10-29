#!/usr/bin/env bash
# diagnose_endpoint.sh — walk the network layer stack for one API host and
# report WHICH layer blocks it.
#
# Usage: bash diagnose_endpoint.sh <host> [api_key]
#        bash diagnose_endpoint.sh api.openai.com "$OPENAI_API_KEY"
#
# Walks: DNS -> TCP -> TLS/SNI -> HTTP -> app layer.
# When it reaches the app layer it runs the three-way auth control test
# (real key / bogus key / no auth) so the verdict on key validity is
# evidence-based rather than guessed.
#
# The key is never printed. Only its presence and the resulting error codes.

set -uo pipefail

HOST="${1:-}"
KEY="${2:-}"
if [[ -z "$HOST" ]]; then
  echo "usage: bash diagnose_endpoint.sh <host> [api_key]" >&2
  exit 2
fi

say() { printf '\n=== %s ===\n' "$1"; }
hr()  { printf '%s\n' "-----------------------------------------"; }

# ---------------------------------------------------------------- baseline
say "STEP 0  baseline egress"
for probe in https://api.github.com https://www.baidu.com; do
  code=$(curl -sS -m 10 -o /dev/null -w '%{http_code}' "$probe" 2>/dev/null)
  printf '  %-28s HTTP:%s\n' "$probe" "${code:-000}"
done
exit_info=$(curl -sS -m 10 https://ipinfo.io/json 2>/dev/null \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ip','?'),d.get('country','?'),d.get('org','?'))" 2>/dev/null)
printf '  exit: %s\n' "${exit_info:-unknown}"

# -------------------------------------------------------------------- DNS
say "STEP 1  DNS"
sys_ip=$(getent hosts "$HOST" 2>/dev/null | awk '{print $1}' | head -1)
printf '  system resolver : %s\n' "${sys_ip:-none}"
for u in "https://223.5.5.5/resolve?name=${HOST}&type=A" \
         "https://doh.pub/dns-query?name=${HOST}&type=A"; do
  ans=$(curl -sS -m 12 "$u" -H 'accept: application/dns-json' 2>/dev/null \
    | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print(' '.join(a.get('data','') for a in d.get('Answer',[]) if a.get('type')==1))
except Exception:
    print('')
" 2>/dev/null)
  printf '  DoH %-46s : %s\n' "$(echo "$u" | sed 's|.*//||; s|?.*||')" "${ans:-unreachable}"
done
if [[ -z "$sys_ip" ]]; then
  echo "  VERDICT: DNS did not resolve. Not an API/key problem."; exit 1
fi

# -------------------------------------------------------------------- TCP
say "STEP 2  TCP :443"
if timeout 6 bash -c "exec 3<>/dev/tcp/${sys_ip}/443" 2>/dev/null; then
  echo "  TCP_OK to ${sys_ip}:443"
else
  echo "  TCP FAILED to ${sys_ip}:443"
  echo "  VERDICT: port unreachable. Not an API/key problem."; exit 1
fi

# ----------------------------------------------------------------- TLS/SNI
say "STEP 3  TLS / SNI"
probe_sni() {
  local sni="$1" out
  out=$(timeout 12 openssl s_client -connect "${sys_ip}:443" -servername "$sni" </dev/null 2>&1)
  if grep -q 'errno=104' <<<"$out"; then echo "RST"
  elif grep -q "subject=CN=${sni%.}" <<<"$out"; then echo "OK"
  elif grep -q 'subject=' <<<"$out"; then echo "OK(other-cert)"
  else echo "NO-HANDSHAKE"; fi
}
base_sni=$(probe_sni "$HOST")
dot_sni=$(probe_sni "${HOST}.")
printf '  SNI %-30s : %s\n' "$HOST" "$base_sni"
printf '  SNI %-30s : %s\n' "${HOST}." "$dot_sni"
if [[ "$base_sni" == "RST" && "$dot_sni" == "OK" ]]; then
  echo "  --> SNI FILTER DETECTED. Trailing-dot SNI bypasses it."
  SNI="${HOST}."
elif [[ "$base_sni" == "RST" ]]; then
  echo "  --> SNI FILTER DETECTED (no trailing-dot bypass)."
  echo "  VERDICT: TLS handshake is blocked by a middlebox."
  echo "           A key cannot be validated through this path."
  exit 1
else
  SNI="$HOST"
fi

# --------------------------------------------------- HTTP + app-layer probe
say "STEP 4  HTTP / app layer"
if [[ "$SNI" == "${HOST}." ]]; then
  # curl resets on these hosts; raw HTTP over openssl works
  raw_req() {
    local auth="$1"
    if [[ -n "$auth" ]]; then
      printf 'GET /v1/models HTTP/1.1\r\nHost: %s.\r\nAuthorization: Bearer %s\r\nConnection: close\r\n\r\n' "$HOST" "$auth"
    else
      printf 'GET /v1/models HTTP/1.1\r\nHost: %s.\r\nConnection: close\r\n\r\n' "$HOST"
    fi
  }
  call_raw() {
    raw_req "$1" | timeout 20 openssl s_client -quiet -connect "${sys_ip}:443" -servername "$SNI" 2>/dev/null \
      | grep -E '^HTTP/|^\{' | head -3
  }
  RES_REAL=$(call_raw "${KEY:-}")
  RES_BOGUS=$(call_raw "sk-proj-BOGUS0000000000000000000000000000000000000000000000000000000000")
  RES_NOAUTH=$(call_raw "")
else
  curl_call() {
    local auth="$1"
    if [[ -n "$auth" ]]; then
      curl -sS -m 25 --resolve "${HOST}:443:${sys_ip}" \
        -H "Authorization: Bearer ${auth}" "https://${HOST}/v1/models" 2>&1 | head -c 400
    else
      curl -sS -m 25 --resolve "${HOST}:443:${sys_ip}" "https://${HOST}/v1/models" 2>&1 | head -c 400
    fi
  }
  RES_REAL=$(curl_call "${KEY:-}")
  RES_BOGUS=$(curl_call "sk-proj-BOGUS0000000000000000000000000000000000000000000000000000000000")
  RES_NOAUTH=$(curl_call "")
fi

echo "  real key   : ${RES_REAL:-<empty>}"
echo "  bogus key  : ${RES_BOGUS:-<empty>}"
echo "  no auth    : ${RES_NOAUTH:-<empty>}"

# ------------------------------------------------------------------ verdict
say "VERDICT"
norm() { tr -d ' \n\r' | cut -c1-200; }
r=$(printf '%s' "$RES_REAL" | norm)
b=$(printf '%s' "$RES_BOGUS" | norm)
n=$(printf '%s' "$RES_NOAUTH" | norm)

if [[ -z "$r" ]]; then
  echo "  UNDETERMINABLE: no app-layer response. Path blocked before the API."
  echo "  The key's validity was never evaluated."
elif [[ "$r" == "$b" && "$r" == "$n" ]]; then
  echo "  UNDETERMINABLE: real / bogus / no-auth responses are IDENTICAL."
  echo "  The rejection happens BEFORE auth, so the response says nothing"
  echo "  about whether the key is valid."
  echo "  Response was: $r"
elif [[ "$r" == *invalid_api_key* || "$r" == *incorrect* ]]; then
  echo "  KEY REJECTED: the API evaluated auth and refused this key."
elif [[ "$r" == *unsupported_country* ]]; then
  echo "  KEY NOT EVALUATED (geo-block). Auth never ran; key validity unknown."
  echo "  Needs an exit whose country the service supports."
elif [[ "$r" == *'"data"'* ]]; then
  echo "  KEY VALID: API returned a model list."
else
  echo "  Reached the app layer; response differs between keys. Inspect above."
fi
