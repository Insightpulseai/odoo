import os
import sys
import unittest
from unittest.mock import MagicMock

# Mocking env before import
os.environ["PFP_APP_ID"] = "bc200-pfp"
os.environ["AZURE_FOUNDRY_ENDPOINT"] = "http://localhost"

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from main import AGENT_ROUTING

class TestBotRouting(unittest.TestCase):
    def test_specialist_mapping(self):
        # Case 1: Known Specialist ID
        self.assertEqual(AGENT_ROUTING.get("bc200-pfp"), "project_finance")
        
        # Case 2: Unknown ID (Should Fallback or be handled in messages)
        # Note: main.py uses AGENT_ROUTING.get(recipient_id, "odoo_sage")
        self.assertIsNone(AGENT_ROUTING.get("unknown"))

if __name__ == "__main__":
    unittest.main()
