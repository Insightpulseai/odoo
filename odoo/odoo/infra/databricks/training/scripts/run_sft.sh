#!/usr/bin/env bash
# Supervised Fine-Tuning (SFT) training script
#
# Prerequisites:
# - Python 3.10+
# - GPU with CUDA (or CPU for small experiments)
# - Training data in data/sft_tasks.jsonl
#
# Usage:
#   ./scripts/run_sft.sh [--model MODEL_NAME] [--epochs NUM_EPOCHS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAINING_DIR="$(dirname "$SCRIPT_DIR")"

cd "$TRAINING_DIR"

# Default parameters
MODEL_NAME="${MODEL_NAME:-microsoft/phi-2}"
NUM_EPOCHS="${NUM_EPOCHS:-3}"
BATCH_SIZE="${BATCH_SIZE:-4}"
LEARNING_RATE="${LEARNING_RATE:-2e-5}"
OUTPUT_DIR="${OUTPUT_DIR:-artifacts/models/sft}"

# Ensure virtual environment
if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import transformers" 2>/dev/null; then
    echo "Installing training dependencies..."
    pip install -U pip
    pip install torch transformers datasets accelerate trl peft evaluate
fi

# Check for training data
if [[ ! -f "data/sft_tasks.jsonl" ]]; then
    echo "Generating training data..."
    python scripts/generate_data.py --count 200 --output data/sft_tasks.jsonl
fi

echo "================================================"
echo "Starting SFT Training"
echo "================================================"
echo "Model: $MODEL_NAME"
echo "Epochs: $NUM_EPOCHS"
echo "Batch Size: $BATCH_SIZE"
echo "Learning Rate: $LEARNING_RATE"
echo "Output: $OUTPUT_DIR"
echo "================================================"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run SFT training
python - <<'TRAINING_SCRIPT'
import json
import os
from pathlib import Path

try:
    from datasets import Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
    )
    from trl import SFTTrainer
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install transformers datasets trl")
    exit(1)

# Load configuration from environment
model_name = os.environ.get("MODEL_NAME", "microsoft/phi-2")
num_epochs = int(os.environ.get("NUM_EPOCHS", "3"))
batch_size = int(os.environ.get("BATCH_SIZE", "4"))
learning_rate = float(os.environ.get("LEARNING_RATE", "2e-5"))
output_dir = os.environ.get("OUTPUT_DIR", "artifacts/models/sft")

# Load training data
print("Loading training data...")
tasks = []
with open("data/sft_tasks.jsonl", "r") as f:
    for line in f:
        task = json.loads(line)
        # Format as instruction-following
        text = f"""### Instruction:
{task['instruction']}

### Context:
{json.dumps(task['context'], indent=2)}

### Response:
{json.dumps(task['expected'], indent=2)}"""
        tasks.append({"text": text})

dataset = Dataset.from_list(tasks)
print(f"Loaded {len(dataset)} training examples")

# Load model and tokenizer
print(f"Loading model: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    device_map="auto",
)

# Training arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    learning_rate=learning_rate,
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    fp16=True,
    gradient_accumulation_steps=4,
    warmup_ratio=0.1,
    report_to="none",
)

# Initialize trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
)

# Train
print("Starting training...")
trainer.train()

# Save model
print(f"Saving model to {output_dir}")
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

print("SFT training complete!")
TRAINING_SCRIPT

echo "================================================"
echo "SFT Training Complete"
echo "Model saved to: $OUTPUT_DIR"
echo "================================================"
