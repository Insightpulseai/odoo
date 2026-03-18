#!/usr/bin/env python3
"""
Generate synthetic training data for Databricks agent training.

This script generates tool-use trajectories, failure/repair traces,
and SQL governance tasks based on the competency specification.

Usage:
    python scripts/generate_data.py [--count 200] [--output data/sft_tasks.jsonl]
"""

import argparse
import json
import pathlib
import random
from typing import Any


def generate_bundle_repair_task(task_id: int) -> dict[str, Any]:
    """Generate bundle repair training task."""
    error_types = [
        {
            "error": "Variable 'catalog' referenced but not defined",
            "files": {
                "databricks.yml": "resources:\n  jobs:\n    etl_job:\n      name: ${var.catalog}-etl\n"
            },
            "fix": "variables:\n  catalog:\n    default: main\n",
        },
        {
            "error": "YAML syntax error at line 15: mapping values are not allowed here",
            "files": {
                "databricks.yml": "resources:\n  jobs:\n    my_job:\n    name: broken\n"
            },
            "fix": "resources:\n  jobs:\n    my_job:\n      name: fixed\n",
        },
        {
            "error": "Resource 'pipelines.bronze_pipeline' not found in target 'dev'",
            "files": {
                "databricks.yml": "resources:\n  jobs:\n    orchestrator:\n      tasks:\n        - pipeline_task:\n            pipeline_id: ${resources.pipelines.bronze_pipeline.id}\n"
            },
            "fix": "resources:\n  pipelines:\n    bronze_pipeline:\n      name: bronze-ingest\n  jobs:\n    orchestrator:\n      tasks:\n        - pipeline_task:\n            pipeline_id: ${resources.pipelines.bronze_pipeline.id}\n",
        },
    ]

    error = random.choice(error_types)
    return {
        "id": f"bundle_repair_{task_id:04d}",
        "task_type": "bundle_repair",
        "instruction": f"Fix a Databricks Asset Bundle deploy failure: {error['error']}",
        "context": {"error": error["error"], "files": error["files"]},
        "expected": {"patch": error["fix"], "validator": "bundle_validate_passes"},
    }


def generate_uc_grant_task(task_id: int) -> dict[str, Any]:
    """Generate UC grants training task."""
    scenarios = [
        {
            "use_case": "data engineering team bronze/silver access",
            "catalog": "analytics",
            "schema": "bronze",
            "team": "data_engineers",
            "sql": [
                "GRANT USAGE ON CATALOG analytics TO `data_engineers`;",
                "GRANT USE SCHEMA ON SCHEMA analytics.bronze TO `data_engineers`;",
                "GRANT SELECT ON SCHEMA analytics.bronze TO `data_engineers`;",
            ],
        },
        {
            "use_case": "analytics team gold layer read access",
            "catalog": "analytics",
            "schema": "gold",
            "team": "analysts",
            "sql": [
                "GRANT USAGE ON CATALOG analytics TO `analysts`;",
                "GRANT USE SCHEMA ON SCHEMA analytics.gold TO `analysts`;",
                "GRANT SELECT ON SCHEMA analytics.gold TO `analysts`;",
            ],
        },
        {
            "use_case": "ML team feature store access",
            "catalog": "ml",
            "schema": "features",
            "team": "ml_engineers",
            "sql": [
                "GRANT USAGE ON CATALOG ml TO `ml_engineers`;",
                "GRANT USE SCHEMA ON SCHEMA ml.features TO `ml_engineers`;",
                "GRANT SELECT, MODIFY ON SCHEMA ml.features TO `ml_engineers`;",
            ],
        },
    ]

    scenario = random.choice(scenarios)
    return {
        "id": f"uc_grant_{task_id:04d}",
        "task_type": "uc_governance",
        "instruction": f"Create Unity Catalog grants for {scenario['use_case']}.",
        "context": {
            "catalog": scenario["catalog"],
            "schema": scenario["schema"],
            "team_group": scenario["team"],
        },
        "expected": {
            "sql": "\n".join(scenario["sql"]),
            "validator": "grants_audit_passes",
        },
    }


def generate_pipeline_debug_task(task_id: int) -> dict[str, Any]:
    """Generate DLT pipeline debugging task."""
    failures = [
        {
            "type": "expectation_failed",
            "error": "Expectation 'valid_customer_id' failed: 15% of records have null customer_id",
            "context": {
                "table": "silver_orders",
                "expectation": "@dlt.expect('valid_customer_id', 'customer_id IS NOT NULL')",
            },
            "fix": "Add data quality handling:\n@dlt.expect_or_drop('valid_customer_id', 'customer_id IS NOT NULL')",
        },
        {
            "type": "schema_mismatch",
            "error": "Schema mismatch: source column 'order_date' is STRING, target expects DATE",
            "context": {"source_table": "bronze_orders", "target_table": "silver_orders"},
            "fix": "Add schema transformation:\n.withColumn('order_date', F.to_date(F.col('order_date'), 'yyyy-MM-dd'))",
        },
        {
            "type": "cluster_timeout",
            "error": "Cluster failed to start: timeout after 20 minutes",
            "context": {"cluster_config": "job_cluster_small.yml"},
            "fix": "Increase cluster timeout or use existing cluster:\nauto_termination_minutes: 30\nnum_workers: 2",
        },
    ]

    failure = random.choice(failures)
    return {
        "id": f"pipeline_debug_{task_id:04d}",
        "task_type": "pipeline_debug",
        "instruction": f"Debug a DLT pipeline failure: {failure['type']}",
        "context": {"error": failure["error"], **failure["context"]},
        "expected": {"fix": failure["fix"], "validator": "pipeline_compiles"},
    }


def generate_app_auth_task(task_id: int) -> dict[str, Any]:
    """Generate Databricks Apps authentication task."""
    patterns = [
        {
            "pattern": "user_oauth",
            "description": "Configure user-based OAuth 2.0 for personalized data access",
            "context": {"app_type": "streamlit", "data_source": "UC tables"},
            "config": """# app.yaml
authorization:
  type: user
  scopes:
    - sql
    - unity-catalog""",
        },
        {
            "pattern": "service_principal",
            "description": "Configure service principal for backend batch operations",
            "context": {"app_type": "api", "data_source": "external API + UC"},
            "config": """# app.yaml
authorization:
  type: app
  service_principal_name: app-backend-sp""",
        },
    ]

    pattern = random.choice(patterns)
    return {
        "id": f"app_auth_{task_id:04d}",
        "task_type": "app_configuration",
        "instruction": f"Configure {pattern['pattern']} for a Databricks App: {pattern['description']}",
        "context": pattern["context"],
        "expected": {"config": pattern["config"], "validator": "app_health_check"},
    }


def generate_tasks(output_path: str, count: int = 200) -> None:
    """Generate training task dataset."""
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    generators = [
        generate_bundle_repair_task,
        generate_uc_grant_task,
        generate_pipeline_debug_task,
        generate_app_auth_task,
    ]

    tasks = []
    for i in range(count):
        generator = generators[i % len(generators)]
        tasks.append(generator(i))

    with open(output_path, "w") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")

    print(f"Generated {len(tasks)} tasks to {output_path}")

    # Also generate eval holdout (10% of count)
    holdout_path = output_path.replace("sft_tasks", "eval_holdout")
    holdout_tasks = []
    for i in range(count // 10):
        generator = random.choice(generators)
        holdout_tasks.append(generator(count + i))

    with open(holdout_path, "w") as f:
        for task in holdout_tasks:
            f.write(json.dumps(task) + "\n")

    print(f"Generated {len(holdout_tasks)} holdout tasks to {holdout_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Databricks agent training data")
    parser.add_argument("--count", type=int, default=200, help="Number of tasks to generate")
    parser.add_argument(
        "--output",
        type=str,
        default="data/sft_tasks.jsonl",
        help="Output file path",
    )
    args = parser.parse_args()

    generate_tasks(args.output, args.count)
