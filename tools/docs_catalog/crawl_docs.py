#!/usr/bin/env python3
"""
Recursively crawl a documentation "catalogue" page and emit:
- catalog.json (nodes)
- edges.csv (link graph)
- catalog.md (readable outline)

Default is safe-ish: same-host only, dedupe, page limit, basic HTML parsing.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

UA = "docs-catalog-bot/1.0 (+https://insightpulseai.net)"
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".zip", ".gz", ".tar", ".tgz", ".mp4", ".mov", ".avi", ".webm")


@dataclass
class Node:
    url: str
    title: str
    h1: str
    breadcrumbs: List[str]
    section: str
    status: int
    word_count: int
    discovered_from: Optional[str]


def norm_url(u: str) -> str:
    u, _frag = urldefrag(u)
    return u.rstrip("/")


def looks_like_doc(url: str) -> bool:
    p = urlparse(url)
    if not p.scheme.startswith("http"):
        return False
    if any(p.path.lower().endswith(ext) for ext in SKIP_EXT):
        return False
    return True


def extract_breadcrumbs(soup: BeautifulSoup) -> List[str]:
    # SAP Help commonly has breadcrumb nav; we try generic patterns.
    crumbs: List[str] = []

    # 1) aria-label breadcrumb nav
    nav = soup.find("nav", attrs={"aria-label": re.compile("breadcrumb", re.I)})
    if nav:
        for a in nav.find_all(["a", "span"], recursive=True):
            t = a.get_text(" ", strip=True)
            if t and t not in crumbs:
                crumbs.append(t)

    # 2) any element with "breadcrumb" class
    if not crumbs:
        bc = soup.select_one(".breadcrumb, .breadcrumbs, [class*='breadcrumb']")
        if bc:
            parts = [x.get_text(" ", strip=True) for x in bc.find_all(["a", "span", "li"])]
            crumbs = [p for p in parts if p]

    return crumbs[:12]


def classify_section(url: str, crumbs: List[str]) -> str:
    hay = " ".join(crumbs + [url]).lower()

    # SAP-style
    for k in ["discover", "what's new", "whats new", "implement", "integrate", "use", "support", "resources", "reference", "operate", "security"]:
        if k in hay:
            return k.replace("whats", "what's")

    # Generic
    if "admin" in hay:
        return "administration"
    if "api" in hay:
        return "api"
    if "release" in hay:
        return "release notes"

    return "docs"


def extract_title_h1(soup: BeautifulSoup) -> Tuple[str, str]:
    title = (soup.title.get_text(" ", strip=True) if soup.title else "").strip()
    h1_el = soup.find(["h1"])
    h1 = (h1_el.get_text(" ", strip=True) if h1_el else "").strip()
    return title[:300], h1[:300]


def word_count(soup: BeautifulSoup) -> int:
    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return len(text.split())


def extract_links(base_url: str, soup: BeautifulSoup) -> List[Tuple[str, str]]:
    links: List[Tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href or href.startswith("#"):
            continue
        u = urljoin(base_url, href)
        u = norm_url(u)
        if not looks_like_doc(u):
            continue
        txt = a.get_text(" ", strip=True)[:200]
        links.append((u, txt))
    return links


def crawl(seed: str, max_pages: int, delay: float, timeout: int) -> Tuple[Dict[str, Node], List[Tuple[str, str, str]]]:
    seed = norm_url(seed)
    host = urlparse(seed).netloc

    q = deque([(seed, None)])  # (url, discovered_from)
    seen: Set[str] = set()
    nodes: Dict[str, Node] = {}
    edges: List[Tuple[str, str, str]] = []  # src, dst, anchor_text

    s = requests.Session()
    s.headers.update({"User-Agent": UA})

    while q and len(nodes) < max_pages:
        url, parent = q.popleft()
        if url in seen:
            continue
        seen.add(url)

        p = urlparse(url)
        if p.netloc != host:
            continue

        try:
            r = s.get(url, timeout=timeout)
            status = r.status_code
            html = r.text if status == 200 else ""
        except Exception:
            status = 0
            html = ""

        soup = BeautifulSoup(html, "html.parser") if html else BeautifulSoup("", "html.parser")
        title, h1 = extract_title_h1(soup)
        crumbs = extract_breadcrumbs(soup)
        section = classify_section(url, crumbs)
        wc = word_count(soup) if html else 0

        nodes[url] = Node(
            url=url,
            title=title or h1 or url,
            h1=h1,
            breadcrumbs=crumbs,
            section=section,
            status=status,
            word_count=wc,
            discovered_from=parent,
        )

        if status == 200 and html:
            for (dst, anchor_txt) in extract_links(url, soup):
                dp = urlparse(dst)
                if dp.netloc != host:
                    continue
                edges.append((url, dst, anchor_txt))
                if dst not in seen and len(nodes) + len(q) < max_pages * 3:
                    q.append((dst, url))

        if delay > 0:
            time.sleep(delay)

    return nodes, edges


def write_outputs(out_dir: str, nodes: Dict[str, Node], edges: List[Tuple[str, str, str]]) -> None:
    import os
    os.makedirs(out_dir, exist_ok=True)

    # catalog.json
    with open(os.path.join(out_dir, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump([asdict(n) for n in nodes.values()], f, ensure_ascii=False, indent=2)

    # edges.csv
    with open(os.path.join(out_dir, "edges.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src", "dst", "anchor_text"])
        for src, dst, txt in edges:
            w.writerow([src, dst, txt])

    # catalog.md (simple grouped outline by section)
    grouped: Dict[str, List[Node]] = {}
    for n in nodes.values():
        grouped.setdefault(n.section, []).append(n)
    for k in grouped:
        grouped[k].sort(key=lambda x: (x.breadcrumbs, x.title))

    with open(os.path.join(out_dir, "catalog.md"), "w", encoding="utf-8") as f:
        f.write(f"# Documentation Catalogue\n\nTotal pages: {len(nodes)}\n\n")
        for section in sorted(grouped.keys()):
            f.write(f"## {section.title()}\n\n")
            for n in grouped[section]:
                label = n.h1 or n.title
                f.write(f"- [{label}]({n.url})\n")
            f.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True, help="Seed catalogue URL")
    ap.add_argument("--out", default="out", help="Output directory")
    ap.add_argument("--max-pages", type=int, default=400, help="Max pages to crawl")
    ap.add_argument("--delay", type=float, default=0.15, help="Delay between requests (seconds)")
    ap.add_argument("--timeout", type=int, default=20, help="HTTP timeout (seconds)")
    args = ap.parse_args()

    nodes, edges = crawl(args.seed, args.max_pages, args.delay, args.timeout)
    write_outputs(args.out, nodes, edges)
    print(f"[ok] crawled={len(nodes)} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
