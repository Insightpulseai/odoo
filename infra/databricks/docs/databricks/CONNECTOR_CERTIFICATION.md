# Connector Certification Process

## Overview

Every connector must pass the 7-check certification suite before deployment to production. The certification validates behavioral correctness, not just code quality.

## Running Certification

```bash
cd infra/databricks
PYTHONPATH=src:$PYTHONPATH python3 -m pytest tests/contract/ -v
```

## Certification Checks

### 1. test_connection_succeeds
- `connector.test_connection()` returns `True`
- Validates credentials and source reachability

### 2. schema_is_stable
- `connector.schema()` called twice returns identical `TableDef` lists
- Ensures deterministic schema declaration

### 3. update_yields_checkpoint
- `connector.update(empty_state)` always ends with at least one CHECKPOINT op
- Without CHECKPOINT, state cannot be advanced safely

### 4. update_is_resumable
- Sync with state A -> CHECKPOINT B
- Re-sync with cursor B -> produces only new data (or empty) + CHECKPOINT
- Validates incremental extraction correctness

### 5. empty_update_is_safe
- Sync with "caught up" state -> no UPSERTs emitted, just CHECKPOINT
- Prevents unnecessary writes when source has no changes

### 6. data_matches_schema
- Every UPSERT op's data keys are a subset of declared column names
- Prevents schema mismatch errors at write time

### 7. close_releases_resources
- After `close()`, connector's client/connection attributes are None/closed
- Prevents resource leaks in long-running jobs

## Adding a New Connector

1. Implement `BaseConnector` subclass with `@register_connector` decorator
2. Add fixture data to `tests/fixtures/connector_fixtures.py`
3. Run certification: `pytest tests/contract/ -v`
4. All 7 checks must pass before merge

## Certification Report Format

```
ConnectorCertifier.certify() returns:
    CertificationReport(
        connector_id="notion",
        checks=[
            CheckResult(name="test_connection_succeeds", passed=True),
            CheckResult(name="schema_is_stable", passed=True),
            ...
        ]
    )
```

## CI Integration

Add to `.github/workflows/connector-ci.yml`:

```yaml
- name: Run connector certification
  run: |
    cd infra/databricks
    PYTHONPATH=src:$PYTHONPATH python3 -m pytest tests/contract/ -v --tb=short
```
