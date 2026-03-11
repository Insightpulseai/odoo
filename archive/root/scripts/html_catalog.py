#!/usr/bin/env python3
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

# pip install beautifulsoup4 lxml


def text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def extract_doc(path: Path) -> dict:
    html = path.read_text(errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    title = text((soup.title.string if soup.title else "") or "")
    h1 = text((soup.find("h1").get_text(" ") if soup.find("h1") else "") or "")

    # Heuristics for "feature" pages / doc pages
    meta = {}
    for m in soup.find_all("meta"):
        if m.get("name") in ("description", "keywords"):
            meta[m["name"]] = text(m.get("content", ""))

    links = []
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        label = text(a.get_text(" "))
        if href and label:
            links.append({"label": label[:160], "href": href[:500]})

    # Pull headings as "outline"
    outline = []
    for tag in soup.find_all(["h2", "h3"]):
        outline.append({"tag": tag.name, "text": text(tag.get_text(" "))[:200]})

    return {
        "file": str(path),
        "title": title,
        "h1": h1,
        "meta": meta,
        "outline": outline[:200],
        "links": links[:400],
    }


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="directory containing mirrored site")
    ap.add_argument("--out", required=True, help="output json path")
    args = ap.parse_args()

    root = Path(args.root)
    pages = []
    for p in root.rglob("*.html"):
        try:
            pages.append(extract_doc(p))
        except Exception:
            continue

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"pages": pages}, indent=2))
    print(f"Wrote {args.out} with {len(pages)} pages")


if __name__ == "__main__":
    main()
