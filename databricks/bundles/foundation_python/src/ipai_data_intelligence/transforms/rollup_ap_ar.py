"""Rollup — AP / AR / Cash Summary (Silver → Gold).

Uses silver.vendor_bills, silver.invoices, and silver.payments to
compute a daily AP, AR, and net cash position snapshot.

Usage::

    from ipai_data_intelligence.transforms.rollup_ap_ar import (
        build_ap_ar_cash_summary,
    )
    build_ap_ar_cash_summary(spark)
"""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    coalesce,
    col,
    current_timestamp,
    lit,
    sum as spark_sum,
)

CATALOG = "dbw_ipai_dev"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"


def build_ap_ar_cash_summary(spark: SparkSession) -> DataFrame:
    """Materialise ``gold.ap_ar_cash_summary``.

    Produces one row per date with:

    - ``date``
    - ``ap_outstanding`` — vendor bills not yet paid, due on or before date
    - ``ar_outstanding`` — invoices not yet paid, due on or before date
    - ``inbound_payments`` — sum of inbound payments on date
    - ``outbound_payments`` — sum of outbound payments on date
    - ``net_cash_flow`` — inbound minus outbound on date
    - ``_loaded_at``
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

    # AP: unpaid vendor bills by date they were recorded
    ap = (
        spark.table(f"{SILVER}.vendor_bills")
        .filter(col("status") != "paid")
        .groupBy(col("date").alias("ap_date"))
        .agg(spark_sum("amount").alias("ap_outstanding"))
    )

    # AR: unpaid invoices by date they were recorded
    ar = (
        spark.table(f"{SILVER}.invoices")
        .filter(col("status") != "paid")
        .groupBy(col("date").alias("ar_date"))
        .agg(spark_sum("amount").alias("ar_outstanding"))
    )

    # Payments by date and type
    payments = spark.table(f"{SILVER}.payments")
    inbound = (
        payments
        .filter(col("type") == "inbound")
        .groupBy("date")
        .agg(spark_sum("amount").alias("inbound_payments"))
    )
    outbound = (
        payments
        .filter(col("type") == "outbound")
        .groupBy("date")
        .agg(spark_sum("amount").alias("outbound_payments"))
    )

    # Union all dates into a single date spine
    all_dates = (
        ap.select(col("ap_date").alias("date"))
        .union(ar.select(col("ar_date").alias("date")))
        .union(inbound.select("date"))
        .union(outbound.select("date"))
        .distinct()
    )

    df = (
        all_dates
        .join(ap, all_dates["date"] == ap["ap_date"], "left")
        .drop("ap_date")
        .join(ar, all_dates["date"] == ar["ar_date"], "left")
        .drop("ar_date")
        .join(inbound, "date", "left")
        .join(outbound, "date", "left")
        .withColumn("ap_outstanding", coalesce(col("ap_outstanding"), lit(0.0)))
        .withColumn("ar_outstanding", coalesce(col("ar_outstanding"), lit(0.0)))
        .withColumn("inbound_payments", coalesce(col("inbound_payments"), lit(0.0)))
        .withColumn("outbound_payments", coalesce(col("outbound_payments"), lit(0.0)))
        .withColumn(
            "net_cash_flow",
            col("inbound_payments") - col("outbound_payments"),
        )
        .withColumn("_loaded_at", current_timestamp())
        .orderBy("date")
    )

    fqn = f"{GOLD}.ap_ar_cash_summary"
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
    print(f"[rollup] {fqn}  ({df.count()} rows)")
    return df
