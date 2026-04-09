"""Live end-to-end invoice analysis through Foundry + Document Intelligence.

The uploaded Dataverse invoice is the mandatory negative fixture.
Expected outcome:
  - extracted values reconcile for line, VAT, gross, and withholding
  - printed total due does NOT reconcile with expected payable
  - verdict must be needs_review
  - PRINTED_TOTAL_DUE_MISMATCH must be in findings

Requires env vars:
  FOUNDRY_PROJECT_ENDPOINT
  FOUNDRY_MODEL
  DOCINTEL_ENDPOINT
  DOCINTEL_KEY

Requires fixture:
  live_invoice_path — path to the Dataverse TBWA invoice PDF

Run:  pytest -xvs agent-platform/tests/e2e/test_invoice_live_foundry.py
CI:   azure_staging_revision gate (after Document Intelligence + Foundry smoke)
"""

import os
import sys

from tests.smoke.conftest import require_env


def test_uploaded_invoice_negative_fixture_live(live_invoice_path):
    require_env(
        "FOUNDRY_PROJECT_ENDPOINT",
        "FOUNDRY_MODEL",
        "DOCINTEL_ENDPOINT",
        "DOCINTEL_KEY",
    )

    # Import the analyzer service — adjust path if your project layout differs
    try:
        from app.services.invoice_analyzer import analyze_invoice
    except ImportError:
        import pytest
        pytest.skip("app.services.invoice_analyzer not available in this environment")

    with live_invoice_path.open("rb") as f:
        result = analyze_invoice(
            file_bytes=f.read(),
            model_name=os.environ["FOUNDRY_MODEL"],
        )

    validation = result["validation"]
    codes = {finding["code"] for finding in validation["findings"]}

    assert validation["status"] == "needs_review"
    assert validation["expected_payable"] == "95408.16"
    assert validation["printed_total_due"] == "85000.00"
    assert "PRINTED_TOTAL_DUE_MISMATCH" in codes
