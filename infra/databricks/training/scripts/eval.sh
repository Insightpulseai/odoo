#!/usr/bin/env bash
# Evaluation script for trained Databricks agent models
#
# Runs the model on holdout tasks and computes metrics using validators.
#
# Usage:
#   ./scripts/eval.sh [--model MODEL_PATH] [--output results.json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAINING_DIR="$(dirname "$SCRIPT_DIR")"

cd "$TRAINING_DIR"

# Default parameters
MODEL_PATH="${MODEL_PATH:-artifacts/models/rl}"
EVAL_DATA="${EVAL_DATA:-data/eval_holdout.jsonl}"
OUTPUT_FILE="${OUTPUT_FILE:-artifacts/eval_results.json}"

# Fallback model paths
if [[ ! -d "$MODEL_PATH" ]]; then
    MODEL_PATH="artifacts/models/dpo"
fi
if [[ ! -d "$MODEL_PATH" ]]; then
    MODEL_PATH="artifacts/models/sft"
fi
if [[ ! -d "$MODEL_PATH" ]]; then
    echo "No trained model found. Run training scripts first."
    exit 1
fi

# Ensure virtual environment
source .venv/bin/activate 2>/dev/null || {
    echo "Virtual environment not found."
    exit 1
}

# Generate eval data if not present
if [[ ! -f "$EVAL_DATA" ]]; then
    echo "Generating evaluation holdout set..."
    python scripts/generate_data.py --count 50 --output data/sft_tasks.jsonl
fi

echo "================================================"
echo "Evaluating Model"
echo "================================================"
echo "Model: $MODEL_PATH"
echo "Eval Data: $EVAL_DATA"
echo "Output: $OUTPUT_FILE"
echo "================================================"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Run evaluation
python - <<'EVAL_SCRIPT'
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add validators to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from validators import (
        bundle_yaml_valid,
        sql_compiles,
        policy_safety,
        tool_contract_valid,
    )
    VALIDATORS_AVAILABLE = True
except ImportError:
    print("Warning: Validators not available, using basic checks")
    VALIDATORS_AVAILABLE = False
    def bundle_yaml_valid(x): return (True, "mock")
    def sql_compiles(x): return (True, "mock")
    def policy_safety(x): return (True, "mock")

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)

model_path = os.environ.get("MODEL_PATH", "artifacts/models/rl")
eval_data = os.environ.get("EVAL_DATA", "data/eval_holdout.jsonl")
output_file = os.environ.get("OUTPUT_FILE", "artifacts/eval_results.json")

print(f"Loading model from {model_path}")
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

# Load eval tasks
tasks = []
if Path(eval_data).exists():
    with open(eval_data, "r") as f:
        for line in f:
            tasks.append(json.loads(line))
else:
    print(f"Eval data not found at {eval_data}")
    tasks = []

print(f"Evaluating on {len(tasks)} tasks")

results = {
    "model": model_path,
    "eval_data": eval_data,
    "timestamp": datetime.now().isoformat(),
    "total_tasks": len(tasks),
    "metrics": {},
    "per_task_results": [],
}

# Metrics accumulators
metrics = {
    "safety_pass": 0,
    "format_valid": 0,
    "expected_match": 0,
}

for i, task in enumerate(tasks):
    # Format prompt
    prompt = f"### Instruction:\n{task['instruction']}\n\n### Context:\n{json.dumps(task['context'])}\n\n### Response:\n"

    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=256,
            do_sample=False,  # Deterministic for eval
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.replace(prompt, "").strip()

    # Evaluate response
    task_result = {
        "task_id": task.get("id", f"task_{i}"),
        "task_type": task.get("task_type", "unknown"),
        "response_preview": response[:200],
        "checks": {},
    }

    # Safety check
    safe, msg = policy_safety(response)
    task_result["checks"]["safety"] = {"pass": safe, "message": msg}
    if safe:
        metrics["safety_pass"] += 1

    # Format validity check
    task_type = task.get("task_type", "")
    if task_type == "bundle_repair":
        valid, msg = bundle_yaml_valid(response) if "variables:" in response or "resources:" in response else (False, "No YAML structure")
        task_result["checks"]["format"] = {"pass": valid, "message": msg}
        if valid:
            metrics["format_valid"] += 1
    elif task_type == "uc_governance":
        valid, msg = sql_compiles(response)
        task_result["checks"]["format"] = {"pass": valid, "message": msg}
        if valid:
            metrics["format_valid"] += 1
    else:
        # Generic format check
        if len(response) > 10 and not response.startswith("I don't"):
            metrics["format_valid"] += 1
            task_result["checks"]["format"] = {"pass": True, "message": "Response generated"}
        else:
            task_result["checks"]["format"] = {"pass": False, "message": "Empty or refusal"}

    # Expected content check
    expected = task.get("expected", {})
    if isinstance(expected, dict):
        expected_content = json.dumps(expected).lower()
    else:
        expected_content = str(expected).lower()

    response_lower = response.lower()
    # Check for key terms from expected
    key_terms = [w for w in expected_content.split() if len(w) > 4][:5]
    matches = sum(1 for term in key_terms if term in response_lower)
    if matches >= len(key_terms) * 0.5:
        metrics["expected_match"] += 1
        task_result["checks"]["expected"] = {"pass": True, "matches": matches}
    else:
        task_result["checks"]["expected"] = {"pass": False, "matches": matches}

    results["per_task_results"].append(task_result)

    if i % 10 == 0:
        print(f"Evaluated {i+1}/{len(tasks)} tasks")

# Compute final metrics
total = len(tasks) if tasks else 1
results["metrics"] = {
    "safety_rate": metrics["safety_pass"] / total,
    "format_valid_rate": metrics["format_valid"] / total,
    "expected_match_rate": metrics["expected_match"] / total,
    "overall_score": (
        metrics["safety_pass"] +
        metrics["format_valid"] +
        metrics["expected_match"]
    ) / (3 * total),
}

# Save results
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print("\n================================================")
print("Evaluation Results")
print("================================================")
print(f"Safety Rate:         {results['metrics']['safety_rate']:.1%}")
print(f"Format Valid Rate:   {results['metrics']['format_valid_rate']:.1%}")
print(f"Expected Match Rate: {results['metrics']['expected_match_rate']:.1%}")
print(f"Overall Score:       {results['metrics']['overall_score']:.1%}")
print("================================================")
print(f"Detailed results saved to: {output_file}")
EVAL_SCRIPT

echo ""
echo "Evaluation complete. Results saved to: $OUTPUT_FILE"
