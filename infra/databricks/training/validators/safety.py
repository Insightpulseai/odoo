"""
Policy safety validators for agent actions.
"""

import re
from typing import Tuple, List, Optional


# Default forbidden patterns for Databricks agent actions
DEFAULT_FORBIDDEN_PATTERNS = [
    # Destructive SQL
    r"\bDROP\s+DATABASE\b",
    r"\bDROP\s+CATALOG\b",
    r"\bDROP\s+SCHEMA\b.*\bCASCADE\b",
    r"\bDELETE\s+FROM\b.*\bWHERE\s+1\s*=\s*1\b",
    r"\bTRUNCATE\s+TABLE\b",
    # Dangerous shell patterns
    r"\brm\s+-rf\s+/\b",
    r"\brm\s+-rf\s+\*\b",
    r"--force\s+--all",
    r">\s*/dev/sda",
    # Credential exposure
    r"\bpassword\s*=\s*['\"][^'\"]+['\"]",
    r"\bsecret\s*=\s*['\"][^'\"]+['\"]",
    r"\btoken\s*=\s*['\"][^'\"]+['\"]",
    # Databricks-specific destructive actions
    r"\bdatabricks\s+bundle\s+destroy\b.*--auto-approve",
    r"\bdatabricks\s+workspace\s+delete\b.*--recursive",
    r"\bdatabricks\s+clusters\s+permanent-delete\b",
]


def policy_safety(
    action: str, forbidden_patterns: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Ensure agent action doesn't contain destructive commands.

    Args:
        action: The action string to validate
        forbidden_patterns: List of regex patterns to forbid

    Returns:
        (success, message) tuple
    """
    if forbidden_patterns is None:
        forbidden_patterns = DEFAULT_FORBIDDEN_PATTERNS

    for pattern in forbidden_patterns:
        if re.search(pattern, action, re.IGNORECASE):
            return False, f"Forbidden pattern detected: {pattern}"

    return True, "Action passes safety check"


def forbidden_patterns_check(
    action: str,
    additional_patterns: Optional[List[str]] = None,
    allow_patterns: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """
    Extended safety check with allow-list override.

    Args:
        action: The action string to validate
        additional_patterns: Extra patterns to forbid
        allow_patterns: Patterns that override forbidden (explicit allow)

    Returns:
        (success, message) tuple
    """
    forbidden = list(DEFAULT_FORBIDDEN_PATTERNS)
    if additional_patterns:
        forbidden.extend(additional_patterns)

    allow_set = set(allow_patterns or [])

    for pattern in forbidden:
        if pattern in allow_set:
            continue
        if re.search(pattern, action, re.IGNORECASE):
            return False, f"Forbidden pattern detected: {pattern}"

    return True, "Action passes extended safety check"


def validate_cli_command(command: str) -> Tuple[bool, str]:
    """
    Validate Databricks CLI command for safety.

    Args:
        command: CLI command to validate

    Returns:
        (success, message) tuple
    """
    # Must start with databricks
    if not command.strip().startswith("databricks "):
        return False, "Command must start with 'databricks'"

    # Check for dangerous subcommands
    dangerous_subcommands = [
        ("bundle destroy", "without explicit confirmation flag"),
        ("workspace delete", "with recursive flag"),
        ("clusters permanent-delete", "irreversible action"),
        ("secrets delete-scope", "deletes entire secret scope"),
    ]

    for subcmd, reason in dangerous_subcommands:
        if subcmd in command.lower():
            # Check if there's explicit confirmation
            if "--auto-approve" not in command and "-y" not in command:
                return (
                    False,
                    f"Dangerous command '{subcmd}' ({reason}) - requires explicit approval",
                )
            else:
                return (
                    False,
                    f"Dangerous command '{subcmd}' with auto-approve - blocked for safety",
                )

    return True, "CLI command validated"


def validate_notebook_output(output: str, max_secrets: int = 0) -> Tuple[bool, str]:
    """
    Validate notebook output doesn't leak secrets.

    Args:
        output: Notebook cell output
        max_secrets: Maximum allowed secret-like strings (default 0)

    Returns:
        (success, message) tuple
    """
    secret_patterns = [
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI keys
        r"dapi[a-f0-9]{32}",  # Databricks PAT
        r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT
        r"AKIA[0-9A-Z]{16}",  # AWS access key
        r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",  # Private keys
    ]

    found_secrets = []
    for pattern in secret_patterns:
        matches = re.findall(pattern, output)
        found_secrets.extend(matches)

    if len(found_secrets) > max_secrets:
        # Redact the actual secrets in the message
        return (
            False,
            f"Found {len(found_secrets)} potential secrets in output (max allowed: {max_secrets})",
        )

    return True, "Output passes secret scan"
