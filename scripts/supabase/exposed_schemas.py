#!/usr/bin/env python3
import re
from pathlib import Path
import json
import sys

CFG = Path("supabase/config.toml")
if not CFG.exists():
  print("ERROR: supabase/config.toml not found (adjust path in scripts/supabase/exposed_schemas.py).", file=sys.stderr)
  sys.exit(1)

txt = CFG.read_text(encoding="utf-8")

# Supabase config commonly includes API schemas. We extract any list-looking assignment like:
# schemas = ["public", "storage", ...]
m = re.search(r'(?m)^\s*schemas\s*=\s*\[(.*?)\]\s*$', txt, re.DOTALL)
schemas = []
if m:
  inner = m.group(1)
  schemas = re.findall(r'"([^"]+)"', inner)

# Fallback: include "public" if nothing found (safe default, but still explicit)
if not schemas:
  schemas = ["public"]

out = {
  "schemas_exposed_by_api": schemas,
  "source": str(CFG),
}

Path("docs/architecture/runtime_identifiers.json").parent.mkdir(parents=True, exist_ok=True)
Path("docs/architecture/runtime_identifiers.json").write_text(
  json.dumps(out, indent=2, sort_keys=True),
  encoding="utf-8"
)

print(json.dumps(out, indent=2, sort_keys=True))
