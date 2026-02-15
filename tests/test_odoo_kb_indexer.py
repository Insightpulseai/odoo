import json
import tempfile
import sys
from pathlib import Path
import pytest

# Add repo root to path to allow importing scripts
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.kb.index_odoo_docs import main as _main  # type: ignore


def test_indexer_emits_expected_files(monkeypatch):
    # Create a tiny fake KB in a temp dir
    with tempfile.TemporaryDirectory() as d:
        kb = Path(d) / "docs" / "kb" / "odoo19"
        (kb / "upstream" / "content" / "developer").mkdir(parents=True, exist_ok=True)
        (kb / "index").mkdir(parents=True, exist_ok=True)

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

        # minimal topic map
        (kb / "index" / "topic_map.yaml").write_text(
            "version: 1\n"
            "topics:\n"
            "  - id: odoo19.dev.orm\n"
            "    label: ORM\n"
            "    include_paths:\n"
            '      - "content/developer/**"\n',
            encoding="utf-8",
        )

        # minimal upstream doc
        (kb / "upstream" / "content" / "developer" / "intro.md").write_text(
            "# Title\n\n## Subtitle\n",
            encoding="utf-8",
        )

        # run the script with argv override
        monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
        monkeypatch.setattr(
            "sys.argv",
            ["index_odoo_docs.py", "--kb-root", str(kb)],
        )

        _main()

        assert (kb / "index" / "manifest.json").exists()
        assert (kb / "index" / "sections.json").exists()
        assert (kb / "index" / "topics.json").exists()
        assert (kb / "index" / "skills_coverage.json").exists()

        topics = json.loads((kb / "index" / "topics.json").read_text(encoding="utf-8"))
        assert topics["topics"][0]["matched_count"] == 1
