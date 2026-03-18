# Workspace Ops Policy

## Allowed Operations

- Read: workspace ls, files ls, repos list, secrets list-scopes, secrets list
- Write: workspace import, workspace mkdirs, files cp, files mkdir, repos create, repos update, secrets create-scope, secrets put-secret
- Delete: workspace delete, files rm, repos delete, secrets delete-secret (all require explicit confirmation)

## Secret Handling

- Secret values are NEVER logged or displayed in output
- `secrets list` returns metadata only (key names, not values)
- `secrets put-secret` reads from stdin, never from command-line arguments
- Secret scopes follow naming convention: `ipai-<domain>`

## Destructive Operation Guards

- `workspace delete` requires `--recursive` flag for directories — agent must confirm intent
- `files rm` with `--recursive` requires explicit confirmation
- `repos delete` removes the Git link, not the remote repo — safe but confirm intent
- `secrets delete-secret` is irreversible — confirm scope and key before executing

## Authentication

- Use profiles (`--profile <name>`) for multi-workspace environments
- Environment variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) for single-workspace
- Never hardcode tokens in scripts or commit them to git
