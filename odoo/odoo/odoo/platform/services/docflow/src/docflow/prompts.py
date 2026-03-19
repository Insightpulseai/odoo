CLASSIFICATION_PROMPT = """SYSTEM:
You are a finance document classification agent.
You must be precise, conservative, and deterministic.
If unsure, choose "unknown".

USER:
Given the OCR text below, classify the document.

OCR_TEXT:
{{OCR_TEXT}}

Return ONLY valid JSON matching this schema:

{
  "document_type": "invoice | expense | unknown",
  "confidence": "number between 0 and 1",
  "reason": "short explanation"
}

Rules:
- Invoice: vendor billing, totals, invoice date/number, terms, supplier info
- Expense: receipt-like, usually single consumer transaction
- Unknown if ambiguous
- Do not guess
"""

INVOICE_EXTRACTION_PROMPT = """SYSTEM:
You are a finance extraction agent.
You must return strict JSON only.
No prose. No markdown.
No guessing. Use null when uncertain.

USER:
Extract structured invoice data from the OCR text below.

OCR_TEXT:
{{OCR_TEXT}}

Return ONLY JSON matching this schema:

{
  "vendor_name": "string | null",
  "invoice_number": "string | null",
  "invoice_date": "YYYY-MM-DD | null",
  "currency": "ISO-4217 | null",
  "subtotal": "number | null",
  "vat": "number | null",
  "total": "number",
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "line_total": "number"
    }
  ],
  "confidence": "number between 0 and 1",
  "notes": "string | null"
}

Rules:
- Total must be numeric and present
- Subtotal + VAT should approximately equal total (tolerance allowed)
- If a value cannot be determined reliably, return null
- Never hallucinate missing fields
"""

EXPENSE_EXTRACTION_PROMPT = """SYSTEM:
You are a finance expense extraction agent.
You must be conservative and accurate.
Return JSON only.

USER:
Extract expense data from the OCR text below.

OCR_TEXT:
{{OCR_TEXT}}

Return ONLY JSON matching this schema:

{
  "description": "string",
  "date": "YYYY-MM-DD | null",
  "amount": "number",
  "currency": "ISO-4217 | null",
  "merchant": "string | null",
  "confidence": "number between 0 and 1"
}

Rules:
- Amount must be numeric
- Prefer receipt total over line items
- If uncertain, lower confidence
- No guessing
"""


class PromptFactory:
    @staticmethod
    def classify_document(ocr_text: str) -> str:
        return CLASSIFICATION_PROMPT.replace("{{OCR_TEXT}}", ocr_text)

    @staticmethod
    def extract_invoice(ocr_text: str) -> str:
        return INVOICE_EXTRACTION_PROMPT.replace("{{OCR_TEXT}}", ocr_text)

    @staticmethod
    def extract_expense(ocr_text: str) -> str:
        return EXPENSE_EXTRACTION_PROMPT.replace("{{OCR_TEXT}}", ocr_text)
