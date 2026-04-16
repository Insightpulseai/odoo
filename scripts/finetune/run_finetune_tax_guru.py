#!/usr/bin/env python3
"""Fine-tune gpt-4o-mini for Tax Guru (PH BIR specialist).

Prerequisites:
  pip install openai azure-identity
  az login (for DefaultAzureCredential)

Usage:
  python scripts/finetune/run_finetune_tax_guru.py [--upload-only | --status <job-id> | --deploy <model-id>]

Doctrine:
  - Fine-tuning runs on ipai-copilot-resource (Foundry), NOT Azure ML
  - Auth via DefaultAzureCredential (MI-first, no API keys)
  - Training data: agents/skills/bir_tax/finetune/training_data.jsonl
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# --- Config ---
ENDPOINT = "https://ipai-copilot-resource.openai.azure.com/"
API_VERSION = "2025-03-01-preview"
BASE_MODEL = "gpt-4o-mini"
SUFFIX = "tax-guru-v1"
TRAINING_FILE = Path(__file__).resolve().parent.parent.parent / "agents/skills/bir_tax/finetune/training_data.jsonl"
DEPLOYMENT_NAME = "tax-guru-ft-v1"
DEPLOYMENT_CAPACITY = 10


def get_client() -> AzureOpenAI:
    """Create AzureOpenAI client with Entra MI auth (no API key)."""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_version=API_VERSION,
        azure_ad_token_provider=token_provider,
    )


def upload_training_file(client: AzureOpenAI) -> str:
    """Upload JSONL training data and return file ID."""
    print(f"Uploading {TRAINING_FILE} ...")
    if not TRAINING_FILE.exists():
        print(f"ERROR: Training file not found: {TRAINING_FILE}")
        sys.exit(1)

    with open(TRAINING_FILE, "rb") as f:
        result = client.files.create(file=f, purpose="fine-tune")

    print(f"Uploaded: file_id={result.id}, status={result.status}, bytes={result.bytes}")
    return result.id


def create_finetune_job(client: AzureOpenAI, file_id: str) -> str:
    """Create a fine-tuning job and return job ID."""
    print(f"Creating fine-tune job: model={BASE_MODEL}, suffix={SUFFIX}, file={file_id}")

    job = client.fine_tuning.jobs.create(
        model=BASE_MODEL,
        training_file=file_id,
        suffix=SUFFIX,
        hyperparameters={
            "n_epochs": 3,
        },
    )

    print(f"Job created: id={job.id}, status={job.status}")
    print(f"Monitor with: python {__file__} --status {job.id}")
    return job.id


def check_status(client: AzureOpenAI, job_id: str) -> None:
    """Poll fine-tune job status."""
    job = client.fine_tuning.jobs.retrieve(job_id)
    print(f"Job {job_id}:")
    print(f"  status: {job.status}")
    print(f"  model: {job.model}")
    print(f"  fine_tuned_model: {job.fine_tuned_model}")
    print(f"  created_at: {job.created_at}")
    print(f"  finished_at: {job.finished_at}")

    if job.error:
        print(f"  ERROR: {job.error.code} — {job.error.message}")

    if job.status == "succeeded" and job.fine_tuned_model:
        print(f"\nFine-tuned model ready: {job.fine_tuned_model}")
        print(f"Deploy with: python {__file__} --deploy {job.fine_tuned_model}")


def deploy_model(client: AzureOpenAI, model_id: str) -> None:
    """Deploy the fine-tuned model. Uses az CLI (SDK deployment not yet stable)."""
    import subprocess

    print(f"Deploying {model_id} as '{DEPLOYMENT_NAME}' ...")

    cmd = [
        "az", "cognitiveservices", "account", "deployment", "create",
        "--resource-group", "rg-data-intel-ph",
        "--name", "ipai-copilot-resource",
        "--deployment-name", DEPLOYMENT_NAME,
        "--model-name", model_id,
        "--model-format", "OpenAI",
        "--sku-name", "Standard",
        "--sku-capacity", str(DEPLOYMENT_CAPACITY),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Deployed: {DEPLOYMENT_NAME}")
        print(f"Endpoint: {ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions")
    else:
        print(f"Deploy failed: {result.stderr}")
        sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tax Guru fine-tuning pipeline")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--upload-only", action="store_true", help="Upload training data only")
    group.add_argument("--status", metavar="JOB_ID", help="Check fine-tune job status")
    group.add_argument("--deploy", metavar="MODEL_ID", help="Deploy a fine-tuned model")
    args = parser.parse_args()

    client = get_client()

    if args.status:
        check_status(client, args.status)
        return 0

    if args.deploy:
        deploy_model(client, args.deploy)
        return 0

    # Default: upload + create job
    file_id = upload_training_file(client)

    if args.upload_only:
        print(f"Upload complete. file_id={file_id}")
        return 0

    # Wait for file processing
    print("Waiting for file processing ...")
    time.sleep(5)

    job_id = create_finetune_job(client, file_id)
    print(f"\nFine-tune job submitted: {job_id}")
    print(f"Monitor: python {__file__} --status {job_id}")
    print(f"Expected duration: 10-30 minutes for {TRAINING_FILE.stat().st_size} bytes of training data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
