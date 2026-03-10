#!/usr/bin/env python3
"""Tests for install_oca_from_ssot.py — SSOT-driven OCA installer.

Operates on fixture YAML strings, not the real SSOT files.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

# Add scripts/odoo to path so we can import the module
import sys

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "scripts" / "odoo")
)

from install_oca_from_ssot import (
    InstallPlan,
    LockEntry,
    RepoEntry,
    load_lock,
    load_registry,
    resolve_plan,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
REGISTRY_YAML = """
version: 1
schema: ssot.odoo.oca_repos.v1
target_version: "19.0"

repos:
  - name: server-tools
    source: https://github.com/OCA/server-tools
    branch: _git_aggregated
    status: ok
    modules: 13

  - name: web
    source: https://github.com/OCA/web
    branch: _git_aggregated
    status: ok
    modules: 9

  - name: mail
    source: https://github.com/OCA/mail
    branch: "19.0"
    status: pinned
    modules: 7

  - name: bank-statement-import
    source: https://github.com/OCA/bank-statement-import
    branch: "18.0"
    status: blocked
    modules: 14

  - name: automation
    source: https://github.com/OCA/automation
    branch: _git_aggregated
    status: empty
    modules: 0

  - name: helpdesk
    source: https://github.com/OCA/helpdesk
    branch: "19.0"
    status: pending_vendor
    modules: 0
"""

LOCK_YAML = """
schema: ssot.odoo.oca_lock.v1
version: 1
odoo_version: "19.0"

repos:
  - name: server-tools
    source: https://github.com/OCA/server-tools
    target_path: addons/oca/server-tools
    branch: "19.0"
    ref: 4ae1186942461cfcc2ee14952335020cfa42af49
    shallow: false
    lifecycle: active

  - name: web
    source: https://github.com/OCA/web
    target_path: addons/oca/web
    branch: "19.0"
    ref: 9c6d0afb51af11191ba3b77872d466de1edbc75a
    shallow: false
    lifecycle: active
"""


def _write_yaml(content: str) -> Path:
    """Write YAML content to a temp file and return its path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestLoadRegistry(unittest.TestCase):
    def test_loads_all_repos(self):
        path = _write_yaml(REGISTRY_YAML)
        repos = load_registry(path)
        self.assertEqual(len(repos), 6)
        names = {r.name for r in repos}
        self.assertIn("server-tools", names)
        self.assertIn("bank-statement-import", names)
        path.unlink()

    def test_missing_repos_key_raises(self):
        path = _write_yaml("version: 1\nfoo: bar\n")
        with self.assertRaises(ValueError):
            load_registry(path)
        path.unlink()

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_registry(Path("/nonexistent/oca_repos.yaml"))


class TestLoadLock(unittest.TestCase):
    def test_loads_pinned_repos(self):
        path = _write_yaml(LOCK_YAML)
        lock = load_lock(path)
        self.assertEqual(len(lock), 2)
        self.assertIn("server-tools", lock)
        self.assertEqual(
            lock["server-tools"].ref,
            "4ae1186942461cfcc2ee14952335020cfa42af49",
        )
        path.unlink()

    def test_missing_file_returns_empty(self):
        lock = load_lock(Path("/nonexistent/oca_lock.yaml"))
        self.assertEqual(lock, {})


class TestResolvePlan(unittest.TestCase):
    def setUp(self):
        reg_path = _write_yaml(REGISTRY_YAML)
        lock_path = _write_yaml(LOCK_YAML)
        self.registry = load_registry(reg_path)
        self.lock = load_lock(lock_path)
        self.target = Path("/tmp/test_oca")
        reg_path.unlink()
        lock_path.unlink()

    def test_installable_count(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        self.assertEqual(plan.installable, 3)  # server-tools, web, mail

    def test_skipped_count(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        self.assertEqual(plan.skipped, 3)  # blocked, empty, pending_vendor

    def test_pinned_count(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        self.assertEqual(plan.pinned, 2)  # server-tools, web

    def test_unpinned_count(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        self.assertEqual(plan.unpinned, 1)  # mail (no lock entry)

    def test_blocked_repo_skipped(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        blocked = [i for i in plan.items if i.repo == "bank-statement-import"]
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0].decision, "skip")
        self.assertEqual(blocked[0].status, "blocked")

    def test_empty_repo_skipped(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        empty = [i for i in plan.items if i.repo == "automation"]
        self.assertEqual(len(empty), 1)
        self.assertEqual(empty[0].decision, "skip")

    def test_pending_vendor_skipped(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        pending = [i for i in plan.items if i.repo == "helpdesk"]
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].decision, "skip")

    def test_lock_sha_used_when_available(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        st = [i for i in plan.items if i.repo == "server-tools"]
        self.assertEqual(len(st), 1)
        self.assertEqual(
            st[0].ref, "4ae1186942461cfcc2ee14952335020cfa42af49"
        )
        self.assertEqual(st[0].decision, "install")

    def test_branch_fallback_when_no_lock(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        mail = [i for i in plan.items if i.repo == "mail"]
        self.assertEqual(len(mail), 1)
        self.assertEqual(mail[0].ref, "")  # no lock entry
        self.assertEqual(mail[0].branch, "19.0")

    def test_strict_mode_fails_on_unpinned(self):
        plan = resolve_plan(
            self.registry, self.lock, self.target, strict=True
        )
        self.assertTrue(len(plan.errors) > 0)
        # mail is installable but unpinned
        mail_errors = [e for e in plan.errors if "mail" in e]
        self.assertEqual(len(mail_errors), 1)

    def test_unknown_state_produces_error(self):
        bad_repo = RepoEntry(
            name="bad-repo",
            source="https://github.com/OCA/bad",
            branch="19.0",
            status="unknown_state",
        )
        plan = resolve_plan(
            [bad_repo], self.lock, self.target
        )
        self.assertEqual(len(plan.errors), 1)
        self.assertIn("unknown lifecycle", plan.errors[0])

    def test_deterministic_output(self):
        """Same input produces identical plan on repeated runs."""
        plan1 = resolve_plan(self.registry, self.lock, self.target)
        plan2 = resolve_plan(self.registry, self.lock, self.target)
        items1 = [(i.repo, i.decision, i.ref) for i in plan1.items]
        items2 = [(i.repo, i.decision, i.ref) for i in plan2.items]
        self.assertEqual(items1, items2)

    def test_items_sorted_by_name(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        names = [i.repo for i in plan.items]
        self.assertEqual(names, sorted(names))

    def test_json_output_valid(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        output = json.dumps(plan.to_dict())
        parsed = json.loads(output)
        self.assertIn("summary", parsed)
        self.assertIn("items", parsed)
        self.assertEqual(len(parsed["items"]), 6)

    def test_no_errors_in_normal_mode(self):
        plan = resolve_plan(self.registry, self.lock, self.target)
        self.assertEqual(len(plan.errors), 0)

    def test_empty_registry_raises(self):
        path = _write_yaml("version: 1\nnothing: here\n")
        with self.assertRaises(ValueError):
            load_registry(path)
        path.unlink()


if __name__ == "__main__":
    unittest.main()
