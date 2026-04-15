"""Contract tests for OData v1 EntitySet `Projects`.

Validates the YAML contract at:
    platform/contracts/odata/v1/entitysets/projects.yaml

Structural validation runs without an Odoo runtime.
Live-endpoint validation skips when ODATA_BASE_URL env var is unset
(the bridge module isn't built until the documented build trigger fires).
"""
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
    / "projects.yaml"
)

EXPECTED_REQUIRED_PROPS = {
    "ProjectId",
    "Name",
    "CompanyId",
    "IsActive",
    "CreatedOn",
    "ModifiedOn",
}


@pytest.fixture(scope="module")
def contract() -> dict:
    assert CONTRACT_PATH.exists(), f"contract missing at {CONTRACT_PATH}"
    with CONTRACT_PATH.open() as fh:
        return yaml.safe_load(fh)


# -- structural --------------------------------------------------------------

def test_contract_metadata(contract):
    assert contract["metadata"]["contract"] == "odata-entityset-projects-v1"
    assert contract["metadata"]["status"] in {"design", "implemented"}


def test_contract_entity_set_identity(contract):
    es = contract["entity_set"]
    assert es["name"] == "Projects"
    assert es["odoo_model"] == "project.project"
    assert es["read_only"] is True


def test_required_properties_present(contract):
    props = set(contract["properties"].keys())
    missing = EXPECTED_REQUIRED_PROPS - props
    assert not missing, f"missing required properties: {sorted(missing)}"


def test_key_property_marked(contract):
    keys = [name for name, p in contract["properties"].items() if p.get("is_key")]
    assert keys == ["ProjectId"], f"expected single key ProjectId, got {keys}"


def test_filterable_subset_valid(contract):
    props = set(contract["properties"].keys())
    invalid = set(contract["filterable_properties"]) - props
    assert not invalid, f"filterable references unknown properties: {invalid}"


def test_orderable_subset_valid(contract):
    props = set(contract["properties"].keys())
    invalid = set(contract["orderable_properties"]) - props
    assert not invalid, f"orderable references unknown properties: {invalid}"


def test_no_writes_in_v1(contract):
    assert contract["entity_set"]["read_only"] is True


# -- live endpoint (skipped until bridge is implemented) ---------------------

ODATA_BASE_URL = os.environ.get("ODATA_BASE_URL")
TENANT = os.environ.get("ODATA_TENANT", "test")
TOKEN = os.environ.get("ODATA_BEARER_TOKEN")

pytestmark_live = pytest.mark.skipif(
    not (ODATA_BASE_URL and TOKEN),
    reason="OData bridge not yet built or env not set; structural tests only",
)


@pytestmark_live
def test_live_metadata_includes_projects():
    import urllib.request

    req = urllib.request.Request(
        f"{ODATA_BASE_URL}/odata/v1/{TENANT}/$metadata",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode()
    assert 'EntitySet Name="Projects"' in body


@pytestmark_live
def test_live_top_skip_count():
    import json
    import urllib.request

    url = (
        f"{ODATA_BASE_URL}/odata/v1/{TENANT}/Projects"
        "?$select=ProjectId,Name&$top=5&$count=true"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())
    assert "@odata.count" in payload
    assert "value" in payload and isinstance(payload["value"], list)
    assert len(payload["value"]) <= 5


@pytestmark_live
def test_live_writes_blocked():
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        f"{ODATA_BASE_URL}/odata/v1/{TENANT}/Projects",
        data=b"{}",
        method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req, timeout=15)
    assert exc.value.code in {405, 403}, "POST must be blocked in v1"
