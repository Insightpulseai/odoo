#!/usr/bin/env python3
"""
Map a documentation catalogue to Odoo CE/OCA 18 modules based on keyword rules.
Reads catalog.json from crawl_docs.py and odoo_map.yaml rules, outputs mapping CSV/MD.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

import yaml


@dataclass
class Rule:
    name: str
    keywords: List[str]
    odoo_ce_modules: List[str]
    oca_repos: List[str]


@dataclass
class Match:
    url: str
    title: str
    h1: str
    breadcrumbs: List[str]
    section: str
    word_count: int
    score: int
    matched_keywords: List[str] = field(default_factory=list)


def load_rules(yaml_path: Path) -> List[Rule]:
    """Load mapping rules from YAML file."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules = []
    for name, cfg in data.get("targets", {}).items():
        rules.append(Rule(
            name=name,
            keywords=cfg.get("keywords", []),
            odoo_ce_modules=cfg.get("odoo_ce_modules", []),
            oca_repos=cfg.get("oca_repos", [])
        ))
    return rules


def score(text: str, rule: Rule) -> tuple[int, List[str]]:
    """
    Score text relevance to rule based on keyword matching.
    Returns (score, matched_keywords).

    Scoring:
    - Exact keyword match: +3
    - All tokens of keyword found: +1
    """
    t = text.lower()
    s = 0
    matched = []

    for kw in rule.keywords:
        kw_lower = kw.lower()
        if kw_lower in t:
            s += 3
            matched.append(kw)
        else:
            # Token-based fallback (handle multi-word keywords)
            toks = re.split(r"[^a-z0-9]+", kw_lower)
            toks = [tok for tok in toks if tok]
            if toks and all(tok in t for tok in toks):
                s += 1
                matched.append(kw)

    return s, matched


def classify(node: dict, rules: List[Rule]) -> Dict[str, Match]:
    """
    Classify a single node against all rules.
    Returns dict of {rule_name: Match} for rules with score > 0.
    """
    # Combine searchable text
    searchable = " ".join([
        node.get("title", ""),
        node.get("h1", ""),
        node.get("section", ""),
        " ".join(node.get("breadcrumbs", []))
    ])

    matches = {}
    for rule in rules:
        s, matched_kw = score(searchable, rule)
        if s > 0:
            matches[rule.name] = Match(
                url=node["url"],
                title=node.get("title", ""),
                h1=node.get("h1", ""),
                breadcrumbs=node.get("breadcrumbs", []),
                section=node.get("section", ""),
                word_count=node.get("word_count", 0),
                score=s,
                matched_keywords=matched_kw
            )

    return matches


def write_csv(out_path: Path, grouped: Dict[str, List[Match]], rules_by_name: Dict[str, Rule]):
    """Write mapping results to CSV."""
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "rule",
            "url",
            "title",
            "section",
            "score",
            "matched_keywords",
            "odoo_ce_modules",
            "oca_repos"
        ])

        for rule_name in sorted(grouped.keys()):
            matches = grouped[rule_name]
            rule = rules_by_name[rule_name]

            for m in matches:
                w.writerow([
                    rule_name,
                    m.url,
                    m.title or m.h1,
                    m.section,
                    m.score,
                    ", ".join(m.matched_keywords),
                    ", ".join(rule.odoo_ce_modules),
                    ", ".join(rule.oca_repos)
                ])


def write_markdown(out_path: Path, grouped: Dict[str, List[Match]], rules_by_name: Dict[str, Rule]):
    """Write mapping results to Markdown."""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Odoo CE/OCA 18 Mapping\n\n")
        f.write("Generated from SAP Concur documentation catalogue.\n\n")

        total_pages = sum(len(matches) for matches in grouped.values())
        f.write(f"**Total Mapped Pages**: {total_pages}\n\n")
        f.write("---\n\n")

        for rule_name in sorted(grouped.keys()):
            matches = grouped[rule_name]
            rule = rules_by_name[rule_name]

            f.write(f"## {rule_name.replace('_', ' ').title()}\n\n")
            f.write(f"**Odoo CE Modules**: {', '.join(rule.odoo_ce_modules)}\n\n")
            f.write(f"**OCA Repositories**: {', '.join(rule.oca_repos)}\n\n")
            f.write(f"**Matched Pages**: {len(matches)}\n\n")

            # Sort by score descending
            for m in sorted(matches, key=lambda x: x.score, reverse=True)[:20]:
                label = m.h1 or m.title
                kw_str = ", ".join(m.matched_keywords[:5])
                f.write(f"- [{label}]({m.url}) (score: {m.score}, keywords: {kw_str})\n")

            if len(matches) > 20:
                f.write(f"\n*...and {len(matches) - 20} more pages*\n")

            f.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, help="Path to catalog.json from crawl_docs.py")
    ap.add_argument("--rules", required=True, help="Path to odoo_map.yaml")
    ap.add_argument("--out", required=True, help="Output directory for mapping CSV/MD")
    args = ap.parse_args()

    catalog_path = Path(args.catalog)
    rules_path = Path(args.rules)
    out_dir = Path(args.out)

    # Load rules
    print(f"[1/4] Loading rules from {rules_path}")
    rules = load_rules(rules_path)
    rules_by_name = {r.name: r for r in rules}
    print(f"      Loaded {len(rules)} rules: {', '.join(r.name for r in rules)}")

    # Load catalog
    print(f"[2/4] Loading catalog from {catalog_path}")
    with open(catalog_path, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    print(f"      Loaded {len(nodes)} pages")

    # Classify all nodes
    print(f"[3/4] Classifying pages against rules")
    grouped: Dict[str, List[Match]] = defaultdict(list)

    for node in nodes:
        matches = classify(node, rules)
        for rule_name, match in matches.items():
            grouped[rule_name].append(match)

    # Report stats
    for rule_name in sorted(grouped.keys()):
        print(f"      {rule_name}: {len(grouped[rule_name])} pages")

    # Write outputs
    print(f"[4/4] Writing outputs to {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "mapping.csv"
    md_path = out_dir / "mapping.md"

    write_csv(csv_path, grouped, rules_by_name)
    print(f"      CSV: {csv_path}")

    write_markdown(md_path, grouped, rules_by_name)
    print(f"      Markdown: {md_path}")

    print("[ok] Mapping complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
