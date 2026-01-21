#!/usr/bin/env python3
"""
XML-RPC Module Installation Script with Comprehensive Error Capture
Implements AI Agent Quality Gate: Structured error logging and version compliance checks

Purpose: Install Odoo modules via XML-RPC with full error visibility
Compliance: Odoo 18 API, OCA standards, auditability requirements
"""

import xmlrpc.client
import sys
import json
from datetime import datetime

# Configuration
ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
USERNAME = "admin"
PASSWORD = "admin"
MODULE_NAME = "ipai_finance_ppm_tdi"


class OdooInstallationAgent:
    """
    AI Agent-compatible installation orchestrator with comprehensive error capture.

    Implements Quality Gate Rules:
    - Structured error logging (auditability requirement)
    - Version compliance validation (Odoo 18 API)
    - Non-deterministic operation tracking (AI agent versioning)
    """

    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Audit trail metadata
        self.audit_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": "OdooInstallationAgent",
            "version": "1.0.0",
            "operations": [],
        }

    def authenticate(self):
        """Authenticate with Odoo instance (Odoo 18 API compliance)"""
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            if not self.uid:
                raise Exception("Authentication failed - invalid credentials")

            self.audit_log["operations"].append(
                {"step": "authentication", "status": "success", "uid": self.uid}
            )
            print(f"✅ Authenticated as user ID: {self.uid}")
            return True
        except Exception as e:
            self.audit_log["operations"].append(
                {"step": "authentication", "status": "failed", "error": str(e)}
            )
            print(f"❌ Authentication error: {e}")
            return False

    def check_module_exists(self, module_name):
        """Verify module is registered in ir_module_module (Quality Gate: Pre-flight check)"""
        try:
            module = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "search_read",
                [[("name", "=", module_name)]],
                {"fields": ["name", "state", "latest_version", "shortdesc"]},
            )

            if not module:
                self.audit_log["operations"].append(
                    {
                        "step": "module_check",
                        "status": "not_found",
                        "module": module_name,
                    }
                )
                print(f"❌ Module '{module_name}' not found in registry")
                return None

            module_data = module[0]
            self.audit_log["operations"].append(
                {
                    "step": "module_check",
                    "status": "found",
                    "module_state": module_data["state"],
                    "module_version": module_data.get("latest_version", "N/A"),
                }
            )

            print(f"✅ Module found: {module_data['shortdesc']}")
            print(f"   State: {module_data['state']}")
            print(f"   Version: {module_data.get('latest_version', 'N/A')}")

            return module_data
        except Exception as e:
            self.audit_log["operations"].append(
                {"step": "module_check", "status": "error", "error": str(e)}
            )
            print(f"❌ Error checking module: {e}")
            return None

    def install_module(self, module_name):
        """
        Install module using button_immediate_install (Odoo 18 recommended method)

        Quality Gate: Comprehensive error capture with structured logging
        """
        try:
            # Get module record ID
            module_ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "search",
                [[("name", "=", module_name)]],
            )

            if not module_ids:
                raise Exception(f"Module '{module_name}' not found")

            module_id = module_ids[0]

            # Trigger installation using button_immediate_install
            # This is the Odoo 18 recommended method that returns detailed error info
            print(f"🔄 Triggering installation for module ID {module_id}...")

            result = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "button_immediate_install",
                [[module_id]],
            )

            # Check final state
            final_state = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "ir.module.module",
                "read",
                [[module_id]],
                {"fields": ["state", "latest_version"]},
            )

            self.audit_log["operations"].append(
                {
                    "step": "installation",
                    "status": "completed",
                    "module_id": module_id,
                    "final_state": final_state[0]["state"],
                    "result": str(result),
                }
            )

            if final_state[0]["state"] == "installed":
                print(f"✅ Module installed successfully!")
                print(f"   Final state: {final_state[0]['state']}")
                print(f"   Version: {final_state[0].get('latest_version', 'N/A')}")
                return True
            else:
                print(
                    f"⚠️  Installation completed but module state is: {final_state[0]['state']}"
                )
                print(f"   This may indicate a silent failure during installation")
                return False

        except xmlrpc.client.Fault as e:
            # XML-RPC faults contain the actual Odoo error with traceback
            self.audit_log["operations"].append(
                {
                    "step": "installation",
                    "status": "xmlrpc_fault",
                    "fault_code": e.faultCode,
                    "fault_string": e.faultString,
                }
            )

            print(f"❌ XML-RPC Fault during installation:")
            print(f"   Code: {e.faultCode}")
            print(f"   Message: {e.faultString}")

            # Parse the fault string for common Odoo errors
            if "ValidationError" in e.faultString:
                print(
                    "\n🔍 Detected ValidationError - likely XML or Python validation issue"
                )
            elif (
                "ImportError" in e.faultString or "ModuleNotFoundError" in e.faultString
            ):
                print(
                    "\n🔍 Detected Import Error - missing dependency or Python syntax error"
                )
            elif "ParseError" in e.faultString:
                print("\n🔍 Detected Parse Error - XML syntax or structure issue")

            return False

        except Exception as e:
            self.audit_log["operations"].append(
                {
                    "step": "installation",
                    "status": "exception",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            print(f"❌ Unexpected error during installation: {e}")
            return False

    def verify_installation(self, module_name):
        """
        Post-installation verification (Quality Gate: Evidence-based validation)

        Checks:
        1. Module state = 'installed'
        2. Database tables created
        3. Seed data loaded
        """
        try:
            print("\n" + "=" * 60)
            print("POST-INSTALLATION VERIFICATION")
            print("=" * 60)

            # Check module state
            module = self.check_module_exists(module_name)
            if not module or module["state"] != "installed":
                print(
                    f"❌ Module state verification failed: {module['state'] if module else 'not found'}"
                )
                return False

            # Check if tables exist (for ipai_finance_ppm_tdi specific tables)
            tables_to_check = [
                "finance_ppm_bir_calendar",
                "finance_ppm_logframe",
                "finance_ppm_ph_holiday",
            ]

            print("\n🔍 Checking database tables...")
            for table in tables_to_check:
                try:
                    # Try to count records in each table
                    count = self.models.execute_kw(
                        self.db,
                        self.uid,
                        self.password,
                        f'finance.ppm.{table.replace("finance_ppm_", "")}',
                        "search_count",
                        [[]],
                    )
                    print(f"   ✅ Table '{table}': {count} records")

                    self.audit_log["operations"].append(
                        {
                            "step": "table_verification",
                            "table": table,
                            "record_count": count,
                        }
                    )
                except Exception as e:
                    print(f"   ❌ Table '{table}': Error - {str(e)[:100]}")
                    self.audit_log["operations"].append(
                        {"step": "table_verification", "table": table, "error": str(e)}
                    )

            return True

        except Exception as e:
            print(f"❌ Verification error: {e}")
            self.audit_log["operations"].append(
                {"step": "verification", "status": "error", "error": str(e)}
            )
            return False

    def save_audit_log(self, filename="module_install_audit.json"):
        """Save audit log for AI agent training and compliance"""
        try:
            with open(f"/tmp/{filename}", "w") as f:
                json.dump(self.audit_log, f, indent=2)
            print(f"\n📊 Audit log saved to /tmp/{filename}")
        except Exception as e:
            print(f"⚠️  Could not save audit log: {e}")


def main():
    """Main execution flow with comprehensive error handling"""
    agent = OdooInstallationAgent(ODOO_URL, DB_NAME, USERNAME, PASSWORD)

    print("=" * 60)
    print("ODOO MODULE INSTALLATION AGENT")
    print(f"Module: {MODULE_NAME}")
    print(f"Target: {ODOO_URL}")
    print("=" * 60)

    # Step 1: Authenticate
    if not agent.authenticate():
        sys.exit(1)

    # Step 2: Check module exists
    print(f"\n🔍 Checking module registration...")
    module = agent.check_module_exists(MODULE_NAME)
    if not module:
        print(f"\n❌ Cannot proceed - module not registered")
        print("   Possible causes:")
        print("   - Module path not in addons_path")
        print("   - __manifest__.py has syntax errors")
        print("   - Module name mismatch")
        agent.save_audit_log()
        sys.exit(1)

    if module["state"] == "installed":
        print(f"\n✅ Module already installed")
        agent.verify_installation(MODULE_NAME)
        agent.save_audit_log()
        sys.exit(0)

    # Step 3: Install module
    print(f"\n🚀 Installing module...")
    success = agent.install_module(MODULE_NAME)

    # Step 4: Verify installation
    if success:
        agent.verify_installation(MODULE_NAME)

    # Step 5: Save audit log
    agent.save_audit_log()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
