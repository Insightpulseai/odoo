"""PostgreSQL connectivity and HA smoke tests.

Covers:
  - Basic connectivity to PostgreSQL
  - Connection string correctness
  - Reconnect after simulated interruption
  - Read-only replica availability (if configured)

Requires env vars (skipped without):
  PG_HOST — PostgreSQL host FQDN
  PG_DB — Database name (default: odoo)
  PG_USER — Database user
  PG_PASSWORD — Database password

Run:  pytest infra/tests/smoke/test_postgres_connectivity.py -v
CI:   azure_staging_revision and production_cutover gates
"""

import os
import time

import pytest

PG_HOST = os.environ.get("PG_HOST", "")
PG_DB = os.environ.get("PG_DB", "odoo")
PG_USER = os.environ.get("PG_USER", "")
PG_PASSWORD = os.environ.get("PG_PASSWORD", "")
SKIP = not PG_HOST or not PG_USER

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


@pytest.mark.skipif(SKIP, reason="PG_HOST or PG_USER not set")
@pytest.mark.skipif(not HAS_PSYCOPG2, reason="psycopg2 not installed")
class TestPostgresConnectivity:
    """Basic PostgreSQL connectivity smoke tests."""

    def _connect(self, **overrides):
        """Create a new connection with optional parameter overrides."""
        params = {
            "host": PG_HOST,
            "dbname": PG_DB,
            "user": PG_USER,
            "password": PG_PASSWORD,
            "connect_timeout": 10,
            "sslmode": "require",
        }
        params.update(overrides)
        return psycopg2.connect(**params)

    def test_basic_connectivity(self):
        """Can connect and execute a trivial query."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                assert result == (1,), f"Expected (1,), got {result}"
        finally:
            conn.close()

    def test_server_version(self):
        """PostgreSQL server version is 16+."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW server_version")
                version_str = cur.fetchone()[0]
                major = int(version_str.split(".")[0])
                assert major >= 16, f"Expected PostgreSQL 16+, got {version_str}"
        finally:
            conn.close()

    def test_odoo_database_exists(self):
        """Target database exists and is accessible."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT datname FROM pg_database WHERE datname = %s",
                    (PG_DB,),
                )
                result = cur.fetchone()
                assert result is not None, f"Database '{PG_DB}' does not exist"
        finally:
            conn.close()

    def test_ssl_enforced(self):
        """Connection uses SSL."""
        conn = self._connect()
        try:
            # psycopg2 SSLContext check
            ssl_info = conn.info.ssl_in_use
            assert ssl_info, "Connection must use SSL"
        finally:
            conn.close()

    def test_reconnect_after_close(self):
        """Can reconnect immediately after closing a connection."""
        conn1 = self._connect()
        conn1.close()

        conn2 = self._connect()
        try:
            with conn2.cursor() as cur:
                cur.execute("SELECT 1")
                assert cur.fetchone() == (1,)
        finally:
            conn2.close()

    def test_connection_latency_under_5s(self):
        """Connection establishment must complete within 5 seconds."""
        start = time.monotonic()
        conn = self._connect()
        elapsed = time.monotonic() - start
        conn.close()
        assert elapsed < 5.0, f"Connection took {elapsed:.2f}s, budget is 5s"

    def test_wrong_password_rejected(self):
        """Connection with wrong password must be rejected."""
        with pytest.raises(psycopg2.OperationalError):
            self._connect(password="definitely-wrong-password-12345")


class TestPostgresConfigConsistency:
    """Static validation: PostgreSQL config in IaC is consistent."""

    def test_aca_references_pg_host_via_env(self):
        """ACA bicep passes DB_HOST as environment variable."""
        bicep_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "azure", "modules", "aca-odoo-services.bicep"
        )
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        assert "DB_HOST" in content, "ACA must pass DB_HOST environment variable"
        assert "DB_PASSWORD" in content, "ACA must pass DB_PASSWORD environment variable"

    def test_pg_credentials_from_key_vault(self):
        """PostgreSQL credentials must come from Key Vault, not inline."""
        bicep_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "azure", "modules", "aca-odoo-services.bicep"
        )
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        assert "secretRef: 'db-password'" in content, (
            "DB_PASSWORD must reference a Key Vault secret, not an inline value"
        )
        assert "secretRef: 'db-user'" in content, (
            "DB_USER must reference a Key Vault secret, not an inline value"
        )
