import ast, glob, json, os, re
from datetime import datetime

ROOT = os.getcwd()

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def find_first(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def parse_manifest(path):
    try:
        return ast.literal_eval(read(path))
    except Exception as e:
        return {"_error": str(e), "_path": path}

def scan_manifests():
    out=[]
    for mf in glob.glob("addons/**/**/__manifest__.py", recursive=True):
        d = parse_manifest(mf)
        out.append({
            "path": mf,
            "module": d.get("name"),
            "technical": os.path.basename(os.path.dirname(mf)),
            "depends": d.get("depends", []),
        })
    return out

def scan_seed_scripts():
    hits=[]
    patterns = [
        "data/seed/*.py",
        "data/finance_seed/*.py",
        "data/**/*.py"
    ]
    files = []
    for pat in patterns:
        files.extend(glob.glob(pat, recursive=True))

    for f in sorted(set(files)):
        if os.path.isfile(f):
            s = read(f)
            models = sorted(set(re.findall(r"env\[['\"]([a-z0-9_.]+)['\"]\]", s)))
            hits.append({
                "file": f,
                "models": models,
                "mentions_base_automation": ("base_automation" in s) or ("base.automation" in s),
            })
    return hits

def scan_compose():
    compose = find_first(["docker-compose.yml", "compose.yaml", "compose.yml"])
    if not compose:
        return {"present": False}
    return {"present": True, "path": compose, "raw_excerpt": read(compose)[:4000]}

def enterprise_smells():
    # heuristic only; you will refine later with a curated mapping table
    patterns = [
        ("studio", r"\bstudio\b"),
        ("web_enterprise", r"\bweb_enterprise\b"),
        ("account_accountant", r"\baccount_accountant\b"),
        ("sale_enterprise", r"\bsale_enterprise\b"),
        ("project_enterprise", r"\bproject_enterprise\b"),
        ("sign", r"\bsign\b"),
        ("documents", r"\bdocuments\b"),
    ]
    files = glob.glob("addons/**/**/__manifest__.py", recursive=True) + sorted(glob.glob("data/**/*.py", recursive=True))
    found=[]
    for f in files:
        if os.path.isfile(f):
            s = read(f).lower()
            for key, rx in patterns:
                if re.search(rx, s):
                    found.append({"token": key, "file": f})
    # dedupe
    uniq=[]
    seen=set()
    for x in found:
        k=(x["token"], x["file"])
        if k not in seen:
            uniq.append(x); seen.add(k)
    return uniq

def md_render(data):
    lines=[]
    lines.append(f"# Prod-Canonical Install Requirements")
    lines.append("")
    lines.append(f"_Generated: {data['generated_at']}_")
    lines.append("")
    lines.append("## What exists in this repo (truth scan)")
    lines.append("")
    lines.append(f"- Docker compose present: **{data['docker']['present']}**")
    if data["docker"]["present"]:
        lines.append(f"- Compose file: `{data['docker']['path']}`")
    lines.append(f"- Custom addons detected: **{len(data['odoo']['custom_addons'])}**")
    lines.append(f"- Seed scripts detected: **{len(data['scripts']['seed_scripts'])}**")
    lines.append("")
    lines.append("## Odoo modules implied (from custom addon manifests)")
    lines.append("")
    deps=set()
    for a in data["odoo"]["custom_addons"]:
        for d in a.get("depends", []):
            if isinstance(d, str):
                deps.add(d)
    for d in sorted(deps):
        lines.append(f"- `{d}`")
    lines.append("")
    lines.append("## Models touched by seed scripts (implied functional areas)")
    lines.append("")
    if not data["scripts"]["seed_scripts"]:
        lines.append("- No seed scripts detected in data/seed/ or data/finance_seed/")
    else:
        for s in data["scripts"]["seed_scripts"]:
            lines.append(f"### `{s['file']}`")
            if s["models"]:
                for m in s["models"]:
                    lines.append(f"- `{m}`")
            else:
                lines.append("- No models detected")
            lines.append("")
    lines.append("## Enterprise-only smell scan (heuristic)")
    lines.append("")
    if not data["enterprise_smells"]:
        lines.append("- None detected by heuristic scan.")
    else:
        for x in data["enterprise_smells"]:
            lines.append(f"- `{x['token']}` in `{x['file']}`")
    lines.append("")
    lines.append("## Verification (CLI-only)")
    lines.append("")
    lines.append("```bash")
    lines.append("# when docker is up")
    lines.append("docker compose up -d")
    lines.append("docker ps")
    lines.append("")
    lines.append("# Container names from actual scan:")
    lines.append("# - odoo-core (port 8069)")
    lines.append("# - odoo-dev (port 9069)")
    lines.append("# - odoo-marketing (port 8070)")
    lines.append("# - odoo-accounting (port 8071)")
    lines.append("")
    lines.append("# run seed scripts (adjust container name and db)")
    if data["scripts"]["seed_scripts"]:
        for s in data["scripts"]["seed_scripts"]:
            lines.append(f"# docker exec -i odoo-core odoo shell -d odoo_core < {s['file']}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)

def main():
    data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "docker": scan_compose(),
        "odoo": {"custom_addons": scan_manifests()},
        "scripts": {"seed_scripts": scan_seed_scripts()},
        "enterprise_smells": enterprise_smells(),
        "assumptions": [
            "This document reflects repo scan only (no external Odoo source introspection).",
            "Enterprise-only scan is heuristic; finalize with explicit mapping table later."
        ]
    }
    os.makedirs("docs", exist_ok=True)
    md_path = "docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.md"
    js_path = "docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.json"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_render(data))
    with open(js_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(md_path)
    print(js_path)

if __name__ == "__main__":
    main()
