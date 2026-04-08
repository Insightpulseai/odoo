import subprocess
import sys
import os
import yaml

def run_gate(agent_id, passport_path, policy_path):
    print(f"--- RELEASE GATE START: {agent_id} ---")
    
    output_path = f"/Users/tbwa/Documents/GitHub/Insightpulseai/docs/evidence/2026-03-20/agent-factory-v2/{agent_id}-validator-result.json"
    
    cmd = [
        "python3", "/Users/tbwa/Documents/GitHub/Insightpulseai/scripts/factory_v2_validator.py",
        "--passport", passport_path,
        "--policy", policy_path,
        "--output", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"PROMOTION PERMITTED: Validator passed for {agent_id}.")
        print(f"Result saved to {output_path}")
        return True
    else:
        print(f"PROMOTION BLOCKED: Validator failed for {agent_id}.")
        print(result.stdout)
        print(result.stderr)
        return False

if __name__ == "__main__":
    # Test with Bank Recon
    run_gate(
        "bank-reconciliation-agent",
        "/Users/tbwa/Documents/GitHub/Insightpulseai/agents/passports/bank-reconciliation-agent.yaml",
        "/Users/tbwa/Documents/GitHub/Insightpulseai/agents/policies/bank-reconciliation-v2.yaml"
    )
    
    # Test with AP Invoice
    run_gate(
        "ap-invoice-agent",
        "/Users/tbwa/Documents/GitHub/Insightpulseai/agents/passports/ap-invoice-agent.yaml",
        "/Users/tbwa/Documents/GitHub/Insightpulseai/agents/policies/ap-invoice-v2.yaml"
    )
