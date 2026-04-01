"""Validate infra policy enforces Azure-native only."""
import yaml
from pathlib import Path


def test_infra_policy_azure_native():
    path = Path(__file__).parent.parent.parent / "ssot" / "policies" / "infra-policy.yaml"
    assert path.exists()
    with open(path) as f:
        policy = yaml.safe_load(f)
    assert policy["azure_native_only"] is True
    assert "cloudflare" in policy["deprecated"]
    assert "nginx" in policy["deprecated"]
