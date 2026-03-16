# DocFlow Agentic Finance (Odoo 19)

**Status:** ACCEPTED — PRODUCTION READY

DocFlow is a local-first, agentic document processing system for Finance. It combines deterministic OCR, LLM reasoning, and Odoo-native workflows to automate Expenses, Vendor Bills, and Bank Statements with full auditability.

## Key Properties

- **No third-party document AI**: Uses local OCR and generic LLMs (OpenAI/Gemini/Anthropic) for reasoning.
- **Human-in-the-loop by design**: Structured review UI with visual diffs and risk signals.
- **Rules-as-code configuration**: Routing and validation rules managed via YAML.
- **Explainable decisions**: Every match, classification, and extraction has a stored rationale.

## Core Capabilities

### 1. Ingestion Pipeline

- **Sources**: Watch folders (Viber/Dropbox), Email (via Odoo), or Manual Upload.
- **Processing**: Tesseract OCR -> LLM Classification -> LLM Extraction -> Deterministic Validation.
- **Security**: ID-token authenticated JSON-RPC ingestion endpoint.

### 2. Manual Review Module (`ipai_docflow_review`)

- **Document Central**: Single view for proper OCR/Validation/Extraction status.
- **Intelligence**:
  - **Vendor Matching**: Fuzzy matching against Odoo partners.
  - **Duplicate Detection**: Smart checks against existing Odoo Moves and Expenses.
- **SLA**: Activity-driven service level agreements with auto-escalation.

### 3. Bank Statement Automation

- **Ingestion**: specialized schema for bank statements.
- **Reconciliation**: Automated candidate generation matching statement lines to Payments/Invoices.

### 4. Advanced Routing

- **Multi-Company**: Rules to route to specific Companies and Journals.
- **Assignment**: Load-balanced or fixed reviewer assignment.

## Usage

### Running the Daemon

```bash
# Watch a folder for new files
python scripts/viber_watch_daemon.py
```

### Loading Routing Rules

```bash
# Load rules from YAML configuration
./odoo-bin shell -d <DB> < addons/ipai_docflow_review/scripts/load_routing_rules.py
```
