#!/usr/bin/env python3
"""
Repo Root Gate - Enforce allowlist of root files/folders

This script ensures the repository root remains clean and organized by:
1. Allowlisting only essential root files and directories
2. Blocking forbidden file extensions in root
3. Preventing accumulation of operational artifacts

Exit codes:
  0: All checks passed
  1: Forbidden files found in root
"""

import sys
from pathlib import Path
from typing import List, Set

# Root directory allowlist - keep this minimal (~15 items)
ALLOWED_ROOT_ITEMS: Set[str] = {
    # Documentation
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    # Build/orchestration
    "Makefile",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    "docker-compose.shell.yml",
    "Dockerfile",
    "Dockerfile.v0.10.0",
    "odoo-bin",
    # Python configuration
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-docs.txt",
    "requirements-oca.txt",
    # Node/JS configuration
    "package.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "turbo.json",
    "vercel.json",
    # Environment
    ".env.example",
    ".env.smtp.example",
    ".env.figma.example",
    # IDE/Editor config
    ".editorconfig",
    ".flake8",
    ".pre-commit-config.yaml",
    ".python-version",
    ".yamllint.yml",
    ".mypy-baseline.txt",
    "odoo.code-workspace",
    "mkdocs.yml",
    # Git configuration
    ".gitignore",
    ".gitmodules",
    ".agentignore",
    ".cursorignore",
    # OCA configuration
    "oca-aggregate.yml",
    "oca.lock.json",
    # Project-specific config
    "figma-make-dev.yaml",
    "figma.config.json",
    "devserver.config.json",
    "superclaude_bridge.yaml",
    "branch_protection.json",
    # Canonical directories
    ".github",
    ".devcontainer",
    ".vscode",
    "addons",
    "apps",
    "config",
    "catalog",
    "scripts",
    "deploy",
    "docs",
    "infra",
    "mcp",
    "oca-parity",
    "packages",
    "parity",
    "sandbox",
    "spec",
    "supabase",
    "templates",
    "third_party",
    "tools",
    "vendor",
    # New canonical buckets
    "reports",
    "artifacts",
    "data",
    "archive",
    "scratch",
    # Tool/framework directories
    ".agent",
    ".ai",
    ".claude",
    ".gemini",
    ".specify",
    ".supabase",
    ".venv",
    ".mypy_cache",
    ".githooks",
    "node_modules",
    "tests",
    # Project directories
    "agents",
    "api",
    "services",
    "src",
    "web",
    "frontend-fluent",
    "workflows",
    "integrations",
    "automations",
    "db",
    "schemas",
    "seeds",
    "runtime",
    "logs",
    "bin",
    "lib",
    ".lib",
    "odoo19",
    "odoo",
    "n8n",
    "tasks",
    "skills",
    "skillpack",
    "registry",
    "memory",
    "kb",
    "handbook",
    "prototypes",
    "research",
    "security",
    "secrets",
    "specs",
    "stack",
    "vercel",
    "releasekit",
    "seed_export",
    "clients",
    "contracts",
    "branding",
    "design",
    "design-tokens",
    "figma",
    "calendar",
    "ccpm",
    "dbt",
    "inventory",
    "baselines",
    "architecture-review",
    "audit",
    "ci",
    "claudedocs",
    "docflow-agentic-finance",
    "docs-assistant",
    "engines",
    "external-src",
    "harness",
    "ipai-platform",
    "mattermost",
    "notion-n8n-monthly-close",
    "ocr-adapter",
    "ocr_service",
    "odoo-schema-mirror",
    "odoo_local",
    "ops",
    "osi",
    "patches",
    "pkgs",
    "platform-kit",
    "agent-library",
    "agent-library-pack",
    "contains-studio-agents",
    "catalogs",
    "dev",
    ".insightpulse",
    ".refactor",
    ".colima",
    ".continue",
    "_work",
    # System files (ignore)
    ".DS_Store",
    ".env",
    ".env.dev",
    ".env.prod",
    ".env.stage",
    ".env.production",
    ".env.platform.local",
    ".env.figma",
}

# Forbidden file extensions in root
FORBIDDEN_EXTENSIONS: Set[str] = {
    ".csv",      # Data files → data/
    ".zip",      # Packages → artifacts/releases/
    ".log",      # Logs → logs/ or scratch/
    ".pid",      # Runtime → scratch/
    ".xlsx",     # Data files → data/
}

# Forbidden file name patterns in root
FORBIDDEN_PATTERNS: List[str] = [
    "parity_report",      # → reports/parity/
    "DEPLOYMENT_",        # → docs/runbooks/deploy/
    "DEPLOY_",            # → scripts/deploy/ or docs/runbooks/deploy/
    "_REPORT",            # → reports/ or docs/evidence/
    "_SUMMARY",           # → docs/ci/ or docs/evidence/
    "verify_",            # → scripts/verify/
    "deploy_",            # → scripts/deploy/
    "import_",            # → scripts/ appropriate subfolder
    "install_",           # → scripts/ appropriate subfolder
    "update_",            # → scripts/ appropriate subfolder
    "ship_",              # → scripts/deploy/
]


def get_root_items() -> List[Path]:
    """Get all items (files and directories) in repository root."""
    repo_root = Path(".")
    return [item for item in repo_root.iterdir() if item.name not in {".git"}]


def check_allowlist(items: List[Path]) -> List[str]:
    """Check if all root items are in the allowlist."""
    violations = []
    for item in items:
        if item.name not in ALLOWED_ROOT_ITEMS:
            violations.append(item.name)
    return violations


def check_forbidden_extensions(items: List[Path]) -> List[str]:
    """Check for forbidden file extensions in root."""
    violations = []
    for item in items:
        if item.is_file():
            ext = item.suffix.lower()
            if ext in FORBIDDEN_EXTENSIONS:
                violations.append(f"{item.name} (extension: {ext})")
    return violations


def check_forbidden_patterns(items: List[Path]) -> List[str]:
    """Check for forbidden file name patterns in root."""
    violations = []
    for item in items:
        if item.is_file():
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.lower() in item.name.lower():
                    violations.append(f"{item.name} (pattern: {pattern})")
                    break
    return violations


def main() -> int:
    """Run all root gate checks."""
    print("🔍 Running repo root gate checks...")
    print()

    items = get_root_items()

    # Check 1: Allowlist
    print("📋 Check 1: Root allowlist compliance")
    allowlist_violations = check_allowlist(items)
    if allowlist_violations:
        print(f"❌ Found {len(allowlist_violations)} non-allowlisted items in root:")
        for violation in sorted(allowlist_violations):
            print(f"  - {violation}")
        print()
    else:
        print("✅ All root items are allowlisted")
        print()

    # Check 2: Forbidden extensions
    print("📋 Check 2: Forbidden file extensions")
    ext_violations = check_forbidden_extensions(items)
    if ext_violations:
        print(f"❌ Found {len(ext_violations)} files with forbidden extensions:")
        for violation in sorted(ext_violations):
            print(f"  - {violation}")
        print()
        print("💡 Move these files to appropriate directories:")
        print("   - .csv → data/")
        print("   - .zip → artifacts/releases/")
        print("   - .log → logs/ or scratch/")
        print()
    else:
        print("✅ No forbidden file extensions in root")
        print()

    # Check 3: Forbidden patterns
    print("📋 Check 3: Forbidden file name patterns")
    pattern_violations = check_forbidden_patterns(items)
    if pattern_violations:
        print(f"❌ Found {len(pattern_violations)} files with forbidden patterns:")
        for violation in sorted(pattern_violations):
            print(f"  - {violation}")
        print()
        print("💡 Move these files to appropriate directories:")
        print("   - DEPLOYMENT_* → docs/runbooks/deploy/")
        print("   - deploy_* → scripts/deploy/")
        print("   - verify_* → scripts/verify/")
        print("   - *_REPORT* → reports/ or docs/evidence/")
        print()
    else:
        print("✅ No forbidden file name patterns in root")
        print()

    # Summary
    total_violations = len(allowlist_violations) + len(ext_violations) + len(pattern_violations)

    if total_violations > 0:
        print(f"❌ FAILED: {total_violations} total violations found")
        print()
        print("Run this command to see suggested locations:")
        print("  python scripts/repo_root_gate.py --suggest")
        return 1
    else:
        print("✅ PASSED: All root gate checks passed")
        print(f"📊 Root contains {len(items)} items (all allowlisted)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
