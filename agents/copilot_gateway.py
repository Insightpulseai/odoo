# agents/copilot_gateway.py
"""
Pulser for Odoo — Copilot Gateway (Normalized)
==============================================
Authoritative entry point for M365 (Teams/Outlook) distribution.
Orchestrates Diva routing to specialized Foundry-native agents.

SDK: azure-ai-projects v2
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# N3: Enable monitoring (Telemetry)
configure_azure_monitor()
tracer = trace.get_tracer(__name__)

# Authoritative Metadata (from ssot/ai/agents.yaml)
PROJECT_ENDPOINT = "https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot"

class PulserGateway:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=self.credential
        )
        self.openai_client = self.client.get_openai_client()

    async def handle_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point for Bot Framework Activity payloads."""
        with tracer.start_as_current_span("handle_activity") as span:
            intent = self._detect_intent(activity)
            # Step 1: Initial Response
            agent_name = self._diva_route(intent)
            response = await self._get_agent_response(agent_name, activity)
            
            # Step 2: Agentic Self-Correction (Phase 36)
            verified_response = await self._verify_and_correct(agent_name, activity, response)
            
            return verified_response

    async def _verify_and_correct(self, agent_name: str, activity: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """Implements the Stop-and-Think self-correction loop."""
        with tracer.start_as_current_span("verify_and_correct") as span:
            score = self._calculate_groundedness(response)
            span.set_attribute("pulser.self_correction.score", score)
            
            if score < 0.8:
                logging.warning(f"Low groundedness ({score}) detected. Attempting self-correction.")
                span.set_attribute("pulser.self_correction.attempt", 1)
                
                # N4: Automatic Re-probe
                corrected_response = await self._get_agent_response(
                    agent_name, 
                    activity, 
                    extra_instructions="[RE-TRY: LOW_GROUNDEDNESS] Please verify your figures against Odoo truth."
                )
                return corrected_response
            
            return response

    def _calculate_groundedness(self, response: Dict[str, Any]) -> float:
        """
        Simulates the Azure AI Inference groundedness check.
        In production, this calls the N4 Eval service.
        """
        text = response.get("text", "")
        # Heuristic: hallu-check (e.g. check if numbers are present but no Odoo refs)
        if "₱" in text and "INV/" not in text:
            return 0.7  # Potential hallucination
        return 0.95

    def _detect_intent(self, activity: Dict[str, Any]) -> str:
        """Simple intent detection - mapped to 'Diva' profiles."""
        text = activity.get("text", "").lower()
        if any(w in text for w in ["approve", "post", "create", "update"]):
            return "transaction"
        elif any(w in text for w in ["draft", "email", "report"]):
            return "authoring"
        return "ask"

    def _diva_route(self, intent: str) -> str:
        """Maps intent to the 5 specialized Foundry-native agents."""
        mapping = {
            "transaction": "pulser-odoo-transaction",
            "authoring": "pulser-odoo-authoring",
            "ask": "pulser-odoo-ask"
        }
        return mapping.get(intent, "pulser-odoo")

    async def _get_agent_response(self, agent_name: str, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Calls the Foundry Agent Service with SDK v2 agent_reference."""
        # Note: Actually calling the project's OpenAI client with the agent_reference
        # Mocking the call for local validation
        logging.info(f"Routing to Foundry Agent: {agent_name}")
        
        # Implementation of m365-copilot-streaming-contract would go here
        return {
            "type": "message",
            "text": f"Response from {agent_name} for intent.",
            "recipient": activity.get("from", {}),
            "serviceUrl": activity.get("serviceUrl")
        }

class M365ActivityAdapter:
    """Translation layer between M365 Activity and Pulser Reasoning."""
    
    @staticmethod
    def to_reasoning_prompt(activity: Dict[str, Any]) -> str:
        """Extracts text content for the reasoning plane."""
        return activity.get("text", "")

    @staticmethod
    def from_reasoning_output(output: str) -> Dict[str, Any]:
        """Wraps reasoning output into a Bot Framework Activity."""
        return {
            "type": "message",
            "text": output
        }

if __name__ == "__main__":
    # Local Smoke Test
    logging.basicConfig(level=logging.INFO)
    gateway = PulserGateway()
    
    mock_activity = {
        "type": "message",
        "text": "Approve the withholding tax for Acme Corp",
        "from": {"id": "user123", "name": "Relationship Manager"},
        "serviceUrl": "https://teams.microsoft.com/v3"
    }
    
    async def main():
        response = await gateway.handle_activity(mock_activity)
        print(json.dumps(response, indent=2))

    asyncio.run(main())
