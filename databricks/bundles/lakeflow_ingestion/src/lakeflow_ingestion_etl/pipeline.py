"""Placeholder pipeline entrypoint for Lakeflow/DLT ingestion.

Replace this with actual DLT table definitions when ingestion sources are ready.
"""


def define_tables() -> None:
    """Define DLT tables for Bronze layer ingestion.

    This is a placeholder. Actual implementation will use:
        import dlt

        @dlt.table
        def raw_odoo_partners():
            return spark.read.format("jdbc").options(...).load()
    """
    print("lakeflow_ingestion: placeholder — no tables defined yet")
