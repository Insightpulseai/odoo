# Sandbox Options (Local CI + Codespaces + Local Docker + DigitalOcean)

## 1. Local CI Gate Validation

Run all local CI gate logic (compose-topology, modules audit, docs state, AI naming):

```bash
scripts/ci/run-all-gates.sh
```

## 2. Local Docker Dev Sandbox

Build + test CE19 EE parity image (if scripts exist) and start dev stack:

```bash
scripts/sandbox/start-local-sandbox.sh
```

## 3. GitHub Codespaces Sandbox

Launch a Codespace with the repository and branch:

```bash
scripts/sandbox/start-codespace.sh
# env:
#   REPO=jgtolentino/odoo-ce
#   BRANCH=main
#   MACHINE=standardLinux32gb
```

## 4. DigitalOcean Sandbox / Prod-Like

Run CE19 build + test on the DigitalOcean host:

```bash
scripts/sandbox/start-do-sandbox.sh
# env:
#   DO_HOST=178.128.112.214
#   REMOTE_DIR=/opt/odoo-ce/repo
#   BRANCH=claude/odoo-oca-enterprise-image-TLHuU
```

## 5. Sandbox Menu

Interactive selector for the above options:

```bash
scripts/sandbox/run-all-sandboxes.sh
```
