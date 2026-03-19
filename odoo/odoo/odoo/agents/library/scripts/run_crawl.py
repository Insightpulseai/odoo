#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sources = yaml.safe_load(Path(args.sources).read_text())
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    for s in sources.get("sources", []):
        sid = s["id"]
        url = s["base_url"]
        out_dir = out_root / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[crawl] {sid}: {url} -> {out_dir}")
        subprocess.check_call(["bash", "scripts/crawl_site.sh", url, str(out_dir)])


if __name__ == "__main__":
    main()
