"""
Rules Evaluator - JSONLogic evaluation for tax rule conditions.

Evaluates JSONLogic-style conditions against transaction data and applies
tax computation rules (VAT, EWT) to produce bucket amounts.
"""

import re
from typing import Any, Dict, List


class RulesEvaluator:
    """Evaluate JSONLogic conditions and apply tax rules to transactions."""

    def __init__(self):
        """Initialize rules evaluator with supported operators."""
        self.supported_operators = {
            "==": self._op_equal,
            "!=": self._op_not_equal,
            ">": self._op_greater,
            ">=": self._op_greater_equal,
            "<": self._op_less,
            "<=": self._op_less_equal,
            "and": self._op_and,
            "or": self._op_or,
            "in": self._op_in,
            "var": self._op_var,
            "if": self._op_if,
            "+": self._op_add,
            "-": self._op_subtract,
            "*": self._op_multiply,
            "/": self._op_divide,
            "always": lambda data, args: True,
        }

    def evaluate_condition(
        self, condition: Dict[str, Any], data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a JSONLogic condition against transaction data.

        Args:
            condition: JSONLogic condition dictionary.
            data: Transaction data dictionary.

        Returns:
            True if condition matches, False otherwise.
        """
        if not condition:
            return True

        # Handle "always: true" special case
        if condition.get("always") is True:
            return True

        # Get the operator (first key in condition dict)
        operator = next(iter(condition))
        args = condition[operator]

        if operator not in self.supported_operators:
            raise ValueError(f"Unsupported operator: {operator}")

        return self.supported_operators[operator](data, args)

    def _op_var(self, data: Dict[str, Any], args: Any) -> Any:
        """Variable lookup: {"var": "field_name"} -> data["field_name"]."""
        if isinstance(args, str):
            return data.get(args)
        return None

    def _op_equal(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Equality: {"==": [{"var": "field"}, "value"]}."""
        if len(args) != 2:
            return False
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        return left == right

    def _op_not_equal(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Not equal operator."""
        return not self._op_equal(data, args)

    def _op_greater(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Greater than operator."""
        if len(args) != 2:
            return False
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) > float(right)
        except (ValueError, TypeError):
            return False

    def _op_greater_equal(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Greater than or equal operator."""
        if len(args) != 2:
            return False
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) >= float(right)
        except (ValueError, TypeError):
            return False

    def _op_less(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Less than operator."""
        if len(args) != 2:
            return False
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) < float(right)
        except (ValueError, TypeError):
            return False

    def _op_less_equal(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Less than or equal operator."""
        if len(args) != 2:
            return False
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) <= float(right)
        except (ValueError, TypeError):
            return False

    def _op_and(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Logical AND: {"and": [condition1, condition2, ...]}."""
        for condition in args:
            if isinstance(condition, dict):
                if not self.evaluate_condition(condition, data):
                    return False
            elif not self._resolve_value(data, condition):
                return False
        return True

    def _op_or(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """Logical OR: {"or": [condition1, condition2, ...]}."""
        for condition in args:
            if isinstance(condition, dict):
                if self.evaluate_condition(condition, data):
                    return True
            elif self._resolve_value(data, condition):
                return True
        return False

    def _op_in(self, data: Dict[str, Any], args: List[Any]) -> bool:
        """IN operator: {"in": [{"var": "field"}, ["value1", "value2"]]}."""
        if len(args) != 2:
            return False
        value = self._resolve_value(data, args[0])
        array = self._resolve_value(data, args[1])
        if not isinstance(array, list):
            return False
        return value in array

    def _op_if(self, data: Dict[str, Any], args: List[Any]) -> Any:
        """IF operator (ternary): {"if": [condition, true_val, false_val]}."""
        if len(args) < 2:
            return None
        condition = (
            self.evaluate_condition(args[0], data)
            if isinstance(args[0], dict)
            else self._resolve_value(data, args[0])
        )
        if condition:
            return self._resolve_value(data, args[1]) if len(args) > 1 else True
        return self._resolve_value(data, args[2]) if len(args) > 2 else False

    def _op_add(self, data: Dict[str, Any], args: List[Any]) -> float:
        """Addition operator."""
        values = [self._resolve_value(data, arg) for arg in args]
        try:
            return sum(float(v) for v in values if v is not None)
        except (ValueError, TypeError):
            return 0.0

    def _op_subtract(self, data: Dict[str, Any], args: List[Any]) -> float:
        """Subtraction operator."""
        if len(args) != 2:
            return 0.0
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) - float(right)
        except (ValueError, TypeError):
            return 0.0

    def _op_multiply(self, data: Dict[str, Any], args: List[Any]) -> float:
        """Multiplication operator."""
        if len(args) != 2:
            return 0.0
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            return float(left) * float(right)
        except (ValueError, TypeError):
            return 0.0

    def _op_divide(self, data: Dict[str, Any], args: List[Any]) -> float:
        """Division operator (safe: returns 0.0 on division by zero)."""
        if len(args) != 2:
            return 0.0
        left = self._resolve_value(data, args[0])
        right = self._resolve_value(data, args[1])
        try:
            right_float = float(right)
            if right_float == 0:
                return 0.0
            return float(left) / right_float
        except (ValueError, TypeError):
            return 0.0

    def _resolve_value(self, data: Dict[str, Any], value: Any) -> Any:
        """Resolve a value: literal, variable reference, or nested expression."""
        if isinstance(value, dict):
            if "var" in value:
                return self._op_var(data, value["var"])
            operator = next(iter(value))
            args = value[operator]
            if operator in self.supported_operators:
                return self.supported_operators[operator](data, args)
        return value

    def regex_match(self, text: str, pattern: str) -> bool:
        """Check if text matches a regex pattern."""
        try:
            return bool(re.match(pattern, str(text)))
        except re.error:
            return False

    def apply_rules(
        self,
        rules: List[Dict[str, Any]],
        transaction: Dict[str, Any],
        rates_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Apply all rules to a transaction and return computed buckets.

        Args:
            rules: List of rule dictionaries.
            transaction: Transaction data.
            rates_data: Optional rates data for rate lookups.

        Returns:
            Dictionary with 'buckets' (name -> amount) and 'matched_rules'.
        """
        buckets: Dict[str, float] = {}
        matched_rules: List[Dict[str, Any]] = []

        for rule in rules:
            condition = rule.get("condition", {})

            if self.evaluate_condition(condition, transaction):
                matched_rules.append(rule)

                bucket = rule.get("output_bucket")
                formula = rule.get("formula")
                base_source = rule.get("base_source")
                rate_value = rule.get("rate_value", 0.0)

                if not bucket:
                    continue

                # Compute amount based on formula
                if formula == "base * rate":
                    base = transaction.get(base_source, 0.0)
                    amount = float(base) * float(rate_value)
                elif formula == "base":
                    base = transaction.get(base_source, 0.0)
                    amount = float(base)
                else:
                    # Aggregate formula — handled by FormulaEngine
                    amount = 0.0

                if bucket in buckets:
                    buckets[bucket] += amount
                else:
                    buckets[bucket] = amount

        return {
            "buckets": buckets,
            "matched_rules": matched_rules,
        }
