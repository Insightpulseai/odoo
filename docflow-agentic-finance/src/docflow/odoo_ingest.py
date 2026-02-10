from __future__ import annotations
import os, base64, json, requests
from pathlib import Path


def ingest_docflow_review_record(
    *,
    odoo_base_url: str,
    token: str,
    filename: str,
    file_path: Path,
    document_id: str,
    source: str,
    state: str,
    doc_type: str,
    confidence: float,
    ocr_text: str | None,
    classification_json: dict | None,
    extraction_json: dict | None,
    validation_json: dict | None,
    confidence_breakdown_json: dict | None,
    vendor_match_partner_id: int | None = None,
    vendor_match_method: str | None = None,
    vendor_match_score: float | None = None,
    dupe_risk: float | None = None,
    dupe_hits_json: list | None = None,
) -> dict:
    file_b64 = base64.b64encode(file_path.read_bytes()).decode("ascii")

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "filename": filename,
            "file_b64": file_b64,
            "document_id": document_id,
            "source": source,
            "state": state,
            "doc_type": doc_type,
            "confidence": confidence,
            "ocr_text": ocr_text,
            "classification_json": classification_json,
            "extraction_json": extraction_json,
            "validation_json": validation_json,
            "confidence_breakdown_json": confidence_breakdown_json,
            "vendor_match_partner_id": vendor_match_partner_id,
            "vendor_match_method": vendor_match_method,
            "vendor_match_score": vendor_match_score,
            "dupe_risk": dupe_risk,
            "dupe_hits_json": dupe_hits_json,
        },
        "id": 1,
    }

    r = requests.post(
        f"{odoo_base_url.rstrip('/')}/docflow/ingest",
        json=payload,
        headers={"X-DocFlow-Token": token},
        timeout=int(os.getenv("ODOO_INGEST_TIMEOUT", "60")),
    )
    r.raise_for_status()
    return r.json()
