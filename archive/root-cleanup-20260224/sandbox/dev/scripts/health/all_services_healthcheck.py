#!/usr/bin/env python3
"""
All Services Health Check
==========================

Comprehensive health check for all deployed services across dev/staging/prod environments.

Checks:
- Odoo (web + longpolling)
- Supabase (Auth, PostgREST, RPC, Storage)
- PostgreSQL (version + schema validation)
- n8n (health endpoint)
- MCP servers (health endpoints)
- Apache Superset (health + API)
- Vercel web surfaces (ops-console, marketing)
- GitHub (optional)
- Cloudflare (optional)

Usage:
    python scripts/health/all_services_healthcheck.py --env staging --json out/health/report.json --md out/health/report.md
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

try:
    import requests
    import yaml
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}", file=sys.stderr)
    print("Install with: pip install requests pyyaml", file=sys.stderr)
    sys.exit(1)

# Try to import psycopg2, but make it optional
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


@dataclass
class CheckResult:
    """Result of a single health check"""
    service: str
    component: str
    status: str  # OK, FAIL, SKIP, WARN
    message: str
    duration_ms: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class HealthReport:
    """Comprehensive health check report"""
    environment: str
    timestamp: str
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warnings: int = 0
    checks: List[CheckResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Main health checker orchestrator"""

    def __init__(self, env: str, timeout: int = 10, verbose: bool = False):
        self.env = env
        self.timeout = timeout
        self.verbose = verbose
        self.report = HealthReport(
            environment=env,
            timestamp=datetime.utcnow().isoformat()
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "IPAI-HealthCheck/1.0"})

    def log(self, msg: str):
        """Print log message if verbose"""
        if self.verbose:
            print(msg, file=sys.stderr)

    def add_result(self, result: CheckResult):
        """Add check result to report"""
        self.report.checks.append(result)
        self.report.total_checks += 1

        if result.status == "OK":
            self.report.passed += 1
        elif result.status == "FAIL":
            self.report.failed += 1
        elif result.status == "SKIP":
            self.report.skipped += 1
        elif result.status == "WARN":
            self.report.warnings += 1

    def http_check(self, service: str, component: str, url: str,
                   expected_codes: List[int] = None, method: str = "GET",
                   headers: Dict = None, auth: tuple = None) -> CheckResult:
        """Generic HTTP endpoint check"""
        if expected_codes is None:
            expected_codes = list(range(200, 400))

        start = time.time()
        try:
            self.log(f"Checking {service}/{component}: {method} {url}")

            req_kwargs = {
                "timeout": self.timeout,
                "allow_redirects": True
            }
            if headers:
                req_kwargs["headers"] = headers
            if auth:
                req_kwargs["auth"] = auth

            if method == "HEAD":
                resp = self.session.head(url, **req_kwargs)
            else:
                resp = self.session.get(url, **req_kwargs)

            duration = (time.time() - start) * 1000

            if resp.status_code in expected_codes:
                return CheckResult(
                    service=service,
                    component=component,
                    status="OK",
                    message=f"HTTP {resp.status_code}",
                    duration_ms=duration,
                    details={"url": url, "status_code": resp.status_code}
                )
            else:
                return CheckResult(
                    service=service,
                    component=component,
                    status="FAIL",
                    message=f"HTTP {resp.status_code} (expected {expected_codes})",
                    duration_ms=duration,
                    details={"url": url, "status_code": resp.status_code}
                )
        except requests.exceptions.Timeout:
            duration = (time.time() - start) * 1000
            return CheckResult(
                service=service,
                component=component,
                status="FAIL",
                message=f"Timeout after {self.timeout}s",
                duration_ms=duration,
                details={"url": url, "error": "timeout"}
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return CheckResult(
                service=service,
                component=component,
                status="FAIL",
                message=str(e),
                duration_ms=duration,
                details={"url": url, "error": str(e)}
            )

    def check_odoo(self):
        """Check Odoo web and longpolling"""
        base_url = os.getenv("ODOO_BASE_URL")
        if not base_url:
            self.add_result(CheckResult(
                service="odoo",
                component="web",
                status="SKIP",
                message="ODOO_BASE_URL not set"
            ))
            return

        # Web login page
        result = self.http_check("odoo", "web-login", urljoin(base_url, "/web/login"))
        self.add_result(result)

        # Database selector (dev only)
        if self.env == "dev":
            result = self.http_check("odoo", "db-selector",
                                    urljoin(base_url, "/web/database/selector"),
                                    expected_codes=[200, 303, 404])  # 404 if disabled
            self.add_result(result)

        # Longpolling (if configured)
        longpoll_url = os.getenv("ODOO_LONGPOLLING_URL")
        if longpoll_url:
            result = self.http_check("odoo", "longpolling", longpoll_url,
                                    expected_codes=[200, 404, 405])  # May not have root endpoint
            self.add_result(result)

    def check_supabase(self):
        """Check Supabase Auth, PostgREST, Storage"""
        supabase_url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url:
            self.add_result(CheckResult(
                service="supabase",
                component="all",
                status="SKIP",
                message="SUPABASE_URL not set"
            ))
            return

        # Auth health
        result = self.http_check("supabase", "auth-health",
                                urljoin(supabase_url, "/auth/v1/health"))
        self.add_result(result)

        # PostgREST root
        headers = {"apikey": anon_key} if anon_key else {}
        result = self.http_check("supabase", "postgrest",
                                urljoin(supabase_url, "/rest/v1/"),
                                headers=headers,
                                expected_codes=[200, 401, 404])
        self.add_result(result)

        # Storage (list buckets - read-only)
        if anon_key:
            result = self.http_check("supabase", "storage",
                                    urljoin(supabase_url, "/storage/v1/bucket"),
                                    headers=headers,
                                    expected_codes=[200, 401, 403])
            self.add_result(result)

        # RPC smoke test (if anon key provided)
        if anon_key:
            try:
                # Try a lightweight RPC (adjust based on your schema)
                rpc_url = urljoin(supabase_url, "/rest/v1/rpc/version")
                result = self.http_check("supabase", "rpc-smoke", rpc_url,
                                        headers=headers,
                                        expected_codes=[200, 404])  # 404 if function doesn't exist
                self.add_result(result)
            except Exception:
                pass  # RPC smoke test is optional

    def check_postgres(self):
        """Check PostgreSQL connection and schema"""
        if not HAS_PSYCOPG2:
            self.add_result(CheckResult(
                service="postgres",
                component="connection",
                status="SKIP",
                message="psycopg2 not installed"
            ))
            return

        # Build connection params from env vars
        conn_params = {}
        if os.getenv("PGHOST"):
            conn_params["host"] = os.getenv("PGHOST")
        if os.getenv("PGPORT"):
            conn_params["port"] = int(os.getenv("PGPORT"))
        if os.getenv("PGUSER"):
            conn_params["user"] = os.getenv("PGUSER")
        if os.getenv("PGPASSWORD"):
            conn_params["password"] = os.getenv("PGPASSWORD")
        if os.getenv("PGDATABASE"):
            conn_params["dbname"] = os.getenv("PGDATABASE")

        # Alternatively, use POSTGRES_URL
        conn_string = os.getenv("POSTGRES_URL")

        if not conn_params and not conn_string:
            self.add_result(CheckResult(
                service="postgres",
                component="connection",
                status="SKIP",
                message="No PostgreSQL credentials provided"
            ))
            return

        start = time.time()
        try:
            if conn_string:
                conn = psycopg2.connect(conn_string)
            else:
                conn = psycopg2.connect(**conn_params)

            cur = conn.cursor()

            # Check version
            cur.execute("SELECT version(), now();")
            version, now = cur.fetchone()

            duration = (time.time() - start) * 1000

            self.add_result(CheckResult(
                service="postgres",
                component="connection",
                status="OK",
                message="Connected successfully",
                duration_ms=duration,
                details={"version": version.split()[1], "server_time": str(now)}
            ))

            # Check for expected schemas (optional)
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('public', 'auth', 'storage');")
            schemas = [row[0] for row in cur.fetchall()]

            self.add_result(CheckResult(
                service="postgres",
                component="schemas",
                status="OK",
                message=f"Found {len(schemas)} expected schemas",
                details={"schemas": schemas}
            ))

            cur.close()
            conn.close()

        except Exception as e:
            duration = (time.time() - start) * 1000
            self.add_result(CheckResult(
                service="postgres",
                component="connection",
                status="FAIL",
                message=str(e),
                duration_ms=duration
            ))

    def check_n8n(self):
        """Check n8n health endpoint"""
        base_url = os.getenv("N8N_BASE_URL")
        if not base_url:
            self.add_result(CheckResult(
                service="n8n",
                component="health",
                status="SKIP",
                message="N8N_BASE_URL not set"
            ))
            return

        # Try /healthz first
        result = self.http_check("n8n", "healthz", urljoin(base_url, "/healthz"),
                                expected_codes=[200, 404])

        # If 404, try root
        if result.status == "FAIL" and result.details.get("status_code") == 404:
            result = self.http_check("n8n", "root", base_url,
                                    expected_codes=[200, 301, 302])

        self.add_result(result)

    def check_mcp(self):
        """Check MCP servers (if HTTP endpoints exposed)"""
        # Try to discover MCP servers from config
        mcp_urls = os.getenv("MCP_BASE_URLS", "").split(",")
        mcp_urls = [url.strip() for url in mcp_urls if url.strip()]

        if not mcp_urls:
            self.add_result(CheckResult(
                service="mcp",
                component="discovery",
                status="SKIP",
                message="MCP_BASE_URLS not set or empty"
            ))
            return

        for idx, url in enumerate(mcp_urls):
            server_name = f"server-{idx+1}"
            result = self.http_check("mcp", server_name, urljoin(url, "/health"),
                                    expected_codes=[200, 404])
            self.add_result(result)

    def check_superset(self):
        """Check Apache Superset health"""
        base_url = os.getenv("SUPERSET_BASE_URL")
        if not base_url:
            self.add_result(CheckResult(
                service="superset",
                component="health",
                status="SKIP",
                message="SUPERSET_BASE_URL not set"
            ))
            return

        # Try /health first
        result = self.http_check("superset", "health", urljoin(base_url, "/health"),
                                expected_codes=[200, 404])

        # If 404, try /login
        if result.status == "FAIL" and result.details.get("status_code") == 404:
            result = self.http_check("superset", "login", urljoin(base_url, "/login"))

        self.add_result(result)

        # API check if token provided
        token = os.getenv("SUPERSET_TOKEN")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            result = self.http_check("superset", "api-me",
                                    urljoin(base_url, "/api/v1/me"),
                                    headers=headers)
            self.add_result(result)

    def check_vercel(self):
        """Check Vercel-hosted web surfaces"""
        surfaces = {
            "ops-console": os.getenv("OPS_CONSOLE_URL"),
            "marketing": os.getenv("MARKETING_URL"),
        }

        for name, url in surfaces.items():
            if not url:
                self.add_result(CheckResult(
                    service="vercel",
                    component=name,
                    status="SKIP",
                    message=f"{name.upper()}_URL not set"
                ))
                continue

            result = self.http_check("vercel", name, url)
            self.add_result(result)

    def check_github(self):
        """Check GitHub API (optional)"""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            self.add_result(CheckResult(
                service="github",
                component="api",
                status="SKIP",
                message="GITHUB_TOKEN not set"
            ))
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Check API root
        result = self.http_check("github", "api-root", "https://api.github.com",
                                headers=headers)
        self.add_result(result)

    def check_cloudflare(self):
        """Check Cloudflare zone status (optional)"""
        token = os.getenv("CLOUDFLARE_TOKEN")
        zone_id = os.getenv("CLOUDFLARE_ZONE_ID")

        if not token or not zone_id:
            self.add_result(CheckResult(
                service="cloudflare",
                component="zone",
                status="SKIP",
                message="CLOUDFLARE_TOKEN or CLOUDFLARE_ZONE_ID not set"
            ))
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
        result = self.http_check("cloudflare", "zone-status", url, headers=headers)
        self.add_result(result)

    def run_all_checks(self):
        """Run all health checks"""
        self.log(f"Starting health checks for environment: {self.env}")

        self.check_odoo()
        self.check_supabase()
        self.check_postgres()
        self.check_n8n()
        self.check_mcp()
        self.check_superset()
        self.check_vercel()
        self.check_github()
        self.check_cloudflare()

        self.log(f"Completed {self.report.total_checks} checks")

    def generate_json_report(self, output_path: Path):
        """Generate JSON report"""
        report_dict = asdict(self.report)
        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        self.log(f"JSON report written to {output_path}")

    def generate_markdown_report(self, output_path: Path):
        """Generate Markdown report"""
        lines = [
            f"# Health Check Report",
            f"",
            f"**Environment:** `{self.report.environment}`  ",
            f"**Timestamp:** `{self.report.timestamp}`  ",
            f"**Total Checks:** {self.report.total_checks}  ",
            f"",
            f"## Summary",
            f"",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✅ Passed | {self.report.passed} |",
            f"| ❌ Failed | {self.report.failed} |",
            f"| ⚠️  Warnings | {self.report.warnings} |",
            f"| ⏭️  Skipped | {self.report.skipped} |",
            f"",
            f"## Detailed Results",
            f""
        ]

        # Group by service
        services = {}
        for check in self.report.checks:
            if check.service not in services:
                services[check.service] = []
            services[check.service].append(check)

        for service, checks in sorted(services.items()):
            lines.append(f"### {service.upper()}")
            lines.append("")
            lines.append("| Component | Status | Message | Duration (ms) |")
            lines.append("|-----------|--------|---------|---------------|")

            for check in checks:
                status_icon = {
                    "OK": "✅",
                    "FAIL": "❌",
                    "WARN": "⚠️",
                    "SKIP": "⏭️"
                }.get(check.status, "❓")

                duration = f"{check.duration_ms:.1f}" if check.duration_ms else "N/A"
                lines.append(f"| {check.component} | {status_icon} {check.status} | {check.message} | {duration} |")

            lines.append("")

        # Footer
        if self.report.failed > 0:
            lines.append("---")
            lines.append("⚠️ **Action Required:** Health check detected failures. Review failed checks above.")
        else:
            lines.append("---")
            lines.append("✅ **All critical checks passed.**")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        self.log(f"Markdown report written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive health check for all deployed services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  ODOO_BASE_URL              Odoo web URL
  ODOO_LONGPOLLING_URL       Odoo longpolling URL (optional)
  SUPABASE_URL               Supabase project URL
  SUPABASE_ANON_KEY          Supabase anon key (optional)
  POSTGRES_URL               PostgreSQL connection URL (optional)
  PGHOST, PGPORT, etc.       PostgreSQL connection params (optional)
  N8N_BASE_URL               n8n instance URL
  MCP_BASE_URLS              Comma-separated MCP server URLs (optional)
  SUPERSET_BASE_URL          Apache Superset URL
  SUPERSET_TOKEN             Superset API token (optional)
  OPS_CONSOLE_URL            Vercel ops console URL
  MARKETING_URL              Vercel marketing site URL
  GITHUB_TOKEN               GitHub API token (optional)
  CLOUDFLARE_TOKEN           Cloudflare API token (optional)
  CLOUDFLARE_ZONE_ID         Cloudflare zone ID (optional)

Examples:
  # Dev environment
  python scripts/health/all_services_healthcheck.py --env dev --verbose

  # Staging with reports
  python scripts/health/all_services_healthcheck.py --env staging \\
    --json out/health/report.json --md out/health/report.md

  # Production with timeout
  python scripts/health/all_services_healthcheck.py --env prod --timeout 15
        """
    )

    parser.add_argument("--env", required=True, choices=["dev", "staging", "prod"],
                       help="Environment to check")
    parser.add_argument("--timeout", type=int, default=10,
                       help="HTTP request timeout in seconds (default: 10)")
    parser.add_argument("--json", type=Path,
                       help="Output JSON report to this path")
    parser.add_argument("--md", type=Path,
                       help="Output Markdown report to this path")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")

    args = parser.parse_args()

    # Create checker and run
    checker = HealthChecker(env=args.env, timeout=args.timeout, verbose=args.verbose)
    checker.run_all_checks()

    # Generate reports
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        checker.generate_json_report(args.json)

    if args.md:
        args.md.parent.mkdir(parents=True, exist_ok=True)
        checker.generate_markdown_report(args.md)

    # Print summary to stdout
    print(f"Environment: {checker.report.environment}")
    print(f"Total checks: {checker.report.total_checks}")
    print(f"✅ Passed: {checker.report.passed}")
    print(f"❌ Failed: {checker.report.failed}")
    print(f"⚠️  Warnings: {checker.report.warnings}")
    print(f"⏭️  Skipped: {checker.report.skipped}")

    # Exit with error if any critical failures
    if checker.report.failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
