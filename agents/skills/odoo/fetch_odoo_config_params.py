"""
Skill: fetch_odoo_config_params

Read configuration parameters from Odoo via JSON-RPC.

Backend: odoo
"""
import os
from typing import Any, Dict, List

import requests


def _odoo_jsonrpc(
    url: str, service: str, method: str, args: List[Any]
) -> Dict[str, Any]:
    """Execute Odoo JSON-RPC call."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": service,
            "method": method,
            "args": args,
        },
        "id": 1,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
    except requests.RequestException as exc:
        raise RuntimeError(f"Odoo JSON-RPC call failed: {exc}") from exc

    if not resp.ok:
        raise RuntimeError(f"Odoo JSON-RPC HTTP error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError("Odoo JSON-RPC response is not valid JSON") from exc

    if "error" in data and data["error"]:
        raise RuntimeError(f"Odoo JSON-RPC error: {data['error']}")

    return data.get("result")


def handle(keys: List[str]) -> Dict[str, Any]:
    """
    Fetch Odoo ir.config_parameter values for the given keys.

    Args:
        keys: List of config parameter keys to fetch

    Returns:
        Dict with params mapping keys to values

    Raises:
        RuntimeError: If Odoo is unreachable or authentication fails
        ValueError: If keys is not a list
    """
    if not isinstance(keys, list):
        raise ValueError("keys must be a list of strings")

    odoo_url = os.getenv("ODOO_URL", "https://erp.insightpulseai.com")
    odoo_db = os.getenv("ODOO_DB")
    odoo_user = os.getenv("ODOO_USER")
    odoo_password = os.getenv("ODOO_PASSWORD")

    if not all([odoo_db, odoo_user, odoo_password]):
        raise RuntimeError(
            "Odoo credentials (ODOO_DB, ODOO_USER, ODOO_PASSWORD) are not fully configured"
        )

    jsonrpc_url = odoo_url.rstrip("/") + "/jsonrpc"

    # Authenticate
    uid = _odoo_jsonrpc(
        jsonrpc_url,
        "common",
        "authenticate",
        [odoo_db, odoo_user, odoo_password, {}],
    )
    if not isinstance(uid, int):
        raise RuntimeError("Failed to authenticate with Odoo")

    params: Dict[str, Any] = {}
    for key in keys:
        if not isinstance(key, str):
            continue
        result = _odoo_jsonrpc(
            jsonrpc_url,
            "object",
            "execute_kw",
            [
                odoo_db,
                uid,
                odoo_password,
                "ir.config_parameter",
                "get_param",
                [key],
            ],
        )
        # get_param returns False if not set
        params[key] = result if result not in (False, None) else None

    return {"params": params}


# Skill metadata
SKILL_YAML = """
name: fetch_odoo_config_params
intent: Read Superset-related configuration parameters from Odoo
inputs:
  keys:
    type: array
outputs:
  params: object
error_conditions:
  - Odoo JSON-RPC endpoint unreachable
  - Authentication failed
  - Invalid response from Odoo
backend: odoo
handler: "python://skills/odoo/fetch_odoo_config_params.py"
"""
