import os
import time
import shutil
import json
import logging
from pathlib import Path
from .config import load_config, DocflowConfig

from .schemas import Classification, InvoiceExtraction, ExpenseExtraction, ProcessResult
from .utils import sha256_file
from .ocr import ocr_file
from .llm_client import LlmClient
from .prompts import PromptFactory
from .validators import validate_invoice, validate_expense
from .odoo_rpc import OdooRpc
from .vendor_match import resolve_vendor_partner_id
from .dupe_check import check_invoice_duplicates, check_expense_duplicates
from .odoo_ingest import ingest_docflow_review_record


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class DocFlowRunner:
    def __init__(self):
        self.cfg = load_config()
        self.llm = (
            LlmClient()
        )  # LlmClient likely needs to be updated to accept key/model or read from env itself.
        # Assuming LlmClient reads env vars internally for now as per previous verify,
        # but good practice would be passing them.
        # For now, load_dotenv() in config.py handles env var setting for LlmClient.
        self.odoo = OdooRpc()

        self.inbox_dir = self.cfg.inbox_dir
        self.archive_dir = self.cfg.archive_dir
        self.artifacts_dir = self.cfg.artifacts_dir

        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.ingest_token = self.cfg.ingest_token
        self.odoo_url = self.cfg.odoo_url

        # Config
        self.dupe_threshold = self.cfg.dupe_threshold
        self.push_needs_review = self.cfg.push_needs_review

    def process_one(self, file_path: Path) -> ProcessResult:
        logger.info(f"Processing {file_path.name}...")

        # 1. SHA256
        file_hash = sha256_file(file_path)

        # 2. OCR
        try:
            ocr_text = ocr_file(file_path)
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ProcessResult(file_path=str(file_path), success=False, error=f"OCR error: {e}")

        # 3. Classify
        try:
            cls_out = self.llm.generate(
                PromptFactory.classify_document(ocr_text), response_schema=Classification
            )
            classification = Classification(**cls_out)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return ProcessResult(
                file_path=str(file_path), success=False, error=f"Classification error: {e}"
            )

        # 4. Extract & Validate & Intelligence
        extraction_data = {}
        validation_res = None
        vendor_match = None
        dupe_result = None
        doc_type = classification.doc_type

        # Default state
        final_state = "extracted"

        if doc_type == "invoice":
            try:
                ext_out = self.llm.generate(
                    PromptFactory.extract_invoice(ocr_text), response_schema=InvoiceExtraction
                )
                extraction = InvoiceExtraction(**ext_out)
                extraction_data = extraction.dict()
                validation_res = validate_invoice(extraction)

                # Vendor Match
                vendor_match = resolve_vendor_partner_id(self.odoo, extraction.vendor_name)

                # Dupe Check
                dupe_result = check_invoice_duplicates(
                    self.odoo,
                    partner_id=vendor_match.partner_id,
                    invoice_number=extraction.invoice_number,
                    total=extraction.total,
                    invoice_date=extraction.invoice_date,
                )
            except Exception as e:
                logger.error(f"Invoice extraction/check failed: {e}")
                return ProcessResult(
                    file_path=str(file_path), success=False, error=f"Extraction error: {e}"
                )

        elif doc_type == "expense":
            try:
                ext_out = self.llm.generate(
                    PromptFactory.extract_expense(ocr_text), response_schema=ExpenseExtraction
                )
                extraction = ExpenseExtraction(**ext_out)
                extraction_data = extraction.dict()
                validation_res = validate_expense(extraction)

                # Dupe Check
                dupe_result = check_expense_duplicates(
                    self.odoo,
                    amount=extraction.amount,
                    date=extraction.date,
                    name_hint=extraction.description,
                )
            except Exception as e:
                logger.error(f"Expense extraction/check failed: {e}")
                return ProcessResult(
                    file_path=str(file_path), success=False, error=f"Extraction error: {e}"
                )
        else:
            logger.warning(f"Unknown document type: {doc_type}")
            doc_type = "unknown"
            final_state = "needs_review"

        # 5. Decide Action
        # Signals: validation_res.ok, dupe_result.risk, vendor_match.score (if invoice)

        is_confident = False
        reasons = []

        if validation_res:
            if not validation_res.ok:
                reasons.append(f"Validation failed: {validation_res.reason}")
            elif dupe_result and dupe_result.risk >= self.dupe_threshold:
                reasons.append(f"High dupe risk: {dupe_result.risk}")
            elif (
                doc_type == "invoice"
                and vendor_match
                and vendor_match.score < 0.6
                and not vendor_match.partner_id
            ):
                reasons.append("Vendor not resolved confidently")
            else:
                is_confident = True

        if not is_confident:
            final_state = "needs_review"
        elif self.push_needs_review:
            final_state = "needs_review"  # Force review mode
        else:
            final_state = "approved"

        # 6. Ingest to Odoo Review Module
        try:
            ingest_res = ingest_docflow_review_record(
                odoo_base_url=self.odoo_url,
                token=self.ingest_token,
                filename=file_path.name,
                file_path=file_path,
                document_id=file_hash[:16],
                source="runner",
                state=final_state,
                doc_type=doc_type,
                confidence=validation_res.confidence if validation_res else 0.0,
                ocr_text=ocr_text,
                classification_json=classification.dict(),
                extraction_json=extraction_data,
                validation_json={"ok": validation_res.ok, "reason": validation_res.reason}
                if validation_res
                else {},
                confidence_breakdown_json={},
                vendor_match_partner_id=vendor_match.partner_id if vendor_match else None,
                vendor_match_method=vendor_match.method if vendor_match else None,
                vendor_match_score=vendor_match.score if vendor_match else None,
                dupe_risk=dupe_result.risk if dupe_result else 0.0,
                dupe_hits_json=[{"id": h.record_id, "score": h.score} for h in dupe_result.hits]
                if dupe_result
                else None,
            )
            docflow_id = ingest_res.get("docflow_id")
            logger.info(f"Ingested DocFlow ID: {docflow_id}, State: {final_state}")

            # 7. Auto-Draft if Approved
            if final_state == "approved" and docflow_id:
                logger.info("Auto-creating draft in Odoo...")
                self.odoo.execute_kw(
                    "docflow.document", "action_approve_create_draft", [[docflow_id]]
                )
                logger.info("Draft created successfully.")

        except Exception as e:
            logger.error(f"Ingestion/Auto-draft failed: {e}")
            return ProcessResult(
                file_path=str(file_path), success=False, error=f"Ingest/Odoo error: {e}"
            )

        # 8. Archive & Artifacts
        self._save_artifacts(file_hash, ocr_text, classification, extraction_data)
        shutil.move(str(file_path), str(self.archive_dir / file_path.name))

        return ProcessResult(file_path=str(file_path), success=True, doc_type=doc_type)

    def _save_artifacts(self, file_hash, ocr_text, classification, extraction):
        base = self.artifacts_dir / file_hash
        (base.parent).mkdir(parents=True, exist_ok=True)  # Ensure artifacts dir exists

        with open(f"{base}_ocr.txt", "w") as f:
            f.write(ocr_text)

        with open(f"{base}_classification.json", "w") as f:
            f.write(json.dumps(classification.dict(), indent=2))

        if extraction:
            with open(f"{base}_extraction.json", "w") as f:
                f.write(json.dumps(extraction, indent=2))

    def run_folder(self):
        files = sorted(
            [p for p in self.inbox_dir.glob("*") if p.is_file() and not p.name.startswith(".")]
        )
        logger.info(f"Found {len(files)} files in inbox.")
        results = []
        for f in files:
            res = self.process_one(f)
            results.append(res)
        return results


if __name__ == "__main__":
    runner = DocFlowRunner()
    runner.run_folder()
