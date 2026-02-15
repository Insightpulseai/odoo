#!/usr/bin/env python3
"""
Local LLM Probe
---------------
Detects, enumerates, and characterizes locally available LLM runtimes.
Outputs a structured JSON capability record to .local/state/local_llm_capabilities.json.

Requirements: None (Standard Library only)
"""

import json
import os
import platform
import subprocess
import time
import urllib.request
import urllib.error
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# --- Configuration ---
OUTPUT_DIR = ".local/state"
OUTPUT_FILE = "local_llm_capabilities.json"
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234"  # Common default


def get_system_info() -> Dict[str, Any]:
    """Gather system hardware and OS details."""
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.machine(),
        "cpu_cores": os.cpu_count(),
        "ram_gb": None,
        "gpu": {"present": False, "type": None},
    }

    try:
        if platform.system() == "Darwin":
            # macOS specific checks
            mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
            info["ram_gb"] = round(mem_bytes / (1024**3))

            # Check for Apple Silicon / Metal
            chip_info = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
            if "Chip:" in chip_info:  # Apple Silicon
                info["gpu"]["present"] = True
                info["gpu"]["type"] = "Apple Silicon (Integrated)"
            else:
                # Check for discrete GPU on Intel Mac
                gpu_info = subprocess.check_output(
                    ["system_profiler", "SPDisplaysDataType"]
                ).decode()
                if "Metal" in gpu_info:
                    info["gpu"]["present"] = True
                    info["gpu"]["type"] = "Metal Supported GPU"

        elif platform.system() == "Linux":
            # Linux specific checks (basic)
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        info["ram_gb"] = round(kb / (1024**2))
                        break

            # Simple check for nvidia-smi
            try:
                subprocess.check_output(["nvidia-smi"])
                info["gpu"]["present"] = True
                info["gpu"]["type"] = "NVIDIA"
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

    except Exception as e:
        print(f"Warning: Failed to gather some system info: {e}")

    return info


def check_ollama(skip_inference: bool = False) -> Optional[Dict[str, Any]]:
    """Detect Ollama runtime and available models."""
    runtime = {
        "name": "ollama",
        "status": "not_found",
        "endpoint": OLLAMA_BASE_URL,
        "models": [],
        "inference_test": None,
    }

    # 1. Check if service is up
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=1) as response:
            if response.status == 200:
                runtime["status"] = "available"
                data = json.loads(response.read().decode())

                for m in data.get("models", []):
                    # Attempt to get more details via 'ollama show' CLI if possible,
                    # otherwise use basic info from API
                    model_id = m["name"]
                    details = m.get("details", {})

                    model_info = {
                        "id": model_id,
                        "params": details.get("parameter_size"),
                        "quantization": details.get("quantization_level"),
                        "context_tokens": None,  # reliable ONLY if verified
                        "capability": "unknown",
                    }

                    # Simple heuristic for capability
                    size_str = details.get("parameter_size", "0")
                    if "B" in size_str:
                        try:
                            size = float(size_str.replace("B", ""))
                            if size <= 3:
                                model_info["capability"] = "tiny"
                            elif size <= 8:
                                model_info["capability"] = "small"
                            elif size <= 14:
                                model_info["capability"] = "medium"
                            else:
                                model_info["capability"] = "large"
                        except ValueError:
                            pass

                    runtime["models"].append(model_info)

    except (urllib.error.URLError, ConnectionRefusedError):
        return None  # Runtime not available

    # 2. Run Inference Test (on first available model)
    if not skip_inference and runtime["status"] == "available" and runtime["models"]:
        test_model = runtime["models"][0]["id"]
        print(f"Testing inference on {test_model}...")

        req_data = json.dumps({"model": test_model, "prompt": "ping", "stream": False}).encode()

        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=req_data,
            headers={"Content-Type": "application/json"},
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    duration = (time.time() - start_time) * 1000
                    runtime["inference_test"] = {
                        "status": "ok",
                        "latency_ms": int(duration),
                        "note": "Measured via /api/generate",
                    }
        except Exception as e:
            runtime["inference_test"] = {"status": "failed", "error": str(e)}

    return runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-inference", action="store_true", help="Skip inference test")
    args = parser.parse_args()

    print("Starting Local LLM Probe...")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report = {
        "schema_version": "1.0.0",
        "system": get_system_info(),
        "runtimes": [],
        "provenance": {
            "captured_at": datetime.now().astimezone().isoformat(),
            "collector": "scripts/local_llm_probe.py",
            "methods": ["sysctl", "urllib", "ollama list", "curl /api/tags"],
        },
        "integrity": {
            "inference_test": "skipped" if args.no_inference else "measured",
            "no_inference_flag": args.no_inference,
        },
        "policy": {
            "default_model": None,
            "max_input_chars": 12000,
            "max_output_tokens": 512,
            "task_classes_local": [
                "lint",
                "classify",
                "route",
                "summarize_small",
                "extract_structured",
            ],
            "task_classes_remote": [
                "codegen_large",
                "architecture",
                "deep_debug",
                "long_context",
                "ambiguous",
            ],
        },
    }

    # Detect Runtimes
    ollama = check_ollama(skip_inference=args.no_inference)
    if ollama:
        report["runtimes"].append(ollama)
        # Set default model if available
        if ollama["models"]:
            report["policy"]["default_model"] = f"ollama:{ollama['models'][0]['id']}"

    # Output
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Probe complete. Capabilities written to {output_path}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
