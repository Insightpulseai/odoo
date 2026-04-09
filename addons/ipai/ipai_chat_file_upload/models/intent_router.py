# -*- coding: utf-8 -*-
"""Attachment-aware intent classification for chat messages.

Classifies user intent when attachments are present so the system
routes to extraction/validation/summarization instead of asking
generic clarification questions.
"""
import re

# Intent categories
INTENT_EXTRACT = 'extract'
INTENT_SUMMARIZE = 'summarize'
INTENT_VALIDATE = 'validate'
INTENT_REVIEW = 'review'
INTENT_GENERAL = 'general'

# Pattern → intent mapping (order matters: first match wins)
_INTENT_PATTERNS = [
    # Extract
    (re.compile(
        r'\b(extract|parse|pull out|get the fields|read the|ocr|'
        r'extract first|show me the data|what does it say)\b', re.I,
    ), INTENT_EXTRACT),
    # Validate / assess / check
    (re.compile(
        r'\b(assess|validate|verify|check|correct|accurate|'
        r'tax computation|total.*(correct|right|match)|'
        r'discrepanc|mismatch|reconcil|complian|'
        r'amount.*(billed|due|correct)|'
        r'is the.*(right|correct|accurate))\b', re.I,
    ), INTENT_VALIDATE),
    # Review
    (re.compile(
        r'\b(review|audit|inspect|examine|look at|analyze|analyse)\b', re.I,
    ), INTENT_REVIEW),
    # Summarize
    (re.compile(
        r'\b(summar\w*|overview|brief|tldr|tl;dr|key points|highlights|'
        r'what is this|what\'s this|describe)\b', re.I,
    ), INTENT_SUMMARIZE),
]

# Document type hints based on extracted text or filename
_DOC_TYPE_PATTERNS = [
    (re.compile(
        r'\b(invoice|billing|bill|vat|tax|withholding|ewt|'
        r'total.*(due|amount|payable)|subtotal|'
        r'tin|taxpayer|bir|receipt|official receipt|'
        r'accounts?\s*(payable|receivable))\b', re.I,
    ), 'invoice'),
    (re.compile(
        r'\b(contract|agreement|terms|party|parties|clause|'
        r'whereas|hereinafter)\b', re.I,
    ), 'contract'),
    (re.compile(
        r'\b(balance sheet|income statement|profit.*(loss|and)|'
        r'cash flow|financial statement|equity)\b', re.I,
    ), 'financial_statement'),
]


def classify_intent(message):
    """Classify user intent from message text.

    Returns one of: extract, summarize, validate, review, general.
    """
    if not message or not message.strip():
        return INTENT_GENERAL
    for pattern, intent in _INTENT_PATTERNS:
        if pattern.search(message):
            return intent
    return INTENT_GENERAL


def classify_document_type(text, filename=''):
    """Classify document type from extracted text or filename.

    Returns: invoice, contract, financial_statement, or general.
    """
    combined = f'{filename}\n{text or ""}'
    for pattern, doc_type in _DOC_TYPE_PATTERNS:
        if pattern.search(combined):
            return doc_type
    return 'general'


def build_system_instruction(intent, doc_type, source_count):
    """Build the system instruction for the Foundry prompt based on intent.

    This replaces the generic "use them to answer" preamble with a
    task-specific instruction that prevents the model from asking
    unnecessary clarification questions.
    """
    if intent == INTENT_EXTRACT:
        return (
            'The user has uploaded a document and wants its content extracted. '
            'Extract all fields, line items, totals, dates, and identifiers '
            'from the source document(s). Present them in a structured format. '
            'Do not ask clarification questions — extract what is in the document.'
        )

    if intent == INTENT_VALIDATE:
        if doc_type == 'invoice':
            return (
                'The user has uploaded an invoice and wants the tax computation '
                'and totals validated. You must:\n'
                '1. Extract all line items, subtotals, tax rates, and totals\n'
                '2. Recompute the expected totals deterministically\n'
                '3. Compare computed values against printed values\n'
                '4. Flag any mismatches with the exact difference\n'
                'Do not ask for invoice numbers or records — the document '
                'is the subject. Show your computation.'
            )
        return (
            'The user has uploaded a document and wants it validated. '
            'Extract key fields and values, verify internal consistency '
            '(totals, dates, references), and report any discrepancies. '
            'Do not ask clarification questions — validate what is in the document.'
        )

    if intent == INTENT_REVIEW:
        return (
            'The user has uploaded a document for review. '
            'Extract and present the key fields, structure, and notable items. '
            'Highlight anything that may need attention. '
            'Do not ask clarification questions — present the document analysis directly.'
        )

    if intent == INTENT_SUMMARIZE:
        return (
            'The user has uploaded a document and wants a summary. '
            'Provide a concise summary of the document content, '
            'including key dates, amounts, parties, and conclusions. '
            'Do not ask clarification questions.'
        )

    # INTENT_GENERAL with attachments
    if source_count > 0:
        return (
            'The user has uploaded source documents. '
            'Use them to answer the question. '
            'If the question is about the document content, '
            'answer from the document — do not ask the user to provide '
            'information that is already in the uploaded file.'
        )

    return None


def has_attachment_context(eligible_sources):
    """Check if there are active indexed sources that should ground the response."""
    return bool(eligible_sources)
