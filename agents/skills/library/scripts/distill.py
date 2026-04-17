#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
import yaml
from datetime import datetime


def slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:80] or "item"


def extract_claims(outline_items):
    # heuristic: treat headings as "claims" seeds
    claims = []
    for o in outline_items:
        t = (o.get("text") or "").strip()
        if t and len(t) >= 6:
            claims.append(t)
    return claims[:120]


def to_atoms(claims):
    atoms = []
    for c in claims:
        # atom form: verb+noun is ideal; heuristic fallback
        atom = c
        atoms.append(
            {
                "id": f"atom_{slug(atom)[:60]}",
                "label": atom[:120],
                "tags": [],
                "synonyms": [],
                "evidence": [],  # filled later
            }
        )
    # de-dupe by id
    seen = set()
    out = []
    for a in atoms:
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        out.append(a)
    return out[:200]


def to_ux_patterns(pages):
    patterns = []
    # heuristic pattern detectors based on presence of outline keywords
    keymap = {
        "accordion": ["faq", "frequently asked", "accordion"],
        "card_grid": ["card", "tiles", "use cases"],
        "breadcrumb": ["breadcrumb"],
        "tabs": ["tab", "what's new", "upcoming"],
        "carousel": ["carousel", "stories", "customers", "logos"],
        "search_bar": ["search"],
    }
    joined = " ".join(
        " ".join([o.get("text", "") for o in p.get("outline", [])]) for p in pages
    ).lower()
    for pid, kws in keymap.items():
        if any(k in joined for k in kws):
            patterns.append(
                {
                    "id": f"ux_{pid}",
                    "name": pid,
                    "intent": "",
                    "recipe": {"components": [], "layout": "", "a11y_notes": []},
                    "evidence": [],
                }
            )
    return patterns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, help="agent-library/dist")
    ap.add_argument("--out", required=True, help="agent-library/dist")
    ap.add_argument("--evidence", required=True, help="agent-library/evidence")
    args = ap.parse_args()

    dist = Path(args.catalog)
    out = Path(args.out)
    evid = Path(args.evidence)
    out.mkdir(parents=True, exist_ok=True)
    evid.mkdir(parents=True, exist_ok=True)

    idx = json.loads((dist / "catalog.index.json").read_text())
    all_pages = []
    for cat_path in idx["catalogs"]:
        data = json.loads(Path(cat_path).read_text())
        all_pages.extend(data.get("pages", []))

    # Evidence: store outlines as traceable excerpts. (URLs are not always present in mirrored HTML; we keep file paths.)
    evidence_path = evid / f"evidence_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    with evidence_path.open("w", encoding="utf-8") as f:
        for p in all_pages:
            file_path = p.get("file", "")
            title = p.get("title", "")
            h1 = p.get("h1", "")
            for o in p.get("outline", [])[:60]:
                row = {
                    "source_file": file_path,
                    "title": title,
                    "h1": h1,
                    "heading": o.get("text", ""),
                    "ts_utc": datetime.utcnow().isoformat() + "Z",
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Atoms and patterns
    claims = []
    for p in all_pages:
        claims.extend(extract_claims(p.get("outline", [])))
    atoms = to_atoms(claims)
    ux = to_ux_patterns(all_pages)

    # Link first evidence rows to first atoms/patterns (placeholder binding; your agent run refines)
    # Keep deterministic: map by index
    ev_ref = evidence_path.name
    for i, a in enumerate(atoms):
        a["evidence"] = [{"ref": ev_ref, "hint": a["label"]}]
    for u in ux:
        u["evidence"] = [{"ref": ev_ref, "hint": u["id"]}]

    (out / "capability_atoms.yaml").write_text(
        yaml.safe_dump({"version": "1.0.0", "atoms": atoms}, sort_keys=False, allow_unicode=True)
    )

    (out / "ux_patterns.yaml").write_text(
        yaml.safe_dump({"version": "1.0.0", "patterns": ux}, sort_keys=False, allow_unicode=True)
    )

    print(
        f"Wrote:\n- {out / 'capability_atoms.yaml'}\n- {out / 'ux_patterns.yaml'}\n- {evidence_path}"
    )


if __name__ == "__main__":
    main()
