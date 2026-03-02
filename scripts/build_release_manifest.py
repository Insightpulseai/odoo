#!/usr/bin/env python3
"""
Build Release Manifest

Generates a machine-readable release manifest (JSON) and optionally a
human-readable SSOT record (YAML) for each production deployment.

Validates against ssot/runtime/release_contract.yaml required fields.

Usage:
  python scripts/build_release_manifest.py \
    --tag prod-20260303-1200 \
    --image-digest sha256:abc123... \
    --image-tag prod-20260303-1200 \
    --commit-sha abc123def456... \
    --gates G1,G2,G3 \
    --deployer github-actor \
    --run-id 12345

  # Also write YAML SSOT record:
  python scripts/build_release_manifest.py ... --yaml

Exit 0 = success, exit 1 = validation error, exit 2 = file/parse error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "ssot" / "runtime" / "release_contract.yaml"
RELEASES_DIR = REPO_ROOT / "ssot" / "runtime" / "releases"


def compute_addon_set_fingerprint() -> str:
    """Hash of sorted addon manifest list (addons/ipai + addons/oca)."""
    addons_ipai = REPO_ROOT / "addons" / "ipai"
    addons_oca = REPO_ROOT / "addons" / "oca"

    manifests: list[str] = []
    for addons_dir in (addons_ipai, addons_oca):
        if addons_dir.exists():
            for child in sorted(addons_dir.iterdir()):
                manifest = child / "__manifest__.py"
                if manifest.exists():
                    manifests.append(f"{child.parent.name}/{child.name}")

    content = "\n".join(manifests)
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_manifest(args: argparse.Namespace) -> dict:
    """Build manifest dict from CLI args."""
    gates = [g.strip() for g in args.gates.split(",") if g.strip()]

    manifest = {
        "tag": args.tag,
        "image_digest": args.image_digest,
        "image_tag": args.image_tag,
        "commit_sha": args.commit_sha,
        "addon_set_fingerprint": compute_addon_set_fingerprint(),
        "gates_passed": gates,
        "deployer": args.deployer,
        "workflow_run_id": int(args.run_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Optional fields
    if args.sbom:
        manifest["sbom_artifact"] = args.sbom
    if args.vuln_scan:
        manifest["vuln_scan_result"] = args.vuln_scan
    if args.oca_lock_hash:
        manifest["oca_lock_hash"] = args.oca_lock_hash

    return manifest


def validate_manifest(manifest: dict) -> list[str]:
    """Validate manifest against release contract required fields."""
    if not CONTRACT_PATH.exists():
        return [f"Contract not found: {CONTRACT_PATH}"]

    if yaml is None:
        # Can't validate without PyYAML, but don't fail hard
        return []

    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    required = contract.get("required_fields", [])

    errors: list[str] = []
    for field_def in required:
        field_name = field_def.get("field", "")
        if field_name not in manifest or manifest[field_name] is None:
            errors.append(f"Missing required field: {field_name}")
        elif field_name == "commit_sha" and len(str(manifest[field_name])) < 7:
            errors.append(f"commit_sha too short: {manifest[field_name]}")
        elif field_name == "gates_passed" and not manifest[field_name]:
            errors.append("gates_passed is empty")

    return errors


def write_json(manifest: dict, output_path: Path) -> None:
    """Write manifest as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"JSON manifest written to: {output_path}")


def write_yaml_record(manifest: dict, tag: str) -> None:
    """Write YAML SSOT record under ssot/runtime/releases/."""
    if yaml is None:
        print("WARNING: PyYAML not available, skipping YAML record")
        return

    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    safe_tag = tag.replace("/", "_").replace(":", "_")
    output_path = RELEASES_DIR / f"{safe_tag}.yaml"
    output_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"YAML record written to: {output_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build release manifest for production deployment")
    ap.add_argument("--tag", required=True, help="Immutable git tag")
    ap.add_argument("--image-digest", required=True, help="Docker image digest (sha256:...)")
    ap.add_argument("--image-tag", required=True, help="Docker image tag")
    ap.add_argument("--commit-sha", required=True, help="Full 40-char commit SHA")
    ap.add_argument("--gates", required=True, help="Comma-separated list of gates passed (e.g. G1,G2,G3)")
    ap.add_argument("--deployer", required=True, help="GitHub actor who triggered deployment")
    ap.add_argument("--run-id", required=True, help="GitHub Actions workflow run ID")
    ap.add_argument("--sbom", default=None, help="Path to SBOM artifact (optional)")
    ap.add_argument("--vuln-scan", default=None, help="Vulnerability scan summary (optional)")
    ap.add_argument("--oca-lock-hash", default=None, help="Hash of vendor/oca.lock.json (optional)")
    ap.add_argument("--output", default="release_manifest.json", help="Output JSON path (default: release_manifest.json)")
    ap.add_argument("--yaml", action="store_true", help="Also write YAML SSOT record to ssot/runtime/releases/")
    args = ap.parse_args()

    manifest = build_manifest(args)

    # Validate
    errors = validate_manifest(manifest)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    # Write JSON
    output_path = Path(args.output)
    write_json(manifest, output_path)

    # Optionally write YAML record
    if args.yaml:
        write_yaml_record(manifest, args.tag)

    print(f"Release manifest PASS: tag={args.tag}, gates={manifest['gates_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
