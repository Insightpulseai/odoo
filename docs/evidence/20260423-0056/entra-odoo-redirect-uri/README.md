# Entra Odoo Redirect URI Fix

- Scope: `erp.insightpulseai.com` OAuth callback mismatch (`AADSTS50011`)
- Local stamp: `20260423-0056` (Asia/Manila)
- Canonical spec anchor: `spec/entra-identity-migration/`

## Problem

Live Odoo login was emitting:

- `http://erp.insightpulseai.com/auth_oauth/signin`

But the Entra app registration `3446e178-3eba-48c9-b5bd-4283ff729eb1` only allowed:

- `https://erp.insightpulseai.com/auth_oauth/signin`

That mismatch reproduced the user-reported `AADSTS50011` failure on 2026-04-22.

## Repo Changes

- Added the deterministic `auth_oauth` HTTPS callback patch to [platform/runtime/docker/docker/Dockerfile.pulser-odoo](/Users/tbwa/Documents/GitHub/Insightpulseai/platform/runtime/docker/docker/Dockerfile.pulser-odoo:223)
- Added the same patch to [docker/Dockerfile.unified](/Users/tbwa/Documents/GitHub/Insightpulseai/docker/Dockerfile.unified:31)

## Deployment

- Built image: `acripaiodoo.azurecr.io/ipai-odoo:18.0-pulser-oauth-https-20260423-0056`
- Build run: `cm81`
- Image digest: `sha256:7dafcb4e8a8e9104da295429b24fd93046cc99f7f33b638be51f86fc01f563e6`
- Updated live Container App: `ipai-odoo-dev`
- Resource group: `rg-ipai-dev-odoo-sea`
- Ready revision after rollout: `ipai-odoo-dev--0000020`

## Verification

- `PASS` Entra app registration still contains `https://erp.insightpulseai.com/auth_oauth/signin`
- `PASS` Live login page before rollout emitted `redirect_uri=http%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin`
- `PASS` Live login page after rollout emitted `redirect_uri=https%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin`
- `PASS` Live Container App now serves image `acripaiodoo.azurecr.io/ipai-odoo:18.0-pulser-oauth-https-20260423-0056`

## Evidence Files

- `live-pre-fix-app-registration.json`
- `live-pre-fix-containerapp.json`
- `live-pre-fix-login-redirect.txt`
- `acr-build.txt`
- `live-post-fix-containerapp.json`
- `live-post-fix-login-redirect.txt`
