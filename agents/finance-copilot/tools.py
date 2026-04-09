"""Finance copilot tools — Databricks gold mart queries."""

import json
import os
from typing import Any

from databricks import sql as databricks_sql
from databricks.sql.client import Connection


def _get_connection() -> Connection:
    return databricks_sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"].replace("https://", ""),
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )


def query_databricks(sql: str) -> list[dict[str, Any]]:
    """Execute SQL against Databricks SQL warehouse and return rows as dicts."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    finally:
        conn.close()


def get_project_profitability(project_name: str | None = None) -> str:
    """Query gold.project_profitability, optionally filtered by project name."""
    sql = "SELECT * FROM gold.project_profitability"
    if project_name:
        safe_name = project_name.replace("'", "''")
        sql += f" WHERE project_name = '{safe_name}'"
    sql += " ORDER BY margin_pct DESC LIMIT 50"
    rows = query_databricks(sql)
    return json.dumps(rows, default=str)


def get_portfolio_health(portfolio_name: str | None = None) -> str:
    """Query gold.portfolio_financial_health, optionally filtered by portfolio."""
    sql = "SELECT * FROM gold.portfolio_financial_health"
    if portfolio_name:
        safe_name = portfolio_name.replace("'", "''")
        sql += f" WHERE portfolio_name = '{safe_name}'"
    sql += " ORDER BY health_score DESC LIMIT 50"
    rows = query_databricks(sql)
    return json.dumps(rows, default=str)


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_project_profitability",
            "description": "Get project profitability data from Databricks gold mart. Returns revenue, cost, margin for projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Optional project name filter. Omit for all projects.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_health",
            "description": "Get portfolio financial health scores from Databricks gold mart. Returns health score, budget utilization, risk indicators.",
            "parameters": {
                "type": "object",
                "properties": {
                    "portfolio_name": {
                        "type": "string",
                        "description": "Optional portfolio name filter. Omit for all portfolios.",
                    }
                },
                "required": [],
            },
        },
    },
]

TOOL_DISPATCH = {
    "get_project_profitability": get_project_profitability,
    "get_portfolio_health": get_portfolio_health,
}
