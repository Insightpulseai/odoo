#!/usr/bin/env python3
"""
Directional Sync Runner for InsightPulse Odoo

Orchestrates PULL, PUSH, and BIDIRECTIONAL sync operations defined in .insightpulse/sync.yaml.

Usage:
    # Dry-run all targets
    python scripts/sync_directional.py --dry-run

    # Sync specific target
    python scripts/sync_directional.py --target oca_repos

    # Sync by direction
    python scripts/sync_directional.py --direction pull

    # Run with verification
    python scripts/sync_directional.py --target oca_repos --verify

    # CI mode (fail on diff, no interactive)
    python scripts/sync_directional.py --ci --fail-on-diff

Examples:
    # Pull OCA repos
    python scripts/sync_directional.py --target oca_repos

    # Push to Notion (all Notion targets)
    python scripts/sync_directional.py --direction push --target notion_*

    # Verify Claude config sync
    python scripts/sync_directional.py --target claude_config --verify --dry-run
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SYNC_CONFIG_PATH = PROJECT_ROOT / ".insightpulse" / "sync.yaml"


class SyncResult:
    """Result of a sync operation."""

    def __init__(
        self,
        target: str,
        direction: str,
        success: bool,
        message: str,
        duration: float,
        outputs_created: List[str] = None,
        verification_passed: bool = None,
    ):
        self.target = target
        self.direction = direction
        self.success = success
        self.message = message
        self.duration = duration
        self.outputs_created = outputs_created or []
        self.verification_passed = verification_passed

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.target} ({self.direction}): {self.message} ({self.duration:.2f}s)"


class DirectionalSync:
    """Directional sync orchestrator."""

    def __init__(self, config_path: Path = SYNC_CONFIG_PATH, dry_run: bool = False):
        self.config_path = config_path
        self.dry_run = dry_run
        self.config = self._load_config()
        self.results: List[SyncResult] = []

    def _load_config(self) -> Dict[str, Any]:
        """Load sync configuration from YAML."""
        if not self.config_path.exists():
            logger.error(f"Config not found: {self.config_path}")
            sys.exit(1)

        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded config: {self.config_path}")
        logger.info(f"Version: {config.get('version', 'unknown')}")
        logger.info(f"Targets: {len(config.get('targets', {}))}")

        return config

    def list_targets(self, direction: Optional[str] = None) -> List[str]:
        """List available sync targets."""
        targets = []
        for name, cfg in self.config.get("targets", {}).items():
            target_direction = cfg.get(
                "direction", self.config["defaults"]["direction"]
            )

            if direction is None or target_direction == direction:
                targets.append(name)

        return targets

    def match_targets(self, pattern: str) -> List[str]:
        """Match targets by pattern (supports wildcards)."""
        all_targets = self.list_targets()
        regex = re.compile(pattern.replace("*", ".*"))
        return [t for t in all_targets if regex.match(t)]

    def _expand_env_vars(self, value: Any) -> Any:
        """Recursively expand environment variables in config values."""
        if isinstance(value, str):
            # Expand $HOME and other env vars
            return os.path.expandvars(value)
        elif isinstance(value, dict):
            return {k: self._expand_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._expand_env_vars(item) for item in value]
        return value

    def _run_command(
        self, command: str, cwd: Path = PROJECT_ROOT, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run shell command with logging."""
        logger.debug(f"Running: {command}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would run: {command}")
            return subprocess.CompletedProcess(
                args=command, returncode=0, stdout="", stderr=""
            )

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 and check:
            logger.error(f"Command failed (exit {result.returncode}): {command}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")

        return result

    def _check_required_env_vars(self, env_vars: List[str]) -> bool:
        """Check if required environment variables are set."""
        missing = [var for var in env_vars if not os.getenv(var)]

        if missing:
            logger.error(f"Missing environment variables: {', '.join(missing)}")
            return False

        return True

    def _run_pre_sync_checks(self, skip_on_pull: bool = False) -> bool:
        """Run pre-sync validation checks."""
        checks = self.config.get("safety", {}).get("pre_sync_checks", [])

        for check in checks:
            if skip_on_pull and check.get("skip_on_pull", False):
                logger.debug(f"Skipping check (pull mode): {check['name']}")
                continue

            logger.info(f"Pre-sync check: {check['name']}")
            result = self._run_command(check["command"], check=False)

            expected_exit = check.get("expected_exit_code", 0)
            if result.returncode != expected_exit:
                logger.error(f"Pre-sync check failed: {check['name']}")
                return False

        return True

    def _run_post_sync_checks(
        self, skip_on_push: bool = False, skip_on_pull: bool = False
    ) -> bool:
        """Run post-sync validation checks."""
        checks = self.config.get("safety", {}).get("post_sync_checks", [])

        for check in checks:
            if skip_on_push and check.get("skip_on_push", False):
                logger.debug(f"Skipping check (push mode): {check['name']}")
                continue

            if skip_on_pull and check.get("skip_on_pull", False):
                logger.debug(f"Skipping check (pull mode): {check['name']}")
                continue

            logger.info(f"Post-sync check: {check['name']}")
            result = self._run_command(check["command"], check=False)

            expected_exit = check.get("expected_exit_code", 0)
            if result.returncode != expected_exit:
                logger.error(f"Post-sync check failed: {check['name']}")
                return False

        return True

    def _verify_target(self, target_name: str, target_config: Dict[str, Any]) -> bool:
        """Verify sync target outputs/expectations."""
        verification = target_config.get("verification")
        if not verification:
            logger.debug(f"No verification defined for: {target_name}")
            return True

        logger.info(f"Verifying: {target_name}")
        result = self._run_command(verification["command"], check=False)

        expected_exit = verification.get("expected_exit_code", 0)
        if result.returncode != expected_exit:
            logger.error(f"Verification failed for: {target_name}")
            logger.error(f"Expected exit code: {expected_exit}, got: {result.returncode}")
            return False

        # Check min/max values if specified
        if "expected_min" in verification:
            try:
                actual_value = int(result.stdout.strip())
                if actual_value < verification["expected_min"]:
                    logger.error(
                        f"Verification failed: {actual_value} < {verification['expected_min']}"
                    )
                    return False
            except ValueError:
                logger.error(f"Could not parse verification output as integer")
                return False

        logger.info(f"Verification passed: {target_name}")
        return True

    def _git_commit_changes(self, message: str) -> bool:
        """Commit changes to git (PULL operations only)."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would commit: {message}")
            return True

        # Check if there are changes
        result = self._run_command("git diff --quiet && git diff --staged --quiet", check=False)
        if result.returncode == 0:
            logger.info("No changes to commit")
            return True

        # Stage all changes
        self._run_command("git add -A")

        # Commit
        self._run_command(f'git commit -m "{message}"')

        logger.info(f"Committed: {message}")
        return True

    def sync_target(
        self,
        target_name: str,
        verify: bool = False,
        fail_on_diff: bool = False,
    ) -> SyncResult:
        """Sync a single target."""
        start_time = datetime.now()
        target_config = self.config["targets"].get(target_name)

        if not target_config:
            return SyncResult(
                target=target_name,
                direction="unknown",
                success=False,
                message="Target not found in config",
                duration=0.0,
            )

        # Expand environment variables in config
        target_config = self._expand_env_vars(target_config)

        direction = target_config.get(
            "direction", self.config["defaults"]["direction"]
        )

        logger.info(f"Syncing: {target_name} ({direction})")
        logger.info(f"Description: {target_config.get('description', 'N/A')}")

        # Check required environment variables
        env_vars = target_config.get("config", {}).get("env_vars", [])
        if env_vars and not self._check_required_env_vars(env_vars):
            return SyncResult(
                target=target_name,
                direction=direction,
                success=False,
                message="Missing required environment variables",
                duration=0.0,
            )

        # Run pre-sync checks
        if not self._run_pre_sync_checks(skip_on_pull=(direction == "pull")):
            return SyncResult(
                target=target_name,
                direction=direction,
                success=False,
                message="Pre-sync checks failed",
                duration=0.0,
            )

        # Execute sync entrypoint
        entrypoint = target_config.get("entrypoint")
        if not entrypoint:
            return SyncResult(
                target=target_name,
                direction=direction,
                success=False,
                message="No entrypoint defined",
                duration=0.0,
            )

        entrypoint_path = PROJECT_ROOT / entrypoint
        if not entrypoint_path.exists():
            logger.warning(f"Entrypoint not found: {entrypoint_path}")

        # Build command
        command = str(entrypoint_path)
        if self.dry_run:
            command += " --dry-run"

        # Run sync
        result = self._run_command(command, check=False)
        success = result.returncode == 0

        # Collect outputs
        outputs_created = []
        for output_pattern in target_config.get("outputs", []):
            # Expand glob patterns
            output_path = PROJECT_ROOT / output_pattern
            if "*" in output_pattern:
                # Glob pattern
                outputs_created.extend([str(p) for p in PROJECT_ROOT.glob(output_pattern)])
            elif output_path.exists():
                outputs_created.append(str(output_path))

        # Run post-sync checks
        if success:
            if not self._run_post_sync_checks(
                skip_on_push=(direction == "push"),
                skip_on_pull=(direction == "pull"),
            ):
                success = False

        # Verify outputs
        verification_passed = None
        if verify or target_config.get("verification"):
            verification_passed = self._verify_target(target_name, target_config)
            if not verification_passed:
                success = False

        # Git commit (PULL operations only)
        if success and direction == "pull" and target_config.get("git_commit_message"):
            git_commit = target_config.get("git_commit", self.config["defaults"].get("git_commit", False))
            if git_commit:
                self._git_commit_changes(target_config["git_commit_message"])

        duration = (datetime.now() - start_time).total_seconds()

        return SyncResult(
            target=target_name,
            direction=direction,
            success=success,
            message=f"{'Success' if success else 'Failed'}",
            duration=duration,
            outputs_created=outputs_created,
            verification_passed=verification_passed,
        )

    def sync_all(
        self,
        direction: Optional[str] = None,
        target_pattern: Optional[str] = None,
        verify: bool = False,
    ) -> List[SyncResult]:
        """Sync all targets (optionally filtered by direction/pattern)."""
        # Determine targets to sync
        if target_pattern:
            targets = self.match_targets(target_pattern)
        elif direction:
            targets = self.list_targets(direction=direction)
        else:
            targets = self.list_targets()

        if not targets:
            logger.warning("No targets matched")
            return []

        logger.info(f"Syncing {len(targets)} targets: {', '.join(targets)}")

        # Sync each target
        results = []
        for target in targets:
            result = self.sync_target(target, verify=verify)
            results.append(result)
            self.results.append(result)

        return results

    def generate_summary(self) -> Dict[str, Any]:
        """Generate sync summary report."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful

        return {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "total_targets": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "N/A",
            "results": [
                {
                    "target": r.target,
                    "direction": r.direction,
                    "success": r.success,
                    "message": r.message,
                    "duration": round(r.duration, 2),
                    "outputs_created": r.outputs_created,
                    "verification_passed": r.verification_passed,
                }
                for r in self.results
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="DirectionalSync - Orchestrate PULL/PUSH/BIDIRECTIONAL sync operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--target",
        type=str,
        help="Sync specific target (supports wildcards: notion_*)",
    )

    parser.add_argument(
        "--direction",
        type=str,
        choices=["pull", "push", "bidirectional"],
        help="Sync only targets with specified direction",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode (show what would be synced)",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification checks after sync",
    )

    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with error if sync produces diffs (CI mode)",
    )

    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode (non-interactive, fail-fast)",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available targets and exit",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=SYNC_CONFIG_PATH,
        help=f"Path to sync config (default: {SYNC_CONFIG_PATH})",
    )

    parser.add_argument(
        "--summary-json",
        type=Path,
        help="Write summary report to JSON file",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize sync
    syncer = DirectionalSync(config_path=args.config, dry_run=args.dry_run)

    # List mode
    if args.list:
        targets = syncer.list_targets()
        print(f"\n📋 Available Sync Targets ({len(targets)}):\n")
        for target in targets:
            cfg = syncer.config["targets"][target]
            direction = cfg.get("direction", syncer.config["defaults"]["direction"])
            desc = cfg.get("description", "")
            print(f"  • {target:25} [{direction:15}] {desc}")
        print()
        sys.exit(0)

    # Run sync
    if args.target:
        result = syncer.sync_target(args.target, verify=args.verify, fail_on_diff=args.fail_on_diff)
        results = [result]
    else:
        results = syncer.sync_all(
            direction=args.direction,
            target_pattern=args.target,
            verify=args.verify,
        )

    # Print results
    print("\n" + "=" * 80)
    print("SYNC RESULTS")
    print("=" * 80)
    for result in results:
        print(result)

    # Generate summary
    summary = syncer.generate_summary()
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total:      {summary['total_targets']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed:     {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")

    # Write summary JSON
    if args.summary_json:
        with open(args.summary_json, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary written to: {args.summary_json}")

    # Exit code
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
