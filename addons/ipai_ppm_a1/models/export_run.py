import json
import urllib.request

from odoo import api, fields, models
from odoo.exceptions import UserError


class IpaiRepoExportRun(models.Model):
    _name = "ipai.repo.export_run"
    _description = "Repo Export Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="Seed Export")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("failed", "Failed")],
        default="draft",
        tracking=True,
    )
    exported_at = fields.Datetime()
    export_path = fields.Char(help="Filesystem path on server (optional).")
    payload_json = fields.Text(help="Full export payload (JSON).")
    webhook_url = fields.Char(help="Optional: POST export payload to CI/n8n webhook.")
    webhook_status = fields.Char()

    @api.model
    def _export_payload(self):
        """Generate export payload from all PPM/STC data."""
        Workstream = self.env["ipai.workstream"].sudo()
        Template = self.env["ipai.ppm.template"].sudo()
        Task = self.env["ipai.ppm.task"].sudo()
        Checklist = self.env["ipai.ppm.task.checklist"].sudo()
        Worklist = self.env["ipai.stc.worklist_type"].sudo()
        Check = self.env["ipai.stc.check"].sudo()
        Scenario = self.env["ipai.stc.scenario"].sudo()
        Overlay = self.env["ipai.localization.overlay"].sudo()

        def serialize_record(record, field_list):
            result = {}
            for f in field_list:
                val = record[f]
                if hasattr(val, "id"):
                    result[f] = val.id
                else:
                    result[f] = val
            return result

        def recs(model, fields_list):
            out = []
            for r in model.search([]):
                out.append(serialize_record(r, fields_list))
            return out

        payload = {
            "workstreams": recs(
                Workstream,
                ["id", "code", "name", "description", "sap_anchor", "odoo_anchor", "active"],
            ),
            "templates": recs(
                Template,
                [
                    "id",
                    "workstream_id",
                    "code",
                    "name",
                    "period_type",
                    "version",
                    "is_active",
                    "sequence",
                ],
            ),
            "tasks": recs(
                Task,
                [
                    "id",
                    "template_id",
                    "code",
                    "name",
                    "category",
                    "phase",
                    "sequence",
                    "due_offset_days",
                    "owner_role",
                    "requires_approval",
                    "evidence_required",
                    "sap_reference",
                ],
            ),
            "checklists": recs(
                Checklist,
                ["id", "task_id", "sequence", "label", "required", "evidence_type", "notes"],
            ),
            "stc_worklist_types": recs(Worklist, ["id", "code", "name", "description"]),
            "stc_checks": recs(
                Check,
                [
                    "id",
                    "workstream_id",
                    "worklist_type_id",
                    "code",
                    "name",
                    "description",
                    "category",
                    "sequence",
                    "severity",
                    "is_active",
                    "sap_reference",
                ],
            ),
            "stc_scenarios": [
                {
                    "id": s.id,
                    "workstream_id": s.workstream_id.id,
                    "code": s.code,
                    "name": s.name,
                    "frequency": s.frequency,
                    "sequence": s.sequence,
                    "check_codes": s.check_ids.mapped("code"),
                    "bir_forms": s.bir_forms,
                    "notes": s.notes,
                    "sap_reference": s.sap_reference,
                }
                for s in Scenario.search([])
            ],
            "localization_overlays": recs(
                Overlay,
                [
                    "id",
                    "country",
                    "workstream_id",
                    "applies_to_code",
                    "patch_type",
                    "patch_payload",
                    "sequence",
                    "active",
                ],
            ),
        }
        return payload

    def action_generate_payload(self):
        """Generate JSON payload from current data."""
        for rec in self:
            payload = rec._export_payload()
            rec.payload_json = json.dumps(payload, indent=2, ensure_ascii=False)
            rec.state = "done"
            rec.exported_at = fields.Datetime.now()

    def action_write_to_path(self):
        """Write payload to filesystem path."""
        for rec in self:
            if not rec.export_path:
                raise UserError("Set export_path first.")
            if not rec.payload_json:
                rec.action_generate_payload()
            with open(rec.export_path, "w", encoding="utf-8") as f:
                f.write(rec.payload_json)
            rec.message_post(body=f"Exported payload to path: {rec.export_path}")

    def action_post_webhook(self):
        """POST payload to webhook URL."""
        for rec in self:
            if not rec.webhook_url:
                raise UserError("Set webhook_url first.")
            if not rec.payload_json:
                rec.action_generate_payload()
            req = urllib.request.Request(
                rec.webhook_url,
                data=rec.payload_json.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    rec.webhook_status = f"{resp.status} {resp.reason}"
            except Exception as e:
                rec.webhook_status = f"FAILED: {e}"
                rec.state = "failed"
                rec.message_post(body=f"Webhook post failed: {e}")
                continue
            rec.message_post(body=f"Webhook posted: {rec.webhook_status}")
