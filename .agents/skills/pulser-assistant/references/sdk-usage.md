# SDK Reference: azure-ai-projects in Odoo

This guide covers the implementation of the `azure-ai-projects` SDK within Pulser for Odoo modules.

## Initialization Pattern

Always use `DefaultAzureCredential` for Entra ID authentication in production. Use environmental variables for endpoints.

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

def get_foundry_client():
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        # Fallback to metadata if env not set
        # Load from .foundry/agent-metadata.yaml
        pass
        
    credential = DefaultAzureCredential()
    return AIProjectClient(
        endpoint=endpoint,
        credential=credential
    )
```

## Agent Creation & Execution

The Pulser Assistant uses the `agents` property to manage stateful interactions.

```python
def run_agent_workflow(client, prompt, model_deployment):
    with client:
        # Get OpenAI client via Foundry
        with client.get_openai_client() as openai_client:
            # Create/Retrieve Agent version
            agent = client.agents.create_version(
                agent_name="PulserAssistant",
                definition={
                    "model": model_deployment,
                    "instructions": "You are the Pulser Assistant for Odoo..."
                }
            )
            
            # Create conversation
            conversation = openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            
            # Execute response
            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent_reference": {"name": agent.name, "type": "agent_reference"}
                }
            )
            return response.output_text
```

## Observations & Tracing

Enable tracing in Odoo to harvest gold datasets for evals.

```python
# Enable OpenTelemetry or custom tracing via Foundry
# Refer to Foundry Studio → Observability
```

## Common Models (Foundry Catalog)
- `gpt-4o` (Standard reasoning/orchestration)
- `gpt-4o-mini` (High-speed routing/classification)
- `phi-3.5-moe` (On-device/Edge optimized)
