# Databricks notebook source
# MAGIC %md
# MAGIC # Lakehouse Connectivity Test
# MAGIC Validates prerequisites before first pipeline run.
# MAGIC Run this notebook after `databricks bundle deploy` to verify environment readiness.

# COMMAND ----------

results = []

def check(name, fn):
    """Run a check and record pass/fail."""
    try:
        detail = fn()
        results.append({"check": name, "status": "PASS", "detail": str(detail)})
        print(f"PASS: {name} — {detail}")
    except Exception as e:
        results.append({"check": name, "status": "FAIL", "detail": str(e)})
        print(f"FAIL: {name} — {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Secret Scope

def check_secrets():
    scopes = [s.name for s in dbutils.secrets.listScopes()]
    assert "odoo-pg" in scopes, f"Secret scope 'odoo-pg' not found. Available: {scopes}"
    keys = [k.key for k in dbutils.secrets.list("odoo-pg")]
    required = {"jdbc_url", "jdbc_user", "jdbc_password"}
    missing = required - set(keys)
    assert not missing, f"Missing keys in odoo-pg: {missing}"
    return f"odoo-pg scope OK, keys: {keys}"

check("Secret scope odoo-pg", check_secrets)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. JDBC Connectivity to Odoo PG

def check_jdbc():
    url = dbutils.secrets.get("odoo-pg", "jdbc_url")
    user = dbutils.secrets.get("odoo-pg", "jdbc_user")
    password = dbutils.secrets.get("odoo-pg", "jdbc_password")
    df = (spark.read
        .format("jdbc")
        .option("url", url)
        .option("user", user)
        .option("password", password)
        .option("query", "SELECT current_database() AS db, current_timestamp AS ts")
        .load())
    row = df.first()
    return f"Connected to {row['db']} at {row['ts']}"

check("JDBC to Odoo PG", check_jdbc)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. ADLS Bronze Path

def check_adls():
    bronze_path = spark.conf.get("bronze_path", "abfss://bronze@stipaidev.dfs.core.windows.net")
    items = dbutils.fs.ls(bronze_path)
    return f"{len(items)} items at {bronze_path}"

check("ADLS Bronze path", check_adls)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Unity Catalog Schemas

def check_catalog():
    catalog = spark.conf.get("catalog", "dev_ipai")
    spark.sql(f"USE CATALOG {catalog}")
    schemas = [r.databaseName for r in spark.sql("SHOW SCHEMAS").collect()]
    required = {"bronze", "silver", "gold"}
    missing = required - set(schemas)
    if missing:
        return f"WARNING: Missing schemas {missing} in {catalog}. Available: {schemas}"
    return f"Catalog {catalog}: {schemas}"

check("Unity Catalog schemas", check_catalog)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Odoo Table Accessibility

def check_odoo_tables():
    url = dbutils.secrets.get("odoo-pg", "jdbc_url")
    user = dbutils.secrets.get("odoo-pg", "jdbc_user")
    password = dbutils.secrets.get("odoo-pg", "jdbc_password")
    tables = ["account_move", "account_move_line", "res_partner", "hr_employee"]
    counts = {}
    for t in tables:
        df = (spark.read
            .format("jdbc")
            .option("url", url)
            .option("user", user)
            .option("password", password)
            .option("query", f"SELECT COUNT(*) AS cnt FROM {t}")
            .load())
        counts[t] = df.first()["cnt"]
    return f"Row counts: {counts}"

check("Odoo source tables", check_odoo_tables)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

import json

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")

print("=" * 60)
print(f"Results: {passed} PASS / {failed} FAIL / {len(results)} total")
print("=" * 60)
for r in results:
    icon = "+" if r["status"] == "PASS" else "X"
    print(f"  [{icon}] {r['check']}: {r['detail'][:80]}")

if failed > 0:
    print("\nFix failures before running the DLT pipeline.")
    dbutils.notebook.exit(json.dumps({"status": "FAIL", "passed": passed, "failed": failed}))
else:
    print("\nAll checks passed. Ready for pipeline deployment.")
    dbutils.notebook.exit(json.dumps({"status": "PASS", "passed": passed, "failed": 0}))
