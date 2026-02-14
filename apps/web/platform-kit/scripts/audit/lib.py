"""
Platform Kit Integration Audit Library
Core utilities for integration health checks.
"""

import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


# =============================================================================
# Result Builders
# =============================================================================

def ok(code: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a passing result."""
    return {
        "status": "ok",
        "code": code,
        "data": data or {}
    }


def fail(code: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a failing result (blocks CI)."""
    return {
        "status": "fail",
        "code": code,
        "data": data or {}
    }


def warn(code: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a warning result (non-blocking, but logged)."""
    return {
        "status": "warn",
        "code": code,
        "data": data or {}
    }


def skip(code: str, reason: str) -> Dict[str, Any]:
    """Return a skipped result (missing prerequisites)."""
    return {
        "status": "skip",
        "code": code,
        "data": {"reason": reason}
    }


# =============================================================================
# Security Helpers
# =============================================================================

def redact(value: str, visible_chars: int = 4) -> str:
    """Redact a secret, showing only the last N characters."""
    if not value:
        return "<empty>"
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


def has_secret(name: str) -> bool:
    """Check if an environment variable is set and non-empty."""
    return bool(os.getenv(name, "").strip())


def get_secret(name: str, default: str = "") -> str:
    """Get an environment variable, returning default if not set."""
    return os.getenv(name, default).strip()


# =============================================================================
# Command Execution
# =============================================================================

def run_cmd(
    cmd: List[str],
    timeout: int = 30,
    capture: bool = True,
    check: bool = False
) -> Dict[str, Any]:
    """
    Run a shell command and return structured output.

    Args:
        cmd: Command as list of strings
        timeout: Timeout in seconds
        capture: Capture stdout/stderr
        check: Raise on non-zero exit

    Returns:
        Dict with stdout, stderr, returncode, success
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            check=check
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout if capture else None,
            "stderr": result.stderr if capture else None
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": None,
            "stderr": f"Command timed out after {timeout}s",
            "error": "timeout"
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "returncode": e.returncode,
            "stdout": e.stdout if capture else None,
            "stderr": e.stderr if capture else None,
            "error": "nonzero_exit"
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": None,
            "stderr": str(e),
            "error": "command_not_found"
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": None,
            "stderr": str(e),
            "error": "exception"
        }


# =============================================================================
# HTTP Helpers
# =============================================================================

def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Make an HTTP GET request.

    Returns:
        Dict with success, status_code, body, error
    """
    req = urllib.request.Request(url, method="GET")
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return {
                "success": True,
                "status_code": resp.status,
                "body": body,
                "headers": dict(resp.headers)
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status_code": e.code,
            "body": e.read().decode("utf-8") if e.fp else None,
            "error": str(e)
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "status_code": None,
            "body": None,
            "error": str(e.reason)
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "body": None,
            "error": str(e)
        }


def http_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Make an HTTP POST request with JSON body.

    Returns:
        Dict with success, status_code, body, error
    """
    body_bytes = json.dumps(data or {}).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, method="POST")
    req.add_header("Content-Type", "application/json")
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return {
                "success": True,
                "status_code": resp.status,
                "body": body,
                "headers": dict(resp.headers)
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status_code": e.code,
            "body": e.read().decode("utf-8") if e.fp else None,
            "error": str(e)
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "status_code": None,
            "body": None,
            "error": str(e.reason)
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "body": None,
            "error": str(e)
        }


# =============================================================================
# DNS Helpers
# =============================================================================

def dig_txt(name: str) -> str:
    """Query TXT records for a domain using dig."""
    r = run_cmd(["dig", "+short", "TXT", name])
    if not r["success"]:
        return ""
    # Remove quotes from TXT records
    return (r.get("stdout") or "").replace('"', '').strip()


def dig_mx(name: str) -> str:
    """Query MX records for a domain using dig."""
    r = run_cmd(["dig", "+short", "MX", name])
    if not r["success"]:
        return ""
    return (r.get("stdout") or "").strip()


def dig_cname(name: str) -> str:
    """Query CNAME records for a domain using dig."""
    r = run_cmd(["dig", "+short", "CNAME", name])
    if not r["success"]:
        return ""
    return (r.get("stdout") or "").strip()


def dig_a(name: str) -> str:
    """Query A records for a domain using dig."""
    r = run_cmd(["dig", "+short", "A", name])
    if not r["success"]:
        return ""
    return (r.get("stdout") or "").strip()


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(pattern.match(url))


def validate_email(email: str) -> bool:
    """Check if a string is a valid email address."""
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(email))


def validate_domain(domain: str) -> bool:
    """Check if a string is a valid domain name."""
    pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    return bool(pattern.match(domain))
