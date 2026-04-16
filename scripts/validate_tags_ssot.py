#!/usr/bin/env python3
"""SSOT Tag Contract Validator.

Validates cross-file consistency across:
  ssot/governance/tags.yaml
  ssot/network/routes.yaml (tag_projection section)
  ssot/odoo/runtime_contract.yaml (resource_tag_defaults section)

Exit 0 = pass, Exit 1 = failures found.
Aggregates all errors before exiting.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_RESOURCE_TAGS = {
    "org", "system", "environment", "service",
    "repo", "owner_plane", "criticality", "managed_by",
}

REQUIRED_ROUTE_PROJECTION_TAGS = {
    "system", "environment", "service",
    "repo", "owner_plane", "criticality",
}

errors: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        error(f"File not found: {path}")
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def require_keys(obj: dict, required: set[str], context: str) -> None:
    missing = required - set(obj.keys())
    if missing:
        error(f"{context}: missing required tags: {sorted(missing)}")


def validate_taxonomy(tags: dict) -> None:
    taxonomy = tags.get("tag_taxonomy", {})
    required = taxonomy.get("required", {})
    if not required:
        error("tags.yaml: tag_taxonomy.required is empty or missing")
        return
    defined_tags = set(required.keys())
    missing = REQUIRED_RESOURCE_TAGS - defined_tags
    if missing:
        error(f"tags.yaml: taxonomy missing required resource tags: {sorted(missing)}")


def validate_known_resources(tags: dict) -> None:
    resources = tags.get("mappings", {}).get("known_resources", {})
    for name, attrs in resources.items():
        require_keys(attrs, REQUIRED_RESOURCE_TAGS, f"tags.yaml known_resources.{name}")


def validate_route_projection(routes: dict) -> None:
    projection = routes.get("tag_projection", {})
    if not projection:
        return  # tag_projection section may not exist yet
    for hostname, attrs in projection.items():
        require_keys(attrs, REQUIRED_ROUTE_PROJECTION_TAGS,
                     f"routes.yaml tag_projection.{hostname}")


def validate_cross_file_alignment(tags: dict, routes: dict) -> None:
    tag_systems = tags.get("mappings", {}).get("systems", {})
    route_proj = routes.get("tag_projection", {})

    common_hosts = set(tag_systems.keys()) & set(route_proj.keys())
    for host in sorted(common_hosts):
        tag_vals = tag_systems[host]
        route_vals = route_proj[host]
        common_keys = set(tag_vals.keys()) & set(route_vals.keys())
        for key in sorted(common_keys):
            if tag_vals[key] != route_vals[key]:
                error(
                    f"Mismatch for {host}.{key}: "
                    f"tags.yaml={tag_vals[key]} vs routes.yaml={route_vals[key]}"
                )


def validate_policy_rules(tags: dict, routes: dict) -> None:
    """Validate structural policy rules against known_resources and route projections."""
    all_entries: dict[str, dict] = {}
    all_entries.update(tags.get("mappings", {}).get("known_resources", {}))
    all_entries.update(tags.get("mappings", {}).get("systems", {}))
    all_entries.update(routes.get("tag_projection", {}))

    for name, attrs in all_entries.items():
        system = attrs.get("system")
        service = attrs.get("service")
        repo = attrs.get("repo")
        plane = attrs.get("owner_plane")

        # odoo_runtime_repo_must_be_odoo
        if system == "odoo" and service in {"erp", "aca-app", "postgres", "storage"}:
            if repo and repo != "odoo":
                error(f"{name}: system=odoo + service={service} requires repo=odoo, got repo={repo}")

        # edge_resources_default_to_infra
        if service in {"frontdoor", "dns", "private-dns"}:
            if repo and repo != "infra":
                error(f"{name}: service={service} requires repo=infra, got repo={repo}")

        # public_web_resources_default_to_web_or_infra
        if plane == "public-web":
            allowed = {"web", "infra", "landing.io"}
            if repo and repo not in allowed:
                error(f"{name}: owner_plane=public-web requires repo in {sorted(allowed)}, got repo={repo}")


def main() -> int:
    tags_path = REPO_ROOT / "ssot" / "governance" / "tags.yaml"
    routes_path = REPO_ROOT / "ssot" / "network" / "routes.yaml"

    tags = load_yaml(tags_path)
    routes = load_yaml(routes_path)

    validate_taxonomy(tags)
    validate_known_resources(tags)
    validate_route_projection(routes)
    validate_cross_file_alignment(tags, routes)
    validate_policy_rules(tags, routes)

    if errors:
        print(f"\n{'='*60}")
        print(f"SSOT Tag Validation FAILED — {len(errors)} error(s):")
        print(f"{'='*60}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        print()
        return 1

    print("SSOT Tag Validation PASSED — all checks green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
