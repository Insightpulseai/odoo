#!/usr/bin/env python3
"""
Integration Audit Library - Common utilities for audit checks.

This module provides:
- HTTP request wrapper with retry/backoff
- Token/secret redaction
- Standard result schema builder
- Rate limit tracking
- Evidence collection helpers
"""

import hashlib
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urljoin

# Try to import requests, fall back to urllib
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False


# =============================================================================
# CONSTANTS
# =============================================================================
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 2
REDACTION_PLACEHOLDER = "[REDACTED]"

# Patterns for sensitive data redaction
SENSITIVE_PATTERNS = [
    # API keys and tokens
    (r'(sk-[a-zA-Z0-9]{20,})', REDACTION_PLACEHOLDER),  # OpenAI
    (r'(ghp_[a-zA-Z0-9]{36})', REDACTION_PLACEHOLDER),  # GitHub PAT
    (r'(gho_[a-zA-Z0-9]{36})', REDACTION_PLACEHOLDER),  # GitHub OAuth
    (r'(xoxb-[a-zA-Z0-9-]+)', REDACTION_PLACEHOLDER),   # Slack bot token
    (r'(xoxp-[a-zA-Z0-9-]+)', REDACTION_PLACEHOLDER),   # Slack user token
    (r'(key-[a-f0-9]{32})', REDACTION_PLACEHOLDER),     # Mailgun
    (r'(figd_[a-zA-Z0-9_-]+)', REDACTION_PLACEHOLDER),  # Figma
    (r'(dop_v1_[a-f0-9]{64})', REDACTION_PLACEHOLDER),  # DigitalOcean
    (r'(sbp_[a-f0-9]{40})', REDACTION_PLACEHOLDER),     # Supabase
    # Generic patterns
    (r'(Bearer\s+)[a-zA-Z0-9._-]+', r'\1' + REDACTION_PLACEHOLDER),
    (r'(password["\']?\s*[:=]\s*["\']?)[^"\';\s]+', r'\1' + REDACTION_PLACEHOLDER),
    (r'(secret["\']?\s*[:=]\s*["\']?)[^"\';\s]+', r'\1' + REDACTION_PLACEHOLDER),
    (r'(token["\']?\s*[:=]\s*["\']?)[^"\';\s]+', r'\1' + REDACTION_PLACEHOLDER),
    (r'(api_?key["\']?\s*[:=]\s*["\']?)[^"\';\s]+', r'\1' + REDACTION_PLACEHOLDER),
]


# =============================================================================
# DATA CLASSES
# =============================================================================
@dataclass
class CheckResult:
    """Standard result schema for integration checks."""
    name: str
    integration: str
    status: str  # PASS, FAIL, PARTIAL, SKIP
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    latency_ms: Optional[float] = None
    http_status: Optional[int] = None
    error: Optional[str] = None
    evidence: dict = field(default_factory=dict)
    rate_limit: Optional[dict] = None
    recommendations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class IntegrationResult:
    """Aggregated result for an entire integration."""
    name: str
    status: str  # PASS, FAIL, PARTIAL
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checks: list = field(default_factory=list)
    access_level: str = "unknown"  # ok, too_broad, insufficient
    risk_tier: str = "unknown"
    latency_avg_ms: Optional[float] = None
    error_count: int = 0
    pass_count: int = 0
    recommendations: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        result = asdict(self)
        result['checks'] = [c.to_dict() if isinstance(c, CheckResult) else c for c in self.checks]
        return {k: v for k, v in result.items() if v is not None}


# =============================================================================
# REDACTION HELPERS
# =============================================================================
def redact_string(text: str) -> str:
    """Redact sensitive information from a string."""
    if not text:
        return text
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def redact_dict(data: Any, depth: int = 0) -> Any:
    """Recursively redact sensitive values in a dictionary."""
    if depth > 10:  # Prevent infinite recursion
        return data

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            # Redact values for sensitive keys
            if any(s in key_lower for s in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                if isinstance(value, str) and len(value) > 0:
                    result[key] = REDACTION_PLACEHOLDER
                else:
                    result[key] = value
            else:
                result[key] = redact_dict(value, depth + 1)
        return result
    elif isinstance(data, list):
        return [redact_dict(item, depth + 1) for item in data]
    elif isinstance(data, str):
        return redact_string(data)
    return data


def redact_headers(headers: dict) -> dict:
    """Redact sensitive headers."""
    sensitive_headers = ['authorization', 'x-api-key', 'apikey', 'x-auth-token', 'cookie', 'set-cookie']
    result = {}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            result[key] = REDACTION_PLACEHOLDER
        else:
            result[key] = value
    return result


# =============================================================================
# HTTP HELPERS
# =============================================================================
class HTTPClient:
    """HTTP client with retry, backoff, and rate limit handling."""

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff: int = DEFAULT_BACKOFF
    ):
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

        if HAS_REQUESTS:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=retries,
                backoff_factor=backoff,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        else:
            self.session = None

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        auth: Optional[tuple] = None
    ) -> dict:
        """
        Make an HTTP request and return standardized result.

        Returns:
            dict with keys: status_code, headers, body, latency_ms, error, rate_limit
        """
        headers = headers or {}
        start_time = time.time()
        result = {
            "status_code": None,
            "headers": {},
            "body": None,
            "latency_ms": None,
            "error": None,
            "rate_limit": None
        }

        try:
            if HAS_REQUESTS:
                resp = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if method in ["POST", "PUT", "PATCH"] else None,
                    params=data if method == "GET" and data else None,
                    auth=auth,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                result["status_code"] = resp.status_code
                result["headers"] = dict(resp.headers)
                try:
                    result["body"] = resp.json()
                except Exception:
                    result["body"] = resp.text[:5000] if resp.text else None
            else:
                # Fallback to urllib
                req = urllib.request.Request(url, method=method)
                for k, v in headers.items():
                    req.add_header(k, v)
                if data and method in ["POST", "PUT", "PATCH"]:
                    req.data = json.dumps(data).encode()
                    req.add_header("Content-Type", "application/json")

                try:
                    with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                        result["status_code"] = resp.status
                        result["headers"] = dict(resp.headers)
                        body = resp.read().decode()
                        try:
                            result["body"] = json.loads(body)
                        except Exception:
                            result["body"] = body[:5000]
                except urllib.error.HTTPError as e:
                    result["status_code"] = e.code
                    result["headers"] = dict(e.headers) if e.headers else {}
                    result["body"] = e.read().decode()[:5000]

            # Extract rate limit info
            rate_headers = {}
            for key, value in result["headers"].items():
                key_lower = key.lower()
                if 'rate' in key_lower or 'limit' in key_lower or 'remaining' in key_lower:
                    rate_headers[key] = value
            if rate_headers:
                result["rate_limit"] = rate_headers

        except Exception as e:
            result["error"] = str(e)

        result["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        return result


# =============================================================================
# ENVIRONMENT HELPERS
# =============================================================================
def get_env(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable with optional requirement enforcement."""
    value = os.environ.get(name, default)
    if required and not value:
        raise EnvironmentError(f"Required environment variable {name} is not set")
    return value


def check_env_vars(required: list, optional: list = None) -> dict:
    """
    Check which environment variables are set.

    Returns:
        dict with 'missing_required', 'missing_optional', 'available'
    """
    optional = optional or []
    result = {
        "missing_required": [],
        "missing_optional": [],
        "available": []
    }

    for var in required:
        if os.environ.get(var):
            result["available"].append(var)
        else:
            result["missing_required"].append(var)

    for var in optional:
        if os.environ.get(var):
            result["available"].append(var)
        else:
            result["missing_optional"].append(var)

    return result


# =============================================================================
# EVIDENCE HELPERS
# =============================================================================
def create_evidence_dir(base_dir: str = "artifacts/audit") -> str:
    """Create timestamped evidence directory."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    evidence_dir = os.path.join(base_dir, timestamp)
    os.makedirs(evidence_dir, exist_ok=True)
    os.makedirs(os.path.join(evidence_dir, "raw"), exist_ok=True)
    return evidence_dir


def save_json(data: Any, filepath: str, redact: bool = True) -> None:
    """Save data to JSON file with optional redaction."""
    if redact:
        data = redact_dict(data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_markdown_report(results: list, filepath: str) -> None:
    """Generate markdown report from integration results."""
    lines = [
        "# Integration Audit Report",
        f"",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"",
        "## Summary",
        f"",
        "| Integration | Status | Checks Passed | Access Level | Risk Tier |",
        "|-------------|--------|---------------|--------------|-----------|"
    ]

    for r in results:
        if isinstance(r, IntegrationResult):
            r = r.to_dict()
        status_emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "SKIP": "⏭️"}.get(r["status"], "❓")
        lines.append(
            f"| {r['name']} | {status_emoji} {r['status']} | "
            f"{r.get('pass_count', 0)}/{len(r.get('checks', []))} | "
            f"{r.get('access_level', 'unknown')} | "
            f"{r.get('risk_tier', 'unknown')} |"
        )

    lines.extend(["", "## Details", ""])

    for r in results:
        if isinstance(r, IntegrationResult):
            r = r.to_dict()
        lines.extend([
            f"### {r['name']}",
            f"",
            f"**Status:** {r['status']}  ",
            f"**Risk Tier:** {r.get('risk_tier', 'unknown')}  ",
            f"**Access Level:** {r.get('access_level', 'unknown')}  ",
            f"**Average Latency:** {r.get('latency_avg_ms', 'N/A')} ms  ",
            f"",
        ])

        if r.get("checks"):
            lines.extend(["#### Checks", ""])
            for check in r["checks"]:
                status_emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "SKIP": "⏭️"}.get(check.get("status", ""), "❓")
                lines.append(f"- {status_emoji} **{check['name']}**: {check.get('description', '')}")
                if check.get("error"):
                    lines.append(f"  - Error: `{check['error']}`")
                if check.get("latency_ms"):
                    lines.append(f"  - Latency: {check['latency_ms']}ms")
            lines.append("")

        if r.get("recommendations"):
            lines.extend(["#### Recommendations", ""])
            for rec in r["recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_issue_payloads(results: list) -> list:
    """Generate GitHub issue payloads for failures."""
    issues = []

    for r in results:
        if isinstance(r, IntegrationResult):
            r = r.to_dict()

        if r["status"] in ["FAIL", "PARTIAL"]:
            failed_checks = [c for c in r.get("checks", []) if c.get("status") == "FAIL"]

            severity = "critical" if r.get("risk_tier") == "critical" else "warning"
            labels = ["integration", "audit", severity]

            body_lines = [
                f"## Integration Audit Failure: {r['name']}",
                f"",
                f"**Status:** {r['status']}",
                f"**Risk Tier:** {r.get('risk_tier', 'unknown')}",
                f"**Timestamp:** {r.get('timestamp', 'unknown')}",
                f"",
                "### Failed Checks",
                ""
            ]

            for check in failed_checks:
                body_lines.extend([
                    f"#### {check['name']}",
                    f"- **Description:** {check.get('description', '')}",
                    f"- **Error:** `{check.get('error', 'Unknown error')}`",
                    f"- **HTTP Status:** {check.get('http_status', 'N/A')}",
                    ""
                ])

            if r.get("recommendations"):
                body_lines.extend(["### Recommendations", ""])
                for rec in r["recommendations"]:
                    body_lines.append(f"- {rec}")

            issues.append({
                "title": f"[Audit] {r['name']} integration {r['status']}",
                "body": "\n".join(body_lines),
                "labels": labels,
                "component": r["name"].lower().replace(" ", "_"),
                "severity": severity
            })

    return issues


# =============================================================================
# MAIN (for testing)
# =============================================================================
if __name__ == "__main__":
    # Quick self-test
    print("Testing redaction...")
    test_data = {
        "api_key": "sk-1234567890abcdef",
        "password": "supersecret",
        "data": {
            "token": "ghp_abcdefghij1234567890abcdefghij1234",
            "normal": "this is fine"
        }
    }
    print(f"Original: {test_data}")
    print(f"Redacted: {redact_dict(test_data)}")

    print("\nTesting HTTP client...")
    client = HTTPClient(timeout=10)
    result = client.request("GET", "https://api.github.com/zen")
    print(f"Status: {result['status_code']}, Latency: {result['latency_ms']}ms")
