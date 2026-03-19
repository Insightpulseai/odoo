#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Replace legacy/picky ":*" patterning with wildcard "*"
# Example recommended by the error:
#   Bash(npm run:*)  -> Bash(npm run *)
# Also fixes cases where ":*" appears mid-pattern:
#   Bash(npm run:* lint) -> Bash(npm run * lint)
#
# We ONLY touch strings inside JSON files, and ONLY when the string contains "Bash(" and ":*".

BASH_PAT = re.compile(r"^Bash\((.*)\)$")

def normalize_cmd(cmd: str) -> str:
    # Convert ":*" to " *" (wildcard matching) and normalize whitespace.
    cmd2 = cmd.replace(":*", " *")
    cmd2 = re.sub(r"\s+", " ", cmd2).strip()
    return cmd2

def walk(v: Any) -> Any:
    if isinstance(v, dict):
        return {k: walk(val) for k, val in v.items()}
    if isinstance(v, list):
        return [walk(x) for x in v]
    if isinstance(v, str):
        if ":*" in v and "Bash(" in v:
            m = BASH_PAT.match(v.strip())
            if m:
                inner = m.group(1)
                fixed = normalize_cmd(inner)
                return f"Bash({fixed})"
        return v
    return v

def main() -> int:
    root = Path(".")
    candidates = []

    # Common Claude Code settings locations in repos
    for p in [
        root / ".claude",
        root,
    ]:
        if p.exists():
            for f in p.rglob("*.json"):
                # avoid node_modules / huge vendor dirs just in case
                if "node_modules" in f.parts or ".git" in f.parts:
                    continue
                candidates.append(f)

    changed = 0
    for f in sorted(set(candidates)):
        try:
            txt = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if ":*" not in txt or "Bash(" not in txt:
            continue

        try:
            data = json.loads(txt)
        except Exception:
            # not valid JSON; skip
            continue

        new_data = walk(data)
        if new_data != data:
            # write pretty + stable
            f.write_text(json.dumps(new_data, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")
            changed += 1
            print(f"fixed: {f}")

    print(f"done: {changed} file(s) updated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
