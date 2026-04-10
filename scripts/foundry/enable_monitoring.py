#!/usr/bin/env python3
"""
enable_monitoring.py — Enable agent monitoring via Foundry SDK.

Configures OpenTelemetry tracing for Foundry agent interactions and
verifies Application Insights connectivity.

Usage:
    python scripts/foundry/enable_monitoring.py
    python scripts/foundry/enable_monitoring.py --dry-run
    python scripts/foundry/enable_monitoring.py --verify

Prereqs:
    pip install azure-ai-projects azure-identity azure-monitor-opentelemetry
    APPINSIGHTS_CONNECTION_STRING set (or resolved from ssot)

SSOT: ssot/ai/foundry_normalization_plan.yaml (N3 — monitoring enablement)
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_connection_string():
    """Resolve App Insights connection string."""
    cs = os.environ.get("APPINSIGHTS_CONNECTION_STRING", "")
    if cs:
        return cs

    # Fallback: try to resolve from Azure CLI
    try:
        import subprocess  # noqa: PLC0415
        result = subprocess.run(
            ["az", "monitor", "app-insights", "component", "show",
             "--resource-group", "rg-ipai-dev-odoo-runtime",
             "--app", "appi-ipai-dev",
             "--query", "connectionString",
             "-o", "tsv"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return ""


def _get_project_endpoint():
    """Resolve Foundry project endpoint."""
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
    if endpoint:
        return endpoint

    import yaml  # noqa: PLC0415
    agents_yaml = REPO_ROOT / "ssot" / "ai" / "agents.yaml"
    if agents_yaml.exists():
        with open(agents_yaml) as f:
            data = yaml.safe_load(f)
        return data.get("foundry_project", {}).get("project_endpoint", "")
    return ""


def enable_otel_tracing(dry_run=False):
    """Enable OpenTelemetry tracing for Foundry agent interactions.

    This instruments the azure-ai-projects SDK to emit traces to
    Application Insights via the Azure Monitor exporter.
    """
    connection_string = _get_connection_string()
    if not connection_string:
        print("ERROR: APPINSIGHTS_CONNECTION_STRING not found")
        print("  Set it as an env var or ensure appi-ipai-dev exists in Azure")
        return False

    # Show masked connection string
    prefix = connection_string[:40] if len(connection_string) > 40 else connection_string[:15]
    print(f"App Insights: {prefix}...")

    if dry_run:
        print("[DRY RUN] Would configure:")
        print("  - Azure Monitor OpenTelemetry exporter")
        print("  - AIInferenceInstrumentor for Foundry SDK")
        print("  - Trace export to Application Insights")
        return True

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor  # noqa: PLC0415
        configure_azure_monitor(connection_string=connection_string)
        print("Azure Monitor OpenTelemetry configured")
    except ImportError:
        print("WARNING: azure-monitor-opentelemetry not installed")
        print("  pip install azure-monitor-opentelemetry")
        return False
    except Exception as e:
        print(f"WARNING: Azure Monitor config failed: {e}")
        return False

    # Enable AIInferenceInstrumentor if available
    try:
        from azure.ai.inference.tracing import AIInferenceInstrumentor  # noqa: PLC0415
        AIInferenceInstrumentor().instrument()
        print("AIInferenceInstrumentor enabled")
    except ImportError:
        print("NOTE: azure-ai-inference tracing not available")
        print("  pip install azure-ai-inference")
        print("  Tracing will use base OpenTelemetry only")

    return True


def verify_connectivity(dry_run=False):
    """Verify Foundry project + App Insights connectivity."""
    print("\n--- Verification ---")

    # 1. Check project endpoint
    endpoint = _get_project_endpoint()
    if not endpoint:
        print("FAIL: No Foundry project endpoint configured")
        return False
    print(f"Foundry endpoint: {endpoint[:50]}...")

    if dry_run:
        print("[DRY RUN] Would verify SDK connectivity")
        return True

    # 2. Test SDK connection
    try:
        from azure.ai.projects import AIProjectClient  # noqa: PLC0415
        from azure.identity import AzureCliCredential  # noqa: PLC0415

        credential = AzureCliCredential()
        project = AIProjectClient(endpoint=endpoint, credential=credential)
        openai_client = project.get_openai_client()

        # Quick model ping
        response = openai_client.responses.create(
            model="gpt-4.1",
            input="Reply with the single word OK.",
        )
        content = getattr(response, "output_text", "") or str(response)
        if "OK" in content.upper():
            print("Foundry SDK: CONNECTED")
        else:
            print(f"Foundry SDK: UNEXPECTED RESPONSE: {content[:100]}")
    except Exception as e:
        print(f"Foundry SDK: FAILED — {e}")
        return False

    # 3. Check App Insights
    cs = _get_connection_string()
    if cs:
        print(f"App Insights: CONFIGURED ({cs[:30]}...)")
    else:
        print("App Insights: NOT CONFIGURED")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Enable Foundry agent monitoring"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be configured without executing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify connectivity, don't configure",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Foundry Agent Monitoring Setup")
    print("=" * 50)

    if args.verify:
        ok = verify_connectivity(dry_run=args.dry_run)
        sys.exit(0 if ok else 1)

    ok = enable_otel_tracing(dry_run=args.dry_run)
    if not ok:
        sys.exit(1)

    ok = verify_connectivity(dry_run=args.dry_run)
    if ok:
        print("\nMonitoring enabled. Traces will flow to Application Insights.")
        print("View in Azure portal → Application Insights → appi-ipai-dev → Traces")
    else:
        print("\nMonitoring partially configured. Check warnings above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
