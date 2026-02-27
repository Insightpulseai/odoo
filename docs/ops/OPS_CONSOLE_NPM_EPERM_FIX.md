# Ops: Fix npm/pnpm EPERM Cache Permissions

> Invariant documentation for `apps/ops-console` install failures.
> Last updated: 2026-02-22

---

## Symptom

```
npm error code EPERM
npm error syscall open
npm error path /Users/<user>/.npm/_cacache/...
npm error errno -1
```

Or for pnpm:

```
EPERM: operation not permitted
pnpm install → exits non-zero
```

## Root Cause

The npm/pnpm cache directory (`~/.npm` or `~/.pnpm-store`) contains files owned
by `root` from a previous `sudo npm install` or privileged process run.
Node.js package managers cannot write to root-owned files as a normal user.

## Invariant

**The cache directory must be owned by the user running the package manager.**

- Local dev: cache must be owned by the developer's UID/GID
- CI runners: cache must be owned by the runner user (typically UID 1001 on GitHub-hosted runners)
- Containers: cache must be owned by the container process user (e.g., `node` or `odoo`)

## Fix (Local macOS)

Determine your UID and GID:

```bash
id   # outputs uid=501(tbwa) gid=20(staff)
```

Fix ownership of the npm cache:

```bash
sudo chown -R 501:20 "$HOME/.npm"
# Replace 501:20 with your uid:gid from `id` output
```

Then verify install works:

```bash
cd apps/ops-console
pnpm install
```

## Fix (CI / Docker)

In CI, never run `npm install` or `pnpm install` as root. Use:

```yaml
# GitHub Actions
- name: Install deps
  run: pnpm install
  # Ensure runner is not root; GitHub-hosted runners run as non-root by default
```

In Docker, use a non-root USER in the Dockerfile and ensure cache volumes are
mounted with correct ownership.

## Prevention

- **Never** run `sudo npm install` or `sudo pnpm install` globally
- **Never** run package manager commands inside a container as root without explicit USER
- For `pnpm`, set the store dir explicitly: `pnpm config set store-dir ~/.pnpm-store`
  and ensure that path is user-owned

## Affected App

- `apps/ops-console/` — Next.js 14 + shadcn/ui + Tailwind ops dashboard
- Package manager: pnpm (workspace root) + npm (ops-console uses package-lock.json)
