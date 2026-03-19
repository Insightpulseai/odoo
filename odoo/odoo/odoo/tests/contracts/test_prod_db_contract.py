"""Contract test: Production DB must be 'odoo', never 'odoo_prod'."""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProdDbContract(unittest.TestCase):
    """Ensure config files pin production DB to 'odoo'."""

    def _read(self, rel_path):
        path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(path):
            self.skipTest(f"{rel_path} not found")
        with open(path) as f:
            return f.read()

    def test_azure_conf_db_name(self):
        content = self._read("config/azure/odoo.conf")
        self.assertIn("db_name = odoo", content)
        self.assertNotIn("db_name = odoo_prod", content)

    def test_azure_conf_dbfilter(self):
        content = self._read("config/azure/odoo.conf")
        self.assertIn("dbfilter = ^odoo$", content)
        self.assertNotIn("odoo_prod", content)

    def test_prod_conf_db_name(self):
        content = self._read("config/prod/odoo.conf")
        self.assertIn("db_name = odoo", content)
        self.assertNotIn("db_name = odoo_prod", content)

    def test_prod_conf_dbfilter(self):
        content = self._read("config/prod/odoo.conf")
        self.assertIn("dbfilter = ^odoo$", content)

    def test_no_active_odoo_prod_references(self):
        """Scan active config/docs for stale odoo_prod references."""
        active_paths = [
            "config/azure/odoo.conf",
            "config/prod/odoo.conf",
        ]
        for rel_path in active_paths:
            content = self._read(rel_path)
            matches = [
                line.strip()
                for line in content.splitlines()
                if "odoo_prod" in line and not line.strip().startswith(";")
            ]
            self.assertEqual(
                matches,
                [],
                f"{rel_path} contains active odoo_prod reference: {matches}",
            )


if __name__ == "__main__":
    unittest.main()
