#!/usr/bin/env python3
"""
install_waves.py — Idempotent OCA module wave installer for Odoo 19.0.

Reads docs/oca/install_manifest.yaml, queries which modules are already
installed via XML-RPC, and installs/upgrades missing modules in waves.

Features:
  - Idempotent: re-running skips already-installed modules
  - Resumable: state saved to .oca_install_state.json (gitignored)
  - Chunked: installs N modules at a time to avoid timeout
  - Retries: retries failed chunks up to --retries times
  - Report: writes verification report to out/ directory

Usage:
    python3 scripts/oca/install_waves.py --wave 1
    python3 scripts/oca/install_waves.py --wave 2,3
    python3 scripts/oca/install_waves.py --all
    python3 scripts/oca/install_waves.py --all --dry-run
    python3 scripts/oca/install_waves.py --verify   # check installed versions
    python3 scripts/oca/install_waves.py --status   # show manifest status

Environment variables (required unless --verify / --status):
    ODOO_URL        e.g. https://erp.insightpulseai.com
    ODOO_DB         e.g. odoo_prod
    ODOO_USER       admin user login
    ODOO_PASSWORD   admin password
    ODOO_BIN        (optional) path to odoo-bin, overrides auto-detect
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
import time
import xmlrpc.client
from datetime import datetime, timezone
from pathlib import Path
import fcntl

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "oca" / "install_manifest.yaml"
STATE_FILE = REPO_ROOT / ".oca_install_state.json"
LOCK_FILE = REPO_ROOT / ".oca_install.lock"
REPORT_DIR = REPO_ROOT / "out" / "oca_install"

CHUNK_SIZE = 5       # modules per odoo-bin call
DEFAULT_RETRIES = 2
DEFAULT_TIMEOUT = 300  # seconds per chunk install


# ---------------------------------------------------------------------------
# XML-RPC helpers
# ---------------------------------------------------------------------------

def _connect():
    url = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
    db = os.environ.get("ODOO_DB", "odoo_prod")
    user = os.environ.get("ODOO_USER", "admin")
    pwd = os.environ.get("ODOO_PASSWORD", "")
    if not pwd:
        print("ERROR: ODOO_PASSWORD required", file=sys.stderr)
        sys.exit(1)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        print("ERROR: Odoo auth failed — check ODOO_USER / ODOO_PASSWORD", file=sys.stderr)
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return db, pwd, uid, models


def _call(m, db, uid, pwd, model, method, *args, **kw):
    return m.execute_kw(db, uid, pwd, model, method, list(args), kw)


def get_installed_modules(db, pwd, uid, models, names: list[str]) -> dict[str, str]:
    """Return {module_name: installed_version} for modules in 'installed' state."""
    rows = _call(models, db, uid, pwd, "ir.module.module", "search_read",
                 [[("name", "in", names), ("state", "=", "installed")]],
                 fields=["name", "installed_version"])
    return {r["name"]: r["installed_version"] for r in rows}


def get_all_module_states(db, pwd, uid, models, names: list[str]) -> dict[str, dict]:
    """Return {name: {state, installed_version}} for all modules."""
    rows = _call(models, db, uid, pwd, "ir.module.module", "search_read",
                 [[("name", "in", names)]],
                 fields=["name", "state", "installed_version"])
    return {r["name"]: {"state": r["state"],
                         "installed_version": r["installed_version"]} for r in rows}


# ---------------------------------------------------------------------------
# Odoo-bin install helper
# ---------------------------------------------------------------------------

def find_odoo_bin() -> str:
    """Find odoo-bin / odoo executable."""
    if "ODOO_BIN" in os.environ:
        return os.environ["ODOO_BIN"]
    for candidate in ["/usr/bin/odoo", "/opt/odoo/odoo-bin",
                      "/usr/local/bin/odoo-bin", "odoo-bin"]:
        if Path(candidate).exists():
            return candidate
    return "odoo-bin"  # hope it's on PATH


def install_chunk(modules: list[str], db: str, dry_run: bool,
                  timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Install a list of modules via odoo-bin -i. Returns True on success."""
    mod_str = ",".join(modules)
    if dry_run:
        print(f"    [DRY-RUN] odoo-bin -d {db} -i {mod_str}")
        return True

    odoo_bin = find_odoo_bin()
    cmd = [odoo_bin, "-d", db, "-i", mod_str, "--stop-after-init", "--no-http"]
    conf = os.environ.get("ODOO_CONF", "")
    if conf:
        cmd += ["--config", conf]

    print(f"    Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    ✅ Install succeeded ({mod_str})")
            return True
        else:
            print(f"    ❌ Install failed (exit {result.returncode})")
            # Show last 20 lines of stderr for diagnosis
            stderr_lines = result.stderr.strip().split("\n")
            for line in stderr_lines[-20:]:
                print(f"       {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ❌ Timeout after {timeout}s installing: {mod_str}")
        return False


# ---------------------------------------------------------------------------
# Concurrency lock (advisory, POSIX flock)
# ---------------------------------------------------------------------------

class InstallLock:
    """Advisory lock to prevent concurrent wave installer runs.

    Uses POSIX flock so the lock is auto-released if the process dies.
    Only active on install/upgrade operations (not --verify / --status).
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._fh = None

    def acquire(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._path, "w")
        try:
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pid_line = self._fh.readline().strip()
            self._fh.close()
            print(f"ERROR: Another installer is running (lock: {self._path}; "
                  f"{pid_line or 'no pid info'}). "
                  f"If no process is running, delete the lock file and retry.",
                  file=sys.stderr)
            sys.exit(1)
        self._fh.write(f"pid={os.getpid()}\n")
        self._fh.flush()

    def release(self) -> None:
        if self._fh:
            fcntl.flock(self._fh, fcntl.LOCK_UN)
            self._fh.close()
            self._fh = None
            try:
                self._path.unlink(missing_ok=True)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def get_wave(manifest: dict, wave_num: int) -> dict | None:
    for wave in manifest.get("waves", []):
        if wave["wave"] == wave_num:
            return wave
    return None


def all_wave_numbers(manifest: dict) -> list[int]:
    return sorted(w["wave"] for w in manifest.get("waves", []))


# ---------------------------------------------------------------------------
# Install logic
# ---------------------------------------------------------------------------

def install_wave(wave: dict, db: str, dry_run: bool,
                 retries: int, state: dict,
                 installed: dict[str, str]) -> dict:
    """Install all pending modules in a wave. Returns updated counts."""
    counts = {"installed": 0, "skipped": 0, "failed": 0}

    modules = wave.get("modules", [])
    to_install = []
    for m in modules:
        name = m["name"]
        if name in installed:
            print(f"  ⏭  SKIP    {name} (already installed: {installed[name]})")
            counts["skipped"] += 1
        elif state.get(name) == "installed":
            print(f"  ⏭  SKIP    {name} (state file: installed)")
            counts["skipped"] += 1
        else:
            to_install.append(name)

    if not to_install:
        print(f"  (all modules in wave {wave['wave']} already installed)")
        return counts

    # Install in chunks
    chunks = [to_install[i:i + CHUNK_SIZE]
              for i in range(0, len(to_install), CHUNK_SIZE)]

    for chunk in chunks:
        success = False
        for attempt in range(1, retries + 2):
            if attempt > 1:
                print(f"    Retry {attempt - 1}/{retries}...")
                time.sleep(5)
            success = install_chunk(chunk, db, dry_run)
            if success:
                break

        if success:
            for name in chunk:
                state[name] = "installed"
                counts["installed"] += 1
        else:
            for name in chunk:
                state[name] = "failed"
                counts["failed"] += 1

    save_state(state)
    return counts


# ---------------------------------------------------------------------------
# Verification report
# ---------------------------------------------------------------------------

def write_report(manifest: dict, all_states: dict, stamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"verification_{stamp}.md"
    lines = [
        f"# OCA Install Verification Report",
        f"",
        f"**Generated**: {stamp}",
        f"**Instance**: {manifest.get('instance', 'unknown')}",
        f"**DB**: {manifest.get('db', 'unknown')}",
        f"",
        f"| Module | Expected Wave | State | Version |",
        f"|--------|--------------|-------|---------|",
    ]
    for wave in manifest.get("waves", []):
        for m in wave.get("modules", []):
            name = m["name"]
            info = all_states.get(name, {})
            state = info.get("state", "not_found")
            ver = info.get("installed_version", "-")
            icon = "✅" if state == "installed" else ("⚠️" if state == "to_install" else "❌")
            lines.append(f"| {name} | {wave['wave']} | {icon} {state} | {ver} |")
    lines.append("")
    content = "\n".join(lines)
    report_path.write_text(content)
    return report_path


# ---------------------------------------------------------------------------
# Status display
# ---------------------------------------------------------------------------

def show_status(manifest: dict, db: str, pwd: str, uid, models) -> None:
    all_names = [m["name"]
                 for wave in manifest.get("waves", [])
                 for m in wave.get("modules", [])]
    all_states = get_all_module_states(db, pwd, uid, models, all_names)

    print(f"\n{'Wave':<6} {'Module':<45} {'State':<15} {'Version'}")
    print("-" * 90)
    for wave in manifest.get("waves", []):
        for m in wave.get("modules", []):
            name = m["name"]
            info = all_states.get(name, {})
            state = info.get("state", "not_in_db")
            ver = info.get("installed_version") or "-"
            icon = "✅" if state == "installed" else ("⏳" if state == "to_install" else "○")
            print(f"{wave['wave']:<6} {name:<45} {icon} {state:<13} {ver}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Idempotent OCA wave installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              --wave 1              Install wave 1 only
              --wave 2,3            Install waves 2 and 3
              --all                 Install all waves in order
              --all --dry-run       Preview what would be installed
              --status              Show current installation status
              --verify              Write verification report
        """),
    )
    p.add_argument("--wave", help="Wave number(s) to install, comma-separated")
    p.add_argument("--all", action="store_true", help="Install all waves")
    p.add_argument("--dry-run", action="store_true", help="Preview only")
    p.add_argument("--verify", action="store_true", help="Write verification report")
    p.add_argument("--status", action="store_true", help="Show module status table")
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                   help=f"Retry count per chunk (default: {DEFAULT_RETRIES})")
    p.add_argument("--reset-state", action="store_true",
                   help="Clear .oca_install_state.json (start fresh)")
    args = p.parse_args()

    if args.reset_state and STATE_FILE.exists():
        STATE_FILE.unlink()
        print("State file cleared.")

    manifest = load_manifest()

    # Acquire advisory lock for install/upgrade operations only
    lock = InstallLock(LOCK_FILE)
    is_write_op = not (args.status or args.verify)
    if is_write_op:
        lock.acquire()

    try:
        return _run(args, manifest)
    finally:
        if is_write_op:
            lock.release()


def _run(args, manifest: dict) -> int:
    db, pwd, uid, models = _connect()
    state = load_state()

    if args.status:
        show_status(manifest, db, pwd, uid, models)
        return 0

    all_names = [m["name"]
                 for wave in manifest.get("waves", [])
                 for m in wave.get("modules", [])]

    if args.verify:
        all_states = get_all_module_states(db, pwd, uid, models, all_names)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
        report = write_report(manifest, all_states, stamp)
        print(f"Verification report written to: {report}")
        return 0

    # Determine waves to install
    if args.all:
        wave_nums = all_wave_numbers(manifest)
    elif args.wave:
        wave_nums = [int(x.strip()) for x in args.wave.split(",")]
    else:
        print("ERROR: specify --wave N or --all", file=sys.stderr)
        return 1

    installed = get_installed_modules(db, pwd, uid, models, all_names)
    print(f"Currently installed OCA modules matching manifest: {len(installed)}")

    total = {"installed": 0, "skipped": 0, "failed": 0}
    for wave_num in wave_nums:
        wave = get_wave(manifest, wave_num)
        if not wave:
            print(f"Wave {wave_num} not found in manifest — skipping.")
            continue

        gate = wave.get("gate", "none")
        if gate == "finance_team_approval" and not os.environ.get("OVERRIDE_FINANCE_GATE"):
            print(f"\nWave {wave_num} ({wave['name']}) requires finance team approval.")
            print("Set OVERRIDE_FINANCE_GATE=1 to bypass (after approval obtained).")
            total["skipped"] += len(wave.get("modules", []))
            continue

        print(f"\n{'='*60}")
        print(f"Wave {wave_num}: {wave['name']} (risk={wave.get('risk','?')})")
        print(f"{'='*60}")

        counts = install_wave(wave, db, args.dry_run, args.retries, state, installed)
        for k in total:
            total[k] += counts[k]

    print(f"\n{'='*60}")
    print(f"TOTAL: installed={total['installed']} skipped={total['skipped']} failed={total['failed']}")
    if total["failed"]:
        print(f"\n❌ {total['failed']} module(s) failed. Check output above.")
        print(f"   Re-run to retry (state file preserves progress).")
        return 1
    print("✅ Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
