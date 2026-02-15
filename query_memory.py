#!/usr/bin/env python3
"""
Query Memory Script
===================

Retrieves configuration values from the local SQLite memory database.
Useful for fetching context without polluting CLAUDE.md.

Usage:
    python3 query_memory.py <key_pattern>

Examples:
    python3 query_memory.py manifest_template
    python3 query_memory.py deploy_checklist
    python3 query_memory.py sca_rules
"""

import sqlite3
import sys
import os
import json

DB_PATH = 'project_memory.db'


def init_db():
    """Initialize the database with default schema if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert some default values if table is empty
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ('manifest_template', json.dumps({
                "name": "Module Name",
                "version": "18.0.1.0.0",
                "category": "Category",
                "author": "InsightPulseAI",
                "license": "AGPL-3",
                "depends": ["base"],
                "data": [],
                "installable": True,
                "application": False,
            }), 'odoo'),
            ('deploy_checklist', json.dumps([
                "Run tests: docker exec -it odoo odoo-bin -d mydb -i module --test-enable",
                "Check README.rst exists in every module",
                "Verify manifest version matches Odoo version (18.0.x.x.x)",
                "Run linter: pre-commit run --all-files",
                "Build assets: docker-compose exec odoo odoo-bin -d mydb -u module",
            ]), 'devops'),
            ('sca_rules', json.dumps({
                "no_hardcoded_secrets": "Use .env files or Odoo system parameters",
                "sql_injection": "Use ORM methods, never raw SQL with user input",
                "xss_prevention": "Use t-esc in QWeb, never t-raw with user content",
                "csrf_protection": "Ensure @http.route has csrf=True for POST",
            }), 'security'),
            ('docker_port', '8069', 'docker'),
            ('postgres_version', '15', 'docker'),
            ('odoo_version', '18.0', 'odoo'),
        ]

        cursor.executemany(
            "INSERT INTO config (key, value, category) VALUES (?, ?, ?)",
            defaults
        )

    conn.commit()
    conn.close()


def query_config(key_pattern):
    """
    Retrieves configuration values from the local SQLite memory.

    Args:
        key_pattern: A string pattern to match against config keys.

    Returns:
        JSON string with matching configuration values.
    """
    if not os.path.exists(DB_PATH):
        init_db()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Simple key-value lookup with LIKE pattern
        cursor.execute(
            "SELECT key, value FROM config WHERE key LIKE ?",
            (f'%{key_pattern}%',)
        )
        results = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        if not results:
            return json.dumps({"info": "No matching config found."})

        # Try to parse JSON values for prettier output
        parsed_results = {}
        for key, value in results.items():
            try:
                parsed_results[key] = json.loads(value)
            except json.JSONDecodeError:
                parsed_results[key] = value

        return json.dumps(parsed_results, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


def set_config(key, value, category=None):
    """
    Sets a configuration value in the database.

    Args:
        key: The configuration key.
        value: The value (will be JSON-encoded if not a string).
        category: Optional category for organization.
    """
    if not os.path.exists(DB_PATH):
        init_db()

    if not isinstance(value, str):
        value = json.dumps(value)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO config (key, value, category, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (key, value, category))

    conn.commit()
    conn.close()

    return json.dumps({"status": "ok", "key": key})


def list_keys():
    """List all configuration keys."""
    if not os.path.exists(DB_PATH):
        init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT key, category FROM config ORDER BY category, key")
    results = cursor.fetchall()

    conn.close()

    return json.dumps({
        "keys": [{"key": r[0], "category": r[1]} for r in results]
    }, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--list":
            print(list_keys())
        elif arg == "--set" and len(sys.argv) >= 4:
            key = sys.argv[2]
            value = sys.argv[3]
            category = sys.argv[4] if len(sys.argv) > 4 else None
            print(set_config(key, value, category))
        elif arg == "--init":
            init_db()
            print(json.dumps({"status": "initialized", "db": DB_PATH}))
        else:
            print(query_config(arg))
    else:
        print("Usage: python3 query_memory.py <config_key>")
        print("       python3 query_memory.py --list")
        print("       python3 query_memory.py --set <key> <value> [category]")
        print("       python3 query_memory.py --init")
