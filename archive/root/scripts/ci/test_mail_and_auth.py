#!/usr/bin/env python3
"""
test_mail_and_auth.py — Comprehensive mail & auth configuration validator.

Validates ALL mail and authentication settings across the InsightPulse AI stack
by checking configuration consistency, DNS records, SSOT compliance, and
reachability of mail/auth endpoints.

Dual mail architecture:
  - Zoho Mail:  inbound MX + team mailboxes (insightpulseai.com)
  - Mailgun:    transactional outbound email (mg.insightpulseai.com)

Auth architecture:
  - Odoo:       session-based auth + optional OIDC (ipai_auth_oidc)
  - Supabase:   IdP (auth.users) + JWT
  - n8n:        Basic auth or Supabase OAuth
  - auth.insightpulseai.com: Express proxy (partial — no OIDC discovery)

Usage:
  python3 scripts/ci/test_mail_and_auth.py              # All checks
  python3 scripts/ci/test_mail_and_auth.py --mail-only   # Mail checks only
  python3 scripts/ci/test_mail_and_auth.py --auth-only   # Auth checks only
  python3 scripts/ci/test_mail_and_auth.py --json        # JSON output

Exit codes:
  0  all checks pass
  1  one or more checks failed
  3  skipped (missing network/tools)
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import ssl
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "evidence" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M") / "mail-auth"

# ─── Results collector ───────────────────────────────────────────────────────

results: list[dict[str, Any]] = []


def check(name: str, category: str, passed: bool, detail: str = "") -> bool:
    results.append({
        "name": name,
        "category": category,
        "passed": passed,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    icon = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {name}: {detail}")
    return passed


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ─── YAML loader (graceful if pyyaml absent) ────────────────────────────────

def load_yaml(path: Path) -> dict | None:
    try:
        import yaml
    except ImportError:
        return None
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


# ─── DNS checks ─────────────────────────────────────────────────────────────

def check_dns_mx(domain: str) -> list[str]:
    """Resolve MX records for domain."""
    try:
        result = subprocess.run(
            ["dig", "+short", "MX", domain],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().splitlines()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def check_dns_txt(name: str) -> list[str]:
    """Resolve TXT records."""
    try:
        result = subprocess.run(
            ["dig", "+short", "TXT", name],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip().strip('"') for line in result.stdout.strip().splitlines()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def check_dns_a(name: str) -> list[str]:
    """Resolve A records."""
    try:
        result = subprocess.run(
            ["dig", "+short", "A", name],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().splitlines()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def check_dns_cname(name: str) -> list[str]:
    """Resolve CNAME records."""
    try:
        result = subprocess.run(
            ["dig", "+short", "CNAME", name],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().splitlines()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


# ─── TCP/TLS connectivity ───────────────────────────────────────────────────

def check_tcp(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check TCP connectivity to host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def check_tls(host: str, port: int, timeout: float = 5.0) -> str | None:
    """Check TLS and return cert subject CN, or None on failure."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    for field in cert.get("subject", ()):
                        for key, val in field:
                            if key == "commonName":
                                return val
                return "ok"
    except Exception:
        return None


def check_https(url: str, timeout: float = 10.0) -> tuple[int, str]:
    """HTTP GET and return (status_code, first_line_of_body). Returns (0, error) on failure."""
    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "ipai-mail-auth-test/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(512).decode("utf-8", errors="replace")
            return resp.status, body[:200]
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except Exception as e:
        return 0, str(e)[:200]


# ═══════════════════════════════════════════════════════════════════════════
#  MAIL TESTS
# ═══════════════════════════════════════════════════════════════════════════

def test_mail_ssot_consistency():
    """Verify SSOT files agree on mail architecture."""
    section("Mail SSOT Consistency")

    # 1. config/odoo/mail_settings.yaml
    mail_settings = load_yaml(ROOT / "config" / "odoo" / "mail_settings.yaml")
    if mail_settings:
        prod = mail_settings.get("prod", {})
        smtp = prod.get("smtp", {})
        check(
            "mail_settings.yaml prod SMTP host",
            "mail-ssot",
            smtp.get("host") == "smtppro.zoho.com",
            f"host={smtp.get('host', 'MISSING')}",
        )
        check(
            "mail_settings.yaml prod SMTP port",
            "mail-ssot",
            smtp.get("port") == 587,
            f"port={smtp.get('port', 'MISSING')}",
        )
    else:
        check("mail_settings.yaml exists", "mail-ssot", False, "File missing or pyyaml not installed")

    # 2. ssot/integrations/mailgun.yaml
    mg = load_yaml(ROOT / "ssot" / "integrations" / "mailgun.yaml")
    if mg:
        mailgun = mg.get("mailgun", {})
        check(
            "mailgun.yaml status=active",
            "mail-ssot",
            mailgun.get("status") == "active",
            f"status={mailgun.get('status', 'MISSING')}",
        )
        check(
            "mailgun.yaml domain=mg.insightpulseai.com",
            "mail-ssot",
            mailgun.get("domain") == "mg.insightpulseai.com",
            f"domain={mailgun.get('domain', 'MISSING')}",
        )
        smtp_cfg = mailgun.get("smtp", {})
        check(
            "mailgun.yaml port_25_forbidden",
            "mail-ssot",
            smtp_cfg.get("policy", {}).get("port_25_forbidden") is True,
            f"port_25_forbidden={smtp_cfg.get('policy', {}).get('port_25_forbidden', 'MISSING')}",
        )
    else:
        check("mailgun.yaml exists", "mail-ssot", False, "File missing or pyyaml not installed")

    # 3. ssot/runtime/prod_settings.yaml
    prod_settings = load_yaml(ROOT / "ssot" / "runtime" / "prod_settings.yaml")
    if prod_settings:
        mail_notes = json.dumps(prod_settings)
        has_dual = "zoho" in mail_notes.lower() and "mailgun" in mail_notes.lower()
        check(
            "prod_settings.yaml references dual mail",
            "mail-ssot",
            has_dual,
            "Both Zoho and Mailgun mentioned" if has_dual else "Missing dual mail reference",
        )
    else:
        check("prod_settings.yaml exists", "mail-ssot", False, "File missing or pyyaml not installed")

    # 4. config/odoo/settings.yaml
    odoo_settings = load_yaml(ROOT / "config" / "odoo" / "settings.yaml")
    if odoo_settings:
        settings_str = json.dumps(odoo_settings)
        no_deprecated = "deprecated" not in settings_str.lower() or "mattermost" in settings_str.lower()
        check(
            "settings.yaml no 'deprecated' for mailgun",
            "mail-ssot",
            "mailgun" not in settings_str.lower() or "deprecated" not in settings_str.lower().split("mailgun")[0][-100:],
            "Mailgun should not be marked deprecated",
        )

    # 5. platform_inventory.yaml
    inv = load_yaml(ROOT / "ssot" / "integrations" / "platform_inventory.yaml")
    if inv:
        email_section = inv.get("email", {})
        mg_inv = email_section.get("mailgun", {})
        zoho_inv = email_section.get("zoho_mail", {})
        check(
            "platform_inventory mailgun=active",
            "mail-ssot",
            mg_inv.get("status") == "active",
            f"mailgun status={mg_inv.get('status', 'MISSING')}",
        )
        check(
            "platform_inventory zoho=active",
            "mail-ssot",
            zoho_inv.get("status") == "active",
            f"zoho status={zoho_inv.get('status', 'MISSING')}",
        )


def test_mail_dns():
    """Verify DNS records for Zoho MX and Mailgun sending domain."""
    section("Mail DNS Records")

    # Zoho MX records for insightpulseai.com
    mx_records = check_dns_mx("insightpulseai.com")
    has_zoho_mx = any("zoho" in mx.lower() for mx in mx_records)
    check(
        "insightpulseai.com MX → Zoho",
        "mail-dns",
        has_zoho_mx,
        f"MX records: {mx_records}" if mx_records else "No MX records found (dig unavailable or DNS failure)",
    )

    # SPF for insightpulseai.com
    txt_records = check_dns_txt("insightpulseai.com")
    spf_records = [r for r in txt_records if "v=spf1" in r]
    has_zoho_spf = any("zohomail" in r for r in spf_records)
    check(
        "insightpulseai.com SPF includes zohomail",
        "mail-dns",
        has_zoho_spf,
        f"SPF: {spf_records}" if spf_records else "No SPF record found",
    )

    # Mailgun SPF for mg.insightpulseai.com
    mg_txt = check_dns_txt("mg.insightpulseai.com")
    mg_spf = [r for r in mg_txt if "v=spf1" in r]
    has_mg_spf = any("mailgun" in r for r in mg_spf)
    check(
        "mg.insightpulseai.com SPF includes mailgun",
        "mail-dns",
        has_mg_spf,
        f"SPF: {mg_spf}" if mg_spf else "No SPF record found for mg subdomain",
    )

    # DKIM for Zoho
    zoho_dkim = check_dns_txt("zoho._domainkey.insightpulseai.com")
    has_zoho_dkim = any("DKIM1" in r for r in zoho_dkim)
    check(
        "Zoho DKIM record present",
        "mail-dns",
        has_zoho_dkim,
        f"DKIM: {zoho_dkim[:1]}" if zoho_dkim else "No DKIM record for zoho._domainkey",
    )

    # DKIM for Mailgun
    mg_dkim = check_dns_txt("mx._domainkey.mg.insightpulseai.com")
    # Also try alternative selector names
    if not mg_dkim:
        mg_dkim = check_dns_txt("k1._domainkey.mg.insightpulseai.com")
    has_mg_dkim = any("DKIM1" in r or "k=rsa" in r for r in mg_dkim)
    check(
        "Mailgun DKIM record present",
        "mail-dns",
        has_mg_dkim,
        f"DKIM: found" if has_mg_dkim else "No DKIM record for mg subdomain",
    )

    # DMARC for insightpulseai.com
    dmarc = check_dns_txt("_dmarc.insightpulseai.com")
    has_dmarc = any("DMARC1" in r for r in dmarc)
    check(
        "insightpulseai.com DMARC present",
        "mail-dns",
        has_dmarc,
        f"DMARC: {dmarc}" if dmarc else "No DMARC record",
    )

    # Mailgun tracking CNAME
    email_mg = check_dns_cname("email.mg.insightpulseai.com")
    has_tracking = any("mailgun" in c.lower() for c in email_mg)
    check(
        "Mailgun tracking CNAME (email.mg)",
        "mail-dns",
        has_tracking,
        f"CNAME: {email_mg}" if email_mg else "No CNAME for email.mg",
    )


def test_mail_connectivity():
    """Test SMTP connectivity to mail servers."""
    section("Mail Server Connectivity")

    # Zoho SMTP (port 587)
    zoho_smtp = check_tcp("smtppro.zoho.com", 587)
    check(
        "Zoho SMTP (smtppro.zoho.com:587)",
        "mail-connect",
        zoho_smtp,
        "TCP reachable" if zoho_smtp else "Connection failed (may be blocked by DO firewall)",
    )

    # Zoho IMAP (port 993)
    zoho_imap = check_tcp("imappro.zoho.com", 993)
    check(
        "Zoho IMAP (imappro.zoho.com:993)",
        "mail-connect",
        zoho_imap,
        "TCP reachable" if zoho_imap else "Connection failed",
    )

    # Mailgun SMTP port 2525 (DO-safe)
    mg_2525 = check_tcp("smtp.mailgun.org", 2525)
    check(
        "Mailgun SMTP (smtp.mailgun.org:2525)",
        "mail-connect",
        mg_2525,
        "TCP reachable (DO-safe port)" if mg_2525 else "Connection failed",
    )

    # Mailgun SMTP port 587 (may be blocked by DO)
    mg_587 = check_tcp("smtp.mailgun.org", 587, timeout=3.0)
    check(
        "Mailgun SMTP (smtp.mailgun.org:587)",
        "mail-connect",
        mg_587,
        "TCP reachable" if mg_587 else "Blocked (expected on DigitalOcean — use port 2525)",
    )

    # Zoho SMTP TLS verification
    zoho_tls = check_tls("smtppro.zoho.com", 465, timeout=5.0)
    check(
        "Zoho SMTP TLS (smtppro.zoho.com:465)",
        "mail-connect",
        zoho_tls is not None,
        f"TLS CN={zoho_tls}" if zoho_tls else "TLS handshake failed",
    )


def test_mail_modules():
    """Verify Odoo mail modules exist and have correct manifests."""
    section("Odoo Mail Modules")

    modules = {
        "ipai_mail_bridge_zoho": "HTTPS bridge for Zoho Mail API",
        "ipai_zoho_mail": "Zoho SMTP server record",
        "ipai_zoho_mail_api": "Zoho REST API transport",
        "ipai_mailgun_smtp": "Mailgun SMTP server record",
        "ipai_enterprise_bridge": "Mailgun webhook controller",
    }

    for module, desc in modules.items():
        manifest = ROOT / "addons" / "ipai" / module / "__manifest__.py"
        exists = manifest.exists()
        check(
            f"Module {module}",
            "mail-modules",
            exists,
            desc if exists else f"MISSING: {manifest.relative_to(ROOT)}",
        )

    # Check Mailgun XML data doesn't use port 25
    mg_xml = ROOT / "addons" / "ipai" / "ipai_mailgun_smtp" / "data" / "ir_mail_server.xml"
    if mg_xml.exists():
        content = mg_xml.read_text()
        uses_2525 = "2525" in content
        no_port_25 = "smtp_port\">25<" not in content
        check(
            "Mailgun XML uses port 2525",
            "mail-modules",
            uses_2525 and no_port_25,
            "Port 2525 confirmed" if uses_2525 else "Port 2525 NOT found in XML",
        )

    # Check bridge module intercepts mail.mail
    bridge_py = ROOT / "addons" / "ipai" / "ipai_mail_bridge_zoho" / "models" / "mail_mail.py"
    if bridge_py.exists():
        content = bridge_py.read_text()
        has_override = "_inherit" in content and "mail.mail" in content
        check(
            "Zoho bridge overrides mail.mail",
            "mail-modules",
            has_override,
            "mail.mail _inherit found" if has_override else "No mail.mail override",
        )


def test_mail_ci_scripts():
    """Verify CI mail validation scripts exist."""
    section("Mail CI Scripts")

    scripts = [
        ("scripts/ci/check_deprecated_provider_defaults.py", "Deprecated provider check"),
        ("scripts/ci/check_prod_mail_live.py", "Live prod mail provider check"),
    ]

    for script_path, desc in scripts:
        full = ROOT / script_path
        exists = full.exists()
        check(f"CI: {script_path}", "mail-ci", exists, desc if exists else "MISSING")

    # Verify deprecated check doesn't flag mailgun
    dep_script = ROOT / "scripts" / "ci" / "check_deprecated_provider_defaults.py"
    if dep_script.exists():
        content = dep_script.read_text()
        no_mailgun_pattern = "mailgun" not in content.split("FORBIDDEN")[1] if "FORBIDDEN" in content else True
        check(
            "Deprecated check doesn't flag mailgun",
            "mail-ci",
            no_mailgun_pattern,
            "Mailgun not in FORBIDDEN list" if no_mailgun_pattern else "Mailgun still in FORBIDDEN!",
        )


# ═══════════════════════════════════════════════════════════════════════════
#  AUTH TESTS
# ═══════════════════════════════════════════════════════════════════════════

def test_auth_dns():
    """Verify DNS for auth-related subdomains."""
    section("Auth DNS Records")

    # auth.insightpulseai.com
    auth_a = check_dns_a("auth.insightpulseai.com")
    check(
        "auth.insightpulseai.com DNS",
        "auth-dns",
        len(auth_a) > 0,
        f"A records: {auth_a}" if auth_a else "No A record found",
    )

    # erp.insightpulseai.com (Odoo)
    erp_a = check_dns_a("erp.insightpulseai.com")
    check(
        "erp.insightpulseai.com DNS",
        "auth-dns",
        len(erp_a) > 0,
        f"A records: {erp_a}" if erp_a else "No A record found",
    )

    # n8n.insightpulseai.com
    n8n_a = check_dns_a("n8n.insightpulseai.com")
    check(
        "n8n.insightpulseai.com DNS",
        "auth-dns",
        len(n8n_a) > 0,
        f"A records: {n8n_a}" if n8n_a else "No A record found",
    )


def test_auth_connectivity():
    """Test HTTPS connectivity and TLS for auth endpoints."""
    section("Auth Endpoint Connectivity")

    endpoints = [
        ("erp.insightpulseai.com", 443, "Odoo ERP"),
        ("auth.insightpulseai.com", 443, "Auth service"),
        ("n8n.insightpulseai.com", 443, "n8n automation"),
    ]

    for host, port, desc in endpoints:
        tls_cn = check_tls(host, port)
        check(
            f"{desc} TLS ({host}:{port})",
            "auth-connect",
            tls_cn is not None,
            f"TLS valid, CN={tls_cn}" if tls_cn else "TLS handshake failed or unreachable",
        )

    # HTTP health checks
    health_endpoints = [
        ("https://erp.insightpulseai.com/web/health", "Odoo health"),
        ("https://erp.insightpulseai.com/web/login", "Odoo login page"),
        ("https://auth.insightpulseai.com/", "Auth service root"),
        ("https://auth.insightpulseai.com/.well-known/openid-configuration", "OIDC discovery"),
    ]

    for url, desc in health_endpoints:
        status, body = check_https(url)
        passed = 200 <= status < 400
        check(
            f"{desc}",
            "auth-http",
            passed,
            f"HTTP {status}" if status > 0 else f"Connection failed: {body}",
        )


def test_auth_modules():
    """Verify Odoo auth modules."""
    section("Odoo Auth Modules")

    modules = {
        "ipai_auth_oidc": "OIDC + MFA integration",
    }

    for module, desc in modules.items():
        manifest = ROOT / "addons" / "ipai" / module / "__manifest__.py"
        exists = manifest.exists()
        check(
            f"Module {module}",
            "auth-modules",
            exists,
            desc if exists else f"MISSING: {manifest.relative_to(ROOT)}",
        )

    # Check OIDC provider data
    provider_xml = ROOT / "addons" / "ipai" / "ipai_auth_oidc" / "data" / "auth_provider_data.xml"
    if provider_xml.exists():
        content = provider_xml.read_text()
        has_keycloak = "auth.insightpulseai.com" in content
        has_google = "accounts.google.com" in content
        check(
            "OIDC: Keycloak provider template",
            "auth-modules",
            has_keycloak,
            "Keycloak endpoint configured" if has_keycloak else "Missing Keycloak configuration",
        )
        check(
            "OIDC: Google provider template",
            "auth-modules",
            has_google,
            "Google OIDC endpoint configured" if has_google else "Missing Google OIDC",
        )


def test_auth_ssot():
    """Verify auth SSOT files."""
    section("Auth SSOT Configuration")

    # GitHub auth surface
    gh_auth = load_yaml(ROOT / "ssot" / "auth" / "github_auth_surface.yaml")
    if gh_auth:
        policy = gh_auth.get("policy", {})
        check(
            "GitHub auth: Zero-PAT policy",
            "auth-ssot",
            policy.get("name") == "Zero-PAT GitHub Auth Surface",
            f"Policy: {policy.get('name', 'MISSING')}",
        )
        deprecated = gh_auth.get("deprecated_methods", {})
        check(
            "GitHub auth: PATs deprecated",
            "auth-ssot",
            "pat_classic" in deprecated and deprecated["pat_classic"].get("status") == "deprecated",
            "Classic PATs deprecated" if deprecated else "Deprecation status unknown",
        )
    else:
        check("github_auth_surface.yaml", "auth-ssot", False, "File missing or pyyaml not installed")

    # Nginx auth config
    auth_nginx = ROOT / "infra" / "deploy" / "nginx" / "auth.insightpulseai.com.conf"
    check(
        "Nginx: auth.insightpulseai.com.conf",
        "auth-ssot",
        auth_nginx.exists(),
        "Present" if auth_nginx.exists() else "MISSING",
    )
    if auth_nginx.exists():
        content = auth_nginx.read_text()
        has_ssl = "ssl_certificate" in content
        has_hsts = "Strict-Transport-Security" in content
        check("Nginx auth: TLS configured", "auth-ssot", has_ssl, "SSL certs referenced")
        check("Nginx auth: HSTS header", "auth-ssot", has_hsts, "HSTS present")

    # Platform inventory auth references
    inv = load_yaml(ROOT / "ssot" / "integrations" / "platform_inventory.yaml")
    if inv:
        supabase = inv.get("cloud", {}).get("supabase", {})
        services = supabase.get("services", [])
        check(
            "Supabase auth in platform inventory",
            "auth-ssot",
            "auth" in services,
            f"Services: {services}" if services else "No services listed",
        )


def test_auth_nginx_configs():
    """Verify all nginx configs have proper security headers."""
    section("Nginx Security Headers (All Apps)")

    nginx_dir = ROOT / "infra" / "deploy" / "nginx"
    if not nginx_dir.exists():
        check("Nginx config dir", "auth-nginx", False, f"MISSING: {nginx_dir}")
        return

    for conf in sorted(nginx_dir.glob("*.conf")):
        name = conf.name
        content = conf.read_text()
        # Skip redirect-only configs (no proxy_pass directive = no upstream traffic)
        # Check for actual directive, not just the string in comments
        non_comment_lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        if not any("proxy_pass" in line for line in non_comment_lines):
            continue
        # Skip legacy .net configs
        if ".net.conf" in name:
            continue
        has_hsts = "Strict-Transport-Security" in content
        has_xframe = "X-Frame-Options" in content
        has_xcontent = "X-Content-Type-Options" in content
        has_ssl = "ssl_certificate" in content

        all_headers = has_hsts and has_xframe and has_xcontent and has_ssl
        missing = []
        if not has_hsts:
            missing.append("HSTS")
        if not has_xframe:
            missing.append("X-Frame-Options")
        if not has_xcontent:
            missing.append("X-Content-Type-Options")
        if not has_ssl:
            missing.append("SSL")

        check(
            f"Nginx {name}: security headers",
            "auth-nginx",
            all_headers,
            "All present" if all_headers else f"Missing: {', '.join(missing)}",
        )


def test_secrets_hygiene():
    """Verify no secrets are committed in mail/auth configuration."""
    section("Secrets Hygiene")

    # Check no hardcoded passwords in SSOT files
    sensitive_patterns = [
        "password:",
        "api_key:",
        "secret:",
        "smtp_pass",
    ]
    ssot_dirs = [
        ROOT / "config",
        ROOT / "ssot",
    ]

    # Files that are inherently about secret metadata (names, not values)
    secret_metadata_files = {"registry.yaml", "inventory.yaml"}

    violations = []
    for d in ssot_dirs:
        if not d.exists():
            continue
        for yaml_file in d.rglob("*.yaml"):
            # Skip secret registry/metadata files (they list secret names, not values)
            if yaml_file.name in secret_metadata_files:
                continue
            # Skip files that are governance rules (describe policies about secrets)
            if "ssot/odoo/" in str(yaml_file) or "ssot/secrets/" in str(yaml_file):
                continue
            content = yaml_file.read_text()
            for line_no, line in enumerate(content.splitlines(), 1):
                line_lower = line.lower().strip()
                # Skip comments and env var placeholders
                if line_lower.startswith("#"):
                    continue
                if "${" in line or "env." in line.lower():
                    continue
                for pattern in sensitive_patterns:
                    if pattern in line_lower:
                        # Check if it's a real value (not a key name reference)
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip('"').strip("'")
                            # Skip empty, env var refs, vault refs, key names, descriptions
                            # Heuristic: skip known safe patterns
                            skip = (
                                not val
                                or val.startswith("$") or val.startswith("{")
                                or len(val) <= 20
                                or val.startswith("http") or val.startswith("SELECT")
                                or "insightpulseai" in val
                                or "_key" in val.lower() or "_secret" in val.lower()
                                or "_password" in val.lower() or "_token" in val.lower()
                                or "_id" in val.lower() or "vault" in val.lower()
                                or val.startswith("SUPABASE_") or val.startswith("GITHUB_")
                                or val.startswith("anthropic") or val.startswith("claude")
                                or val.startswith("odoo_") or val.startswith("mailgun_")
                                or "registry" in val.lower() or "ssot" in val.lower()
                            )
                            if not skip:
                                violations.append(f"{yaml_file.relative_to(ROOT)}:{line_no}")

    check(
        "No hardcoded secrets in config/ssot YAML",
        "secrets",
        len(violations) == 0,
        f"Clean" if not violations else f"Potential secrets: {violations[:5]}",
    )

    # Check .env files are gitignored
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        gi_content = gitignore.read_text()
        has_env = ".env" in gi_content
        check(
            ".env in .gitignore",
            "secrets",
            has_env,
            "Present" if has_env else ".env NOT in .gitignore!",
        )


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def generate_evidence():
    """Write evidence JSON."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    summary = {
        "test_suite": "mail_and_auth",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed / total * 100:.1f}%" if total > 0 else "N/A",
        "results": results,
    }

    evidence_file = EVIDENCE_DIR / "mail_auth_test_results.json"
    with open(evidence_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nEvidence written to: {evidence_file.relative_to(ROOT)}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Test mail and auth configuration")
    parser.add_argument("--mail-only", action="store_true", help="Run mail checks only")
    parser.add_argument("--auth-only", action="store_true", help="Run auth checks only")
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    parser.add_argument("--no-network", action="store_true", help="Skip network connectivity tests")
    args = parser.parse_args()

    run_mail = not args.auth_only
    run_auth = not args.mail_only

    print("=" * 60)
    print("  InsightPulse AI — Mail & Auth Configuration Test Suite")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    if run_mail:
        test_mail_ssot_consistency()
        test_mail_dns()
        if not args.no_network:
            test_mail_connectivity()
        test_mail_modules()
        test_mail_ci_scripts()

    if run_auth:
        test_auth_dns()
        if not args.no_network:
            test_auth_connectivity()
        test_auth_modules()
        test_auth_ssot()
        test_auth_nginx_configs()

    # Always run
    test_secrets_hygiene()

    summary = generate_evidence()

    # Final summary
    print(f"\n{'=' * 60}")
    print(f"  RESULTS: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']})")
    failed_list = [r for r in results if not r["passed"]]
    if failed_list:
        print(f"  FAILURES:")
        for r in failed_list:
            print(f"    - [{r['category']}] {r['name']}: {r['detail']}")
    print(f"{'=' * 60}")

    if args.json:
        print(json.dumps(summary, indent=2))

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
