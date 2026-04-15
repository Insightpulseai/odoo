"""Contract tests for OData v1 EntitySet `ProjectTasks`."""
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
    / "project_tasks.yaml"
)

EXPECTED_REQUIRED_PROPS = {
    "TaskId",
    "Subject",
    "ProjectId",
    "CompanyId",
    "IsClosed",
    "CreatedOn",
    "ModifiedOn",
}


@pytest.fixture(scope="module")
def contract() -> dict:
    assert CONTRACT_PATH.exists(), f"contract missing at {CONTRACT_PATH}"
    with CONTRACT_PATH.open() as fh:
        return yaml.safe_load(fh)


def test_contract_metadata(contract):
    assert contract["metadata"]["contract"] == "odata-entityset-projecttasks-v1"


def test_entity_set_identity(contract):
    es = contract["entity_set"]
    assert es["name"] == "ProjectTasks"
    assert es["odoo_model"] == "project.task"
    assert es["read_only"] is True


def test_required_properties_present(contract):
    props = set(contract["properties"].keys())
    missing = EXPECTED_REQUIRED_PROPS - props
    assert not missing, f"missing required properties: {sorted(missing)}"


def test_key_property_marked(contract):
    keys = [name for name, p in contract["properties"].items() if p.get("is_key")]
    assert keys == ["TaskId"]


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
def test_live_filter_by_project_and_state():
    import json
    import urllib.request

    url = (
        f"{ODATA_BASE_URL}/odata/v1/{TENANT}/ProjectTasks"
        "?$filter=IsClosed eq false&$select=TaskId,Subject,DueDate&$top=10"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())
    assert "value" in payload
    assert all("TaskId" in row and "Subject" in row for row in payload["value"])
