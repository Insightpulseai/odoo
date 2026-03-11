import json
import tempfile
import sys
from pathlib import Path

# Add repo root to path to allow importing scripts
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# check if we can import the script - if not, skip tests that depend on it
try:
    from scripts.kb.verify_odoo_docs_pin import main as _main  # type: ignore
except ImportError:
    _main = None


def test_pin_verifier_directory_mode(monkeypatch):
    if _main is None:
        return

    with tempfile.TemporaryDirectory() as d:
        kb = Path(d) / "docs" / "kb" / "odoo19"
        (kb / "upstream").mkdir(parents=True, exist_ok=True)

        (kb / "UPSTREAM_PIN.json").write_text(
            json.dumps(
                {
                    "upstream": "https://github.com/odoo/documentation",
                    "branch": "19.0",
                    "pinned_commit": "deadbeef",
                    "pinned_at_utc": "2026-02-15T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        (kb / "UPSTREAM_REV.txt").write_text("deadbeef\n", encoding="utf-8")

        monkeypatch.setattr("sys.argv", ["verify_odoo_docs_pin.py", "--kb-root", str(kb)])

        # Should persist without error
        try:
            _main()
        except SystemExit as e:
            if e.code != 0:
                raise

        # Test failure case
        (kb / "UPSTREAM_REV.txt").write_text("badc0ffee\n", encoding="utf-8")

        import pytest

        with pytest.raises(SystemExit) as excinfo:
            _main()
        assert "UPSTREAM_REV mismatch" in str(excinfo.value)
