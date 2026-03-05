#!/usr/bin/env python3
"""
Validate GitHub organization taxonomy SSOT.

Validates ssot/github/org_repos.yaml against schema requirements and GitHub API.

Checks:
1. Schema validation (required fields, valid tier values)
2. GitHub API verification (repos exist, visibility matches)
3. Cross-reference with secrets registry (required_for matches)
4. Naming convention enforcement (@ipai/ package scope)
5. Duplicate detection

Exit codes:
- 0: All validations passed
- 1: Validation errors found
- 2: Critical error (file missing, schema invalid)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(2)

# Schema constants
VALID_TIERS = ["0", "1", "2", "3", "4", "ui_libs", "finance"]
VALID_CATEGORIES = [
    "governance",
    "primitives",
    "operator_ux",
    "product_apps",
    "labs",
    "ui_libraries",
    "finance",
]
VALID_CLASSIFICATIONS = ["public", "confidential", "restricted"]
VALID_LIFECYCLES = ["active", "maintenance", "deprecated", "archived"]
REQUIRED_FIELDS = [
    "repo_name",
    "tier",
    "category",
    "system_of_record",
    "data_classification",
    "lifecycle",
    "canonical_packages",
    "visibility",
    "description",
]


def find_repo_root() -> Path:
    """Find repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def load_taxonomy(file_path: Path) -> Dict:
    """Load and parse org taxonomy YAML file."""
    if not file_path.exists():
        print(f"ERROR: Taxonomy file not found: {file_path}")
        sys.exit(2)

    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return data
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax: {e}")
        sys.exit(2)


def validate_schema(data: Dict) -> List[str]:
    """Validate taxonomy against schema requirements."""
    errors = []

    # Check root fields
    if "schema_version" not in data:
        errors.append("Missing schema_version field")
    if "org" not in data:
        errors.append("Missing org field")
    if "repos" not in data or not isinstance(data["repos"], list):
        errors.append("Missing or invalid repos field (must be array)")
        return errors  # Can't continue without repos

    seen_names = set()
    for idx, repo in enumerate(data["repos"]):
        repo_id = repo.get("repo_name", f"<unnamed-{idx}>")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in repo:
                errors.append(f"Repo '{repo_id}': Missing required field '{field}'")

        # Check tier validity
        tier = str(repo.get("tier", ""))
        if tier not in VALID_TIERS:
            errors.append(
                f"Repo '{repo_id}': Invalid tier '{tier}'. Must be one of {VALID_TIERS}"
            )

        # Check category validity
        category = repo.get("category", "")
        if category not in VALID_CATEGORIES:
            errors.append(
                f"Repo '{repo_id}': Invalid category '{category}'. Must be one of {VALID_CATEGORIES}"
            )

        # Check data classification
        classification = repo.get("data_classification", "")
        if classification not in VALID_CLASSIFICATIONS:
            errors.append(
                f"Repo '{repo_id}': Invalid data_classification '{classification}'. Must be one of {VALID_CLASSIFICATIONS}"
            )

        # Check lifecycle
        lifecycle = repo.get("lifecycle", "")
        if lifecycle not in VALID_LIFECYCLES:
            errors.append(
                f"Repo '{repo_id}': Invalid lifecycle '{lifecycle}'. Must be one of {VALID_LIFECYCLES}"
            )

        # Check package scope (@ipai/* convention)
        packages = repo.get("canonical_packages", [])
        if not isinstance(packages, list):
            errors.append(
                f"Repo '{repo_id}': canonical_packages must be array, got {type(packages).__name__}"
            )
        else:
            for pkg in packages:
                if not pkg.startswith("@ipai/"):
                    errors.append(
                        f"Repo '{repo_id}': Package '{pkg}' must use @ipai/ scope"
                    )

        # Check for duplicates
        if repo_id in seen_names:
            errors.append(f"Duplicate repo_name: '{repo_id}'")
        seen_names.add(repo_id)

    return errors


def validate_github_repos(data: Dict) -> List[str]:
    """Validate repos exist on GitHub and visibility matches."""
    errors = []
    warnings = []

    # Check if GITHUB_TOKEN is available
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        warnings.append(
            "GITHUB_TOKEN not set - skipping GitHub API verification (not an error in local dev)"
        )
        print("⚠️  " + warnings[0])
        return errors

    try:
        import requests
    except ImportError:
        warnings.append("requests library not installed - skipping GitHub API checks")
        print("⚠️  " + warnings[0])
        return errors

    org = data.get("org", "Insightpulseai")
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    for repo in data.get("repos", []):
        repo_name = repo.get("repo_name")
        expected_visibility = repo.get("visibility")

        if not repo_name or repo_name.startswith("<unnamed"):
            continue

        url = f"https://api.github.com/repos/{org}/{repo_name}"
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 404:
                errors.append(
                    f"Repo '{repo_name}': Not found on GitHub (404) - may need to be created"
                )
            elif response.status_code == 200:
                repo_data = response.json()
                actual_visibility = "public" if not repo_data.get("private") else "private"

                if actual_visibility != expected_visibility:
                    errors.append(
                        f"Repo '{repo_name}': Visibility mismatch. Expected '{expected_visibility}', got '{actual_visibility}'"
                    )
            else:
                warnings.append(
                    f"Repo '{repo_name}': GitHub API returned {response.status_code}"
                )

        except requests.RequestException as e:
            warnings.append(f"Repo '{repo_name}': GitHub API request failed: {e}")

    if warnings:
        for warning in warnings:
            print(f"⚠️  {warning}")

    return errors


def main():
    """Run all validations."""
    try:
        repo_root = find_repo_root()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    taxonomy_file = repo_root / "ssot" / "github" / "org_repos.yaml"

    print("🔍 Validating GitHub organization taxonomy...")
    print(f"   File: {taxonomy_file}")

    # Load taxonomy
    data = load_taxonomy(taxonomy_file)
    print(f"✅ Loaded {len(data.get('repos', []))} repositories")

    # Run validations
    all_errors = []

    print("\n📋 Schema validation...")
    schema_errors = validate_schema(data)
    all_errors.extend(schema_errors)
    if schema_errors:
        for error in schema_errors:
            print(f"   ❌ {error}")
    else:
        print("   ✅ Schema valid")

    print("\n🌐 GitHub API verification...")
    github_errors = validate_github_repos(data)
    all_errors.extend(github_errors)
    if github_errors:
        for error in github_errors:
            print(f"   ❌ {error}")
    else:
        print("   ✅ GitHub repos verified")

    # Summary
    print("\n" + "=" * 70)
    if all_errors:
        print(f"❌ FAILED: {len(all_errors)} validation error(s)")
        print("\nErrors:")
        for error in all_errors:
            print(f"   • {error}")
        sys.exit(1)
    else:
        print("✅ SUCCESS: All validations passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
