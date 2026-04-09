"""ACA health probe smoke tests — validates startup/readiness/liveness probes.

Covers:
  - /web/health returns HTTP 200 on odoo-web
  - Response body is valid (non-empty)
  - Response time within acceptable budget
  - Health probe paths match between ACA config and Front Door config

Requires env vars (skipped in CI pre-deploy):
  ODOO_WEB_URL — Base URL of the Odoo web container (e.g. https://erp.insightpulseai.com)

Run:  pytest infra/tests/smoke/test_aca_health_probes.py -v
CI:   azure_staging_revision gate
"""

import os
import time

import pytest
import yaml

# ---------------------------------------------------------------------------
# Skip when target URL is not available (CI pre-deploy, local dev)
# ---------------------------------------------------------------------------
ODOO_WEB_URL = os.environ.get("ODOO_WEB_URL", "")
SKIP_LIVE = not ODOO_WEB_URL

INFRA_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


# ===========================================================================
# Static: config consistency checks (always run)
# ===========================================================================
class TestHealthProbeConfigConsistency:
    """Verify health probe paths are consistent across ACA and Front Door config."""

    def test_aca_probe_path_is_web_health(self):
        """ACA bicep defines /web/health for all HTTP probes on odoo-web."""
        bicep_path = os.path.join(INFRA_ROOT, "azure", "modules", "aca-odoo-services.bicep")
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep file not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        # All three probe types must reference /web/health
        assert content.count("/web/health") >= 3, (
            "Expected at least 3 /web/health references (startup, readiness, liveness) "
            f"in aca-odoo-services.bicep, found {content.count('/web/health')}"
        )

    def test_front_door_probe_matches_aca(self):
        """Front Door origin health probe must use the same path as ACA probes."""
        fd_path = os.path.join(INFRA_ROOT, "azure", "front-door-routes.yaml")
        if not os.path.exists(fd_path):
            pytest.skip(f"Front Door routes not found: {fd_path}")

        with open(fd_path, "r") as f:
            fd_config = yaml.safe_load(f)

        # Find the odoo-web origin group
        odoo_group = None
        for group in fd_config.get("origin_groups", []):
            if group["name"] == "odoo-web":
                odoo_group = group
                break

        assert odoo_group is not None, "odoo-web origin group not found in front-door-routes.yaml"
        assert odoo_group["health_probe"]["path"] == "/web/health", (
            f"Front Door odoo-web health probe path is '{odoo_group['health_probe']['path']}', "
            "expected '/web/health' to match ACA probe"
        )

    def test_front_door_waf_bypasses_health_probe(self):
        """WAF must have an allow rule for the health probe path."""
        fd_path = os.path.join(INFRA_ROOT, "azure", "front-door-routes.yaml")
        if not os.path.exists(fd_path):
            pytest.skip(f"Front Door routes not found: {fd_path}")

        with open(fd_path, "r") as f:
            fd_config = yaml.safe_load(f)

        # Find WAF overrides for erp route group
        erp_overrides = None
        for override in fd_config.get("waf_overrides", []):
            if override.get("route_group") == "erp":
                erp_overrides = override
                break

        assert erp_overrides is not None, "No WAF overrides for 'erp' route group"

        health_bypass = None
        for rule in erp_overrides.get("rules", []):
            if "/web/health" in rule.get("paths", []):
                health_bypass = rule
                break

        assert health_bypass is not None, "No WAF bypass rule for /web/health"
        assert health_bypass["action"] == "allow", (
            f"WAF rule for /web/health has action '{health_bypass['action']}', expected 'allow'"
        )

    def test_all_origin_groups_have_health_probes(self):
        """Every origin group must define a health probe."""
        fd_path = os.path.join(INFRA_ROOT, "azure", "front-door-routes.yaml")
        if not os.path.exists(fd_path):
            pytest.skip(f"Front Door routes not found: {fd_path}")

        with open(fd_path, "r") as f:
            fd_config = yaml.safe_load(f)

        missing = []
        for group in fd_config.get("origin_groups", []):
            if "health_probe" not in group:
                missing.append(group["name"])

        assert not missing, f"Origin groups missing health_probe: {missing}"


# ===========================================================================
# Live: HTTP probe checks (staging/prod only)
# ===========================================================================
@pytest.mark.skipif(SKIP_LIVE, reason="ODOO_WEB_URL not set")
class TestLiveHealthProbes:
    """Live health probe checks against a running Odoo instance."""

    def _get(self, path: str, timeout: float = 10.0) -> "tuple[int, str, float]":
        """GET a URL and return (status_code, body, elapsed_seconds)."""
        import urllib.request
        import urllib.error

        url = f"{ODOO_WEB_URL.rstrip('/')}{path}"
        start = time.monotonic()
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                elapsed = time.monotonic() - start
                return resp.status, body, elapsed
        except urllib.error.HTTPError as e:
            elapsed = time.monotonic() - start
            return e.code, e.read().decode("utf-8", errors="replace"), elapsed
        except Exception as e:
            elapsed = time.monotonic() - start
            pytest.fail(f"Health probe request failed: {e} (elapsed: {elapsed:.2f}s)")

    def test_web_health_returns_200(self):
        """GET /web/health must return HTTP 200."""
        status, body, elapsed = self._get("/web/health")
        assert status == 200, f"/web/health returned {status}, expected 200"

    def test_web_health_response_not_empty(self):
        """Health probe response must have a non-empty body."""
        status, body, elapsed = self._get("/web/health")
        assert len(body.strip()) > 0, "/web/health returned empty body"

    def test_web_health_latency_under_5s(self):
        """Health probe must respond within 5 seconds."""
        status, body, elapsed = self._get("/web/health")
        assert elapsed < 5.0, f"/web/health took {elapsed:.2f}s, budget is 5s"

    def test_web_login_accessible(self):
        """GET /web/login must return HTTP 200 (basic page load)."""
        status, body, elapsed = self._get("/web/login")
        assert status == 200, f"/web/login returned {status}"
        assert "Odoo" in body or "odoo" in body.lower(), (
            "/web/login page does not contain 'Odoo' — may be an error page"
        )

    def test_web_health_multiple_calls_stable(self):
        """Health probe must be stable across 3 consecutive calls."""
        results = []
        for _ in range(3):
            status, body, elapsed = self._get("/web/health")
            results.append(status)
            time.sleep(0.5)

        assert all(s == 200 for s in results), (
            f"Health probe unstable: {results}"
        )
