#!/usr/bin/env python3
"""
Deploy Finance PPM PBIP project to Power BI Service via fabric-cicd.

No Power BI Desktop required — pushes TMDL + report definitions
directly to a Fabric workspace using the REST API.

Prerequisites:
  pip install fabric-cicd azure-identity

Usage:
  # Interactive (browser login)
  python deploy.py --workspace-id <WORKSPACE_ID>

  # Service principal (CI/CD)
  export AZURE_CLIENT_ID=...
  export AZURE_TENANT_ID=...
  export AZURE_CLIENT_SECRET=...
  python deploy.py --workspace-id <WORKSPACE_ID> --auth sp

  # List workspaces (to find your workspace ID)
  python deploy.py --list-workspaces
"""

import argparse
import json
import os
import sys


def get_token(auth_method: str = "interactive"):
    """Get Azure AD token for Power BI API."""
    if auth_method == "sp":
        from azure.identity import ClientSecretCredential

        credential = ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
    elif auth_method == "cli":
        from azure.identity import AzureCliCredential

        credential = AzureCliCredential()
    else:
        from azure.identity import InteractiveBrowserCredential

        credential = InteractiveBrowserCredential()

    token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
    return token.token


def list_workspaces(token: str):
    """List all Power BI workspaces the user has access to."""
    import requests

    resp = requests.get(
        "https://api.powerbi.com/v1.0/myorg/groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    workspaces = resp.json()["value"]

    print(f"\n{'Name':<45} {'ID':<38} {'Type'}")
    print("-" * 100)
    for ws in sorted(workspaces, key=lambda w: w["name"]):
        ws_type = ws.get("type", "Workspace")
        print(f"{ws['name']:<45} {ws['id']:<38} {ws_type}")
    print(f"\nTotal: {len(workspaces)} workspaces")


def deploy(workspace_id: str, auth_method: str = "interactive"):
    """Deploy PBIP project to Power BI Service workspace."""
    from fabric_cicd import FabricWorkspace

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Deploying Finance PPM to workspace {workspace_id}")
    print(f"  Source: {script_dir}")
    print(f"  Auth: {auth_method}")
    print()

    # fabric-cicd handles authentication internally when using
    # environment variables, or we can pass a token
    if auth_method == "sp":
        # Service principal — fabric-cicd reads AZURE_* env vars
        ws = FabricWorkspace(
            workspace_id=workspace_id,
            repository_directory=script_dir,
            item_type_in_scope=["SemanticModel", "Report"],
        )
    elif auth_method == "cli":
        # Azure CLI credential
        from azure.identity import AzureCliCredential

        ws = FabricWorkspace(
            workspace_id=workspace_id,
            repository_directory=script_dir,
            item_type_in_scope=["SemanticModel", "Report"],
            token_credential=AzureCliCredential(),
        )
    else:
        # Interactive browser login
        from azure.identity import InteractiveBrowserCredential

        ws = FabricWorkspace(
            workspace_id=workspace_id,
            repository_directory=script_dir,
            item_type_in_scope=["SemanticModel", "Report"],
            token_credential=InteractiveBrowserCredential(),
        )

    print("Publishing items to workspace...")
    from fabric_cicd import publish_all_items

    publish_all_items(ws)
    print()
    print("Deploy complete.")
    print()
    print("Next steps:")
    print("  1. Open Power BI Service → your workspace")
    print("  2. Configure data source credentials (PostgreSQL)")
    print("  3. Trigger a dataset refresh")
    print("  4. File → Embed report → Website or portal → copy URL")
    print("  5. Set ipai_ppm.powerbi_report_url in Odoo")


def main():
    parser = argparse.ArgumentParser(description="Deploy Finance PPM to Power BI Service")
    parser.add_argument("--workspace-id", help="Target Power BI workspace ID")
    parser.add_argument(
        "--auth",
        choices=["interactive", "cli", "sp"],
        default="cli",
        help="Authentication method (default: cli = Azure CLI)",
    )
    parser.add_argument(
        "--list-workspaces",
        action="store_true",
        help="List available workspaces and exit",
    )

    args = parser.parse_args()

    if args.list_workspaces:
        token = get_token(args.auth)
        list_workspaces(token)
        return

    if not args.workspace_id:
        print("Error: --workspace-id required (use --list-workspaces to find it)")
        sys.exit(1)

    deploy(args.workspace_id, args.auth)


if __name__ == "__main__":
    main()
