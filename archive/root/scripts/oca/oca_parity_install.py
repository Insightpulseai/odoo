#!/usr/bin/env python3
"""
oca_parity_install.py — Unified OCA parity installer for Odoo 19.0.

Single entry point replacing install_from_allowlist*.sh scripts.
Reads docs/oca/install_manifest.yaml, validates against
odoo/ssot/oca_installed_allowlist.yaml, and installs modules in waves.

Features:
  - Auto-detects Docker vs local runtime
  - Allowlist cross-validation (warns on unconfirmed modules)
  - Idempotent: re-running skips already-installed modules
  - Resumable: state saved to .oca_install_state.json (gitignored)
  - Chunked: installs N modules at a time to avoid timeout
  - Retries: retries failed chunks up to --retries times
  - Selftest: --selftest runs 9 inline tests, no network needed
  - Report: writes verification report to out/ directory

Usage:
    python3 scripts/oca/oca_parity_install.py --selftest
    python3 scripts/oca/oca_parity_install.py --wave 1 --dry-run
    python3 scripts/oca/oca_parity_install.py --wave 1
    python3 scripts/oca/oca_parity_install.py --wave 2,3
    python3 scripts/oca/oca_parity_install.py --all
    python3 scripts/oca/oca_parity_install.py --status
    python3 scripts/oca/oca_parity_install.py --verify

Environment variables (required unless --dry-run / --status / --verify / --selftest):
    ODOO_URL        e.g. http://localhost:8069
    ODOO_DB         e.g. odoo (Docker) or odoo_dev (local)
    ODOO_USER       admin user login
    ODOO_PASSWORD   admin password
    ODOO_BIN        (optional) path to odoo-bin, overrides auto-detect
    OVERRIDE_FINANCE_GATE=1   bypass Wave 3 finance_team_approval gate
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
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


# =============================================================================
# Section 1: Imports + Constants
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "oca" / "install_manifest.yaml"
ALLOWLIST_PATH = REPO_ROOT / "odoo" / "ssot" / "oca_installed_allowlist.yaml"
STATE_FILE = REPO_ROOT / ".oca_install_state.json"
LOCK_FILE = REPO_ROOT / ".oca_install.lock"
REPORT_DIR = REPO_ROOT / "out" / "oca_install"

CHUNK_SIZE = 5        # modules per odoo-bin call
DEFAULT_RETRIES = 2
DEFAULT_TIMEOUT = 300  # seconds per chunk install


# =============================================================================
# Section 2: detect_runtime() — NEW
# =============================================================================

def detect_runtime() -> str:
    """Return 'docker' if running inside a container, else 'local'."""
    if Path("/.dockerenv").exists() or Path("/run/.containerenv").exists():
        return "docker"
    return "local"


# =============================================================================
# Section 3: get_connection_defaults() — NEW
# =============================================================================

def get_connection_defaults(runtime: str) -> dict:
    """Return sensible connection defaults based on detected runtime."""
    if runtime == "docker":
        return {"url": "http://localhost:8069", "db": "odoo", "user": "admin"}
    return {"url": "http://localhost:8069", "db": "odoo_dev", "user": "admin"}


# =============================================================================
# Section 4: XML-RPC helpers — ported verbatim from install_waves.py
# =============================================================================

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


# =============================================================================
# Section 5: Odoo-bin helpers — ported verbatim from install_waves.py
# =============================================================================

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
            print(f"    \u2705 Install succeeded ({mod_str})")
            return True
        else:
            print(f"    \u274c Install failed (exit {result.returncode})")
            stderr_lines = result.stderr.strip().split("\n")
            for line in stderr_lines[-20:]:
                print(f"       {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    \u274c Timeout after {timeout}s installing: {mod_str}")
        return False


# =============================================================================
# Section 6: InstallLock — ported verbatim from install_waves.py
# =============================================================================

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


# =============================================================================
# Section 7: State management — ported from install_waves.py (path injectable)
# =============================================================================

def load_state(path: Path = STATE_FILE) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# =============================================================================
# Section 8: Manifest + allowlist loading
# =============================================================================

def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_allowlist(path: Path = ALLOWLIST_PATH) -> set:
    """Return set of allowed OCA module names from allowlist YAML."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return set(data.get("oca_modules", []))


def get_wave(manifest: dict, wave_num: int) -> dict | None:
    for wave in manifest.get("waves", []):
        if wave["wave"] == wave_num:
            return wave
    return None


def all_wave_numbers(manifest: dict) -> list[int]:
    return sorted(w["wave"] for w in manifest.get("waves", []))


# =============================================================================
# Section 9: Module discovery
# =============================================================================

def discover_modules(manifest: dict) -> list[str]:
    """Return flat list of all module names across all waves in manifest."""
    return [m["name"]
            for wave in manifest.get("waves", [])
            for m in wave.get("modules", [])]


def check_against_allowlist(modules: list[str], allowlist: set) -> dict:
    """Partition modules into confirmed (in allowlist) and unconfirmed.

    Returns:
        {"confirmed": [...], "unconfirmed": [...]}
    """
    confirmed = [m for m in modules if m in allowlist]
    unconfirmed = [m for m in modules if m not in allowlist]
    return {"confirmed": confirmed, "unconfirmed": unconfirmed}


# =============================================================================
# Section 10: check_prerequisites()
# =============================================================================

def check_prerequisites(args) -> list[str]:
    """Pre-flight check. Returns list of error strings (empty list = all OK).

    Skips password check when --dry-run or --selftest is set.
    """
    if getattr(args, "dry_run", False) or getattr(args, "selftest", False):
        return []
    errors = []
    if not os.environ.get("ODOO_PASSWORD"):
        errors.append("ODOO_PASSWORD environment variable is not set")
    return errors


# =============================================================================
# Section 11: install_wave() — ported verbatim from install_waves.py
# =============================================================================

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
            print(f"  \u23ed  SKIP    {name} (already installed: {installed[name]})")
            counts["skipped"] += 1
        elif state.get(name) == "installed":
            print(f"  \u23ed  SKIP    {name} (state file: installed)")
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


# =============================================================================
# Section 12: write_report() — ported verbatim from install_waves.py
# =============================================================================

def write_report(manifest: dict, all_states: dict, stamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"verification_{stamp}.md"
    lines = [
        "# OCA Install Verification Report",
        "",
        f"**Generated**: {stamp}",
        f"**Instance**: {manifest.get('instance', 'unknown')}",
        f"**DB**: {manifest.get('db', 'unknown')}",
        "",
        "| Module | Expected Wave | State | Version |",
        "|--------|--------------|-------|---------|",
    ]
    for wave in manifest.get("waves", []):
        for m in wave.get("modules", []):
            name = m["name"]
            info = all_states.get(name, {})
            state = info.get("state", "not_found")
            ver = info.get("installed_version", "-")
            icon = "\u2705" if state == "installed" else ("\u26a0\ufe0f" if state == "to_install" else "\u274c")
            lines.append(f"| {name} | {wave['wave']} | {icon} {state} | {ver} |")
    lines.append("")
    content = "\n".join(lines)
    report_path.write_text(content)
    return report_path


# =============================================================================
# Section 13: show_status() — ported verbatim from install_waves.py
# =============================================================================

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
            icon = "\u2705" if state == "installed" else ("\u23f3" if state == "to_install" else "\u25cb")
            print(f"{wave['wave']:<6} {name:<45} {icon} {state:<13} {ver}")


# =============================================================================
# Section 14: run_selftest() — 9 inline tests, no network required
# =============================================================================

def run_selftest() -> int:
    """Run 9 inline sanity tests. Returns 0 if all pass, 1 if any fail."""
    _passed = 0
    _failed = 0

    def _ok(label: str) -> None:
        nonlocal _passed
        _passed += 1
        n = _passed + _failed
        print(f"  \u2705 T{n}: {label}")

    def _fail(label: str, reason: str) -> None:
        nonlocal _failed
        _failed += 1
        n = _passed + _failed
        print(f"  \u274c T{n}: {label} \u2014 {reason}")

    print("Running selftest (9 tests, no network required)...")

    # T1: load_manifest() returns dict with 'waves' list
    try:
        manifest = load_manifest()
        assert isinstance(manifest, dict) and "waves" in manifest
        _ok("load_manifest() returns dict with 'waves' list")
    except Exception as exc:
        _fail("load_manifest() returns dict with 'waves' list", str(exc))
        manifest = {"waves": []}  # fallback so later tests can proceed

    # T2: all_wave_numbers() returns [1, 2, 3, 4]
    try:
        wave_nums = all_wave_numbers(manifest)
        assert wave_nums == [1, 2, 3, 4], f"got {wave_nums}"
        _ok("all_wave_numbers() returns [1, 2, 3, 4]")
    except Exception as exc:
        _fail("all_wave_numbers() returns [1, 2, 3, 4]", str(exc))

    # T3: discover_modules() returns non-empty flat list
    try:
        mods = discover_modules(manifest)
        assert isinstance(mods, list) and len(mods) > 0
        _ok(f"discover_modules() returns non-empty flat list ({len(mods)} modules)")
    except Exception as exc:
        _fail("discover_modules() returns non-empty flat list", str(exc))
        mods = []

    # T4: check_against_allowlist() correctly partitions confirmed vs unconfirmed
    try:
        test_allowlist = {"mod_a", "mod_b"}
        test_modules = ["mod_a", "mod_b", "mod_c"]
        result = check_against_allowlist(test_modules, test_allowlist)
        assert result["confirmed"] == ["mod_a", "mod_b"], f"confirmed={result['confirmed']}"
        assert result["unconfirmed"] == ["mod_c"], f"unconfirmed={result['unconfirmed']}"
        _ok("check_against_allowlist() correctly partitions confirmed vs unconfirmed")
    except Exception as exc:
        _fail("check_against_allowlist() partitions correctly", str(exc))

    # T5: detect_runtime() returns 'local' or 'docker' (no exception)
    try:
        rt = detect_runtime()
        assert rt in ("local", "docker"), f"got {rt!r}"
        _ok(f"detect_runtime() returns valid runtime (got {rt!r})")
    except Exception as exc:
        _fail("detect_runtime() returns 'local' or 'docker'", str(exc))

    # T6: load_state() returns {} when state file absent
    try:
        with tempfile.NamedTemporaryFile(suffix=".json") as tf:
            absent_path = Path(tf.name)
        # File is now deleted (NamedTemporaryFile closed)
        result = load_state(path=absent_path)
        assert result == {}, f"got {result!r}"
        _ok("load_state() returns {} when state file absent")
    except Exception as exc:
        _fail("load_state() returns {} when state file absent", str(exc))

    # T7: check_prerequisites() returns error containing ODOO_PASSWORD when unset
    try:
        saved = os.environ.pop("ODOO_PASSWORD", None)

        class _FakeArgs:
            dry_run = False
            selftest = False
            status = False
            verify = False

        errors = check_prerequisites(_FakeArgs())
        assert any("ODOO_PASSWORD" in e for e in errors), f"errors={errors}"
        _ok("check_prerequisites() returns error for missing ODOO_PASSWORD")
        if saved is not None:
            os.environ["ODOO_PASSWORD"] = saved
    except Exception as exc:
        _fail("check_prerequisites() returns error for missing ODOO_PASSWORD", str(exc))
        if "saved" in dir() and saved is not None:
            os.environ["ODOO_PASSWORD"] = saved

    # T8: install_chunk(dry_run=True) returns True without spawning subprocess
    try:
        result = install_chunk(["base"], "testdb", dry_run=True)
        assert result is True
        _ok("install_chunk(dry_run=True) returns True without spawning subprocess")
    except Exception as exc:
        _fail("install_chunk(dry_run=True) returns True", str(exc))

    # T9: load_allowlist() returns non-empty set
    try:
        allowlist = load_allowlist()
        assert isinstance(allowlist, set) and len(allowlist) > 0
        _ok(f"load_allowlist() returns non-empty set ({len(allowlist)} modules)")
    except Exception as exc:
        _fail("load_allowlist() returns non-empty set", str(exc))

    total = _passed + _failed
    print(f"\n{_passed}/{total} tests passed")
    return 0 if _failed == 0 else 1


# =============================================================================
# Section 15: build_parser() + main()
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Unified OCA parity installer (replaces install_from_allowlist*.sh)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              --selftest            Run 9 inline tests (no Odoo needed)
              --wave 1              Install wave 1 only
              --wave 2,3            Install waves 2 and 3
              --all                 Install all waves in order
              --all --dry-run       Preview what would be installed
              --status              Show current installation status
              --verify              Write verification report to out/oca_install/
              --reset-state         Clear .oca_install_state.json (start fresh)
        """),
    )
    p.add_argument("--wave", help="Wave number(s) to install, comma-separated")
    p.add_argument("--all", action="store_true", help="Install all waves in order")
    p.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    p.add_argument("--selftest", action="store_true",
                   help="Run 9 inline tests, exit 0 if all pass")
    p.add_argument("--verify", action="store_true", help="Write verification report")
    p.add_argument("--status", action="store_true", help="Show module status table")
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                   help=f"Retry count per chunk (default: {DEFAULT_RETRIES})")
    p.add_argument("--reset-state", action="store_true",
                   help="Clear .oca_install_state.json (start fresh)")
    p.add_argument("--manifest", type=Path, default=MANIFEST_PATH,
                   help="Override manifest path (for tests)")
    p.add_argument("--allowlist", type=Path, default=ALLOWLIST_PATH,
                   help="Override allowlist path (for tests)")
    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()

    # Selftest mode — runs standalone, no Odoo connection needed
    if args.selftest:
        return run_selftest()

    if args.reset_state and STATE_FILE.exists():
        STATE_FILE.unlink()
        print("State file cleared.")

    manifest = load_manifest(args.manifest)

    # Pre-flight validation
    errors = check_prerequisites(args)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print("Hint: use --dry-run to preview without connecting to Odoo.", file=sys.stderr)
        return 1

    # Allowlist cross-check (warn only, not a hard block)
    allowlist = load_allowlist(args.allowlist)
    modules = discover_modules(manifest)
    partitioned = check_against_allowlist(modules, allowlist)
    if partitioned["unconfirmed"]:
        print(f"\u26a0\ufe0f  {len(partitioned['unconfirmed'])} manifest module(s) not in allowlist "
              f"(install may fail): {partitioned['unconfirmed']}")

    # Acquire advisory lock for write operations only
    lock = InstallLock(LOCK_FILE)
    is_write_op = not (args.status or args.verify)
    if is_write_op and not args.dry_run:
        lock.acquire()

    try:
        return _run(args, manifest)
    finally:
        if is_write_op and not args.dry_run:
            lock.release()


def _run(args, manifest: dict) -> int:
    # status / verify always require a live connection
    if args.status or args.verify:
        db, pwd, uid, models = _connect()
        state = load_state()
        if args.status:
            show_status(manifest, db, pwd, uid, models)
            return 0
        # --verify
        all_names = discover_modules(manifest)
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

    state = load_state()

    # Dry-run: no connection needed — assume nothing installed, show preview
    if args.dry_run:
        installed: dict[str, str] = {}
        db = os.environ.get("ODOO_DB", "odoo_dev")
        print(f"[DRY-RUN] No connection to Odoo — showing what would be installed (db={db})")
    else:
        db, pwd, uid, models = _connect()
        all_names = discover_modules(manifest)
        installed = get_installed_modules(db, pwd, uid, models, all_names)
        print(f"Currently installed OCA modules matching manifest: {len(installed)}")

    total = {"installed": 0, "skipped": 0, "failed": 0}
    for wave_num in wave_nums:
        wave = get_wave(manifest, wave_num)
        if not wave:
            print(f"Wave {wave_num} not found in manifest \u2014 skipping.")
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
        print(f"\n\u274c {total['failed']} module(s) failed. Check output above.")
        print("   Re-run to retry (state file preserves progress).")
        return 1
    print("\u2705 Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
