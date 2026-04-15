"""Contract tests for OData v1 EntitySet `TimeEntries`."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

CONTRACT_PATH = (
    Path(__file__).resolve().parents[3]
    / "platform"
    / "contracts"
    / "odata"
    / "v1"
    / "entitysets"
    / "time_entries.yaml"
)

EXPECTED_REQUIRED_PROPS = {
    "TimeEntryId",
    "Description",
    "EntryDate",
    "Duration",
    "AnalyticAccountId",
    "CompanyId",
    "CreatedOn",
    "ModifiedOn",
}


@pytest.fixture(scope="module")
def contract() -> dict:
    assert CONTRACT_PATH.exists(), f"contract missing at {CONTRACT_PATH}"
    with CONTRACT_PATH.open() as fh:
        return yaml.safe_load(fh)


def test_contract_metadata(contract):
    assert contract["metadata"]["contract"] == "odata-entityset-timeentries-v1"


def test_entity_set_identity(contract):
    es = contract["entity_set"]
    assert es["name"] == "TimeEntries"
    assert es["odoo_model"] == "account.analytic.line"
    assert es["read_only"] is True


def test_required_properties_present(contract):
    props = set(contract["properties"].keys())
    missing = EXPECTED_REQUIRED_PROPS - props
    assert not missing, f"missing required properties: {sorted(missing)}"


def test_key_property_marked(contract):
    keys = [name for name, p in contract["properties"].items() if p.get("is_key")]
    assert keys == ["TimeEntryId"]


def test_default_domain_excludes_non_project_lines(contract):
    domain = contract.get("default_domain", [])
    assert any("project_id" in str(clause) for clause in domain), (
        "TimeEntries must filter to lines with project_id set"
    )


def test_filterable_subset_valid(contract):
    props = set(contract["properties"].keys())
    invalid = set(contract["filterable_properties"]) - props
    assert not invalid, f"filterable references unknown properties: {invalid}"


def test_orderable_subset_valid(contract):
    props = set(contract["properties"].keys())
    invalid = set(contract["orderable_properties"]) - props
    assert not invalid, f"orderable references unknown properties: {invalid}"


# -- live endpoint --------------------------------------------------------

ODATA_BASE_URL = os.environ.get("ODATA_BASE_URL")
TENANT = os.environ.get("ODATA_TENANT", "test")
TOKEN = os.environ.get("ODATA_BEARER_TOKEN")

pytestmark_live = pytest.mark.skipif(
    not (ODATA_BASE_URL and TOKEN),
    reason="OData bridge not yet built or env not set; structural tests only",
)


@pytestmark_live
def test_live_date_range_filter():
    import json
    import urllib.parse
    import urllib.request

    qs = urllib.parse.urlencode(
        {
            "$filter": "EntryDate ge 2026-04-01 and EntryDate le 2026-04-30",
            "$select": "TimeEntryId,EntryDate,Duration",
            "$top": "20",
        }
    )
    url = f"{ODATA_BASE_URL}/odata/v1/{TENANT}/TimeEntries?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())
    assert "value" in payload
    assert all("TimeEntryId" in row for row in payload["value"])


@pytestmark_live
def test_live_top_capped_at_max():
    import urllib.error
    import urllib.request

    url = f"{ODATA_BASE_URL}/odata/v1/{TENANT}/TimeEntries?$top=10000"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req, timeout=15)
    assert exc.value.code == 400, "$top above max must return 400"
