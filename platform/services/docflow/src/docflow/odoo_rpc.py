from __future__ import annotations
import os
import json
import requests
from typing import Any, Dict, Optional


class OdooRpc:
    def __init__(self):
        self.base = os.getenv("ODOO_BASE_URL", "").rstrip("/")
        self.db = os.getenv("ODOO_DB", "")
        self.login = os.getenv("ODOO_LOGIN", "")
        self.password = os.getenv("ODOO_API_KEY", "")
        if not all([self.base, self.db, self.login, self.password]):
            raise ValueError("ODOO_BASE_URL/ODOO_DB/ODOO_LOGIN/ODOO_API_KEY are required")
        self.timeout = int(os.getenv("ODOO_HTTP_TIMEOUT", "60"))
        self.session = requests.Session()

    def authenticate(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"db": self.db, "login": self.login, "password": self.password},
            "id": 1,
        }
        r = self.session.post(
            f"{self.base}/web/session/authenticate", json=payload, timeout=self.timeout
        )
        r.raise_for_status()
        if not r.json().get("result"):
            raise RuntimeError(f"Odoo authenticate failed: {r.text}")

    def call_kw(
        self, model: str, method: str, args: list, kwargs: Optional[Dict[str, Any]] = None
    ) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"model": model, "method": method, "args": args, "kwargs": kwargs or {}},
            "id": 2,
        }
        r = self.session.post(
            f"{self.base}/web/dataset/call_kw", json=payload, timeout=self.timeout
        )
        r.raise_for_status()
        j = r.json()
        if "error" in j:
            raise RuntimeError(f"Odoo call_kw error: {j['error']}")
        return j.get("result")

    def create_attachment(
        self, name: str, mimetype: str, data_b64: str, res_model: str, res_id: int
    ) -> int:
        vals = {
            "name": name,
            "type": "binary",
            "mimetype": mimetype,
            "datas": data_b64,
            "res_model": res_model,
            "res_id": res_id,
        }
        return int(self.call_kw("ir.attachment", "create", [vals], {}))
