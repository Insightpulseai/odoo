#!/usr/bin/env bash
# Direct Preference Optimization (DPO) training script
#
# Prerequisites:
# - SFT model from run_sft.sh
# - Preference pairs in data/preference_pairs.jsonl
#
# Usage:
#   ./scripts/run_dpo.sh [--model SFT_MODEL_PATH]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAINING_DIR="$(dirname "$SCRIPT_DIR")"

cd "$TRAINING_DIR"

# Default parameters
SFT_MODEL="${SFT_MODEL:-artifacts/models/sft}"
NUM_EPOCHS="${NUM_EPOCHS:-1}"
BATCH_SIZE="${BATCH_SIZE:-2}"
BETA="${BETA:-0.1}"
OUTPUT_DIR="${OUTPUT_DIR:-artifacts/models/dpo}"

# Ensure virtual environment
source .venv/bin/activate 2>/dev/null || {
    echo "Virtual environment not found. Run run_sft.sh first."
    exit 1
}

# Check for SFT model
if [[ ! -d "$SFT_MODEL" ]]; then
    echo "SFT model not found at $SFT_MODEL"
    echo "Run run_sft.sh first to train the base model."
    exit 1
fi

# Generate preference pairs if not present
if [[ ! -f "data/preference_pairs.jsonl" ]]; then
    echo "Generating preference pairs..."
    python - <<'GENSCRIPT'
import json
import pathlib

pathlib.Path("data").mkdir(exist_ok=True)

# Generate synthetic preference pairs
pairs = []
for i in range(100):
    pairs.append({
        "prompt": f"Fix bundle validation error: Variable 'catalog' undefined",
        "chosen": json.dumps({
            "patch": "variables:\n  catalog:\n    default: main",
            "explanation": "Added missing variable definition"
        }),
        "rejected": json.dumps({
            "patch": "# TODO: fix later",
            "explanation": "Placeholder, not a real fix"
        })
    })
    pairs.append({
        "prompt": "Create UC grants for data engineering team",
        "chosen": "GRANT USAGE ON CATALOG analytics TO `data_engineers`;\nGRANT USE SCHEMA ON SCHEMA analytics.bronze TO `data_engineers`;",
        "rejected": "GRANT ALL ON CATALOG analytics TO `data_engineers`;  -- Too permissive"
    })

with open("data/preference_pairs.jsonl", "w") as f:
    for p in pairs:
        f.write(json.dumps(p) + "\n")
print(f"Generated {len(pairs)} preference pairs")
GENSCRIPT
fi

echo "================================================"
echo "Starting DPO Training"
echo "================================================"
echo "Base Model: $SFT_MODEL"
echo "Epochs: $NUM_EPOCHS"
echo "Beta: $BETA"
echo "Output: $OUTPUT_DIR"
echo "================================================"

mkdir -p "$OUTPUT_DIR"

# Run DPO training
python - <<'TRAINING_SCRIPT'
import json
import os

try:
    from datasets import Dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOTrainer, DPOConfig
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install trl>=0.7.0")
    exit(1)

sft_model = os.environ.get("SFT_MODEL", "artifacts/models/sft")
num_epochs = int(os.environ.get("NUM_EPOCHS", "1"))
beta = float(os.environ.get("BETA", "0.1"))
output_dir = os.environ.get("OUTPUT_DIR", "artifacts/models/dpo")

# Load preference pairs
print("Loading preference pairs...")
pairs = []
with open("data/preference_pairs.jsonl", "r") as f:
    for line in f:
        pairs.append(json.loads(line))

dataset = Dataset.from_list(pairs)
print(f"Loaded {len(dataset)} preference pairs")

# Load model
print(f"Loading SFT model from {sft_model}")
tokenizer = AutoTokenizer.from_pretrained(sft_model)
model = AutoModelForCausalLM.from_pretrained(sft_model, device_map="auto")

# DPO config
dpo_config = DPOConfig(
    output_dir=output_dir,
    num_train_epochs=num_epochs,
    per_device_train_batch_size=2,
    beta=beta,
    logging_steps=10,
    save_steps=50,
    fp16=True,
    report_to="none",
)

# Train
trainer = DPOTrainer(
    model=model,
    ref_model=None,  # Use implicit reference
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

print("Starting DPO training...")
trainer.train()

print(f"Saving model to {output_dir}")
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

print("DPO training complete!")
TRAINING_SCRIPT

echo "================================================"
echo "DPO Training Complete"
echo "Model saved to: $OUTPUT_DIR"
echo "================================================"
