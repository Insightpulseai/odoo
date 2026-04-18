"""Pack 100 contract tests."""
from __future__ import annotations

import pathlib

import yaml

PACK_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "ssot" / "demo" / "100-system-shared"


def _load(name: str) -> dict:
    return yaml.safe_load((PACK_DIR / name).read_text(encoding="utf-8"))


def test_companies_have_required_keys():
    payload = _load("companies.yaml")
    assert payload["companies"], "companies required"
    for row in payload["companies"]:
        for k in ("key", "name", "code", "country_code", "currency"):
            assert k in row, f"company {row.get('key')} missing {k}"


def test_journals_reference_known_companies():
    companies = {c["key"] for c in _load("companies.yaml")["companies"]}
    for j in _load("journals.yaml")["journals"]:
        assert j["company"] in companies, f"journal {j['key']} references unknown company {j['company']}"


def test_dms_taxonomy_paths_unique():
    folders = _load("dms-taxonomy.yaml")["folders"]
    paths = [f["path"] for f in folders]
    assert len(paths) == len(set(paths)), "dms folder paths must be unique"
