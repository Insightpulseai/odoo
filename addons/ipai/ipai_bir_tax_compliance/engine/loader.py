"""
Rules Loader - Load tax rules and rates from the module's data directory.

Adapted for Odoo module layout: loads from data/rates/ and data/rules/
relative to the ipai_bir_tax_compliance module root.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml


def _get_module_data_path() -> Path:
    """Return the path to this module's data/ directory."""
    return Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"


class RulesLoader:
    """Load and parse tax rules from YAML configuration files."""

    def __init__(self, data_path: str = None):
        """
        Initialize rules loader.

        Args:
            data_path: Path to the module's data directory. If None,
                       auto-detects from this file's location.
        """
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = _get_module_data_path()

        self.rules_dir = self.data_path / "rules"
        self.rates_dir = self.data_path / "rates"

        # Cached data
        self._rules_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._rates_cache: Dict[str, Dict[str, Any]] = {}

    def load_rules(self, rule_file: str) -> List[Dict[str, Any]]:
        """
        Load tax rules from a YAML file.

        Args:
            rule_file: Rule file name (e.g., 'vat.rules.yaml').

        Returns:
            List of rule dictionaries sorted by priority (descending).

        Raises:
            FileNotFoundError: If the rule file does not exist.
        """
        if rule_file in self._rules_cache:
            return self._rules_cache[rule_file]

        file_path = self.rules_dir / rule_file

        if not file_path.exists():
            raise FileNotFoundError(f"Rule file not found: {file_path}")

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        rules = data.get("rules", [])
        rules.sort(key=lambda r: r.get("priority", 0), reverse=True)

        self._rules_cache[rule_file] = rules
        return rules

    def load_all_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all rule files from the rules directory.

        Returns:
            Dictionary mapping rule file names to rule lists.
        """
        all_rules: Dict[str, List[Dict[str, Any]]] = {}

        if not self.rules_dir.exists():
            return all_rules

        for rule_file in self.rules_dir.glob("*.rules.yaml"):
            rule_name = rule_file.name
            all_rules[rule_name] = self.load_rules(rule_name)

        return all_rules

    def load_rates(self, rates_file: str) -> Dict[str, Any]:
        """
        Load tax rates from a JSON file.

        Args:
            rates_file: Rates file name (e.g., 'ph_rates_2025.json').

        Returns:
            Dictionary of rate data.

        Raises:
            FileNotFoundError: If the rates file does not exist.
        """
        if rates_file in self._rates_cache:
            return self._rates_cache[rates_file]

        file_path = self.rates_dir / rates_file

        if not file_path.exists():
            raise FileNotFoundError(f"Rates file not found: {file_path}")

        with open(file_path, "r") as f:
            rates = json.load(f)

        self._rates_cache[rates_file] = rates
        return rates

    def get_rate_value(
        self, rate_code: str, rates_data: Dict[str, Any]
    ) -> float:
        """
        Extract rate value from rates data by code.

        Args:
            rate_code: Rate code (e.g., 'W010', 'VAT_12_SALES').
            rates_data: Loaded rates dictionary.

        Returns:
            Rate value as decimal (e.g., 0.10 for 10%).
        """
        # Check VAT rates
        if rate_code.startswith("VAT"):
            vat_data = rates_data.get("vat", {})
            if rate_code in ("VAT_12_SALES", "VAT_12_PURCHASE"):
                return vat_data.get("standard_rate", 0.12)
            if rate_code in ("VAT_ZERO_EXPORTS", "VAT_ZERO_PURCHASE"):
                return vat_data.get("zero_rated_exports", 0.00)

        # Check EWT rates
        ewt_data = rates_data.get("expanded_withholding_tax", {})
        if rate_code in ewt_data:
            return ewt_data[rate_code].get("rate", 0.0)

        # Check FWT rates (resident and non_resident subsections)
        fwt_data = rates_data.get("final_withholding_tax", {})
        # Support both flat and nested FWT structure
        if rate_code in fwt_data:
            entry = fwt_data[rate_code]
            if isinstance(entry, dict) and "rate" in entry:
                return entry.get("rate", 0.0)
        for subsection in ("resident", "non_resident"):
            sub = fwt_data.get(subsection, {})
            if rate_code in sub:
                return sub[rate_code].get("rate", 0.0)

        return 0.0

    def clear_cache(self):
        """Clear all cached data."""
        self._rules_cache.clear()
        self._rates_cache.clear()
