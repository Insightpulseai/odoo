#!/usr/bin/env python3
"""
DNS audit script using DNS-over-HTTPS (Cloudflare/Google).
Works in network-restricted environments where UDP DNS is blocked.
"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path


def parse_yaml(cfg_path):
    """Minimal YAML parser for our simple format."""
    text = Path(cfg_path).read_text(encoding="utf-8").splitlines()
    domain = None
    records = []
    for line in text:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("domain:"):
            domain = line.split(":", 1)[1].strip()
        if line.startswith("- {"):
            inner = line[line.find("{") + 1:line.rfind("}")]
            parts = [p.strip() for p in inner.split(",")]
            d = {}
            for p in parts:
                if ":" not in p:
                    continue
                k, v = p.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "priority":
                    try:
                        v = int(v)
                    except:
                        pass
                d[k] = v
            records.append(d)
    return domain, records


def query_dns_doh(fqdn, rtype):
    """Query DNS using Cloudflare DNS-over-HTTPS."""
    results = []
    try:
        # Cloudflare DoH endpoint
        url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(fqdn)}&type={rtype}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/dns-json",
            "User-Agent": "odoo-audit/1.0"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("Status") != 0:
            return results

        for answer in data.get("Answer", []):
            answer_type = answer.get("type")
            answer_data = answer.get("data", "")

            # Type mapping: 1=A, 5=CNAME, 15=MX, 16=TXT, 257=CAA
            if rtype == "A" and answer_type == 1:
                results.append(answer_data)
            elif rtype == "CNAME" and answer_type == 5:
                results.append(answer_data)
            elif rtype == "MX" and answer_type == 15:
                # MX data format: "priority hostname"
                results.append(answer_data)
            elif rtype == "TXT" and answer_type == 16:
                # TXT data comes with quotes
                txt = answer_data.strip('"')
                results.append(txt)
            elif rtype == "CAA" and answer_type == 257:
                results.append(answer_data)
            elif str(answer_type) == rtype:
                results.append(answer_data)

    except Exception as e:
        print(f"DoH query error for {fqdn} {rtype}: {e}", file=sys.stderr)
    return results


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "scripts/audit/dns_expected.yaml"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "out/dns_audit.json"

    domain, records = parse_yaml(cfg_path)
    if not domain:
        print("Error: domain missing in yaml", file=sys.stderr)
        sys.exit(1)

    results = []
    pass_ct = fail_ct = 0

    for r in records:
        name = r["name"]
        rtype = r["type"].upper()
        fqdn = domain if name == "@" else f"{name}.{domain}"

        got = query_dns_doh(fqdn, rtype)
        ok = False
        expected = r.get("value")
        contains = r.get("value_contains")
        prio = r.get("priority")

        # Normalize comparisons
        if expected:
            ok = any(g.strip().lower() == expected.strip().lower() for g in got)
        elif contains:
            ok = any(contains.lower() in g.lower() for g in got)
        else:
            ok = bool(got)

        # Special-case MX priority checks: DoH returns "10 mxa.mailgun.org."
        if rtype == "MX" and expected:
            exp = f"{prio} {expected}".strip().lower()
            ok = any(g.lower() == exp for g in got)

        results.append({
            "record": r,
            "fqdn": fqdn,
            "got": got,
            "pass": ok
        })
        if ok:
            pass_ct += 1
        else:
            fail_ct += 1

    report = {
        "domain": domain,
        "summary": {"pass": pass_ct, "fail": fail_ct, "total": pass_ct + fail_ct},
        "results": results
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({pass_ct}/{pass_ct + fail_ct} passing)")


if __name__ == "__main__":
    main()
