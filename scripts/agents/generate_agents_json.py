#!/usr/bin/env python3
"""
Generate agents/registry/agents.json (LIST SHAPE) from agents/registry/agents.yaml

Output:
  - agents/registry/agents.json      -> JSON array of agents (runtime-compatible)
  - agents/registry/agents.meta.json -> generator metadata (sha, provenance)

Design goals:
- deterministic output (stable sort + stable JSON formatting)
- minimal schema validation (id required, no dupes)
- minimal deps (requires PyYAML)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_text_if_changed(path: str, content: str) -> bool:
    existing = ""
    if os.path.exists(path):
        existing = _read_text(path)
    if existing == content:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load_yaml(yaml_path: str) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "PyYAML is required to run this generator. Install with: pip install pyyaml"
        ) from e
    return yaml.safe_load(_read_text(yaml_path))


def _canonicalize_agents(data: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Accepts either:
      - {"agents": [ ... ]} (preferred)
      - [ ... ] (legacy)
    Returns: (agents_list, warnings)
    """
    warnings: List[str] = []

    if isinstance(data, dict) and "agents" in data:
        agents = data["agents"]
    elif isinstance(data, list):
        agents = data
        warnings.append("YAML root is a list; consider migrating to {agents: [...]} shape.")
    else:
        raise ValueError("Invalid YAML shape. Expected {agents: [...]} or a list of agents.")

    if not isinstance(agents, list):
        raise ValueError("Invalid agents YAML: agents must be a list.")

    required_keys = {"id"}
    normalized: List[Dict[str, Any]] = []

    for i, a in enumerate(agents):
        if not isinstance(a, dict):
            raise ValueError(f"Agent at index {i} must be a mapping/object.")
        missing = required_keys - set(a.keys())
        if missing:
            raise ValueError(f"Agent at index {i} missing required keys: {sorted(missing)}")
        a2 = dict(a)
        a2["id"] = str(a2["id"]).strip()
        if not a2["id"]:
            raise ValueError(f"Agent at index {i} has empty id.")
        normalized.append(a2)

    # Deterministic ordering
    normalized.sort(key=lambda x: x["id"])

    # Duplicate ids
    seen = set()
    dups = []
    for a in normalized:
        if a["id"] in seen:
            dups.append(a["id"])
        seen.add(a["id"])
    if dups:
        raise ValueError(f"Duplicate agent ids found: {sorted(set(dups))}")

    return normalized, warnings


def _render_agents_json_list(agents: List[Dict[str, Any]]) -> str:
    return json.dumps(agents, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _render_meta_json(*, yaml_path: str, yaml_raw: str, out_path: str) -> str:
    meta = {
        "do_not_edit_agents_json_by_hand": True,
        "generated_from": os.path.relpath(yaml_path),
        "generator": "scripts/agents/generate_agents_json.py",
        "yaml_sha256": _sha256_hex(yaml_raw),
        "agents_json_path": os.path.relpath(out_path),
        "format": "list",
    }
    return json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="agents/registry/agents.yaml")
    ap.add_argument("--out", dest="out", default="agents/registry/agents.json")
    ap.add_argument(
        "--meta-out",
        dest="meta_out",
        default="agents/registry/agents.meta.json",
        help="Sidecar metadata file (drift-proofing).",
    )
    ap.add_argument("--check", action="store_true", help="Fail if outputs would change")
    args = ap.parse_args()

    yaml_raw = _read_text(args.inp)
    data = _load_yaml(args.inp)
    agents, warnings = _canonicalize_agents(data)

    agents_json = _render_agents_json_list(agents)
    meta_json = _render_meta_json(yaml_path=args.inp, yaml_raw=yaml_raw, out_path=args.out)

    existing_agents = _read_text(args.out) if os.path.exists(args.out) else ""
    existing_meta = _read_text(args.meta_out) if os.path.exists(args.meta_out) else ""

    if args.check:
        if existing_agents != agents_json or existing_meta != meta_json:
            sys.stderr.write("Agents registry outputs are out of date. Run generator.\n")
            return 2
        return 0

    _write_text_if_changed(args.out, agents_json)
    _write_text_if_changed(args.meta_out, meta_json)

    for w in warnings:
        sys.stderr.write(f"warning: {w}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
