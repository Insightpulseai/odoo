"""Front Door origin health probe smoke tests.

Covers:
  - All origin groups have health probes defined
  - Health probe paths are reachable on live services
  - Probe intervals and timeouts are within Azure limits
  - TLS configuration is complete

Requires env vars for live checks (skipped without):
  FRONT_DOOR_ENDPOINT — Front Door endpoint (e.g. https://ipai-prod.z01.azurefd.net)

Run:  pytest infra/tests/smoke/test_front_door_origin_health.py -v
CI:   production_cutover gate
"""

import os

import pytest
import yaml

INFRA_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
FD_CONFIG_PATH = os.path.join(INFRA_ROOT, "azure", "front-door-routes.yaml")
FRONT_DOOR_ENDPOINT = os.environ.get("FRONT_DOOR_ENDPOINT", "")
SKIP_LIVE = not FRONT_DOOR_ENDPOINT


def _load_fd_config():
    """Load and return the Front Door routes YAML config."""
    if not os.path.exists(FD_CONFIG_PATH):
        pytest.skip(f"Front Door config not found: {FD_CONFIG_PATH}")
    with open(FD_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class TestFrontDoorConfig:
    """Static validation of Front Door routing configuration."""

    def test_config_loads_without_error(self):
        """Front Door YAML must parse without errors."""
        config = _load_fd_config()
        assert config is not None
        assert "origin_groups" in config
        assert "route_groups" in config

    def test_all_origin_groups_have_health_probes(self):
        """Every origin group must define a health_probe."""
        config = _load_fd_config()
        missing = []
        for group in config["origin_groups"]:
            if "health_probe" not in group:
                missing.append(group["name"])
        assert not missing, f"Origin groups missing health_probe: {missing}"

    def test_health_probe_intervals_valid(self):
        """Probe intervals must be between 5 and 120 seconds."""
        config = _load_fd_config()
        for group in config["origin_groups"]:
            probe = group.get("health_probe", {})
            interval = probe.get("interval_seconds", 30)
            assert 5 <= interval <= 120, (
                f"Origin group '{group['name']}' has invalid probe interval: {interval}s"
            )

    def test_health_probe_timeouts_valid(self):
        """Probe timeouts must be less than probe intervals."""
        config = _load_fd_config()
        for group in config["origin_groups"]:
            probe = group.get("health_probe", {})
            interval = probe.get("interval_seconds", 30)
            timeout = probe.get("timeout_seconds", 10)
            assert timeout < interval, (
                f"Origin group '{group['name']}': timeout ({timeout}s) must be < interval ({interval}s)"
            )

    def test_all_probes_use_https(self):
        """All health probes must use HTTPS protocol."""
        config = _load_fd_config()
        for group in config["origin_groups"]:
            probe = group.get("health_probe", {})
            protocol = probe.get("protocol", "Https")
            assert protocol == "Https", (
                f"Origin group '{group['name']}' probe uses {protocol}, must use Https"
            )

    def test_tls_minimum_version(self):
        """TLS minimum version must be 1.2 or higher."""
        config = _load_fd_config()
        tls = config.get("tls", {})
        min_version = tls.get("minimum_version", "TLS1_2")
        assert min_version in ("TLS1_2", "TLS1_3"), (
            f"TLS minimum version is {min_version}, must be TLS1_2 or TLS1_3"
        )

    def test_custom_domains_include_erp(self):
        """Custom domains must include erp.insightpulseai.com."""
        config = _load_fd_config()
        tls = config.get("tls", {})
        domains = tls.get("custom_domains", [])
        assert "erp.insightpulseai.com" in domains, (
            "erp.insightpulseai.com must be in custom_domains for TLS"
        )

    def test_route_groups_reference_valid_origin_groups(self):
        """Every route group must reference an existing origin group."""
        config = _load_fd_config()
        origin_names = {g["name"] for g in config["origin_groups"]}
        for route_group in config["route_groups"]:
            og = route_group["origin_group"]
            assert og in origin_names, (
                f"Route group '{route_group['name']}' references origin group '{og}' "
                f"which does not exist. Available: {origin_names}"
            )

    def test_waf_policy_is_prevention_mode(self):
        """WAF must be in Prevention mode (not Detection)."""
        config = _load_fd_config()
        waf = config.get("waf_policy", {})
        assert waf.get("mode") == "Prevention", (
            f"WAF mode is '{waf.get('mode')}', must be 'Prevention'"
        )

    def test_diagnostics_enabled(self):
        """Access logging and WAF logging must be enabled."""
        config = _load_fd_config()
        diag = config.get("diagnostics", {})
        assert diag.get("access_log") is True, "access_log must be enabled"
        assert diag.get("waf_log") is True, "waf_log must be enabled"
        assert diag.get("health_probe_log") is True, "health_probe_log must be enabled"


@pytest.mark.skipif(SKIP_LIVE, reason="FRONT_DOOR_ENDPOINT not set")
class TestFrontDoorLive:
    """Live health probe checks via Front Door."""

    def _get(self, hostname: str, path: str, timeout: float = 10.0):
        """GET via Front Door with Host header override."""
        import urllib.request
        import urllib.error

        url = f"{FRONT_DOOR_ENDPOINT.rstrip('/')}{path}"
        req = urllib.request.Request(url, headers={"Host": hostname})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code

    def test_erp_health_via_front_door(self):
        """GET /web/health via Front Door with erp.insightpulseai.com host."""
        status = self._get("erp.insightpulseai.com", "/web/health")
        assert status == 200, f"Expected 200, got {status}"

    def test_erp_login_via_front_door(self):
        """GET /web/login via Front Door returns 200."""
        status = self._get("erp.insightpulseai.com", "/web/login")
        assert status == 200, f"Expected 200, got {status}"
