#!/usr/bin/env python3
import json, re, time
from collections import defaultdict

INV="out/repos_inventory.json"
FILES="out/repos_files.jsonl"

inv=json.load(open(INV,"r",encoding="utf-8"))
files=[json.loads(l) for l in open(FILES,"r",encoding="utf-8")]

# index
meta={r["url"].split("github.com/")[-1]: r for r in inv}
presence=defaultdict(dict)
counts=defaultdict(dict)

for row in files:
    repo=row["repo"]
    if "path" in row:
        presence[repo][f"dir:{row['path']}"]=row["exists"]
    if "file" in row:
        presence[repo][f"file:{row['file']}"]=row["exists"]
    if "releases" in row:
        counts[repo]["releases"]=row["releases"]
        counts[repo]["tags"]=row["tags"]

def b(repo, key): return bool(presence[repo].get(key, False))

def recency_score(iso):
    # ISO like 2026-01-26T...Z
    try:
        t=time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
        age_days=(time.time()-time.mktime(t))/86400.0
    except Exception:
        return 0
    if age_days <= 30: return 20
    if age_days <= 90: return 15
    if age_days <= 180: return 10
    if age_days <= 365: return 5
    return 0

out=[]
for repo_full, r in meta.items():
    if r.get("isArchived") or r.get("isFork"):
        continue
    p=presence[repo_full]
    c=counts[repo_full]

    # A Governance (25)
    A=0
    A += 6 if b(repo_full,"file:README.md") else 0
    A += 4 if b(repo_full,"file:LICENSE") else 0
    A += 4 if b(repo_full,"file:SECURITY.md") else 0
    A += 3 if b(repo_full,"file:CONTRIBUTING.md") else 0
    A += 3 if b(repo_full,"file:.github/CODEOWNERS") else 0
    A += 2 if b(repo_full,"file:CODE_OF_CONDUCT.md") else 0
    A += 3 if b(repo_full,"file:.github/dependabot.yml") else 0
    A=min(A,25)

    # B Automation (25)
    B=0
    B += 10 if b(repo_full,"dir:.github/workflows") else 0
    # heuristic: if workflows dir exists, give partial CI credit; deep inspection can be added later
    B += 8 if b(repo_full,"dir:.github/workflows") else 0
    B += 2 if b(repo_full,"dir:.devcontainer") else 0
    B=min(B,25)

    # C Docs (15)
    C=0
    C += 6 if b(repo_full,"dir:docs") else 0
    C += 4 if b(repo_full,"dir:spec") else 0
    C += 3 if b(repo_full,"dir:architecture") else 0
    C=min(C,15)

    # D Delivery maturity (15)
    D=0
    rel=c.get("releases",0)
    tags=c.get("tags",0)
    D += 10 if rel and rel>0 else (4 if tags and tags>0 else 0)
    D += 5 if tags and tags>=5 else (2 if tags and tags>0 else 0)
    D=min(D,15)

    # E Activity (20)
    E=recency_score(r.get("pushedAt") or r.get("updatedAt") or "")
    E=min(E,20)

    total=A+B+C+D+E
    out.append({
        "repo": repo_full,
        "total": total,
        "breakdown": {"governance":A,"automation":B,"docs":C,"delivery":D,"activity":E},
        "evidence": {
            "pushedAt": r.get("pushedAt"),
            "updatedAt": r.get("updatedAt"),
            "stars": r.get("stargazerCount"),
            "forks": r.get("forkCount"),
            "has_workflows": b(repo_full,"dir:.github/workflows"),
            "has_docs": b(repo_full,"dir:docs"),
            "has_spec": b(repo_full,"dir:spec")
        }
    })

out.sort(key=lambda x: x["total"], reverse=True)
json.dump(out, open("out/repos_scored.json","w",encoding="utf-8"), indent=2)

# Markdown summary
lines=[]
lines.append("# Top Repositories by Completeness\n")
lines.append("| Rank | Repo | Score | Gov | Auto | Docs | Delivery | Activity | Evidence |")
lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---|")
for i,row in enumerate(out[:10], start=1):
    b=row["breakdown"]; e=row["evidence"]
    ev=f"pushedAt={e.get('pushedAt')} workflows={e.get('has_workflows')} docs={e.get('has_docs')} spec={e.get('has_spec')}"
    lines.append(f"| {i} | `{row['repo']}` | {row['total']} | {b['governance']} | {b['automation']} | {b['docs']} | {b['delivery']} | {b['activity']} | {ev} |")
open("out/TOP_REPOS.md","w",encoding="utf-8").write("\n".join(lines)+"\n")

# Flagship recommendation (top1, with rationale)
top=out[0] if out else None
if top:
    b=top["breakdown"]
    txt=f"""# Flagship Repo Recommendation

## Recommended: `{top['repo']}`

Why:
- Highest overall completeness score ({top['total']})
- Governance={b['governance']}/25, Automation={b['automation']}/25, Docs={b['docs']}/15, Delivery={b['delivery']}/15, Activity={b['activity']}/20

Next actions:
- Link this repo from org profile README and enterprise catalog as primary "flagship"
- Ensure it has: SECURITY.md, CODEOWNERS, CI workflows, release tagging, and a docs portal entry
"""
    open("out/FLAGSHIP_REPO_RECOMMENDATION.md","w",encoding="utf-8").write(txt)
