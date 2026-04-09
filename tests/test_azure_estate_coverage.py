"""
test_azure_estate_coverage.py — Verify estate audit coverage contract

Ensures:
1. Every authoritative type in estate_coverage.yaml has a query block in the audit script
2. Every query_key in the script is declared in estate_coverage.yaml
3. No authoritative type is silently unhandled
"""
import os
import re
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERAGE_FILE = os.path.join(REPO_ROOT, "ssot", "azure", "estate_coverage.yaml")
AUDIT_SCRIPT = os.path.join(REPO_ROOT, "scripts", "ci", "azure_estate_audit.sh")


@pytest.fixture
def coverage():
    with open(COVERAGE_FILE, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def script_content():
    with open(AUDIT_SCRIPT, "r") as f:
        return f.read()


@pytest.fixture
def script_query_keys(script_content):
    """Extract all section headers (query_keys) from the audit script."""
    # Matches lines like: echo "container_apps:" >> "${ESTATE_FILE}"
    pattern = r'echo "(\w+):" >> "\$\{ESTATE_FILE\}"'
    keys = re.findall(pattern, script_content)
    # Filter out non-query sections
    excluded = {"resource_groups", "summary", "per_type_counts"}
    return {k for k in keys if k not in excluded and not k.startswith("#")}


@pytest.fixture
def coverage_query_keys(coverage):
    """Extract all query_keys from coverage policy."""
    return {
        item["query_key"]
        for item in coverage.get("authoritative_types", [])
        if "query_key" in item
    }


def test_coverage_file_exists():
    assert os.path.exists(COVERAGE_FILE), f"Coverage policy missing: {COVERAGE_FILE}"


def test_audit_script_exists():
    assert os.path.exists(AUDIT_SCRIPT), f"Audit script missing: {AUDIT_SCRIPT}"


def test_every_coverage_type_has_query_block(coverage_query_keys, script_query_keys):
    """Every query_key in coverage policy must have a section in the script."""
    missing = coverage_query_keys - script_query_keys
    assert not missing, (
        f"Coverage policy declares query_keys not implemented in audit script: {missing}"
    )


def test_every_script_section_is_declared(script_query_keys, coverage_query_keys):
    """Every query section in the script must be declared in coverage policy."""
    undeclared = script_query_keys - coverage_query_keys
    assert not undeclared, (
        f"Audit script has query sections not declared in coverage policy: {undeclared}"
    )


def test_no_duplicate_query_keys(coverage):
    """No query_key should appear twice in coverage policy."""
    keys = [
        item["query_key"]
        for item in coverage.get("authoritative_types", [])
        if "query_key" in item
    ]
    duplicates = [k for k in keys if keys.count(k) > 1]
    assert not duplicates, f"Duplicate query_keys in coverage policy: {set(duplicates)}"


def test_all_types_classified(coverage):
    """Every type list must be non-empty or explicitly empty."""
    for tier in ["authoritative_types", "derived_types", "out_of_band_types"]:
        assert tier in coverage, f"Missing tier: {tier}"
        assert isinstance(coverage[tier], list), f"{tier} must be a list"


def test_critical_types_are_subset_of_authoritative(coverage):
    """Every critical type must also be an authoritative type."""
    auth_types = {
        item["type"].split(" ")[0]  # strip notes like "(Front Door)"
        for item in coverage.get("authoritative_types", [])
    }
    critical = set(coverage.get("critical_types", []))
    not_auth = critical - auth_types
    assert not not_auth, (
        f"Critical types not in authoritative_types: {not_auth}"
    )


def test_drift_gate_policy_exists(coverage):
    """Drift gate policy must define critical_missing as 'fail'."""
    policy = coverage.get("drift_gate_policy", {})
    assert policy.get("critical_missing") == "fail", (
        "drift_gate_policy.critical_missing must be 'fail'"
    )


def test_promotion_rule_exists(coverage):
    """Promotion rule must explicitly prohibit auto-update."""
    policy = coverage.get("drift_gate_policy", {})
    rule = policy.get("promotion_rule", "")
    assert "never" in rule.lower() or "Never" in rule, (
        "Promotion rule must explicitly say 'never auto-update'"
    )
