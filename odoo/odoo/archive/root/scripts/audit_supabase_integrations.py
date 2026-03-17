#!/usr/bin/env python3
"""
audit_supabase_integrations.py — Supabase integration auditor.

Two modes:
  --repo     (default) Scan repo source for integration evidence.
             Deterministic, CI-safe. Never reads secret VALUES.
  --machine  Scan local machine for installed CLI tools, MCP configs,
             and running services. Read-only, best-effort, local only.

Outputs:
  docs/supabase/integrations_detected.json      (--repo)
  docs/supabase/machine_integrations_detected.json  (--machine)

Also updates:
  reports/supabase_feature_integration_matrix.json
    integrations.*          from --repo evidence
    machine_autodetection   from --machine scan

Usage:
  python scripts/audit_supabase_integrations.py               # --repo default
  python scripts/audit_supabase_integrations.py --repo
  python scripts/audit_supabase_integrations.py --machine
  python scripts/audit_supabase_integrations.py --repo --machine
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

INTEGRATIONS_DETECTED_PATH = REPO_ROOT / "docs" / "supabase" / "integrations_detected.json"
MACHINE_DETECTED_PATH = REPO_ROOT / "docs" / "supabase" / "machine_integrations_detected.json"
MATRIX_PATH = REPO_ROOT / "reports" / "supabase_feature_integration_matrix.json"

LANE_IDS = [
    "deployment_hosting",
    "automation_workflows",
    "auth_providers",
    "data_ops_sync",
    "cms_admin",
    "observability",
    "templates",
]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    key: str
    lane: str
    name: str
    confidence: str  # "high" | "medium" | "low"
    evidence: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    def as_dict(self) -> dict:
        d: dict = {
            "key": self.key,
            "lane": self.lane,
            "name": self.name,
            "confidence": self.confidence,
            "evidence": sorted(self.evidence),
        }
        if self.notes:
            d["notes"] = self.notes
        return d


# ---------------------------------------------------------------------------
# Repo-evidence scanning helpers
# ---------------------------------------------------------------------------


def _rel(path: Path) -> str:
    """Return repo-relative forward-slash path."""
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _scan_file_globs(patterns: List[str]) -> List[str]:
    """Return sorted list of matching repo-relative file paths."""
    hits: List[str] = []
    for pattern in patterns:
        for p in REPO_ROOT.glob(pattern):
            if p.is_file():
                hits.append(_rel(p))
    return sorted(set(hits))


def _scan_package_json_deps(dep_names: List[str]) -> List[str]:
    """
    Scan package.json files in known workspace locations for listed dependency names.
    Returns sorted list of '<rel-path>:<dep-name>' evidence strings.
    Never reads lock files or reads values — only dependency NAMES.
    Scoped to workspace roots (not rglob of entire repo) for performance.
    """
    evidence: List[str] = []
    # Targeted workspace glob patterns — avoids 128K-file rglob
    pkg_patterns = [
        "package.json",
        "apps/*/package.json",
        "apps/*/*/package.json",
        "web/*/package.json",
        "web/*/*/package.json",
        "packages/*/package.json",
        "agents/*/package.json",
        "agents/*/*/package.json",
        "templates/*/package.json",
    ]
    exclude_dirs = {"node_modules", ".pnpm-store", ".cache", "dist", "build", ".next"}
    seen: set = set()
    pkg_paths: List[Path] = []
    for pattern in pkg_patterns:
        for p in REPO_ROOT.glob(pattern):
            if p.is_file() and str(p) not in seen:
                if not any(part in exclude_dirs for part in p.parts):
                    seen.add(str(p))
                    pkg_paths.append(p)

    for pkg_path in pkg_paths:
        try:
            data = json.loads(pkg_path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue

        all_deps: dict = {}
        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            if isinstance(data.get(section), dict):
                all_deps.update(data[section])

        for dep in dep_names:
            if dep in all_deps:
                evidence.append(f"{_rel(pkg_path)}:{dep}")

    return sorted(evidence)


def _scan_env_var_names(name_patterns: List[str]) -> List[str]:
    """
    Scan high-signal files for env var NAME patterns (not values).
    Scoped to: *.env.example, *.env.sample, docs/**/*.md, apps/**/*.md,
    .github/**/*.yml, infra/**/*.yml — to avoid scanning 17K+ files.
    Uses regex anchored at word boundaries.
    Returns sorted list of '<rel-path>:<matched-name>' evidence strings.
    """
    evidence: List[str] = []
    exclude_dirs = {"node_modules", ".pnpm-store", ".cache", "dist", "build", ".next"}
    # Narrow glob patterns to high-signal locations only
    # NOTE: Never use bare "**/<pattern>" as that walks 128K+ files.
    glob_patterns = [
        "*.env.example",
        "*.env.sample",
        "apps/*/.env.example",
        "apps/*/.env.sample",
        "web/*/.env.example",
        "web/*/.env.sample",
        "docs/ops/*.md",
        "docs/architecture/*.md",
        "apps/**/*.md",
        ".github/**/*.yml",
        "infra/**/*.yml",
        "infra/**/*.yaml",
        "config/**/*.md",
    ]
    seen_files: set = set()

    for pattern in glob_patterns:
        for path in REPO_ROOT.glob(pattern):
            if not path.is_file():
                continue
            if any(part in exclude_dirs for part in path.parts):
                continue
            rel = _rel(path)
            if rel in seen_files:
                continue
            seen_files.add(rel)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for name_pat in name_patterns:
                # Match variable name occurrence (not value)
                if re.search(r"\b" + re.escape(name_pat) + r"\b", text, re.IGNORECASE):
                    evidence.append(f"{rel}:{name_pat}")

    return sorted(set(evidence))


# ---------------------------------------------------------------------------
# Integration SIGNALS definition
# ---------------------------------------------------------------------------

# Each signal: (key, lane, name, file_globs, pkg_deps, env_var_names, confidence)
REPO_SIGNALS = [
    # --- deployment_hosting ---
    {
        "key": "vercel",
        "lane": "deployment_hosting",
        "name": "Vercel",
        "file_globs": [
            "vercel.json",
            "apps/*/vercel.json",
            "web/*/vercel.json",
            ".github/workflows/*vercel*.yml",
            ".vercel/**",
        ],
        "pkg_deps": ["vercel", "@vercel/analytics", "@vercel/speed-insights", "@vercel/og"],
        "env_var_names": ["VERCEL_TOKEN", "VERCEL_ORG_ID", "VERCEL_PROJECT_ID", "NEXT_PUBLIC_VERCEL_URL"],
        "confidence_file": "high",
    },
    # --- automation_workflows ---
    {
        "key": "n8n",
        "lane": "automation_workflows",
        "name": "n8n",
        "file_globs": [
            "automations/n8n/**/*.json",
            "automations/n8n/**/*.yml",
            ".github/workflows/*n8n*.yml",
            "infra/**/*n8n*",
        ],
        "pkg_deps": ["n8n", "n8n-nodes-base"],
        "env_var_names": ["N8N_HOST", "N8N_PORT", "N8N_WEBHOOK_URL", "N8N_API_KEY"],
        "confidence_file": "high",
    },
    # --- auth_providers ---
    {
        "key": "supabase-auth",
        "lane": "auth_providers",
        "name": "Supabase Auth",
        "file_globs": [
            "supabase/config.toml",
            "supabase/**/*.sql",
            ".github/workflows/*supabase*.yml",
        ],
        "pkg_deps": ["@supabase/supabase-js", "@supabase/auth-helpers-nextjs", "@supabase/auth-ui-react"],
        "env_var_names": ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "NEXT_PUBLIC_SUPABASE_URL"],
        "confidence_file": "high",
    },
    {
        "key": "ipai-auth-oidc",
        "lane": "auth_providers",
        "name": "ipai_auth_oidc (OIDC relay)",
        "file_globs": [
            "addons/ipai/ipai_auth_oidc/**",
        ],
        "pkg_deps": [],
        "env_var_names": ["OIDC_CLIENT_ID", "OIDC_CLIENT_SECRET", "OIDC_PROVIDER_URL"],
        "confidence_file": "high",
    },
    {
        "key": "auth0",
        "lane": "auth_providers",
        "name": "Auth0",
        "file_globs": [
            ".github/workflows/*auth0*.yml",
        ],
        "pkg_deps": ["@auth0/nextjs-auth0", "auth0", "express-openid-connect"],
        "env_var_names": ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET", "AUTH0_SECRET"],
        "confidence_file": "high",
    },
    {
        "key": "clerk",
        "lane": "auth_providers",
        "name": "Clerk",
        "file_globs": [],
        "pkg_deps": ["@clerk/nextjs", "@clerk/clerk-react", "@clerk/clerk-sdk-node"],
        "env_var_names": ["NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY"],
        "confidence_file": "high",
    },
    {
        "key": "okta",
        "lane": "auth_providers",
        "name": "Okta",
        "file_globs": [],
        "pkg_deps": ["@okta/okta-sdk-nodejs", "@okta/oidc-middleware"],
        "env_var_names": ["OKTA_DOMAIN", "OKTA_CLIENT_ID", "OKTA_CLIENT_SECRET"],
        "confidence_file": "high",
    },
    # --- data_ops_sync ---
    {
        "key": "github-actions",
        "lane": "data_ops_sync",
        "name": "GitHub Actions",
        "file_globs": [
            ".github/workflows/*.yml",
        ],
        "pkg_deps": [],
        "env_var_names": ["GITHUB_TOKEN", "GH_TOKEN"],
        "confidence_file": "high",
    },
    {
        "key": "airbyte",
        "lane": "data_ops_sync",
        "name": "Airbyte",
        "file_globs": [
            "**/airbyte*.yml",
            "infra/**/*airbyte*",
        ],
        "pkg_deps": ["airbyte-api"],
        "env_var_names": ["AIRBYTE_URL", "AIRBYTE_CLIENT_ID", "AIRBYTE_CLIENT_SECRET"],
        "confidence_file": "medium",
    },
    {
        "key": "stacksync",
        "lane": "data_ops_sync",
        "name": "Stacksync",
        "file_globs": [],
        "pkg_deps": ["stacksync"],
        "env_var_names": ["STACKSYNC_API_KEY", "STACKSYNC_WORKSPACE_ID"],
        "confidence_file": "medium",
    },
    # --- cms_admin ---
    {
        "key": "directus",
        "lane": "cms_admin",
        "name": "Directus",
        "file_globs": [
            "infra/**/*directus*",
            ".github/workflows/*directus*.yml",
        ],
        "pkg_deps": ["directus", "@directus/sdk"],
        "env_var_names": ["DIRECTUS_URL", "DIRECTUS_TOKEN", "DIRECTUS_ADMIN_EMAIL"],
        "confidence_file": "high",
    },
    # --- observability ---
    {
        "key": "digitalocean-monitoring",
        "lane": "observability",
        "name": "DigitalOcean Monitoring",
        "file_globs": [
            "infra/observability/**",
            ".github/workflows/*digitalocean*.yml",
            "infra/do/**",
        ],
        "pkg_deps": ["@digitalocean/api-sdk"],
        "env_var_names": ["DO_ACCESS_TOKEN", "DIGITALOCEAN_API_TOKEN", "DO_SPACE_ENDPOINT"],
        "confidence_file": "high",
    },
    {
        "key": "sentry",
        "lane": "observability",
        "name": "Sentry",
        "file_globs": [
            "sentry.*.config.*",
            ".github/workflows/*sentry*.yml",
        ],
        "pkg_deps": ["@sentry/nextjs", "@sentry/node", "@sentry/react", "sentry-sdk"],
        "env_var_names": ["SENTRY_DSN", "NEXT_PUBLIC_SENTRY_DSN", "SENTRY_AUTH_TOKEN"],
        "confidence_file": "high",
    },
    {
        "key": "datadog",
        "lane": "observability",
        "name": "Datadog",
        "file_globs": [
            "datadog.yaml",
            "infra/**/*datadog*",
        ],
        "pkg_deps": ["dd-trace", "datadog-lambda-js"],
        "env_var_names": ["DD_API_KEY", "DD_APP_KEY", "DATADOG_API_KEY"],
        "confidence_file": "high",
    },
    # --- templates ---
    {
        "key": "supabase-templates",
        "lane": "templates",
        "name": "Supabase Template Starters",
        "file_globs": [
            "templates/**",
            ".specifyrc*",
        ],
        "pkg_deps": ["create-next-app", "create-remix"],
        "env_var_names": [],
        "confidence_file": "low",
    },
]


def discover_repo() -> List[Finding]:
    """Scan repo for integration evidence. Returns list of Finding objects."""
    findings: List[Finding] = []

    for sig in REPO_SIGNALS:
        key = sig["key"]
        lane = sig["lane"]
        name = sig["name"]
        evidence: List[str] = []

        # File globs
        file_hits = _scan_file_globs(sig.get("file_globs", []))
        evidence.extend(f"file:{h}" for h in file_hits)

        # package.json deps
        dep_hits = _scan_package_json_deps(sig.get("pkg_deps", []))
        evidence.extend(f"pkg:{h}" for h in dep_hits)

        # Env var names in docs/templates
        env_hits = _scan_env_var_names(sig.get("env_var_names", []))
        evidence.extend(f"env_name:{h}" for h in env_hits)

        if not evidence:
            continue  # No evidence found — skip

        # Determine confidence
        has_file = bool(file_hits)
        confidence = sig.get("confidence_file", "medium") if has_file else "low"
        if dep_hits:
            confidence = "high"

        findings.append(Finding(
            key=key,
            lane=lane,
            name=name,
            confidence=confidence,
            evidence=evidence,
        ))

    # Deduplicate by key (keep first occurrence, highest confidence)
    seen: dict = {}
    for f in findings:
        if f.key not in seen:
            seen[f.key] = f
        else:
            # Upgrade confidence if better evidence found
            rank = {"high": 3, "medium": 2, "low": 1}
            if rank.get(f.confidence, 0) > rank.get(seen[f.key].confidence, 0):
                seen[f.key].confidence = f.confidence
            seen[f.key].evidence.extend(f.evidence)

    return sorted(seen.values(), key=lambda x: (x.lane, x.key))


# ---------------------------------------------------------------------------
# Machine scanning helpers
# ---------------------------------------------------------------------------

_MACHINE_TOOL_TIMEOUT = 3  # seconds


def _detect_cli(tool: str) -> Optional[dict]:
    """
    Safely detect a CLI tool: check presence via shutil.which,
    then try to capture version string.
    Returns dict with path and version (first non-empty line), or None.
    """
    path = shutil.which(tool)
    if not path:
        return None

    version = "(unknown)"
    version_flags = ["--version", "-v", "version", "-V"]
    for flag in version_flags:
        try:
            result = subprocess.run(
                [path, flag],
                capture_output=True,
                text=True,
                timeout=_MACHINE_TOOL_TIMEOUT,
            )
            # Take first non-empty line from stdout or stderr
            for line in (result.stdout + result.stderr).splitlines():
                line = line.strip()
                if line:
                    version = line[:120]  # cap length
                    break
            if version != "(unknown)":
                break
        except (subprocess.TimeoutExpired, OSError, PermissionError):
            continue

    return {"tool": tool, "path": path, "version": version}


CLI_TOOLS = [
    "supabase", "psql", "docker", "docker-compose",
    "node", "npm", "pnpm", "yarn",
    "gh", "git", "jq", "rg",
    "python", "python3", "terraform", "kubectl",
]


def _detect_mcp_configs() -> List[str]:
    """
    Discover MCP configuration file paths (repo + common user config dirs).
    Returns sorted list of absolute path strings (files only, no values read).
    """
    paths: List[str] = []

    # Repo-level MCP configs
    repo_patterns = ["**/*.mcp.json", "mcp/**/*.yml", "mcp/**/*.yaml", ".mcp.json"]
    for pattern in repo_patterns:
        for p in REPO_ROOT.glob(pattern):
            if p.is_file():
                paths.append(str(p))

    # User-level config dirs (common locations)
    home = Path.home()
    user_dirs = [
        home / ".claude",
        home / ".config" / "claude",
        home / ".config" / "mcp",
        home / "Library" / "Application Support" / "Claude",  # macOS
    ]
    user_patterns = ["mcp*.json", "*mcp*.json", "mcp-servers.json", "claude_mcp.json"]

    for base in user_dirs:
        if not base.exists():
            continue
        for pattern in user_patterns:
            for p in base.rglob(pattern):
                if p.is_file():
                    paths.append(str(p))

    return sorted(set(paths))


def _detect_docker_services() -> List[str]:
    """
    Attempt to list running Docker container names (non-invasive, names only).
    Returns sorted list or empty list if Docker is unavailable.
    """
    docker = shutil.which("docker")
    if not docker:
        return []
    try:
        result = subprocess.run(
            [docker, "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=_MACHINE_TOOL_TIMEOUT,
        )
        names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(names)
    except (subprocess.TimeoutExpired, OSError, PermissionError):
        return []


def discover_machine() -> dict:
    """
    Scan local machine for tools, MCP configs, and service hints.
    Returns a dict suitable for machine_integrations_detected.json.
    """
    tools: List[dict] = []
    for tool_name in sorted(CLI_TOOLS):
        info = _detect_cli(tool_name)
        if info:
            tools.append(info)

    mcp_configs = _detect_mcp_configs()
    docker_services = _detect_docker_services()

    return {
        "_meta": {
            "generated": datetime.now(tz=timezone.utc).isoformat(),
            "source": "local-machine-read-only",
            "note": "Local only — never commit this file.",
        },
        "cli_tools": tools,
        "mcp_config_paths": mcp_configs,
        "docker_service_names": docker_services,
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_integrations_detected(findings: List[Finding]) -> None:
    """Write docs/supabase/integrations_detected.json."""
    INTEGRATIONS_DETECTED_PATH.parent.mkdir(parents=True, exist_ok=True)

    lanes: dict = {lane: [] for lane in LANE_IDS}
    for f in findings:
        if f.lane in lanes:
            lanes[f.lane].append(f.as_dict())

    output = {
        "_meta": {
            "version": "1.0.0",
            "generated": datetime.now(tz=timezone.utc).isoformat(),
            "source": "repo-evidence-only",
            "note": "Auto-generated by scripts/audit_supabase_integrations.py --repo. Do not hand-edit.",
        },
        "findings_count": len(findings),
        "integrations": lanes,
    }

    INTEGRATIONS_DETECTED_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[REPO] Wrote {len(findings)} findings → {_rel(INTEGRATIONS_DETECTED_PATH)}")


def write_machine_detected(machine_data: dict) -> None:
    """Write docs/supabase/machine_integrations_detected.json."""
    MACHINE_DETECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    MACHINE_DETECTED_PATH.write_text(
        json.dumps(machine_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    tools_count = len(machine_data.get("cli_tools", []))
    mcp_count = len(machine_data.get("mcp_config_paths", []))
    services_count = len(machine_data.get("docker_service_names", []))
    print(
        f"[MACHINE] Wrote → {_rel(MACHINE_DETECTED_PATH)} "
        f"({tools_count} tools, {mcp_count} MCP configs, {services_count} services)"
    )


def update_matrix_repo(findings: List[Finding]) -> None:
    """
    Update reports/supabase_feature_integration_matrix.json integrations.* lanes
    with repo-detected entries. Also sets autodetection.source.
    """
    if not MATRIX_PATH.exists():
        print(f"[WARN] Matrix file not found: {_rel(MATRIX_PATH)} — skipping update")
        return

    try:
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] Cannot read matrix: {e} — skipping update")
        return

    # Reset lanes
    integrations: dict = {lane: [] for lane in LANE_IDS}
    for f in findings:
        if f.lane in integrations:
            entry = {"key": f.key, "name": f.name, "confidence": f.confidence}
            integrations[f.lane].append(entry)

    matrix["integrations"] = integrations
    matrix.setdefault("autodetection", {})["source"] = "repo-evidence-only"
    matrix.setdefault("autodetection", {})["output"] = _rel(INTEGRATIONS_DETECTED_PATH)
    matrix.setdefault("autodetection", {})["last_run"] = datetime.now(tz=timezone.utc).isoformat()

    MATRIX_PATH.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[REPO] Updated matrix integrations.* → {_rel(MATRIX_PATH)}")


def update_matrix_machine(machine_data: dict) -> None:
    """
    Update reports/supabase_feature_integration_matrix.json machine_autodetection section.
    Stores tool names/versions/paths only — no secrets.
    """
    if not MATRIX_PATH.exists():
        print(f"[WARN] Matrix file not found: {_rel(MATRIX_PATH)} — skipping update")
        return

    try:
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] Cannot read matrix: {e} — skipping update")
        return

    tools = [
        {"tool": t["tool"], "version": t["version"], "path": t["path"]}
        for t in machine_data.get("cli_tools", [])
    ]

    matrix["machine_autodetection"] = {
        "source": "local-machine-read-only",
        "last_run": machine_data["_meta"]["generated"],
        "cli_tools": tools,
        "mcp_config_paths": machine_data.get("mcp_config_paths", []),
        "docker_service_hints": machine_data.get("docker_service_names", []),
        "note": "Tool names/versions/paths only — no secrets.",
    }

    # If both repo and machine have run, update the composite source
    if matrix.get("autodetection", {}).get("source") == "repo-evidence-only":
        matrix["autodetection"]["source"] = "repo+machine"

    MATRIX_PATH.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[MACHINE] Updated matrix machine_autodetection → {_rel(MATRIX_PATH)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Supabase integrations in this repo (--repo) and/or local machine (--machine)."
    )
    parser.add_argument(
        "--repo",
        action="store_true",
        help="Scan repo source for integration evidence (default if no flags given).",
    )
    parser.add_argument(
        "--machine",
        action="store_true",
        help="Scan local machine for CLI tools, MCP configs, and service hints (read-only, local only).",
    )
    args = parser.parse_args()

    # Default: --repo if no flags
    if not args.repo and not args.machine:
        args.repo = True

    if args.repo:
        print("[REPO] Scanning repo for integration signals...")
        findings = discover_repo()
        write_integrations_detected(findings)
        update_matrix_repo(findings)
        print(f"[REPO] Done — {len(findings)} integration(s) detected.")

    if args.machine:
        print("[MACHINE] Scanning local machine (read-only)...")
        machine_data = discover_machine()
        write_machine_detected(machine_data)
        update_matrix_machine(machine_data)
        print("[MACHINE] Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
