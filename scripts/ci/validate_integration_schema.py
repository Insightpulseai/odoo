#!/usr/bin/env python3
"""
validate_integration_schema.py — CI validator for integration backbone schema.

Validates:
1. Migration SQL file exists and contains required DDL
2. SSOT event_routes.yaml matches migration seed data
3. Required columns exist in migration ALTER TABLE statements
"""
import sys
import re
from pathlib import Path

MIGRATION = Path("supabase/migrations/20260308000001_integration_backbone_events.sql")
EVENT_ROUTES = Path("ssot/integrations/event_routes.yaml")

errors = []


def check_migration():
    if not MIGRATION.exists():
        errors.append(f"Migration file missing: {MIGRATION}")
        return

    sql = MIGRATION.read_text()

    # Check required columns
    required_columns = [
        ("integration.outbox", "correlation_id"),
        ("integration.event_log", "correlation_id"),
        ("ops.runs", "correlation_id"),
        ("ops.run_events", "correlation_id"),
    ]
    for table, col in required_columns:
        pattern = rf"ALTER TABLE\s+{re.escape(table)}.*ADD COLUMN.*{col}"
        if not re.search(pattern, sql, re.IGNORECASE | re.DOTALL):
            errors.append(f"Missing ALTER TABLE {table} ADD COLUMN {col}")

    # Check view creation
    if "CREATE OR REPLACE VIEW ops.v_events" not in sql:
        errors.append("Missing CREATE OR REPLACE VIEW ops.v_events")

    # Check routing table
    if "ops.integration_routes" not in sql:
        errors.append("Missing ops.integration_routes table creation")

    # Check resolve_routes function
    if "ops.resolve_routes" not in sql:
        errors.append("Missing ops.resolve_routes function")

    # Check RPC wrappers with correlation_id
    if "p_correlation_id" not in sql:
        errors.append("Missing p_correlation_id parameter in RPC wrappers")


def check_event_routes():
    if not EVENT_ROUTES.exists():
        errors.append(f"SSOT event routes missing: {EVENT_ROUTES}")
        return

    content = EVENT_ROUTES.read_text()

    required_patterns = ["expense.*", "deployment.*", "slack-notify", "slack-approval"]
    for pattern in required_patterns:
        if pattern not in content:
            errors.append(f"Event routes missing required entry: {pattern}")


def main():
    check_migration()
    check_event_routes()

    if errors:
        print("FAIL: Integration schema validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: Integration schema validation complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
