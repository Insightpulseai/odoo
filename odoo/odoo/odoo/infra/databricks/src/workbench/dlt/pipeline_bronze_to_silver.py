"""DLT Pipeline: Bronze to Silver transformation.

This pipeline is designed to run as a Delta Live Tables pipeline.
Deploy via: databricks bundle deploy
"""

import dlt
from pyspark.sql.functions import (
    col,
    current_timestamp,
    get_json_object,
    to_date,
    to_timestamp,
)


@dlt.table(
    name="notion_programs",
    comment="Normalized programs from Notion",
    table_properties={"quality": "silver"},
)
def silver_programs():
    """Transform raw Notion programs to silver layer."""
    return (
        dlt.read("notion_raw_pages")
        .filter(col("source_table") == "programs")
        .select(
            get_json_object(col("raw_json"), "$.id").alias("program_id"),
            get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
            get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
            get_json_object(col("raw_json"), "$.properties.Owner.people[0].name").alias("owner"),
            to_date(get_json_object(col("raw_json"), "$.properties.Start Date.date.start")).alias(
                "start_date"
            ),
            to_date(get_json_object(col("raw_json"), "$.properties.End Date.date.start")).alias(
                "end_date"
            ),
            get_json_object(col("raw_json"), "$.properties.Budget.number")
            .cast("decimal(18,2)")
            .alias("budget"),
            to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
                "last_modified_at"
            ),
            current_timestamp().alias("_etl_loaded_at"),
        )
    )


@dlt.table(
    name="notion_projects",
    comment="Normalized projects from Notion",
    table_properties={"quality": "silver"},
)
def silver_projects():
    """Transform raw Notion projects to silver layer."""
    return (
        dlt.read("notion_raw_pages")
        .filter(col("source_table") == "projects")
        .select(
            get_json_object(col("raw_json"), "$.id").alias("project_id"),
            get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
            get_json_object(col("raw_json"), "$.properties.Program.relation[0].id").alias(
                "program_id"
            ),
            get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
            get_json_object(col("raw_json"), "$.properties.Priority.select.name").alias("priority"),
            get_json_object(col("raw_json"), "$.properties.Owner.people[0].name").alias("owner"),
            to_date(get_json_object(col("raw_json"), "$.properties.Start Date.date.start")).alias(
                "start_date"
            ),
            to_date(get_json_object(col("raw_json"), "$.properties.End Date.date.start")).alias(
                "end_date"
            ),
            get_json_object(col("raw_json"), "$.properties.Budget.number")
            .cast("decimal(18,2)")
            .alias("budget"),
            get_json_object(col("raw_json"), "$.properties.Actual.number")
            .cast("decimal(18,2)")
            .alias("actual"),
            to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
                "last_modified_at"
            ),
            current_timestamp().alias("_etl_loaded_at"),
        )
    )


@dlt.table(
    name="notion_budget_lines",
    comment="Normalized budget lines from Notion",
    table_properties={"quality": "silver"},
)
def silver_budget_lines():
    """Transform raw Notion budget lines to silver layer."""
    return (
        dlt.read("notion_raw_pages")
        .filter(col("source_table") == "budget_lines")
        .select(
            get_json_object(col("raw_json"), "$.id").alias("budget_line_id"),
            get_json_object(col("raw_json"), "$.properties.Project.relation[0].id").alias(
                "project_id"
            ),
            get_json_object(col("raw_json"), "$.properties.Category.select.name").alias("category"),
            get_json_object(
                col("raw_json"), "$.properties.Description.rich_text[0].plain_text"
            ).alias("description"),
            get_json_object(col("raw_json"), "$.properties.Amount.number")
            .cast("decimal(18,2)")
            .alias("amount"),
            get_json_object(col("raw_json"), "$.properties.Type.select.name").alias("line_type"),
            to_date(get_json_object(col("raw_json"), "$.properties.Date.date.start")).alias(
                "line_date"
            ),
            current_timestamp().alias("_etl_loaded_at"),
        )
    )


@dlt.table(
    name="notion_risks",
    comment="Normalized risks from Notion",
    table_properties={"quality": "silver"},
)
def silver_risks():
    """Transform raw Notion risks to silver layer."""
    return (
        dlt.read("notion_raw_pages")
        .filter(col("source_table") == "risks")
        .select(
            get_json_object(col("raw_json"), "$.id").alias("risk_id"),
            get_json_object(col("raw_json"), "$.properties.Project.relation[0].id").alias(
                "project_id"
            ),
            get_json_object(col("raw_json"), "$.properties.Name.title[0].plain_text").alias("name"),
            get_json_object(col("raw_json"), "$.properties.Category.select.name").alias("category"),
            get_json_object(col("raw_json"), "$.properties.Severity.select.name").alias("severity"),
            get_json_object(col("raw_json"), "$.properties.Probability.select.name").alias(
                "probability"
            ),
            get_json_object(col("raw_json"), "$.properties.Status.select.name").alias("status"),
            get_json_object(
                col("raw_json"), "$.properties.Mitigation.rich_text[0].plain_text"
            ).alias("mitigation"),
            to_timestamp(get_json_object(col("raw_json"), "$.last_edited_time")).alias(
                "last_modified_at"
            ),
            current_timestamp().alias("_etl_loaded_at"),
        )
    )
