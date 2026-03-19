#!/usr/bin/env python3
"""Populate file_count in ssot/knowledge/corpus_registry.yaml.

Scans each corpus path, counts matching files, and updates the YAML in-place.
Designed to be run locally or in CI (T-KAPA-01).

Usage:
    python scripts/index_corpus_registry.py          # update in-place
    python scripts/index_corpus_registry.py --check   # exit 1 if any file_count == 0
    python scripts/index_corpus_registry.py --sync-db # also upsert to Supabase RAG tables
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import os
import sys

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)  # scripts/ -> repo root
REGISTRY_PATH = os.path.join(REPO_ROOT, "ssot", "knowledge", "corpus_registry.yaml")


def count_files(path_glob: str, include: list[str], exclude: list[str]) -> int:
    """Count files matching the corpus glob patterns relative to repo root."""
    matched: set[str] = set()

    # Use include_patterns if provided, else fall back to path glob
    patterns = include if include else [path_glob]

    for pattern in patterns:
        full_pattern = os.path.join(REPO_ROOT, pattern)
        for fpath in glob.glob(full_pattern, recursive=True):
            if os.path.isfile(fpath):
                rel = os.path.relpath(fpath, REPO_ROOT)
                # Check exclude patterns
                excluded = False
                for exc in exclude:
                    if fnmatch.fnmatch(rel, exc):
                        excluded = True
                        break
                if not excluded:
                    matched.add(rel)

    return len(matched)


def main() -> int:
    parser = argparse.ArgumentParser(description="Index corpus registry file counts")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: exit 1 if any corpus has file_count == 0",
    )
    parser.add_argument(
        "--sync-db",
        action="store_true",
        help="After indexing, upsert files into Supabase RAG tables (requires SUPABASE_URL)",
    )
    args = parser.parse_args()

    # Parse YAML to get corpus definitions
    with open(REGISTRY_PATH) as f:
        data = yaml.safe_load(f)

    # Count files for each corpus
    count_map: dict[str, int] = {}
    all_populated = True

    for corpus in data.get("corpora", []):
        cid = corpus["id"]
        path_glob = corpus["path"]
        include = corpus.get("include_patterns", [])
        exclude = corpus.get("exclude_patterns", [])

        count = count_files(path_glob, include, exclude)
        count_map[cid] = count

        status = "OK" if count > 0 else "EMPTY"
        if count == 0:
            all_populated = False
        print(f"  {cid}: {count} files [{status}]")

    if args.check:
        if not all_populated:
            print("\nFAIL: one or more corpora have file_count == 0")
            return 1
        print(f"\nPASS: all {len(data['corpora'])} corpora populated")
        return 0

    # Update file_count lines in-place, preserving comments
    with open(REGISTRY_PATH) as f:
        original_lines = f.readlines()

    current_corpus_id = None
    updated_lines: list[str] = []

    for line in original_lines:
        stripped = line.strip()

        # Track which corpus we're in
        if stripped.startswith("- id:"):
            current_corpus_id = stripped.split(":", 1)[1].strip()

        # Replace file_count line
        if stripped.startswith("file_count:") and current_corpus_id in count_map:
            indent = line[: len(line) - len(line.lstrip())]
            new_count = count_map[current_corpus_id]
            # Preserve inline comment if present
            comment_part = ""
            if "#" in stripped:
                comment_idx = stripped.index("#")
                comment_part = "  " + stripped[comment_idx:]
            updated_lines.append(f"{indent}file_count: {new_count}{comment_part}\n")
        else:
            updated_lines.append(line)

    with open(REGISTRY_PATH, "w") as f:
        f.writelines(updated_lines)

    print(f"\nUpdated {REGISTRY_PATH}")

    # Optional: sync to Supabase RAG tables
    if args.sync_db:
        print("\n── Syncing to Supabase RAG tables ──")
        try:
            import subprocess

            upsert_script = os.path.join(SCRIPT_DIR, "rag", "supabase_upsert.py")
            if not os.path.exists(upsert_script):
                print("  SKIP: scripts/rag/supabase_upsert.py not found")
            else:
                result = subprocess.run(
                    [sys.executable, upsert_script],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )
                print(result.stdout)
                if result.returncode != 0:
                    print(f"  WARNING: upsert exited with code {result.returncode}")
                    if result.stderr:
                        print(f"  {result.stderr[:500]}")
        except Exception as e:
            print(f"  WARNING: DB sync failed: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
