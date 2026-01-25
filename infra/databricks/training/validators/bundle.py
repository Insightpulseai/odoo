"""
Databricks Asset Bundle validators.
"""

import subprocess
import json
from typing import Tuple


def bundle_validate_passes(workspace_path: str, timeout: int = 60) -> Tuple[bool, str]:
    """
    Validate DAB bundle configuration.

    Args:
        workspace_path: Path to the bundle directory
        timeout: Command timeout in seconds

    Returns:
        (success, message) tuple
    """
    try:
        result = subprocess.run(
            ["databricks", "bundle", "validate"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, "Bundle validation passed"
        return False, f"Bundle validation failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Bundle validation timed out"
    except FileNotFoundError:
        return False, "Databricks CLI not found"
    except Exception as e:
        return False, f"Validation error: {e}"


def deploy_status_check(
    workspace_path: str, target: str = "dev", timeout: int = 120
) -> Tuple[bool, str]:
    """
    Check bundle deployment status.

    Args:
        workspace_path: Path to the bundle directory
        target: Deployment target (dev, staging, prod)
        timeout: Command timeout in seconds

    Returns:
        (success, message) tuple
    """
    try:
        result = subprocess.run(
            ["databricks", "bundle", "summary", "--target", target],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, f"Deployment to {target} verified"
        return False, f"Deployment check failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Deployment status check timed out"
    except FileNotFoundError:
        return False, "Databricks CLI not found"
    except Exception as e:
        return False, f"Deployment check error: {e}"


def bundle_yaml_valid(yaml_content: str) -> Tuple[bool, str]:
    """
    Validate bundle YAML syntax without running Databricks CLI.

    Args:
        yaml_content: The YAML content to validate

    Returns:
        (success, message) tuple
    """
    try:
        import yaml

        parsed = yaml.safe_load(yaml_content)
        if not isinstance(parsed, dict):
            return False, "Bundle YAML must be a dictionary"

        # Check required top-level keys
        if "bundle" not in parsed:
            return False, "Missing required 'bundle' section"

        bundle_section = parsed.get("bundle", {})
        if not isinstance(bundle_section, dict):
            return False, "'bundle' section must be a dictionary"

        if "name" not in bundle_section:
            return False, "Missing required 'bundle.name'"

        return True, "Bundle YAML syntax valid"

    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"
