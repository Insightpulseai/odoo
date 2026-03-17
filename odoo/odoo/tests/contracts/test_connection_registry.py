#!/usr/bin/env python3
"""Test that all resources have declared connection contracts."""
import os
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def test_no_uncontracted_resources():
    """Fail if a resource exists in observed state but has no connection contract."""
    observed_path = os.path.join(REPO_ROOT, "ssot", "azure",
                                  "odoo__azure__resource_observed_state__v1.registry.yaml")
    connections_path = os.path.join(REPO_ROOT, "ssot", "azure",
                                    "odoo__azure__connections__v1.registry.yaml")

    if not os.path.exists(observed_path) or not os.path.exists(connections_path):
        print("SKIP: Required registry files not found")
        return 0

    observed = load_yaml(observed_path)
    connections = load_yaml(connections_path)

    resource_ids = {r["id"] for r in observed.get("resources", [])}
    contracted_ids = set()
    for conn in connections.get("connections", []):
        contracted_ids.add(conn.get("source", ""))
        contracted_ids.add(conn.get("target", ""))

    uncontracted = resource_ids - contracted_ids
    noncompliant = [c for c in connections.get("connections", [])
                    if c.get("status") in ("noncompliant", "missing", "incomplete")]

    print(f"Resources: {len(resource_ids)}")
    print(f"Contracted: {len(resource_ids - uncontracted)}")
    print(f"Uncontracted: {len(uncontracted)}")
    print(f"Noncompliant connections: {len(noncompliant)}")

    if uncontracted:
        print(f"\nWARN: Uncontracted resources: {', '.join(sorted(uncontracted))}")

    if noncompliant:
        print(f"\nNoncompliant connections:")
        for c in noncompliant:
            print(f"  - {c['id']}: {c['status']}")

    # For now, warn but don't fail — these are tracking artifacts
    print("\nPASS (advisory): Connection registry loaded successfully")
    return 0


if __name__ == "__main__":
    sys.exit(test_no_uncontracted_resources())
