#!/usr/bin/env python3
"""
Azure Resource Graph ↔ SSOT Reconciliation

Queries Azure Resource Graph for actual resources, compares against
ssot/architecture/services.yaml and infra/ssot/azure/service-matrix.yaml.

Exits non-zero if drift is found. Designed for CI or local use.

Usage:
    python3 scripts/ci/azure_resource_reconcile.py [--snapshot /path/to/snapshot.json]
    # If --snapshot is given, uses a pre-captured JSON instead of live query.
    # Otherwise requires `az` CLI logged in.

Output:
    docs/evidence/<timestamp>/resource-reconcile/reconcile.json
"""

import json
import os
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SERVICES_YAML = REPO_ROOT / "ssot" / "architecture" / "services.yaml"
SERVICE_MATRIX = REPO_ROOT / "infra" / "ssot" / "azure" / "service-matrix.yaml"
DNS_REGISTRY = REPO_ROOT / "infra" / "dns" / "subdomain-registry.yaml"


def query_resource_graph():
    """Query Azure Resource Graph for all resources."""
    cmd = [
        "az", "graph", "query",
        "-q", "Resources | project name, type, resourceGroup, location | order by resourceGroup asc",
        "--first", "200",
        "-o", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: az graph query failed: {result.stderr}", file=sys.stderr)
        sys.exit(2)
    data = json.loads(result.stdout)
    return data.get("data", data)


def load_snapshot(path):
    """Load a pre-captured Resource Graph snapshot."""
    with open(path) as f:
        data = json.load(f)
    return data.get("data", data)


def load_yaml(path):
    """Load a YAML file, return None if missing."""
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def classify_resource(r):
    """Map Azure resource type to a platform plane."""
    t = r.get("type", "").lower()
    name = r.get("name", "").lower()

    if "containerapps" in t or "managedenvironments" in t:
        return "compute"
    if "dbforpostgresql" in t:
        return "database"
    if "containerregistry" in t:
        return "registry"
    if "keyvault" in t:
        return "secrets"
    if "machinelearningservices" in t:
        return "ai_foundry"
    if "cognitiveservices" in t:
        if "openai" in name or "oai" in name:
            return "ai_openai"
        if "docai" in name or "intel" in name:
            return "ai_doc_intel"
        if "vision" in name:
            return "ai_vision"
        if "lang" in name:
            return "ai_language"
        return "ai_cognitive"
    if "databricks" in t:
        return "databricks"
    if "search" in t:
        return "ai_search"
    if "storage" in t:
        return "storage"
    if "virtualnetworks" in t or "networksecurity" in t or "networkintent" in t:
        return "networking"
    if "privatednszones" in t:
        return "private_dns"
    if "dnszones" in t and "private" not in t:
        return "public_dns"
    if "managedidentity" in t:
        return "identity"
    if "insights" in t or "operationalinsights" in t:
        return "observability"
    if "devopsinfrastructure" in t:
        return "devops"
    if "networkwatchers" in t:
        return "system"
    if "visualstudio" in t:
        return "devops"
    return "other"


def check_ssot_services(resources, services_data):
    """Compare live resources against services.yaml declarations."""
    issues = []

    if not services_data:
        issues.append({"severity": "warn", "msg": "services.yaml not found"})
        return issues

    active = services_data.get("active_services", {})
    retired = services_data.get("retired_services", [])

    # Build lookup of live resource names
    live_names = {r["name"].lower() for r in resources}
    live_types = {r["type"].lower() for r in resources}

    # Check retired services aren't still running as ACA apps
    retired_names = {s.get("name", "").lower() for s in retired}
    aca_apps = [r for r in resources if "containerapps" in r["type"].lower()
                and "managedenvironments" not in r["type"].lower()
                and "managedcertificates" not in r["type"].lower()]

    for app in aca_apps:
        app_name = app["name"].lower()
        for retired_name in retired_names:
            if retired_name in app_name:
                issues.append({
                    "severity": "error",
                    "msg": f"Retired service '{retired_name}' still has ACA app '{app['name']}' running",
                    "resource": app["name"],
                    "rg": app["resourceGroup"]
                })

    # Check declared active services have matching resources
    resource_expectations = {
        "azure_openai": "oai-ipai",
        "azure_doc_intelligence": "docai-ipai",
        "azure_databricks": "dbw-ipai",
        "azure_key_vault": "kv-ipai",
        "azure_container_apps": "ipai-odoo-dev-env",
        "azure_container_registry": "acr",
        "azure_monitor": "appi-ipai",
    }

    for svc_key, name_fragment in resource_expectations.items():
        if svc_key in active:
            found = any(name_fragment in r["name"].lower() for r in resources)
            if not found:
                issues.append({
                    "severity": "warn",
                    "msg": f"Active service '{svc_key}' declared but no resource matching '{name_fragment}' found",
                })

    return issues


def check_dns_registry(resources, dns_data):
    """Compare live DNS zone against subdomain registry."""
    issues = []

    if not dns_data:
        issues.append({"severity": "warn", "msg": "subdomain-registry.yaml not found"})
        return issues

    # Check if Azure DNS zone exists
    dns_zones = [r for r in resources if "dnszones" in r["type"].lower()
                 and "private" not in r["type"].lower()]

    subdomains = dns_data.get("subdomains", [])
    for sub in subdomains:
        name = sub.get("name", "")
        status = sub.get("status", "")
        lifecycle = sub.get("lifecycle", "")

        if lifecycle == "removed" or status == "removed":
            continue

        if status == "active" and lifecycle == "active":
            target = sub.get("target", "")
            if target and target != "null":
                # Active subdomain with a target — check if backend exists
                if "ipai-fd-dev" in str(target):
                    # Front Door backed — check if FD exists
                    fd_exists = any("cdn/profiles" in r["type"].lower()
                                    or "frontdoor" in r["type"].lower()
                                    for r in resources)
                    if not fd_exists:
                        issues.append({
                            "severity": "error",
                            "msg": f"Subdomain '{name}' routes through Front Door but no Front Door resource exists",
                        })

    return issues


def check_service_matrix(resources, matrix_data):
    """Compare live resources against service-matrix.yaml."""
    issues = []

    if not matrix_data:
        issues.append({"severity": "warn", "msg": "service-matrix.yaml not found"})
        return issues

    services = matrix_data.get("services", [])
    aca_names = {r["name"].lower() for r in resources
                 if "containerapps" in r["type"].lower()
                 and "managedenvironments" not in r["type"].lower()
                 and "managedcertificates" not in r["type"].lower()}

    for svc in services:
        status = svc.get("status", "")
        aca_name = svc.get("aca_name", "").lower()
        name = svc.get("name", "")

        if status in ("decommissioned", "decommission_ready"):
            if aca_name and aca_name in aca_names:
                issues.append({
                    "severity": "error",
                    "msg": f"Service '{name}' marked decommissioned but ACA '{aca_name}' still exists",
                })
        elif status == "active" and aca_name:
            if aca_name not in aca_names:
                issues.append({
                    "severity": "warn",
                    "msg": f"Service '{name}' marked active but ACA '{aca_name}' not found",
                })

    return issues


def main():
    snapshot_path = None
    if "--snapshot" in sys.argv:
        idx = sys.argv.index("--snapshot")
        if idx + 1 < len(sys.argv):
            snapshot_path = sys.argv[idx + 1]

    # Get resources
    if snapshot_path:
        resources = load_snapshot(snapshot_path)
    else:
        resources = query_resource_graph()

    print(f"Resources found: {len(resources)}")

    # Load SSOT files
    services_data = load_yaml(SERVICES_YAML)
    matrix_data = load_yaml(SERVICE_MATRIX)
    dns_data = load_yaml(DNS_REGISTRY)

    # Run checks
    all_issues = []
    all_issues.extend(check_ssot_services(resources, services_data))
    all_issues.extend(check_service_matrix(resources, matrix_data))
    all_issues.extend(check_dns_registry(resources, dns_data))

    # Classify resources
    resource_summary = {}
    for r in resources:
        plane = classify_resource(r)
        resource_summary.setdefault(plane, []).append(r["name"])

    # Build report
    errors = [i for i in all_issues if i["severity"] == "error"]
    warns = [i for i in all_issues if i["severity"] == "warn"]

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "resource_count": len(resources),
        "resource_summary": {k: len(v) for k, v in sorted(resource_summary.items())},
        "errors": errors,
        "warnings": warns,
        "pass": len(errors) == 0,
    }

    # Output
    print(f"\n{'PASS' if report['pass'] else 'FAIL'}: {len(errors)} errors, {len(warns)} warnings")

    for e in errors:
        print(f"  ERROR: {e['msg']}")
    for w in warns:
        print(f"  WARN:  {w['msg']}")

    print(f"\nResource summary by plane:")
    for plane, count in sorted(report["resource_summary"].items()):
        print(f"  {plane:20s}: {count}")

    # Save evidence
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    evidence_dir = REPO_ROOT / "docs" / "evidence" / ts / "resource-reconcile"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    with open(evidence_dir / "reconcile.json", "w") as f:
        json.dump(report, f, indent=2)

    with open(evidence_dir / "resource-graph-snapshot.json", "w") as f:
        json.dump(resources, f, indent=2)

    print(f"\nEvidence saved to: {evidence_dir}")

    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
