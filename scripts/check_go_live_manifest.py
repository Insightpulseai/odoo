#!/usr/bin/env python3
import csv
import glob
import os
import re
import sys
from pathlib import Path

REQUIRED_MD = Path("docs/RELEASE_NOTES_GO_LIVE.md")

REQUIRED_STRINGS = [
    "# GO-LIVE RELEASE MANIFEST",
    "## 1) Shipped Modules (Go-Live Set)",
    "## 2) Features Included (What’s Live)",
    "## 3) Configuration Toggles (Settings / System Params)",
    "## 4) Acceptance Checks (Go/No-Go)",
    "## 5) Operational Notes / Known Gaps (Explicit)",
    "## 6) Evidence Artifacts (from this go-live)",
    # Non-negotiables for your setup
    "Finance Supervisor = Beng Manalo (beng.manalo@omc.com)",
    "ipai.ask_ai.provider = openai | gemini",
    "ipai.ask_ai.invite_only = True",
    'ipai.ask_ai.domain_allowlist = "omc.com,tbwa-smp.com"',
]

PLACEHOLDER_PATTERNS = [
    r"<<MAP:",
    r"<<.*?>>",
]

# Where CI should look for generated CSVs in-repo (if committed)
CSV_GLOBS = [
    "data/odoo_import_month_end_*.csv",
    "artifacts/**/odoo_import_month_end_*.csv",
]

ROLE_MAP_HINTS = [
    ("Finance Supervisor", "beng.manalo@omc.com"),
]


def fail(msg: str) -> None:
    print(f"::error::{msg}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"::warning::{msg}")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"Missing required file: {p}")
    except Exception as e:
        fail(f"Failed to read {p}: {e}")


def check_manifest() -> None:
    text = read_text(REQUIRED_MD)
    for s in REQUIRED_STRINGS:
        if s not in text:
            fail(f"Go-live manifest missing required line/section: {s}")

    # Basic sanity: date must be present (YYYY-MM-DD)
    if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text):
        fail("Go-live manifest must include an ISO date (YYYY-MM-DD).")


def iter_csv_files():
    files = []
    for pat in CSV_GLOBS:
        files.extend(glob.glob(pat, recursive=True))
    # de-dupe + only real files
    uniq = []
    for f in sorted(set(files)):
        if os.path.isfile(f):
            uniq.append(f)
    return uniq


def check_csv_no_placeholders(path: str) -> None:
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, raw):
            fail(f"CSV contains placeholders ({pat}): {path}")


def check_role_map_beng(path: str) -> None:
    # Accept either "role,email" or Odoo import-style headers; just scan rows.
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        fail(f"Failed reading CSV {path}: {e}")

    flat = ["|".join([c.strip() for c in r]) for r in rows]
    joined = "\n".join(flat).lower()
    for role, email in ROLE_MAP_HINTS:
        if role.lower() in joined and email.lower() in joined:
            return
    fail(
        f"Role map does not confirm 'Finance Supervisor' -> beng.manalo@omc.com in: {path}"
    )


def check_csvs() -> None:
    csvs = iter_csv_files()
    if not csvs:
        # Not all teams commit import artifacts. If you don’t commit them, manifest still enforced.
        warn(
            "No odoo_import_month_end_*.csv found in repo (data/ or artifacts/). Skipping CSV checks."
        )
        return

    for f in csvs:
        check_csv_no_placeholders(f)

    # If a role map exists, enforce Beng mapping
    role_map_candidates = [
        c for c in csvs if "role" in c.lower() and "map" in c.lower()
    ]
    if role_map_candidates:
        # enforce first candidate; if multiple, all must pass
        for rm in role_map_candidates:
            check_role_map_beng(rm)
    else:
        warn("No role_email_map CSV found; Beng mapping enforcement skipped.")


def main() -> None:
    check_manifest()
    check_csvs()
    print("OK: Go-live manifest gate passed.")


if __name__ == "__main__":
    main()
