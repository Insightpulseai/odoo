"""Document Intelligence live smoke test — prebuilt-invoice extraction.

Validates that the Document Intelligence endpoint can analyze a real invoice
using the prebuilt-invoice model.

Requires env vars:
  DOCINTEL_ENDPOINT — Document Intelligence endpoint URL
  DOCINTEL_KEY — API key for Document Intelligence

Requires fixture:
  live_invoice_path — path to the test invoice PDF

Run:  DOCINTEL_ENDPOINT=... DOCINTEL_KEY=... pytest -xvs
CI:   azure_staging_revision gate
"""

import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

from .conftest import require_env


def test_document_intelligence_prebuilt_invoice_smoke(live_invoice_path):
    require_env("DOCINTEL_ENDPOINT", "DOCINTEL_KEY")

    client = DocumentIntelligenceClient(
        endpoint=os.environ["DOCINTEL_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["DOCINTEL_KEY"]),
    )

    with live_invoice_path.open("rb") as f:
        result = client.begin_analyze_document(
            "prebuilt-invoice",
            body=f.read(),
        ).result()

    assert result is not None
    assert getattr(result, "content", None) or getattr(result, "documents", None)
