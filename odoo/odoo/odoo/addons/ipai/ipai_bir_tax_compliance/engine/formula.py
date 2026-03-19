"""
Formula Engine - Evaluate aggregate formulas on computed buckets.

Supports SUM, MAX, MIN, ABS, ROUND functions over named bucket values
and arithmetic expressions for BIR form line computation.
"""

import re
from typing import Any, Dict, List


class FormulaEngine:
    """Evaluate formulas for bucket aggregations and form line computations."""

    def __init__(self):
        """Initialize formula engine with supported functions."""
        self.functions = {
            "SUM": self._func_sum,
            "MAX": self._func_max,
            "MIN": self._func_min,
            "ABS": self._func_abs,
            "ROUND": self._func_round,
        }

    def evaluate(
        self,
        formula: str,
        buckets: Dict[str, float],
        form_lines: Dict[str, float] = None,
    ) -> float:
        """
        Evaluate a formula with access to buckets and form lines.

        Args:
            formula: Formula string (e.g., "SUM(VAT_OUTPUT_12) - SUM(VAT_INPUT_12)").
            buckets: Dictionary of bucket names to values.
            form_lines: Optional dictionary of form line IDs to values.

        Returns:
            Computed result as float.
        """
        if not formula:
            return 0.0

        resolved_formula = self._resolve_references(
            formula, buckets, form_lines or {}
        )
        result = self._evaluate_functions(resolved_formula, buckets)

        # Safe arithmetic evaluation using only numeric operations
        try:
            # Validate that the result string contains only safe characters
            sanitized = result.strip()
            if not re.match(r'^[\d\s\+\-\*\/\.\(\)]+$', sanitized):
                return 0.0
            return float(eval(sanitized))  # noqa: S307 — input is sanitized above
        except Exception:
            return 0.0

    def _resolve_references(
        self,
        formula: str,
        buckets: Dict[str, float],
        form_lines: Dict[str, float],
    ) -> str:
        """Replace form line references with their values."""
        resolved = formula
        for line_id, value in form_lines.items():
            resolved = resolved.replace(line_id, str(value))
        return resolved

    def _evaluate_functions(
        self, formula: str, buckets: Dict[str, float]
    ) -> str:
        """Evaluate function calls like SUM(bucket1, bucket2)."""
        result = formula
        pattern = r'(\w+)\(([\w\s,]+)\)'

        while True:
            match = re.search(pattern, result)
            if not match:
                break

            func_name = match.group(1)
            args_str = match.group(2)
            args = [arg.strip() for arg in args_str.split(",")]

            if func_name in self.functions:
                func_result = self.functions[func_name](args, buckets)
                result = result.replace(match.group(0), str(func_result))
            else:
                break

        return result

    def _func_sum(
        self, args: List[str], buckets: Dict[str, float]
    ) -> float:
        """SUM function - sum all specified buckets."""
        total = 0.0
        for arg in args:
            value = buckets.get(arg, 0.0)
            try:
                total += float(value)
            except (ValueError, TypeError):
                pass
        return total

    def _func_max(
        self, args: List[str], buckets: Dict[str, float]
    ) -> float:
        """MAX function - return maximum value."""
        values = []
        for arg in args:
            if arg in buckets:
                values.append(float(buckets[arg]))
            else:
                try:
                    values.append(float(arg))
                except ValueError:
                    pass
        return max(values) if values else 0.0

    def _func_min(
        self, args: List[str], buckets: Dict[str, float]
    ) -> float:
        """MIN function - return minimum value."""
        values = []
        for arg in args:
            if arg in buckets:
                values.append(float(buckets[arg]))
            else:
                try:
                    values.append(float(arg))
                except ValueError:
                    pass
        return min(values) if values else 0.0

    def _func_abs(
        self, args: List[str], buckets: Dict[str, float]
    ) -> float:
        """ABS function - absolute value."""
        if not args:
            return 0.0
        arg = args[0]
        if arg in buckets:
            value = buckets[arg]
        else:
            try:
                value = float(arg)
            except ValueError:
                return 0.0
        return abs(float(value))

    def _func_round(
        self, args: List[str], buckets: Dict[str, float]
    ) -> float:
        """ROUND function - round to specified decimal places."""
        if len(args) < 2:
            return 0.0
        value_arg = args[0]
        decimals_arg = args[1]
        if value_arg in buckets:
            value = buckets[value_arg]
        else:
            try:
                value = float(value_arg)
            except ValueError:
                return 0.0
        try:
            decimals = int(decimals_arg)
        except ValueError:
            decimals = 2
        return round(float(value), decimals)

    def evaluate_form_lines(
        self,
        mapping: Dict[str, Any],
        buckets: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Evaluate all form lines using mapping configuration.

        Args:
            mapping: Form mapping configuration (from mapping YAML).
            buckets: Computed bucket values.

        Returns:
            Dictionary of form line IDs to computed values.
        """
        form_lines: Dict[str, float] = {}

        for section_key, section_data in mapping.items():
            if not isinstance(section_data, dict) or "lines" not in section_data:
                continue

            lines = section_data.get("lines", [])
            for line in lines:
                line_id = line.get("line")
                bucket_source = line.get("bucket")
                formula = line.get("formula")

                if not line_id:
                    continue

                if bucket_source:
                    form_lines[f"line_{line_id}"] = buckets.get(
                        bucket_source, 0.0
                    )
                elif formula:
                    computed_value = self.evaluate(formula, buckets, form_lines)
                    form_lines[f"line_{line_id}"] = computed_value
                else:
                    form_lines[f"line_{line_id}"] = 0.0

        return form_lines

    def evaluate_aggregation_rules(
        self,
        rules: List[Dict[str, Any]],
        buckets: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Evaluate aggregation rules (priority >= 200) that compute derived buckets.

        Args:
            rules: List of rule dictionaries (filtered to aggregation rules).
            buckets: Current bucket values.

        Returns:
            Updated buckets dictionary with aggregated values.
        """
        for rule in rules:
            priority = rule.get("priority", 0)
            if priority < 200:
                continue

            bucket = rule.get("output_bucket")
            formula = rule.get("formula")

            if not bucket or not formula:
                continue

            computed_value = self.evaluate(formula, buckets)
            buckets[bucket] = computed_value

        return buckets
