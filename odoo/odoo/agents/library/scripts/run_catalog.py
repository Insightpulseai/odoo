#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="agent-library/raw")
    ap.add_argument("--out", required=True, help="agent-library/dist")
    args = ap.parse_args()

    raw = Path(args.root)
    dist = Path(args.out)
    dist.mkdir(parents=True, exist_ok=True)

    catalogs = []
    for site_dir in sorted([p for p in raw.iterdir() if p.is_dir()]):
        out_file = dist / f"{site_dir.name}.catalog.json"
        subprocess.check_call(
            ["python3", "scripts/html_catalog.py", "--root", str(site_dir), "--out", str(out_file)]
        )
        catalogs.append(str(out_file))

    index = {"catalogs": catalogs}
    (dist / "catalog.index.json").write_text(json.dumps(index, indent=2))
    print(f"Wrote {dist / 'catalog.index.json'}")


if __name__ == "__main__":
    main()
