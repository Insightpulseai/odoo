# Colima (Mac Optional)

Colima is an optional acceleration layer for Docker on macOS.
It is **NOT** required for this repo.

## Repo Policy

- **Compose is the SSOT** — all services defined in `docker-compose.yml`
- **Devcontainer must work without Colima** — no Mac-specific dependencies
- **Colima docs are convenience-only** — nothing in CI or dev workflow depends on it

## When to Use

Colima can improve Docker performance on macOS compared to Docker Desktop.
Use it if you develop locally on a Mac and want faster container performance.

## Quick Start (optional)

```bash
# Install
brew install colima docker docker-compose

# Start with resources
colima start --cpu 4 --memory 8 --disk 60

# Verify
docker context list
docker compose version
```

## Notes

- Colima is Mac-specific; Linux and CI runners use native Docker
- If using Colima, ensure the Docker context is set correctly
- Devcontainer and CI workflows do not depend on Colima
