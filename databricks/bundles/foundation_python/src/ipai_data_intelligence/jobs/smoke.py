"""Smoke job — validates the Databricks runtime environment.

Run this job after bundle deployment to confirm:
- Python environment is functional
- Spark session is available
- Catalog and schema variables resolve correctly
"""


def main() -> None:
    """Entry point for the smoke job."""
    print("smoke: start")

    try:
        from pyspark.sql import SparkSession  # type: ignore[import-untyped]

        spark = SparkSession.builder.getOrCreate()
        print(f"smoke: spark version = {spark.version}")
        print(f"smoke: catalog = {spark.catalog.currentCatalog()}")
        print(f"smoke: database = {spark.catalog.currentDatabase()}")
    except ImportError:
        print("smoke: pyspark not available (local test mode)")

    print("smoke: done")


if __name__ == "__main__":
    main()
