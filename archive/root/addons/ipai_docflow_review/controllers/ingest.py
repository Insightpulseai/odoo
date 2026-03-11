import base64
import hashlib
import json
import mimetypes

from odoo.http import request

from odoo import http


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class DocflowIngestController(http.Controller):
    @http.route(
        "/docflow/ingest", type="json", auth="none", csrf=False, methods=["POST"]
    )
    def ingest(self, **payload):
        token = request.httprequest.headers.get("X-DocFlow-Token", "")
        expected = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("docflow.ingest_token", default="")
        )
        if not expected or token != expected:
            return {"ok": False, "error": "unauthorized"}

        filename = payload.get("filename") or "document.bin"
        file_b64 = payload.get("file_b64")
        if not file_b64:
            return {"ok": False, "error": "file_b64 required"}

        file_bytes = base64.b64decode(file_b64.encode("ascii"))
        file_hash = _sha256_bytes(file_bytes)
        document_id = payload.get("document_id") or file_hash[:16]

        doc_type = payload.get("doc_type") or "unknown"
        confidence = float(payload.get("confidence") or 0.0)

        classification_json = payload.get("classification_json")
        extraction_json = payload.get("extraction_json")
        validation_json = payload.get("validation_json")
        confidence_breakdown_json = payload.get("confidence_breakdown_json")
        vendor_match_partner_id = payload.get("vendor_match_partner_id")
        vendor_match_method = payload.get("vendor_match_method")
        vendor_match_score = payload.get("vendor_match_score")
        dupe_risk = payload.get("dupe_risk")
        dupe_hits_json = payload.get("dupe_hits_json")

        mt, _ = mimetypes.guess_type(filename)
        attachment = (
            request.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": filename,
                    "type": "binary",
                    "mimetype": mt or "application/octet-stream",
                    "datas": base64.b64encode(file_bytes).decode("ascii"),
                    "res_model": "docflow.document",
                    "res_id": 0,
                }
            )
        )

        Doc = request.env["docflow.document"].sudo()
        existing = Doc.search([("document_id", "=", document_id)], limit=1)

        vals = {
            "name": f"DocFlow {document_id}",
            "document_id": document_id,
            "file_hash": file_hash,
            "source": payload.get("source") or "viber",
            "state": payload.get("state") or "extracted",
            "doc_type": doc_type,
            "confidence": confidence,
            "ocr_text": payload.get("ocr_text") or None,
            "llm_classification_json": (
                json.dumps(classification_json, ensure_ascii=False)
                if isinstance(classification_json, dict)
                else classification_json
            ),
            "llm_extraction_json": (
                json.dumps(extraction_json, ensure_ascii=False)
                if isinstance(extraction_json, dict)
                else extraction_json
            ),
            "validation_json": (
                json.dumps(validation_json, ensure_ascii=False)
                if isinstance(validation_json, dict)
                else validation_json
            ),
            "confidence_breakdown_json": (
                json.dumps(confidence_breakdown_json, ensure_ascii=False)
                if isinstance(confidence_breakdown_json, dict)
                else confidence_breakdown_json
            ),
            "attachment_id": attachment.id,
            "vendor_match_partner_id": (
                int(vendor_match_partner_id) if vendor_match_partner_id else False
            ),
            "vendor_match_method": vendor_match_method,
            "vendor_match_score": float(vendor_match_score or 0.0),
            "dupe_risk": float(dupe_risk or 0.0),
            "dupe_hits_json": (
                json.dumps(dupe_hits_json, ensure_ascii=False)
                if isinstance(dupe_hits_json, (list, dict))
                else dupe_hits_json
            ),
        }

        if existing:
            existing.write(vals)
            doc = existing
        else:
            doc = Doc.create(vals)

        # Link attachment
        attachment.write({"res_id": doc.id})

        # Parse JSON into structured fields
        doc._docflow_parse_extraction_into_fields()

        # DocFlow v2: Bank Statement
        if doc.doc_type == "bank_statement":
            payload = (
                json.loads(doc.llm_extraction_json or "{}")
                if doc.llm_extraction_json
                else {}
            )
            # expected schema: see prompts section
            stmt = (
                request.env["docflow.bank.statement"]
                .sudo()
                .create(
                    {
                        "name": payload.get("statement_name")
                        or f"Statement {doc.document_id}",
                        "document_id": doc.id,
                        "journal_id": int(
                            payload.get("journal_id") or 0
                        ),  # daemon provides journal_id OR you map by IBAN/account
                        "currency_id": request.env["res.currency"]
                        .search(
                            [("name", "=", payload.get("currency", "PHP"))], limit=1
                        )
                        .id,
                        "date_from": payload.get("date_from"),
                        "date_to": payload.get("date_to"),
                        "opening_balance": float(payload.get("opening_balance") or 0.0),
                        "closing_balance": float(payload.get("closing_balance") or 0.0),
                    }
                )
            )
            for li in payload.get("lines", []):
                request.env["docflow.bank.statement.line"].sudo().create(
                    {
                        "statement_id": stmt.id,
                        "date": li["date"],
                        "amount": float(li["amount"]),
                        "direction": li["direction"],
                        "reference": li.get("reference"),
                        "memo": li.get("memo"),
                        "counterparty": li.get("counterparty"),
                    }
                )
            doc.bank_statement_id = stmt.id

            # create recon session
            sess = (
                request.env["docflow.recon.session"]
                .sudo()
                .create(
                    {
                        "name": f"Recon {stmt.name}",
                        "statement_id": stmt.id,
                    }
                )
            )
            doc.recon_session_id = sess.id

        # Hardening: Activity Automation for High Risk
        if doc.state == "needs_review" and (
            doc.dupe_risk >= 0.85
            or (doc.vendor_match_score < 0.6 and doc.doc_type == "invoice")
        ):
            # Try to find a suitable user (e.g., admin or current user)
            # In a real deployment, this might be configured via settings
            user_id = request.env.user.id

            summary = "Review High Risk Document"
            if doc.dupe_risk >= 0.85:
                summary = f"Review Possible Duplicate (Risk: {doc.dupe_risk:.0%})"
            elif doc.vendor_match_score < 0.6:
                summary = "Vendor Resolution Needed"

            doc.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user_id,
                summary=summary,
                note=f"Confidence: {doc.confidence:.2f}, Dupe Risk: {doc.dupe_risk:.2f}",
            )

        return {"ok": True, "document_id": document_id, "docflow_id": doc.id}
