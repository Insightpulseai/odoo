"""Foundry project client + OpenAI-compatible client live smoke test.

Validates the current Foundry SDK v2 pattern:
  AIProjectClient(endpoint, credential) → get_openai_client() → responses.create()

Requires env vars:
  FOUNDRY_PROJECT_ENDPOINT — Azure AI Foundry project endpoint
  FOUNDRY_MODEL — Model deployment name (e.g. gpt-4.1)

Run:  FOUNDRY_PROJECT_ENDPOINT=... FOUNDRY_MODEL=... pytest -xvs
CI:   azure_staging_revision gate
"""

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from .conftest import require_env


def test_foundry_project_client_and_openai_client_smoke():
    require_env("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL")

    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    with project_client.get_openai_client() as openai_client:
        response = openai_client.responses.create(
            model=os.environ["FOUNDRY_MODEL"],
            input="Reply with the single token OK.",
        )

    assert response is not None
    assert getattr(response, "output_text", None)
