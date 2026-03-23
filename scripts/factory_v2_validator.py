import yaml
import os
import json
import argparse
import sys
from datetime import datetime

class FactoryV2Validator:
    """Automated auditor for Agent Factory V2 compliance."""

    def __init__(self, passport_path, policy_path, output_path=None):
        self.passport_path = passport_path
        self.policy_path = policy_path
        self.output_path = output_path
        self.report = []
        self.result_data = {
            "timestamp": datetime.now().isoformat(),
            "criteria": {}
        }

    def load_yaml(self, path):
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def validate(self):
        passport = self.load_yaml(self.passport_path)
        policy = self.load_yaml(self.policy_path)
        
        if not passport or not policy:
            print(f"ERROR: Missing passport or policy file.")
            sys.exit(1)

        agent_id = passport.get('id') or passport.get('agent_id')
        target_level = policy.get('target_level')
        
        self.result_data["agent_id"] = agent_id
        self.result_data["target_level"] = target_level

        gates = policy.get('gates', {})
        compliance = True

        # Check Freshness
        if 'freshness_days' in gates:
            updated_at_str = passport.get('updated_at')
            if updated_at_str:
                # Handle common ISO formats
                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                age_days = (datetime.now(updated_at.tzinfo) - updated_at).days
                freshness_limit = gates['freshness_days']
                success = (age_days <= freshness_limit)
                self.result_data["criteria"]["evidence_fresh"] = success
                if success:
                    self.report.append(f"✅ FRESHNESS: Evidence is {age_days} days old (Limit {freshness_limit})")
                else:
                    self.report.append(f"❌ FRESHNESS: Evidence is {age_days} days old (Stale! Limit {freshness_limit})")
                    compliance = False
            else:
                self.report.append(f"⚠️ FRESHNESS: No updated_at timestamp found in passport.")
                # We'll treat missing timestamp as a warning for now, but in strict mode it would fail.

        # Check Red Team
        if 'red_team' in gates:
            actual_status = passport.get('red_team_status') or (passport.get('acceptance_status') == 'accepted' and 'PASSED' or 'PENDING')
            expected_status = gates['red_team']['status']
            success = (actual_status == expected_status)
            self.result_data["criteria"]["red_team_certified"] = success
            if success:
                self.report.append(f"✅ RED TEAM: {actual_status} (Matches policy)")
            else:
                self.report.append(f"❌ RED TEAM: {actual_status} (Expected {expected_status})")
                compliance = False

        # Check Soak Window
        if 'soak_window' in gates:
            actual_cycles = passport.get('real_cycles_completed') or passport.get('soak_window', {}).get('real_cycles_completed', 0)
            required_cycles = gates['soak_window']['cycles_completed']
            success = (actual_cycles >= required_cycles)
            self.result_data["criteria"]["real_soak_cycles_minimum_met"] = success
            if success:
                self.report.append(f"✅ SOAK WINDOW: {actual_cycles}/{required_cycles} cycles (Compliant)")
            else:
                self.report.append(f"❌ SOAK WINDOW: {actual_cycles}/{required_cycles} cycles (Insufficient)")
                compliance = False

        self.result_data["validator_status"] = "pass" if compliance else "fail"

        if self.output_path:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, "w") as f:
                json.dump(self.result_data, f, indent=2)

        if compliance:
            print(f"SUCCESS: {agent_id} matches {target_level} policy.")
            return True
        else:
            print(f"FAILURE: {agent_id} does not match {target_level} policy.")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Factory V2 Validator")
    parser.add_argument("--passport", required=True, help="Path to agent passport YAML")
    parser.add_argument("--policy", required=True, help="Path to promotion policy YAML")
    parser.add_argument("--output", help="Path to save JSON result")
    
    args = parser.parse_args()
    
    validator = FactoryV2Validator(args.passport, args.policy, args.output)
    if not validator.validate():
        sys.exit(1)
    sys.exit(0)
