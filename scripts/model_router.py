#!/usr/bin/env python3
"""
Model Router
------------
Reads the local LLM capabilities registry and recommends routing
decisions based on task class and input size constraints.
Emits machine-actionable JSON and logs evidence.
"""

import json
import os
import argparse
import sys
import hashlib
import time
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

CAPABILITIES_FILE = ".local/state/local_llm_capabilities.json"
EVIDENCE_DIR = "docs/evidence"


def load_capabilities() -> Optional[Dict[str, Any]]:
    """Load the capabilities JSON."""
    if not os.path.exists(CAPABILITIES_FILE):
        return None
    try:
        with open(CAPABILITIES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def is_runtime_available(model_tag: str) -> bool:
    """
    Check if Ollama is reachable and has the model.
    model_tag example: 'ollama:llama3.2:1b' -> check endpoint + model 'llama3.2:1b'
    """
    if not model_tag.startswith("ollama:"):
        return False  # Only support checking ollama for now

    model_name = model_tag.replace("ollama:", "")
    endpoint = "http://127.0.0.1:11434"  # Default for now, ideally read from caps

    try:
        with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=0.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                for m in data.get("models", []):
                    # Robust check: exact match or tag match
                    if m["name"] == model_name:
                        return True
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
        return False

    return False


def log_evidence(decision: Dict[str, Any]):
    """Log the routing decision to evidence directory."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    day_dir = os.path.join(EVIDENCE_DIR, datetime.now().strftime("%Y-%m-%d"), "routing")
    os.makedirs(day_dir, exist_ok=True)

    filename = f"decision_{ts}_{os.getpid()}.json"
    path = os.path.join(day_dir, filename)

    with open(path, "w") as f:
        json.dump(decision, f, indent=2)


def get_route(task_class: str, input_chars: int = 0) -> Dict[str, Any]:
    """
    Determine the best route for a task.
    """
    caps = load_capabilities()

    # Default fallback
    decision = {
        "tier": "remote",
        "model": "remote-default",
        "reason_codes": ["NO_CAPABILITIES_FOUND"],
        "limits": {},
        "policy_version": "unknown",
    }

    if not caps:
        return decision

    decision["policy_version"] = caps.get("schema_version", "unknown")

    # Policy Check
    policy = caps.get("policy", {})
    decision["limits"] = {
        "max_input_chars": policy.get("max_input_chars", 0),
        "max_output_tokens": policy.get("max_output_tokens", 0),
    }

    # 1. Check Task Class
    if task_class in policy.get("task_classes_remote", []):
        decision["reason_codes"] = ["TASK_CLASS_REMOTE"]
        return decision

    if task_class not in policy.get("task_classes_local", []):
        decision["reason_codes"] = ["TASK_CLASS_UNKNOWN"]
        return decision

    # 2. Check Input Size
    max_chars = policy.get("max_input_chars", 0)
    if input_chars > max_chars:
        decision["reason_codes"] = ["OVER_CHAR_LIMIT"]
        return decision

    # 3. Check Local Model
    default_model = policy.get("default_model")
    if not default_model:
        decision["reason_codes"] = ["NO_LOCAL_MODEL_CONFIGURED"]
        return decision

    # 4. Live Availability Check
    if is_runtime_available(default_model):
        decision["tier"] = "local"
        decision["model"] = default_model
        decision["reason_codes"] = ["TASK_CLASS_LOCAL", "UNDER_CHAR_LIMIT", "RUNTIME_AVAILABLE"]
    else:
        decision["tier"] = "remote"
        decision["model"] = "remote-default"
        decision["reason_codes"] = ["RUNTIME_UNAVAILABLE"]

    return decision


def main():
    parser = argparse.ArgumentParser(description="Route tasks to local or remote LLMs.")
    parser.add_argument("--task", type=str, required=True, help="Task classification")
    parser.add_argument("--input-len", type=int, default=0, help="Length of input characters")

    args = parser.parse_args()

    route = get_route(args.task, args.input_len)

    # Log Evidence
    try:
        log_evidence(route)
    except Exception as e:
        # Do not fail routing if logging works, but maybe stderr
        sys.stderr.write(f"Warning: Failed to log evidence: {e}\n")

    print(json.dumps(route, indent=2))

    if route["tier"] == "remote":
        sys.exit(1)


if __name__ == "__main__":
    main()
