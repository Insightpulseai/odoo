"""
SQL and Unity Catalog validators.
"""

import subprocess
import re
from typing import Tuple, List


def sql_compiles(sql: str, dialect: str = "databricks") -> Tuple[bool, str]:
    """
    Validate SQL syntax using sqlfluff.

    Args:
        sql: SQL statement to validate
        dialect: SQL dialect (databricks, ansi, etc.)

    Returns:
        (success, message) tuple
    """
    try:
        result = subprocess.run(
            ["sqlfluff", "lint", "--dialect", dialect, "-"],
            input=sql,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "SQL syntax valid"
        # Parse lint output for specific errors
        errors = result.stdout.strip()
        return False, f"SQL errors: {errors[:500]}"
    except FileNotFoundError:
        # Fallback: basic syntax check
        return _basic_sql_check(sql)
    except subprocess.TimeoutExpired:
        return False, "SQL validation timed out"
    except Exception as e:
        return False, f"SQL validation error: {e}"


def _basic_sql_check(sql: str) -> Tuple[bool, str]:
    """
    Basic SQL syntax validation without external tools.

    Args:
        sql: SQL statement to check

    Returns:
        (success, message) tuple
    """
    sql_upper = sql.upper().strip()

    # Check for unclosed quotes
    single_quotes = sql.count("'") - sql.count("\\'")
    if single_quotes % 2 != 0:
        return False, "Unclosed single quote"

    double_quotes = sql.count('"') - sql.count('\\"')
    if double_quotes % 2 != 0:
        return False, "Unclosed double quote"

    # Check for balanced parentheses
    if sql.count("(") != sql.count(")"):
        return False, "Unbalanced parentheses"

    # Check for common statement starters
    valid_starters = [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "ALTER",
        "DROP",
        "GRANT",
        "REVOKE",
        "USE",
        "SHOW",
        "DESCRIBE",
        "WITH",
        "SET",
        "MERGE",
    ]
    has_valid_start = any(sql_upper.startswith(s) for s in valid_starters)
    if not has_valid_start:
        return False, f"Unknown SQL statement type"

    return True, "Basic SQL syntax check passed"


def grants_audit_passes(
    grants: List[str], required_patterns: List[str] = None
) -> Tuple[bool, str]:
    """
    Validate that required grant patterns are present.

    Args:
        grants: List of GRANT SQL statements
        required_patterns: List of patterns that must be matched

    Returns:
        (success, message) tuple
    """
    if required_patterns is None:
        required_patterns = [
            r"GRANT\s+USAGE\s+ON\s+CATALOG",
            r"GRANT\s+USE\s+SCHEMA\s+ON",
        ]

    all_grants = " ".join(grants).upper()
    missing = []

    for pattern in required_patterns:
        if not re.search(pattern, all_grants, re.IGNORECASE):
            missing.append(pattern)

    if missing:
        return False, f"Missing required grant patterns: {missing}"

    return True, "All required grant patterns present"


def uc_object_name_valid(name: str) -> Tuple[bool, str]:
    """
    Validate Unity Catalog object naming conventions.

    Args:
        name: Object name (catalog.schema.table format)

    Returns:
        (success, message) tuple
    """
    # Check for valid characters
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", name):
        return False, f"Invalid UC object name: {name}"

    parts = name.split(".")
    if len(parts) > 3:
        return False, "UC object name can have at most 3 parts (catalog.schema.object)"

    for part in parts:
        if len(part) > 255:
            return False, f"UC object name part too long: {part[:50]}..."
        if part.upper() in ["ALL", "AND", "OR", "NOT", "NULL", "TRUE", "FALSE"]:
            return False, f"Reserved word used as object name: {part}"

    return True, "UC object name valid"
