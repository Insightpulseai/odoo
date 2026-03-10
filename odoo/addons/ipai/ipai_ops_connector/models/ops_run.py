import json
import uuid
import requests
from odoo import api, fields, models

class IpaOpsRun(models.Model):
    _name = "ipai.ops.run"
    _description = "IPAI Ops Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(default=lambda self: f"run_{uuid.uuid4().hex[:10]}", readonly=True)
    status = fields.Selection([
        ("queued","Queued"),
        ("running","Running"),
        ("succeeded","Succeeded"),
        ("failed","Failed"),
        ("canceled","Canceled"),
    ], default="queued", tracking=True)

    kind = fields.Char(required=True, tracking=True)  # e.g. "ocr.expense", "ai.prompt", "browser.qa"
    payload_json = fields.Text(required=True)         # deterministic request
    result_json = fields.Text(readonly=True)
    external_run_id = fields.Char(index=True, readonly=True)
    error = fields.Text(readonly=True)

    # Config via env (no UI): service endpoint + auth token
    def _endpoint(self):
        return self.env["ir.config_parameter"].sudo().get_param("ipai_ops.endpoint")

    def _token(self):
        return self.env["ir.config_parameter"].sudo().get_param("ipai_ops.token")

    def action_dispatch(self):
        for r in self.filtered(lambda x: x.status == "queued"):
            try:
                endpoint = self._endpoint()
                token = self._token()
                if not endpoint or not token:
                    raise ValueError("Missing ipai_ops.endpoint or ipai_ops.token (ir.config_parameter)")

                resp = requests.post(
                    f"{endpoint.rstrip('/')}/runs",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=r.payload_json,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                r.write({"status":"running", "external_run_id": data.get("id")})
            except Exception as e:
                r.write({"status":"failed", "error": str(e)})

    @api.model
    def create_run(self, kind: str, payload: dict):
        return self.create({
            "kind": kind,
            "payload_json": json.dumps(payload, separators=(",",":"), sort_keys=True),
        }).id

    def apply_result(self, external_run_id: str, status: str, result: dict | None = None, error: str | None = None):
        r = self.search([("external_run_id","=",external_run_id)], limit=1)
        if not r:
            return False
        vals = {"status": status}
        if result is not None:
            vals["result_json"] = json.dumps(result, separators=(",",":"), sort_keys=True)
        if error:
            vals["error"] = error
        r.write(vals)
        return True
