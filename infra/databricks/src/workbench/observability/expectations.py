"""Data quality expectations framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, lit, when

from workbench.config.logging import get_logger

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = get_logger(__name__)


class ExpectationType(Enum):
    """Types of data quality expectations."""

    NOT_NULL = "not_null"
    UNIQUE = "unique"
    IN_SET = "in_set"
    RANGE = "range"
    PATTERN = "pattern"
    CUSTOM = "custom"


@dataclass
class Expectation:
    """A data quality expectation."""

    name: str
    type: ExpectationType
    column: str | None = None
    columns: list[str] | None = None
    values: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None
    sql: str | None = None
    threshold: float = 0.0  # Allowed failure percentage


@dataclass
class ExpectationResult:
    """Result of running an expectation."""

    expectation: Expectation
    passed: bool
    total_rows: int
    failed_rows: int
    failure_percentage: float
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _evaluate_not_null(df: DataFrame, exp: Expectation) -> ExpectationResult:
    """Evaluate NOT NULL expectation."""
    total = df.count()
    failed = df.filter(col(exp.column).isNull()).count()
    failure_pct = (failed / total * 100) if total > 0 else 0
    passed = failure_pct <= exp.threshold

    return ExpectationResult(
        expectation=exp,
        passed=passed,
        total_rows=total,
        failed_rows=failed,
        failure_percentage=failure_pct,
    )


def _evaluate_unique(df: DataFrame, exp: Expectation) -> ExpectationResult:
    """Evaluate UNIQUE expectation."""
    columns = exp.columns or [exp.column]
    total = df.count()
    distinct = df.select(*columns).distinct().count()
    failed = total - distinct
    failure_pct = (failed / total * 100) if total > 0 else 0
    passed = failure_pct <= exp.threshold

    return ExpectationResult(
        expectation=exp,
        passed=passed,
        total_rows=total,
        failed_rows=failed,
        failure_percentage=failure_pct,
    )


def _evaluate_in_set(df: DataFrame, exp: Expectation) -> ExpectationResult:
    """Evaluate IN_SET expectation."""
    total = df.count()
    failed = df.filter(~col(exp.column).isin(exp.values)).count()
    failure_pct = (failed / total * 100) if total > 0 else 0
    passed = failure_pct <= exp.threshold

    return ExpectationResult(
        expectation=exp,
        passed=passed,
        total_rows=total,
        failed_rows=failed,
        failure_percentage=failure_pct,
    )


def _evaluate_range(df: DataFrame, exp: Expectation) -> ExpectationResult:
    """Evaluate RANGE expectation."""
    total = df.count()
    conditions = []
    if exp.min_value is not None:
        conditions.append(col(exp.column) < exp.min_value)
    if exp.max_value is not None:
        conditions.append(col(exp.column) > exp.max_value)

    if conditions:
        from functools import reduce
        from operator import or_

        failed = df.filter(reduce(or_, conditions)).count()
    else:
        failed = 0

    failure_pct = (failed / total * 100) if total > 0 else 0
    passed = failure_pct <= exp.threshold

    return ExpectationResult(
        expectation=exp,
        passed=passed,
        total_rows=total,
        failed_rows=failed,
        failure_percentage=failure_pct,
    )


def run_expectations(
    df: DataFrame, expectations: list[Expectation]
) -> list[ExpectationResult]:
    """Run a set of expectations against a DataFrame.

    Args:
        df: DataFrame to validate
        expectations: List of expectations to run

    Returns:
        List of expectation results
    """
    results = []

    for exp in expectations:
        logger.info(f"Evaluating expectation: {exp.name}")

        if exp.type == ExpectationType.NOT_NULL:
            result = _evaluate_not_null(df, exp)
        elif exp.type == ExpectationType.UNIQUE:
            result = _evaluate_unique(df, exp)
        elif exp.type == ExpectationType.IN_SET:
            result = _evaluate_in_set(df, exp)
        elif exp.type == ExpectationType.RANGE:
            result = _evaluate_range(df, exp)
        else:
            logger.warning(f"Unsupported expectation type: {exp.type}")
            continue

        results.append(result)
        status = "PASSED" if result.passed else "FAILED"
        logger.info(
            f"  {status}: {result.failed_rows}/{result.total_rows} "
            f"({result.failure_percentage:.2f}%)"
        )

    return results
