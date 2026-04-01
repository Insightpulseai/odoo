"""Validate design policy SSOT."""
import yaml
from pathlib import Path


def test_design_policy_no_hand_edits():
    path = Path(__file__).parent.parent.parent / "ssot" / "policy" / "design-policy.yaml"
    assert path.exists()
    with open(path) as f:
        policy = yaml.safe_load(f)
    assert policy["hand_edit_exports"] is False
    assert policy["figma_parity"] == "required"
