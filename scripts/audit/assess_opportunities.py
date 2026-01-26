#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

OUT_MD = Path(sys.argv[1] if len(sys.argv) > 1 else "out/INTEGRATIONS_OPPORTUNITIES.md")
OUT_MD.parent.mkdir(parents=True, exist_ok=True)

def load(p):
    if not Path(p).exists():
        return None
    return json.loads(Path(p).read_text(encoding="utf-8"))

dns = load("out/dns_audit.json") or {}
mailgun = load("out/mailgun_audit.json")
supabase = load("out/supabase_audit.json")
vercel = load("out/vercel_audit.json")

opps = []

# DNS/Mailgun quick heuristics
dmarc_txt = None
for r in dns.get("results", []):
    if r.get("record", {}).get("name") == "_dmarc.mg" and r.get("record", {}).get("type") == "TXT":
        got = r.get("got", [])
        if got:
            dmarc_txt = got[0]
if dmarc_txt and " p=none" in dmarc_txt.replace(";", "; "):
    opps.append({
        "area": "Mailgun / Deliverability",
        "title": "Graduate DMARC from p=none to p=quarantine (then p=reject) with staged enforcement",
        "why": "p=none is monitoring-only; staged enforcement reduces spoofing and improves alignment once SPF/DKIM are stable.",
        "evidence": dmarc_txt,
        "next_steps_cli": [
            "Generate staged DMARC records for mg subdomain (quarantine 10% → 50% → 100%, then reject).",
            "Validate DMARC aggregate reports already configured (rua/ruf).",
            "Run DNS audit after each change."
        ]
    })

# Supabase: if present, recommend MCP strategy
if supabase:
    opps.append({
        "area": "Supabase / AI",
        "title": "Standardize on MCP via Supabase Edge Functions (BYO MCP server) for agent tool access",
        "why": "Keeps AI tool access behind your controlled functions; avoids exposing internal MCP endpoints directly.",
        "evidence": f"supabase mode={supabase.get('mode')}",
        "next_steps_cli": [
            "Add an Edge Function MCP server for your agents (tools: SQL RPC, storage, queues).",
            "Gate with JWT/RLS; keep service_role only in function env.",
            "Add log drains / alerts for MCP tool calls."
        ]
    })

# Vercel: marketplace integration opportunities
if vercel:
    opps.append({
        "area": "Vercel / Platform",
        "title": "Inventory integrations & harden deployment surface (env vars, log drains, webhook routing)",
        "why": "Vercel integration APIs let you formalize installs, configuration, and observability for each deployed app.",
        "evidence": f"projects={vercel.get('project_count')}",
        "next_steps_cli": [
            "Enumerate projects and enforce baseline env var contract.",
            "Add log drains for runtime + function logs to your observability sink.",
            "If you plan marketplace distribution, create a Native Integration product and map categories."
        ]
    })

md = []
md.append("# Integrations & Opportunities Assessment (Automated)\n")
md.append("## Inputs Collected\n")
md.append(f"- DNS audit: {dns.get('summary', {}).get('pass','?')}/{dns.get('summary', {}).get('total','?')} records passing\n")
md.append(f"- Mailgun audit: {'present' if mailgun else 'not run'}\n")
md.append(f"- Supabase audit: {'present' if supabase else 'not run'}\n")
md.append(f"- Vercel audit: {'present' if vercel else 'not run'}\n")

md.append("\n## Opportunity Backlog (Ranked)\n")
if not opps:
    md.append("- No opportunities generated (run API checks and re-run).\n")
else:
    for i,o in enumerate(opps, start=1):
        md.append(f"### {i}. [{o['area']}] {o['title']}\n")
        md.append(f"**Why:** {o['why']}\n\n")
        md.append(f"**Evidence:** `{o['evidence']}`\n\n")
        md.append("**Next steps (CLI):**\n")
        for s in o["next_steps_cli"]:
            md.append(f"- {s}\n")
        md.append("\n")

OUT_MD.write_text("".join(md), encoding="utf-8")
print(f"Wrote {OUT_MD}")
