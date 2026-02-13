#!/usr/bin/env python3
"""
Superset Database Setup Script
Tests connections and optionally configures Superset databases programmatically.
"""

import os
import sys
from typing import Optional

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def test_connection(name: str, host: str, port: int, user: str, database: str, password: str) -> bool:
    """Test PostgreSQL connection."""
    print(f"\nTesting: {name}")
    print(f"  Host: {host}:{port}")
    print(f"  Database: {database}")
    print(f"  User: {user}")

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        conn.close()

        print(f"  {Colors.GREEN}✅ Connection successful{Colors.NC}")
        print(f"  Version: {version[:60]}...")
        return True

    except psycopg2.OperationalError as e:
        print(f"  {Colors.RED}❌ Connection failed{Colors.NC}")
        print(f"  Error: {str(e)[:100]}")
        return False


def generate_uri(
    name: str,
    user: str,
    password: str,
    host: str,
    port: int,
    database: str,
    ssl: bool = False
) -> str:
    """Generate SQLAlchemy URI for Superset."""
    uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    if ssl:
        uri += "?sslmode=require"

    print(f"\n📋 Superset Connection URI for: {name}")
    print("━" * 60)
    # Mask password in output
    masked_uri = uri.replace(f":{password}@", ":***@")
    print(masked_uri)
    print("━" * 60)

    return uri


def check_schema_exists(host: str, port: int, user: str, database: str, password: str, schema: str) -> bool:
    """Check if a schema exists in the database."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;",
            (schema,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            print(f"{Colors.GREEN}✅ '{schema}' schema exists{Colors.NC}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  '{schema}' schema not found{Colors.NC}")
            return False

    except Exception as e:
        print(f"{Colors.RED}❌ Error checking schema: {str(e)}{Colors.NC}")
        return False


def main():
    print("🔍 Testing Superset Database Connections...")

    # Test 1: Odoo PostgreSQL
    print("\n" + "━" * 60)
    print("Test 1: Odoo PostgreSQL (Local Development)")
    print("━" * 60)

    odoo_config = {
        "name": "Odoo Development",
        "host": os.getenv("ODOO_DB_HOST", "localhost"),
        "port": int(os.getenv("ODOO_DB_PORT", "5432")),
        "user": os.getenv("ODOO_DB_USER", "odoo"),
        "database": os.getenv("ODOO_DB_NAME", "odoo_dev"),
        "password": os.getenv("ODOO_DB_PASSWORD", "odoo"),
    }

    if test_connection(**odoo_config):
        generate_uri(**odoo_config, ssl=False)

    # Test 2: Supabase PostgreSQL (Direct)
    print("\n" + "━" * 60)
    print("Test 2: Supabase PostgreSQL (Direct Connection)")
    print("━" * 60)

    supabase_password = os.getenv("SUPABASE_DB_PASSWORD")
    if not supabase_password:
        print(f"{Colors.YELLOW}⚠️  SUPABASE_DB_PASSWORD not set. Skipping Supabase test.{Colors.NC}")
        print("   Set it in .env or export SUPABASE_DB_PASSWORD=your_password")
    else:
        supabase_config = {
            "name": "Supabase (OPS)",
            "host": os.getenv("SUPABASE_DB_HOST", "aws-0-us-east-1.pooler.supabase.com"),
            "port": int(os.getenv("SUPABASE_DB_PORT", "5432")),
            "user": os.getenv("SUPABASE_DB_USER", "postgres.spdtwktxdalcfigzeqrz"),
            "database": os.getenv("SUPABASE_DB_NAME", "postgres"),
            "password": supabase_password,
        }

        if test_connection(**supabase_config):
            generate_uri(**supabase_config, ssl=True)

            # Check for ops schema
            print("\nChecking for 'ops' schema...")
            check_schema_exists(
                supabase_config["host"],
                supabase_config["port"],
                supabase_config["user"],
                supabase_config["database"],
                supabase_config["password"],
                "ops"
            )

    # Test 3: Supabase PostgreSQL (Pooler)
    print("\n" + "━" * 60)
    print("Test 3: Supabase PostgreSQL (Pooler - Recommended)")
    print("━" * 60)

    if supabase_password:
        supabase_pooler_config = {
            "name": "Supabase Pooler (Transactional)",
            "host": os.getenv("SUPABASE_DB_HOST", "aws-0-us-east-1.pooler.supabase.com"),
            "port": 6543,  # Pooler port
            "user": os.getenv("SUPABASE_DB_USER", "postgres.spdtwktxdalcfigzeqrz"),
            "database": os.getenv("SUPABASE_DB_NAME", "postgres"),
            "password": supabase_password,
        }

        if test_connection(**supabase_pooler_config):
            generate_uri(**supabase_pooler_config, ssl=True)

    # Summary
    print("\n" + "━" * 60)
    print("Summary")
    print("━" * 60)
    print("\n✅ Copy the connection URIs above into Superset")
    print("📖 Full documentation: docs/superset/DATABASE_CONNECTIONS.md")
    print("\nNext steps:")
    print("  1. Open Superset: http://localhost:8088")
    print("  2. Go to: Data → Databases → + Database")
    print("  3. Paste the connection URI from above")
    print("  4. Click 'Test Connection' then 'Connect'")
    print()


if __name__ == "__main__":
    main()
