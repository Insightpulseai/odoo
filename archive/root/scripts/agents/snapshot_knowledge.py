#!/usr/bin/env python3
"""Snapshot knowledge corpus with content-addressed hashing."""
import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "ssot/agents/knowledge"

SCAN_DIRS = ["docs", "spec", "ssot"]
EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".txt", ".dbml", ".mmd", ".puml"}

def hash_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

def scan_knowledge_corpus():
    corpus = []

    for scan_dir in SCAN_DIRS:
        base = REPO_ROOT / scan_dir
        if not base.is_dir():
            continue

        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in EXTENSIONS:
                continue
            if ".git" in str(p) or "node_modules" in str(p):
                continue

            rel = str(p.relative_to(REPO_ROOT))
            stat = p.stat()

            corpus.append({
                "path": rel,
                "domain": scan_dir,
                "extension": p.suffix.lower(),
                "sha256_prefix": hash_file(p),
                "size_bytes": stat.st_size,
                "lines": sum(1 for _ in open(p, errors="replace")),
            })

    return corpus

def compute_summary(corpus):
    by_domain = {}
    by_ext = {}
    total_bytes = 0
    total_lines = 0

    for item in corpus:
        d = item["domain"]
        e = item["extension"]
        by_domain[d] = by_domain.get(d, 0) + 1
        by_ext[e] = by_ext.get(e, 0) + 1
        total_bytes += item["size_bytes"]
        total_lines += item["lines"]

    return {
        "total_files": len(corpus),
        "total_bytes": total_bytes,
        "total_lines": total_lines,
        "by_domain": by_domain,
        "by_extension": by_ext,
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    corpus = scan_knowledge_corpus()
    summary = compute_summary(corpus)

    registry = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus": corpus,
        "summary": summary,
    }

    out_file = OUT / "knowledge_registry.json"
    out_file.write_text(json.dumps(registry, indent=2) + "\n")

    print(f"Knowledge corpus: {summary['total_files']} files, {summary['total_lines']} lines, {summary['total_bytes']} bytes")
    print(f"  By domain: {json.dumps(summary['by_domain'])}")
    print(f"Written to: {out_file.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    main()
