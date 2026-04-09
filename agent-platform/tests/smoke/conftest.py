import os
from pathlib import Path

import pytest


def require_env(*names: str) -> None:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        pytest.skip(f"missing required env: {', '.join(missing)}")


@pytest.fixture
def live_invoice_path() -> Path:
    candidate = Path(
        os.getenv(
            "TEST_INVOICE_PATH",
            "tests/fixtures/invoices/dataverse_tbwa_0001.pdf",
        )
    )
    if not candidate.exists():
        pytest.skip(f"missing test invoice fixture: {candidate}")
    return candidate
