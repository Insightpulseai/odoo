from odoo import http
from odoo.http import request
import requests

class IPAICopilotController(http.Controller):
    @http.route("/ipai/copilot/query", type="json", auth="user")
    def copilot_query(self, message, context=None):
        icp = request.env["ir.config_parameter"].sudo()
        api_url = (icp.get_param("ipai.copilot.api_url") or "").rstrip("/")
        api_key = icp.get_param("ipai.copilot.api_key") or ""

        if not api_url:
            return {"ok": False, "error": "Copilot API URL not configured (Settings -> General Settings -> IPAI Copilot)."}

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "message": message,
            "odoo": {
                "db": request.db,
                "uid": request.uid,
                "context": context or {},
                # Optional screen context (you can enrich this later from JS)
            },
        }

        try:
            r = requests.post(f"{api_url}/copilot/query", json=payload, headers=headers, timeout=45)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
