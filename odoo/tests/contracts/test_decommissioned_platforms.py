"""
Drift guard: ensure decommissioned platforms stay removed.

Vercel and DigitalOcean are decommissioned as of 2026-03-13.
Azure Container Apps is the canonical compute target.
This test prevents accidental reintroduction of removed platform artifacts.
"""

import pathlib
import re
import subprocess
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestNoVercelArtifacts(unittest.TestCase):
    """Vercel is deprecated. No vercel.json or Vercel workflows should exist."""

    def test_no_vercel_json_files(self):
        """No vercel.json files should exist anywhere in the repo."""
        matches = list(REPO_ROOT.rglob("vercel.json"))
        # Filter out node_modules and .git
        matches = [
            m for m in matches
            if ".git" not in m.parts and "node_modules" not in m.parts
        ]
        self.assertEqual(
            matches,
            [],
            f"Found vercel.json files that should have been removed: {matches}",
        )

    def test_no_vercel_workflows(self):
        """No GitHub workflows should reference Vercel deployments."""
        workflow_dir = REPO_ROOT / ".github" / "workflows"
        if not workflow_dir.exists():
            return
        vercel_workflows = []
        for wf in workflow_dir.glob("*.yml"):
            content = wf.read_text(errors="replace")
            if re.search(r"vercel[_-](preview|production|deploy)", content, re.I):
                vercel_workflows.append(wf.name)
        # Also check nested workflow dirs
        for wf in REPO_ROOT.rglob(".github/workflows/vercel-*.yml"):
            if ".git" not in wf.parts and "node_modules" not in wf.parts:
                vercel_workflows.append(str(wf.relative_to(REPO_ROOT)))
        self.assertEqual(
            vercel_workflows,
            [],
            f"Found Vercel workflow files: {vercel_workflows}",
        )

    def test_vercel_ssot_marked_deprecated(self):
        """Vercel SSOT provider file must show status: deprecated."""
        provider_file = REPO_ROOT / "infra" / "ssot" / "providers" / "vercel" / "sandbox.yaml"
        if not provider_file.exists():
            self.skipTest("Vercel provider file not found")
        content = provider_file.read_text()
        self.assertIn("status: deprecated", content)


class TestNoDigitalOceanActive(unittest.TestCase):
    """DigitalOcean is decommissioned. SSOT must reflect this."""

    def test_do_ssot_marked_decommissioned(self):
        """DO SSOT provider file must show status: decommissioned."""
        provider_file = REPO_ROOT / "infra" / "ssot" / "providers" / "digitalocean" / "provider.yaml"
        if not provider_file.exists():
            self.skipTest("DO provider file not found")
        content = provider_file.read_text()
        self.assertIn("status: decommissioned", content)


if __name__ == "__main__":
    unittest.main()
