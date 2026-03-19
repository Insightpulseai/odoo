#!/usr/bin/env python3
"""
Infrastructure Well-Architected Framework Assessment Script.

Assess DigitalOcean + Docker Compose + Cloudflare stack.
"""

import argparse
import sys
import yaml
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path to import lib
sys.path.append(str(Path(__file__).resolve().parent))
from lib import CheckResult, save_json, create_evidence_dir

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "infra/docker-compose.prod.yaml"
MODEL_PATH = ROOT / "docs/arch/infra-waf-model.yaml"


def load_model():
    if not MODEL_PATH.exists():
        print(f"ERROR: Model not found at {MODEL_PATH}")
        sys.exit(1)
    with open(MODEL_PATH) as f:
        return yaml.safe_load(f)


def load_compose():
    if not COMPOSE_FILE.exists():
        return None
    with open(COMPOSE_FILE) as f:
        return yaml.safe_load(f)


def assess_reliability(model, compose_data):
    """Assess Reliability pillar (P1)."""
    checks = []

    # Check 1: Docker Restart Policy
    score = 0
    desc = "No compose file"
    services = compose_data.get("services", {}) if compose_data else {}

    if services:
        total_services = len(services)
        valid_services = 0
        failed_services = []

        for name, svc in services.items():
            restart = svc.get("restart", "")
            if restart in ["always", "unless-stopped"]:
                valid_services += 1
            else:
                failed_services.append(name)

        if valid_services == total_services:
            score = 4
            desc = "All services have restart policy"
        elif valid_services > 0:
            score = 2
            desc = f"{valid_services}/{total_services} services compliant"
        else:
            score = 0
            desc = "No services have valid restart policy"

    checks.append(
        CheckResult(
            name="docker_restart_policy",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"failed_services": failed_services} if services else {},
        )
    )

    # Check 2: Docker Healthchecks
    score = 0
    desc = "No compose file"

    if services:
        # Filter for services exposing ports (likely need healthchecks)
        exposed_services = [n for n, s in services.items() if "ports" in s]
        total = len(exposed_services)
        valid = 0
        failed = []

        for name in exposed_services:
            svc = services[name]
            if "healthcheck" in svc:
                valid += 1
            else:
                failed.append(name)

        if total == 0:
            # No exposed services? Pass by default or Skip? Pass for now.
            score = 4
            desc = "No exposed services requiring healthchecks"
        elif valid == total:
            score = 4
            desc = "All exposed services have healthchecks"
        elif valid > 0:
            score = 2
            desc = f"{valid}/{total} exposed services compliant"
        else:
            score = 0
            desc = "No exposed services have healthchecks"

    checks.append(
        CheckResult(
            name="docker_healthchecks",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"failed_services": failed} if services else {},
        )
    )

    # Check 3: DB Backups (Managed Check - Proxy via Env/Compose?)
    # We check if DB host points to DO managed DB (heuristic)
    score = 0
    desc = "Database not managed or unknown"
    # Try to find DB host in env vars of services
    db_host_markers = ["ondigitalocean.com", "db.ondigitalocean.com"]
    found_managed = False

    if services:
        for name, svc in services.items():
            env = svc.get("environment", {})
            # Handle list or dict env
            if isinstance(env, dict):
                for k, v in env.items():
                    if v and any(m in str(v) for m in db_host_markers):
                        found_managed = True
                        break
            elif isinstance(env, list):
                for item in env:
                    if any(m in item for m in db_host_markers):
                        found_managed = True
                        break

    if found_managed:
        score = 4
        desc = "Managed Database detected (Backups assumed)"
    else:
        score = 2  # Neutral / Manual check needed
        desc = "Managed Database not explicitly detected in Compose"

    checks.append(
        CheckResult(
            name="db_backup_configured",
            integration="infra-waf",
            status="PASS" if score >= 2 else "PARTIAL",
            description=desc,
            evidence={},
        )
    )

    return checks


def assess_security(model, compose_data):
    """Assess Security pillar (P2)."""
    checks = []

    # Check 1: Secrets in Compose
    score = 0
    desc = "No compose file"
    services = compose_data.get("services", {}) if compose_data else {}

    if services:
        failed = []
        suspicious_keys = ["PASSWORD", "SECRET", "KEY", "TOKEN"]

        for name, svc in services.items():
            env = svc.get("environment", {})
            if isinstance(env, dict):
                for k, v in env.items():
                    if any(s in k.upper() for s in suspicious_keys):
                        # Use str(v) to handle ensure we have a string
                        val = str(v)
                        # Check if value looks hardcoded (not starting with $)
                        if val and not val.startswith("$") and len(val) > 1:
                            failed.append(f"{name}:{k}")
            elif isinstance(env, list):
                for item in env:
                    if "=" in item:
                        k, v = item.split("=", 1)
                        if any(s in k.upper() for s in suspicious_keys):
                            if v and not v.startswith("$") and len(v) > 1:
                                failed.append(f"{name}:{k}")

        if not failed:
            score = 4
            desc = "No hardcoded secrets found in environment variables"
        else:
            score = 0
            desc = f"Hardcoded secrets detected in: {', '.join(failed[:3])}..."

    checks.append(
        CheckResult(
            name="no_hardcoded_secrets_compose",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"failed": failed} if services and failed else {},
        )
    )

    # Check 2: Cloudflare Proxy (Heuristic from tf files)
    # Check if 'proxied = true' exists in infra/cloudflare
    cf_dir = ROOT / "infra/cloudflare"
    score = 0
    desc = "No Cloudflare terraform found"

    if cf_dir.exists():
        try:
            out = subprocess.check_output(
                ["grep", "-r", "proxied.*=.*true", str(cf_dir)], stderr=subprocess.DEVNULL
            ).decode()
            score = 4
            desc = "Cloudflare proxying explicitly enabled in Terraform"
        except:
            score = 0
            desc = "No explicit Cloudflare proxying found in Terraform"

    checks.append(
        CheckResult(
            name="cloudflare_proxy_enabled",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={},
        )
    )

    return checks


def assess_cost_optimization(model, compose_data):
    """Assess Cost Optimization pillar (P3)."""
    checks = []
    return checks  # Placeholder


def assess_operational_excellence(model, compose_data):
    """Assess Operational Excellence pillar (P4)."""
    checks = []
    # Logging Driver Check
    score = 0
    desc = "No compose file"
    services = compose_data.get("services", {}) if compose_data else {}

    if services:
        total = len(services)
        valid = 0
        failed = []
        for name, svc in services.items():
            logging = svc.get("logging", {})
            driver = logging.get("driver", "")
            if driver == "json-file":
                # Check options
                opts = logging.get("options", {})
                if "max-size" in opts and "max-file" in opts:
                    valid += 1
                else:
                    failed.append(f"{name} (missing options)")
            else:
                failed.append(f"{name} (wrong driver: {driver})")

        if valid == total:
            score = 4
            desc = "All services comply with logging standards"
        elif valid > 0:
            score = 2
            desc = f"{valid}/{total} services compliant"
        else:
            score = 0
            desc = "No services comply with logging standards"

    checks.append(
        CheckResult(
            name="logging_driver_configured",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"failed": failed} if services else {},
        )
    )

    return checks


def assess_performance_efficiency(model, compose_data):
    """Assess Performance Efficiency pillar (P5)."""
    checks = []

    # Check 1: Volume Configuration
    # Persistent data should use named volumes or host binds (but named is better for portability/performance on some drivers)
    # Actually, for standard caching/DB, checking volumes existence is good.
    score = 0
    desc = "No compose file"
    volumes = compose_data.get("volumes", {}) if compose_data else {}
    services = compose_data.get("services", {}) if compose_data else {}

    if services:
        # Check if DB service uses volumes
        # Heuristic: find service with 'db' or 'postgres' image
        db_services = [
            n
            for n, s in services.items()
            if "db" in s.get("image", "") or "postgres" in s.get("image", "")
        ]

        valid_db = True
        if db_services:
            for db in db_services:
                svc_vols = services[db].get("volumes", [])
                if not svc_vols:
                    valid_db = False

        # Also check top-level volumes presence if any named volumes used
        if volumes or (not db_services and services):
            # If no DB, but we have volumes, maybe OK?
            # Let's check generally if 'volumes' section exists in services
            has_volumes = any("volumes" in s for s in services.values())
            if has_volumes:
                score = 4
                desc = "Volumes configured for persistence"
            else:
                score = 2
                desc = "No volumes defined (stateless?)"
        else:
            score = 2
            desc = "No top-level volumes defined"

    checks.append(
        CheckResult(
            name="volumes_configured",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"volumes": list(volumes.keys())} if volumes else {},
        )
    )

    return checks


def assess_integration(model):
    """Assess Integration Ecosystem pillar (P6)."""
    checks = []

    # Check 1: Supabase
    # Config location: infra/stack/supabase/config.toml or similar.
    # We'll search for common locations.
    supabase_config = None
    possible_paths = [
        ROOT / "supabase/config.toml",
        ROOT / "infra/stack/supabase/config.toml",
        ROOT / "config.toml",
    ]
    for p in possible_paths:
        if p.exists():
            supabase_config = p
            break

    if supabase_config:
        score = 4
        desc = f"Supabase config found at {supabase_config.relative_to(ROOT)}"
        # Could parse TOML here ensuring `api.enabled = true` etc.
    else:
        # Check if we have a supabase dir at least
        if (ROOT / "supabase").exists():
            score = 2
            desc = "Supabase directory exists but no config.toml found in standard locations"
        else:
            score = 0
            desc = "Supabase config not found"

    checks.append(
        CheckResult(
            name="supabase_config_valid",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"path": str(supabase_config.relative_to(ROOT))} if supabase_config else {},
        )
    )

    # Check 2: Vercel
    # Logically should be at root or web/*/vercel.json
    vercel_files = list(ROOT.glob("**/vercel.json"))
    # Exclude node_modules
    vercel_files = [f for f in vercel_files if "node_modules" not in str(f)]

    if vercel_files:
        score = 4
        desc = f"Found {len(vercel_files)} vercel.json configuration files"
    else:
        score = 0
        desc = "No vercel.json files found"

    checks.append(
        CheckResult(
            name="vercel_config_valid",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"files": [str(f.relative_to(ROOT)) for f in vercel_files]},
        )
    )

    # Check 3: n8n
    # Look for .json files in n8n/workflows/ or automations/n8n/workflows/
    n8n_files = list(ROOT.glob("**/n8n/workflows/**/*.json")) + list(
        ROOT.glob("**/automations/n8n/workflows/**/*.json")
    )
    # Eliminate duplicates
    n8n_files = list(set(n8n_files))

    valid_workflows = 0
    failed_workflows = []

    if n8n_files:
        for f in n8n_files:
            try:
                with open(f) as wf:
                    json.load(wf)
                valid_workflows += 1
            except json.JSONDecodeError:
                failed_workflows.append(str(f.relative_to(ROOT)))

        if failed_workflows:
            score = 2
            desc = f"{valid_workflows}/{len(n8n_files)} workflows valid JSON"
        else:
            score = 4
            desc = f"All {len(n8n_files)} n8n workflows are valid JSON"
    else:
        score = 0
        desc = "No n8n workflows found"

    checks.append(
        CheckResult(
            name="n8n_workflows_valid",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"failed": failed_workflows, "count": len(n8n_files)},
        )
    )

    # Check 4: Figma
    # Check for scripts like scripts/figma*
    figma_scripts = list(ROOT.glob("scripts/figma*")) + list(ROOT.glob("scripts/figma/*"))
    # Check env var presence implies configuration
    # This is a static check

    if figma_scripts:
        score = 4
        desc = f"Found {len(figma_scripts)} Figma automation scripts"
    else:
        score = 0
        desc = "No Figma automation scripts found"

    checks.append(
        CheckResult(
            name="figma_automation_configured",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={"scripts": [str(f.relative_to(ROOT)) for f in figma_scripts]},
        )
    )

    # Check 5: Slack
    # Check for usage of SLACK token in common files
    try:
        out = subprocess.check_output(
            ["grep", "-r", "SLACK_BOT_TOKEN", str(ROOT / ".env.example")], stderr=subprocess.DEVNULL
        ).decode()
        score = 4
        desc = "Slack Bot Token defined in .env.example"
    except:
        try:
            # Check scripts for usage
            out2 = subprocess.check_output(
                ["grep", "-r", "SLACK_BOT_TOKEN", str(ROOT / "scripts")], stderr=subprocess.DEVNULL
            ).decode()
            score = 4
            desc = "Slack Bot Token usage found in scripts"
        except:
            score = 0
            desc = "Slack Bot Token not found in templates or scripts"

    checks.append(
        CheckResult(
            name="slack_token_configured",
            integration="infra-waf",
            status="PASS" if score >= 2 else "FAIL",
            description=desc,
            evidence={},
        )
    )

    return checks


def calculate_score(pillar_checks, model):
    """Calculate weighted score."""
    metrics = {"total_score": 0.0, "pillars": {}}
    total_weighted_maturity = 0.0

    for pillar_key, checks in pillar_checks.items():
        if not checks:
            metrics["pillars"][pillar_key] = {
                "score": 0.0,
                "passed": 0,
                "total": 0,
                "weight": model["pillars"][pillar_key]["weight"],
            }
            continue

        weight = model["pillars"][pillar_key]["weight"]
        total_checks = len(checks)
        pillar_sum = 0
        passed_checks = 0

        for c in checks:
            if c.status == "PASS":
                pillar_sum += 4
                passed_checks += 1
            elif c.status == "PARTIAL":
                pillar_sum += 2

        pillar_maturity = pillar_sum / total_checks if total_checks > 0 else 0

        metrics["pillars"][pillar_key] = {
            "score": round(pillar_maturity, 2),
            "passed": passed_checks,
            "total": total_checks,
            "weight": weight,
        }
        total_weighted_maturity += pillar_maturity * weight

    metrics["total_score"] = round(total_weighted_maturity, 2)
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Infra WAF Assessment")
    parser.add_argument("--api", action="store_true", help="Run API-dependent checks")
    args = parser.parse_args()

    print("Loading assessment model...")
    model = load_model()
    compose_data = load_compose()

    if not compose_data:
        print(f"WARNING: Compose file not found at {COMPOSE_FILE}")

    pillar_results = {}

    print("Assessing Reliability (P1)...")
    pillar_results["reliability"] = assess_reliability(model, compose_data)
    pillar_results["security"] = assess_security(model, compose_data)
    pillar_results["cost_optimization"] = assess_cost_optimization(model, compose_data)
    pillar_results["operational_excellence"] = assess_operational_excellence(model, compose_data)
    pillar_results["performance_efficiency"] = assess_performance_efficiency(model, compose_data)
    pillar_results["integration"] = assess_integration(model)

    all_checks = []
    for checks in pillar_results.values():
        all_checks.extend(checks)

    metrics = calculate_score(pillar_results, model)

    print("\n" + "=" * 40)
    print(f"INFRA WELL-ARCHITECTED SCORE: {metrics['total_score']} / 4.0")
    print("=" * 40 + "\n")

    for p_key, p_val in metrics["pillars"].items():
        print(
            f"Pillar: {p_key.title():<22} Score: {p_val['score']}/4.0 (Weight: {p_val['weight']})"
        )

    print("\n--- Failures ---")
    for check in all_checks:
        if check.status == "FAIL":
            print(f"[{check.name}] {check.description}")
            if hasattr(check, "evidence") and check.evidence:
                print(f"  Evidence: {check.evidence}")

    evidence_dir = create_evidence_dir()
    evidence = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "checks": [c.to_dict() for c in all_checks],
    }
    save_json(evidence, str(Path(evidence_dir) / "infra-assessment-results.json"))
    print(f"\nEvidence saved to: {evidence_dir}")

    return 0


if __name__ == "__main__":
    main()
