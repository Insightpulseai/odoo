#!/usr/bin/env bash
set -euo pipefail

CFG="${1:-scripts/audit/dns_expected.yaml}"
OUT_JSON="${2:-out/dns_audit.json}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1" >&2; exit 2; }; }
need python3
need dig

python3 - <<'PY' "$CFG" "$OUT_JSON"
import json, re, sys, subprocess

cfg_path, out_path = sys.argv[1], sys.argv[2]

# Minimal YAML-ish parser (enough for this file)
# Assumption: simple "key: value" + list of inline dicts "{ k: v, ... }"
text = open(cfg_path, "r", encoding="utf-8").read().splitlines()
domain = None
records = []
for line in text:
    line=line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("domain:"):
        domain=line.split(":",1)[1].strip()
    if line.startswith("- {"):
        inner=line[line.find("{")+1:line.rfind("}")]
        parts=[p.strip() for p in inner.split(",")]
        d={}
        for p in parts:
            k,v=p.split(":",1)
            k=k.strip()
            v=v.strip().strip('"').strip("'")
            # coerce
            if k=="priority":
                try: v=int(v)
                except: pass
            d[k]=v
        records.append(d)

if not domain:
    raise SystemExit("domain missing in yaml")

def dig(name, rtype):
    fqdn = domain if name=="@" else f"{name}.{domain}"
    cmd=["dig","+short",fqdn,rtype]
    out=subprocess.check_output(cmd, text=True).strip().splitlines()
    return [o.strip() for o in out if o.strip()]

results=[]
pass_ct=fail_ct=0

for r in records:
    name=r["name"]
    rtype=r["type"].upper()
    got=dig(name, rtype)
    ok=False
    expected=r.get("value")
    contains=r.get("value_contains")
    prio=r.get("priority")

    # Normalize comparisons
    if expected:
        ok = any(g.strip().lower()==expected.strip().lower() for g in got)
    elif contains:
        ok = any(contains.lower() in g.lower() for g in got)
    else:
        ok = bool(got)

    # Special-case MX priority checks: dig +short returns "10 mxa.mailgun.org."
    if rtype=="MX" and expected:
        exp = f"{prio} {expected}".strip().lower()
        ok = any(g.lower()==exp for g in got)

    results.append({
        "record": r,
        "fqdn": domain if name=="@" else f"{name}.{domain}",
        "got": got,
        "pass": ok
    })
    if ok: pass_ct += 1
    else: fail_ct += 1

report={
    "domain": domain,
    "summary": {"pass": pass_ct, "fail": fail_ct, "total": pass_ct+fail_ct},
    "results": results
}
open(out_path,"w",encoding="utf-8").write(json.dumps(report, indent=2))
print(f"Wrote {out_path} ({pass_ct}/{pass_ct+fail_ct} passing)")
PY
