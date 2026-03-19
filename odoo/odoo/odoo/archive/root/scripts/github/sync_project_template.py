#!/usr/bin/env python3
"""Sync GitHub Projects v2 from SSOT template spec."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = REPO_ROOT / "ssot/github/projects/templates/finops_month_end.project.yaml"
DRIFT_REPORT_PATH = REPO_ROOT / "artifacts/github/projects/drift_report.json"


class SyncError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SyncError("PyYAML is required. Install with: pip install pyyaml") from exc

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SyncError(f"Invalid spec {path}: top-level must be an object")
    return data


def run_gh(args: list[str], expect_json: bool = True, check: bool = True) -> Any:
    proc = subprocess.run(
        ["gh", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise SyncError(proc.stderr.strip() or proc.stdout.strip() or f"gh command failed: {' '.join(args)}")
    if not expect_json:
        return proc.stdout
    if not proc.stdout.strip():
        return {}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SyncError(f"Failed to parse gh JSON response: {exc}\n{proc.stdout[:300]}") from exc


def gql(query: str, variables: dict[str, Any] | None = None, check: bool = True) -> dict[str, Any]:
    args = ["api", "graphql", "-f", f"query={query}"]
    if variables:
        for k, v in variables.items():
            if isinstance(v, (dict, list)):
                args.extend(["-f", f"{k}={json.dumps(v)}"])
            else:
                args.extend(["-f", f"{k}={v}"])
    data = run_gh(args, expect_json=True, check=check)
    if isinstance(data, dict) and data.get("errors"):
        msg = "; ".join(err.get("message", "unknown GraphQL error") for err in data["errors"])
        raise SyncError(msg)
    return data


def token_scope_header() -> set[str]:
    # Works reliably for PAT-backed gh auth; may be empty for some app tokens.
    output = run_gh(["api", "-i", "user"], expect_json=False, check=False)
    scopes: set[str] = set()
    for line in output.splitlines():
        if line.lower().startswith("x-oauth-scopes:"):
            tail = line.split(":", 1)[1]
            scopes = {s.strip() for s in tail.split(",") if s.strip()}
            break
    return scopes


def raise_scope_error() -> None:
    raise SyncError("CI.GH_PROJECTS_TOKEN_MISSING_SCOPE read:project|project")


def preflight(require_write: bool) -> None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise SyncError("Missing token: set GITHUB_TOKEN or GH_TOKEN")

    # Basic auth check
    try:
        gql("query { viewer { login } }")
    except SyncError as exc:
        if "scope" in str(exc).lower() or "resource not accessible" in str(exc).lower():
            raise_scope_error()
        raise

    scopes = token_scope_header()
    if scopes:
        if "read:project" not in scopes and "project" not in scopes:
            raise_scope_error()
        if require_write and "project" not in scopes:
            raise_scope_error()


def find_project(org: str, title: str, number: int | None) -> dict[str, Any] | None:
    q = """
    query($org: String!, $after: String) {
      organization(login: $org) {
        projectsV2(first: 50, after: $after) {
          pageInfo { hasNextPage endCursor }
          nodes { id title number shortDescription }
        }
      }
    }
    """
    after = None
    while True:
        vars_payload = {"org": org}
        if after:
            vars_payload["after"] = after
        res = gql(q, vars_payload)
        nodes = (
            res.get("data", {})
            .get("organization", {})
            .get("projectsV2", {})
            .get("nodes", [])
        )
        for p in nodes:
            if number and p.get("number") == number:
                return p
            if p.get("title") == title:
                return p
        page = res.get("data", {}).get("organization", {}).get("projectsV2", {}).get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        after = page.get("endCursor")
    return None


def get_project_fields(project_id: str) -> list[dict[str, Any]]:
    q = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 100) {
            nodes {
              __typename
              ... on ProjectV2FieldCommon { id name dataType }
              ... on ProjectV2SingleSelectField {
                options { id name color description }
              }
              ... on ProjectV2IterationField {
                configuration {
                  duration
                  startDay
                  iterations { id title startDate duration }
                }
              }
            }
          }
        }
      }
    }
    """
    res = gql(q, {"projectId": project_id})
    return res.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])


def diff_spec_vs_live(spec: dict[str, Any], live_fields: list[dict[str, Any]]) -> dict[str, Any]:
    desired = spec.get("fields", [])
    live_by_name = {f.get("name"): f for f in live_fields if f.get("name")}
    desired_by_name = {f.get("name"): f for f in desired if isinstance(f, dict) and f.get("name")}

    missing = []
    changed = []
    option_diffs = []
    extra = []

    for name, d in desired_by_name.items():
        l = live_by_name.get(name)
        if not l:
            missing.append({"name": name, "type": d.get("type")})
            continue
        if l.get("dataType") != d.get("type"):
            changed.append(
                {
                    "name": name,
                    "expected_type": d.get("type"),
                    "actual_type": l.get("dataType"),
                }
            )
            continue
        if d.get("type") == "SINGLE_SELECT":
            desired_opts = [o.get("name") for o in d.get("options", []) if isinstance(o, dict)]
            live_opts = [o.get("name") for o in l.get("options", []) if isinstance(o, dict)]
            if desired_opts != live_opts:
                option_diffs.append(
                    {
                        "name": name,
                        "expected": desired_opts,
                        "actual": live_opts,
                    }
                )

    for name, l in live_by_name.items():
        if name not in desired_by_name:
            extra.append({"name": name, "type": l.get("dataType")})

    return {
        "missing_fields": missing,
        "extra_fields": extra,
        "changed_fields": changed,
        "option_diffs": option_diffs,
        "has_drift": bool(missing or extra or changed or option_diffs),
    }


def create_project(org: str, title: str) -> dict[str, Any]:
    org_lookup = gql(
        "query($org: String!) { organization(login: $org) { id } }",
        {"org": org},
    )
    org_id = org_lookup.get("data", {}).get("organization", {}).get("id")
    if not org_id:
        raise SyncError(f"Could not resolve organization id for {org}")

    m = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: { ownerId: $ownerId, title: $title }) {
        projectV2 { id number title }
      }
    }
    """
    res = gql(m, {"ownerId": org_id, "title": title})
    project = res.get("data", {}).get("createProjectV2", {}).get("projectV2")
    if not project:
        raise SyncError("createProjectV2 returned no project")
    return project


def create_field(project_id: str, field: dict[str, Any]) -> None:
    ftype = field.get("type")
    if ftype == "SINGLE_SELECT":
        m = """
        mutation($projectId: ID!, $name: String!, $opts: [ProjectV2SingleSelectFieldOptionInput!]) {
          createProjectV2Field(input: {
            projectId: $projectId,
            dataType: SINGLE_SELECT,
            name: $name,
            singleSelectOptions: $opts
          }) {
            projectV2Field { ... on ProjectV2SingleSelectField { id } }
          }
        }
        """
        opts = [
            {
                "name": o.get("name"),
                "color": o.get("color", "GRAY"),
                "description": o.get("description", ""),
            }
            for o in field.get("options", [])
            if isinstance(o, dict)
        ]
        gql(m, {"projectId": project_id, "name": field["name"], "opts": opts})
        return

    if ftype == "ITERATION":
        m = """
        mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {
            projectId: $projectId,
            dataType: ITERATION,
            name: $name
          }) {
            projectV2Field {
              ... on ProjectV2IterationField { id }
            }
          }
        }
        """
        created = gql(m, {"projectId": project_id, "name": field["name"]})
        field_id = (
            created.get("data", {})
            .get("createProjectV2Field", {})
            .get("projectV2Field", {})
            .get("id")
        )
        iteration_cfg = field.get("iteration") or {}
        if field_id and iteration_cfg:
            u = """
            mutation($fieldId: ID!, $cfg: ProjectV2IterationFieldConfigurationInput!) {
              updateProjectV2Field(input: {
                fieldId: $fieldId,
                iterationConfiguration: $cfg
              }) {
                projectV2Field { ... on ProjectV2IterationField { id } }
              }
            }
            """
            gql(u, {"fieldId": field_id, "cfg": {
                "duration": iteration_cfg.get("duration"),
                "startDate": iteration_cfg.get("start_date"),
                "iterations": [
                    {
                        "title": i.get("title"),
                        "startDate": i.get("start_date"),
                        "duration": i.get("duration"),
                    }
                    for i in iteration_cfg.get("iterations", [])
                    if isinstance(i, dict)
                ],
            }})
        return

    # TEXT / NUMBER / DATE
    m = """
    mutation($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!) {
      createProjectV2Field(input: {
        projectId: $projectId,
        dataType: $dataType,
        name: $name
      }) {
        projectV2Field { ... on ProjectV2FieldCommon { id } }
      }
    }
    """
    gql(m, {"projectId": project_id, "name": field["name"], "dataType": ftype})


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", default=str(DEFAULT_SPEC), help="Template spec path")
    p.add_argument("--dry-run", action="store_true", help="Compute drift only")
    p.add_argument("--apply", action="store_true", help="Apply mutations to GitHub")
    p.add_argument("--output", default=str(DRIFT_REPORT_PATH), help="Drift report path")
    return p.parse_args()


def write_blocked_report(spec: dict[str, Any], output_path: Path, reason: str) -> None:
    report = {
        "spec_id": spec.get("template_id"),
        "org": spec.get("org"),
        "project_title": spec.get("title"),
        "project_number": ((spec.get("project") or {}).get("number")),
        "mode": "dry-run",
        "status": "blocked",
        "reason": reason,
        "required_scopes": ["read:project", "project"],
        "missing_fields": [],
        "extra_fields": [],
        "changed_fields": [],
        "option_diffs": [],
        "has_drift": False,
    }
    write_report(report, output_path)


def main() -> int:
    args = parse_args()
    if args.dry_run == args.apply:
        print("Use exactly one of --dry-run or --apply", file=sys.stderr)
        return 2

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Spec not found: {spec_path}", file=sys.stderr)
        return 2

    spec: dict[str, Any] | None = None
    try:
        spec = load_yaml(spec_path)
        preflight(require_write=args.apply)

        org = spec.get("org")
        title = spec.get("title")
        number = ((spec.get("project") or {}).get("number"))
        if not org or not title:
            raise SyncError("Spec must include 'org' and 'title'")

        project = find_project(org, title, number)
        created = False
        if not project:
            if args.dry_run:
                report = {
                    "spec_id": spec.get("template_id"),
                    "org": org,
                    "project_title": title,
                    "project_number": None,
                    "mode": "dry-run",
                    "missing_project": True,
                    "missing_fields": [
                        {"name": f.get("name"), "type": f.get("type")}
                        for f in spec.get("fields", [])
                        if isinstance(f, dict)
                    ],
                    "extra_fields": [],
                    "changed_fields": [],
                    "option_diffs": [],
                    "has_drift": True,
                }
                write_report(report, Path(args.output))
                print(f"Dry-run complete. Drift report written: {args.output}")
                return 0

            project = create_project(org, title)
            created = True

        project_id = project["id"]
        live_fields = get_project_fields(project_id)
        drift = diff_spec_vs_live(spec, live_fields)

        if args.apply and drift["missing_fields"]:
            desired_by_name = {f.get("name"): f for f in spec.get("fields", []) if isinstance(f, dict)}
            for mf in drift["missing_fields"]:
                field = desired_by_name.get(mf["name"])
                if field:
                    create_field(project_id, field)

            live_fields = get_project_fields(project_id)
            drift = diff_spec_vs_live(spec, live_fields)

        report = {
            "spec_id": spec.get("template_id"),
            "org": org,
            "project_title": title,
            "project_number": project.get("number"),
            "project_id": project_id,
            "mode": "apply" if args.apply else "dry-run",
            "created_project": created,
            **drift,
        }
        write_report(report, Path(args.output))

        if args.apply and drift["has_drift"]:
            raise SyncError("Drift remains after apply. See drift report.")

        print(f"{report['mode']} complete. Drift report written: {args.output}")
        return 0

    except SyncError as exc:
        message = str(exc)
        if "scope" in message.lower() or "resource not accessible" in message.lower():
            message = "CI.GH_PROJECTS_TOKEN_MISSING_SCOPE read:project|project"
        if args.dry_run and spec is not None and (
            "Missing token" in message or "CI.GH_PROJECTS_TOKEN_MISSING_SCOPE" in message
        ):
            write_blocked_report(spec, Path(args.output), "token_missing_or_scope_missing")
            print(f"dry-run blocked. Drift report written: {args.output}")
            return 0
        print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
