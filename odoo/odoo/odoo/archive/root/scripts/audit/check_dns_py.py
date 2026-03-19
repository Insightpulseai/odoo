#!/usr/bin/env python3
"""
DNS audit script using dnspython (no dig dependency).
Validates DNS records against expected configuration.
"""
import json
import sys
from pathlib import Path

try:
    import dns.resolver
    import dns.exception
except ImportError:
    print("Installing dnspython...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dnspython", "-q"])
    import dns.resolver
    import dns.exception

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


def query_dns(fqdn, rtype):
    """Query DNS records using dnspython with public resolvers."""
    results = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']  # Use public DNS
        resolver.timeout = 5
        resolver.lifetime = 10
        answers = resolver.resolve(fqdn, rtype)
        for rdata in answers:
            if rtype == "MX":
                results.append(f"{rdata.preference} {rdata.exchange.to_text()}")
            elif rtype == "TXT":
                # Join TXT record parts
                results.append("".join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings]))
            elif rtype == "CAA":
                results.append(f'{rdata.flags} {rdata.tag.decode()} "{rdata.value.decode()}"')
            elif rtype == "CNAME":
                results.append(rdata.target.to_text())
            else:
                results.append(rdata.to_text())
    except dns.resolver.NXDOMAIN:
        pass
    except dns.resolver.NoAnswer:
        pass
    except dns.exception.Timeout:
        pass
    except Exception as e:
        print(f"DNS query error for {fqdn} {rtype}: {e}", file=sys.stderr)
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

        got = query_dns(fqdn, rtype)
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

        # Special-case MX priority checks
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
