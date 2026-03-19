"""Silver layer data quality checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, lit, sum as spark_sum, when

from workbench.config.logging import get_logger

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = get_logger(__name__)


@dataclass
class QualityCheckResult:
    """Result of a data quality check."""

    check_name: str
    table_name: str
    passed: bool
    total_rows: int
    failed_rows: int
    failure_percentage: float
    details: str | None = None


def check_not_null(df: DataFrame, columns: list[str], table_name: str) -> list[QualityCheckResult]:
    """Check that specified columns are not null.

    Args:
        df: DataFrame to check
        columns: Columns that should not be null
        table_name: Name of the table for reporting

    Returns:
        List of check results
    """
    results = []
    total_rows = df.count()

    for column in columns:
        null_count = df.filter(col(column).isNull()).count()
        passed = null_count == 0
        failure_pct = (null_count / total_rows * 100) if total_rows > 0 else 0

        results.append(
            QualityCheckResult(
                check_name=f"not_null_{column}",
                table_name=table_name,
                passed=passed,
                total_rows=total_rows,
                failed_rows=null_count,
                failure_percentage=failure_pct,
            )
        )

    return results


def check_unique(df: DataFrame, columns: list[str], table_name: str) -> QualityCheckResult:
    """Check that specified columns form a unique key.

    Args:
        df: DataFrame to check
        columns: Columns that should be unique together
        table_name: Name of the table for reporting

    Returns:
        Check result
    """
    total_rows = df.count()
    distinct_rows = df.select(*columns).distinct().count()
    duplicate_rows = total_rows - distinct_rows
    passed = duplicate_rows == 0
    failure_pct = (duplicate_rows / total_rows * 100) if total_rows > 0 else 0

    return QualityCheckResult(
        check_name=f"unique_{'_'.join(columns)}",
        table_name=table_name,
        passed=passed,
        total_rows=total_rows,
        failed_rows=duplicate_rows,
        failure_percentage=failure_pct,
    )


def check_referential_integrity(
    df: DataFrame,
    ref_df: DataFrame,
    column: str,
    ref_column: str,
    table_name: str,
    ref_table_name: str,
) -> QualityCheckResult:
    """Check referential integrity between tables.

    Args:
        df: Source DataFrame
        ref_df: Reference DataFrame
        column: Column in source table
        ref_column: Column in reference table
        table_name: Name of source table
        ref_table_name: Name of reference table

    Returns:
        Check result
    """
    total_rows = df.count()

    # Get orphaned rows (source values not in reference)
    orphaned = df.join(
        ref_df.select(col(ref_column).alias("_ref_key")),
        df[column] == col("_ref_key"),
        "left_anti",
    )
    orphaned_count = orphaned.count()

    passed = orphaned_count == 0
    failure_pct = (orphaned_count / total_rows * 100) if total_rows > 0 else 0

    return QualityCheckResult(
        check_name=f"fk_{column}_to_{ref_table_name}",
        table_name=table_name,
        passed=passed,
        total_rows=total_rows,
        failed_rows=orphaned_count,
        failure_percentage=failure_pct,
        details=f"References {ref_table_name}.{ref_column}",
    )


def run_quality_checks(
    spark: SparkSession, table_name: str, checks: list[dict]
) -> list[QualityCheckResult]:
    """Run a set of quality checks on a table.

    Args:
        spark: Spark session
        table_name: Fully qualified table name
        checks: List of check configurations

    Returns:
        List of check results
    """
    logger.info(f"Running quality checks on {table_name}")
    df = spark.read.format("delta").table(table_name)
    results: list[QualityCheckResult] = []

    for check in checks:
        check_type = check["type"]

        if check_type == "not_null":
            results.extend(check_not_null(df, check["columns"], table_name))
        elif check_type == "unique":
            results.append(check_unique(df, check["columns"], table_name))
        elif check_type == "referential_integrity":
            ref_df = spark.read.format("delta").table(check["ref_table"])
            results.append(
                check_referential_integrity(
                    df,
                    ref_df,
                    check["column"],
                    check["ref_column"],
                    table_name,
                    check["ref_table"],
                )
            )

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    logger.info(f"Quality checks complete: {passed}/{total} passed")

    return results
