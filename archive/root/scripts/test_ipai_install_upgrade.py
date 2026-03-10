#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPAI Module Install/Upgrade Test Runner

Tests each ipai_* module for:
1. Installation on clean database
2. Upgrade after installation
3. Captures tracebacks and errors

Usage:
    # Test all modules
    python scripts/test_ipai_install_upgrade.py

    # Test specific modules
    python scripts/test_ipai_install_upgrade.py ipai_finance_ppm ipai_ask_ai

    # With custom Odoo path
    ODOO_BIN=/path/to/odoo-bin python scripts/test_ipai_install_upgrade.py

Output:
    - Console: Real-time progress
    - docs/audits/ipai_modules/install_test_results.json
    - docs/audits/ipai_modules/install_test_results.csv
    - docs/audits/ipai_modules/install_test_results.md
"""

import subprocess
import sys
import os
import json
import csv
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
ADDONS_PATH = REPO_ROOT / "addons" / "ipai"
OUTPUT_DIR = REPO_ROOT / "docs" / "audits" / "ipai_modules"

# Odoo configuration
ODOO_BIN = os.environ.get("ODOO_BIN", "odoo-bin")
ODOO_CONF = os.environ.get("ODOO_CONF", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "odoo")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "odoo")
TEST_DB_PREFIX = "ipai_test_"

# Timeout for operations (in seconds)
INSTALL_TIMEOUT = 300  # 5 minutes per module
UPGRADE_TIMEOUT = 180  # 3 minutes per upgrade


def get_ipai_modules() -> list:
    """Get list of all IPAI modules from addons/ipai directory."""
    modules = []

    # Root namespace module
    if (ADDONS_PATH / "__manifest__.py").exists():
        modules.append("ipai")

    # Child modules
    for item in sorted(ADDONS_PATH.iterdir()):
        if item.is_dir() and item.name.startswith("ipai_"):
            manifest = item / "__manifest__.py"
            if manifest.exists():
                modules.append(item.name)

    return modules


def parse_manifest(module_path: Path) -> Optional[dict]:
    """Parse a module's __manifest__.py file."""
    manifest_path = module_path / "__manifest__.py"
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, "r") as f:
            content = f.read()
        # Safe eval with restricted globals
        manifest = eval(content, {"__builtins__": {}})
        return manifest
    except Exception as e:
        return {"error": str(e)}


def get_module_dependencies(module_name: str) -> list:
    """Get dependencies for a module."""
    if module_name == "ipai":
        module_path = ADDONS_PATH
    else:
        module_path = ADDONS_PATH / module_name

    manifest = parse_manifest(module_path)
    if manifest and "depends" in manifest:
        return manifest["depends"]
    return ["base"]


def is_installable(module_name: str) -> bool:
    """Check if module is marked as installable."""
    if module_name == "ipai":
        module_path = ADDONS_PATH
    else:
        module_path = ADDONS_PATH / module_name

    manifest = parse_manifest(module_path)
    if manifest:
        return manifest.get("installable", True)
    return False


def create_test_database(db_name: str) -> tuple:
    """Create a test database. Returns (success, error_message)."""
    try:
        # Drop if exists
        subprocess.run(
            [
                "dropdb",
                "-h",
                DB_HOST,
                "-p",
                DB_PORT,
                "-U",
                DB_USER,
                "--if-exists",
                db_name,
            ],
            env={**os.environ, "PGPASSWORD": DB_PASSWORD},
            capture_output=True,
            timeout=30,
        )

        # Create new database
        result = subprocess.run(
            ["createdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, db_name],
            env={**os.environ, "PGPASSWORD": DB_PASSWORD},
            capture_output=True,
            timeout=30,
        )

        if result.returncode != 0:
            return False, result.stderr.decode()

        return True, None
    except subprocess.TimeoutExpired:
        return False, "Database creation timed out"
    except Exception as e:
        return False, str(e)


def drop_test_database(db_name: str):
    """Drop a test database."""
    try:
        subprocess.run(
            [
                "dropdb",
                "-h",
                DB_HOST,
                "-p",
                DB_PORT,
                "-U",
                DB_USER,
                "--if-exists",
                db_name,
            ],
            env={**os.environ, "PGPASSWORD": DB_PASSWORD},
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass  # Ignore errors during cleanup


def run_odoo_command(
    db_name: str, command: str, module: str, timeout: int = INSTALL_TIMEOUT
) -> dict:
    """
    Run an Odoo command (install or upgrade).

    Returns dict with:
        - success: bool
        - duration: float (seconds)
        - stdout: str
        - stderr: str
        - error: str (if any)
    """
    start_time = time.time()

    # Build command
    cmd = [
        ODOO_BIN,
        "-d",
        db_name,
        f"--{command}={module}",
        "--stop-after-init",
        "--log-level=warning",
        f"--addons-path={REPO_ROOT / 'odoo' / 'addons'},{REPO_ROOT / 'addons'},{ADDONS_PATH}",
        f"--db_host={DB_HOST}",
        f"--db_port={DB_PORT}",
        f"--db_user={DB_USER}",
        f"--db_password={DB_PASSWORD}",
    ]

    if ODOO_CONF:
        cmd.extend(["-c", ODOO_CONF])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            env={**os.environ, "PGPASSWORD": DB_PASSWORD},
        )

        duration = time.time() - start_time
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        # Check for errors in output
        has_error = (
            result.returncode != 0
            or "Traceback" in stderr
            or "Error" in stderr
            or "CRITICAL" in stderr
        )

        return {
            "success": not has_error,
            "duration": round(duration, 2),
            "stdout": stdout[-2000:] if len(stdout) > 2000 else stdout,  # Truncate
            "stderr": stderr[-2000:] if len(stderr) > 2000 else stderr,  # Truncate
            "error": extract_error(stderr) if has_error else None,
            "return_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "success": False,
            "duration": round(duration, 2),
            "stdout": "",
            "stderr": "",
            "error": f"Command timed out after {timeout} seconds",
            "return_code": -1,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "duration": 0,
            "stdout": "",
            "stderr": "",
            "error": f"Odoo binary not found: {ODOO_BIN}",
            "return_code": -1,
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "duration": round(duration, 2),
            "stdout": "",
            "stderr": "",
            "error": str(e),
            "return_code": -1,
        }


def extract_error(stderr: str) -> str:
    """Extract the most relevant error message from stderr."""
    lines = stderr.strip().split("\n")

    # Look for Traceback
    for i, line in enumerate(lines):
        if "Traceback" in line:
            # Return traceback and a few lines after
            return "\n".join(lines[i : min(i + 10, len(lines))])

    # Look for Error/CRITICAL
    for line in reversed(lines):
        if "Error" in line or "CRITICAL" in line:
            return line

    # Return last few lines
    return "\n".join(lines[-5:])


def test_module(module_name: str, test_id: int) -> dict:
    """
    Test a single module for install and upgrade.

    Returns test result dict.
    """
    db_name = f"{TEST_DB_PREFIX}{test_id}_{module_name[:20]}"
    result = {
        "module": module_name,
        "installable": is_installable(module_name),
        "dependencies": get_module_dependencies(module_name),
        "install": {"tested": False},
        "upgrade": {"tested": False},
        "overall_success": False,
        "tested_at": datetime.now().isoformat(),
    }

    if not result["installable"]:
        result["install"]["skipped"] = "Module not installable"
        result["upgrade"]["skipped"] = "Module not installable"
        return result

    # Create test database
    db_success, db_error = create_test_database(db_name)
    if not db_success:
        result["install"]["tested"] = True
        result["install"]["success"] = False
        result["install"]["error"] = f"Failed to create test database: {db_error}"
        return result

    try:
        # Test installation
        print(f"    Installing {module_name}...", end=" ", flush=True)
        install_result = run_odoo_command(db_name, "init", module_name, INSTALL_TIMEOUT)
        result["install"] = {
            "tested": True,
            "success": install_result["success"],
            "duration": install_result["duration"],
            "error": install_result.get("error"),
        }

        if install_result["success"]:
            print(f"OK ({install_result['duration']}s)")

            # Test upgrade
            print(f"    Upgrading {module_name}...", end=" ", flush=True)
            upgrade_result = run_odoo_command(
                db_name, "update", module_name, UPGRADE_TIMEOUT
            )
            result["upgrade"] = {
                "tested": True,
                "success": upgrade_result["success"],
                "duration": upgrade_result["duration"],
                "error": upgrade_result.get("error"),
            }

            if upgrade_result["success"]:
                print(f"OK ({upgrade_result['duration']}s)")
            else:
                print(f"FAIL")
        else:
            print(f"FAIL")
            result["upgrade"]["skipped"] = "Install failed"

        # Overall success
        result["overall_success"] = result["install"].get("success", False) and result[
            "upgrade"
        ].get("success", False)

    finally:
        # Cleanup
        drop_test_database(db_name)

    return result


def generate_reports(results: list, output_dir: Path):
    """Generate JSON, CSV, and Markdown reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()

    # Summary stats
    total = len(results)
    install_pass = sum(1 for r in results if r["install"].get("success"))
    install_fail = sum(
        1
        for r in results
        if r["install"].get("tested") and not r["install"].get("success")
    )
    install_skip = sum(1 for r in results if r["install"].get("skipped"))
    upgrade_pass = sum(1 for r in results if r["upgrade"].get("success"))
    upgrade_fail = sum(
        1
        for r in results
        if r["upgrade"].get("tested") and not r["upgrade"].get("success")
    )
    upgrade_skip = sum(1 for r in results if r["upgrade"].get("skipped"))

    report_data = {
        "generated_at": timestamp,
        "total_modules": total,
        "summary": {
            "install": {
                "pass": install_pass,
                "fail": install_fail,
                "skip": install_skip,
            },
            "upgrade": {
                "pass": upgrade_pass,
                "fail": upgrade_fail,
                "skip": upgrade_skip,
            },
            "overall_pass": sum(1 for r in results if r["overall_success"]),
        },
        "results": results,
    }

    # JSON report
    json_path = output_dir / "install_test_results.json"
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"\nJSON report: {json_path}")

    # CSV report
    csv_path = output_dir / "install_test_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "module",
                "installable",
                "install_success",
                "install_duration",
                "install_error",
                "upgrade_success",
                "upgrade_duration",
                "upgrade_error",
                "overall_success",
            ]
        )
        for r in results:
            writer.writerow(
                [
                    r["module"],
                    r["installable"],
                    r["install"].get("success", ""),
                    r["install"].get("duration", ""),
                    r["install"].get("error", r["install"].get("skipped", "")),
                    r["upgrade"].get("success", ""),
                    r["upgrade"].get("duration", ""),
                    r["upgrade"].get("error", r["upgrade"].get("skipped", "")),
                    r["overall_success"],
                ]
            )
    print(f"CSV report: {csv_path}")

    # Markdown report
    md_path = output_dir / "install_test_results.md"
    with open(md_path, "w") as f:
        f.write("# IPAI Module Install/Upgrade Test Results\n\n")
        f.write(f"Generated: {timestamp}\n\n")

        f.write("## Summary\n\n")
        f.write(f"| Metric | Pass | Fail | Skip |\n")
        f.write(f"|--------|------|------|------|\n")
        f.write(f"| Install | {install_pass} | {install_fail} | {install_skip} |\n")
        f.write(f"| Upgrade | {upgrade_pass} | {upgrade_fail} | {upgrade_skip} |\n")
        f.write(
            f"\n**Overall Pass Rate**: {report_data['summary']['overall_pass']}/{total} "
        )
        f.write(
            f"({100*report_data['summary']['overall_pass']//total if total else 0}%)\n\n"
        )

        f.write("## Results by Module\n\n")
        f.write("| Module | Install | Upgrade | Overall |\n")
        f.write("|--------|---------|---------|----------|\n")

        for r in results:
            install_status = (
                "PASS"
                if r["install"].get("success")
                else ("SKIP" if r["install"].get("skipped") else "FAIL")
            )
            upgrade_status = (
                "PASS"
                if r["upgrade"].get("success")
                else ("SKIP" if r["upgrade"].get("skipped") else "FAIL")
            )
            overall_status = "PASS" if r["overall_success"] else "FAIL"
            f.write(
                f"| {r['module']} | {install_status} | {upgrade_status} | {overall_status} |\n"
            )

        # Failed modules details
        failed = [
            r
            for r in results
            if not r["overall_success"] and not r["install"].get("skipped")
        ]
        if failed:
            f.write("\n## Failed Module Details\n\n")
            for r in failed:
                f.write(f"### {r['module']}\n\n")
                if r["install"].get("error"):
                    f.write(
                        f"**Install Error:**\n```\n{r['install']['error']}\n```\n\n"
                    )
                if r["upgrade"].get("error"):
                    f.write(
                        f"**Upgrade Error:**\n```\n{r['upgrade']['error']}\n```\n\n"
                    )

    print(f"Markdown report: {md_path}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("IPAI Module Install/Upgrade Test Runner")
    print("=" * 60)

    # Get modules to test
    if len(sys.argv) > 1:
        modules = sys.argv[1:]
        print(f"\nTesting specified modules: {', '.join(modules)}")
    else:
        modules = get_ipai_modules()
        print(f"\nFound {len(modules)} IPAI modules to test")

    # Check if Odoo is available
    print(f"\nOdoo binary: {ODOO_BIN}")
    print(f"Database host: {DB_HOST}:{DB_PORT}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Run tests
    results = []
    for i, module in enumerate(modules, 1):
        print(f"[{i}/{len(modules)}] Testing {module}:")
        result = test_module(module, i)
        results.append(result)

    # Generate reports
    print("\n" + "=" * 60)
    print("Generating reports...")
    generate_reports(results, OUTPUT_DIR)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["overall_success"])
    print(f"\n{'=' * 60}")
    print(f"FINAL: {passed}/{total} modules passed all tests")
    print(f"{'=' * 60}")

    # Exit with error code if any failures
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
