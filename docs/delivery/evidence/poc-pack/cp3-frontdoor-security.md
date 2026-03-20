# CP-3: Front Door Security Evidence

**Date**: 2026-03-20T07:40Z
**Status**: PARTIAL — code committed & pushed, awaiting pipeline deploy

## Front Door path (erp.insightpulseai.com)
- /web/login: HTTP 200
- /web/health: HTTP 200

## Direct ACA URL bypass test
- /web/login: HTTP 200 (EXPECTED: 403 after FDID module deployed)

## DB Manager access
- /web/database/manager: HTTP 200 (EXPECTED: 404 after middleware deployed)

## Asset bundles (3 distinct hashes = healthy)
```
/web/assets/20aca75/
/web/assets/97f7589/
/web/assets/b278281/
```

## Commits pushed
- 562b45b feat(security): add Front Door FDID validation middleware
- f4eabb7 feat(copilot): add streaming response support via gateway proxy
- 67e8fa9 fix(security): add Dockerfile.prod + block DB manager route

## Remaining
- Pipeline must complete Build + Deploy stages to activate FDID middleware
- After deploy: re-test ACA direct URL (expect 403) and DB manager (expect 404)
- AZURE_FRONTDOOR_ID already set on all 3 ACA containers: 38c7f9ab-c904-4c47-ad53-4b9fb1abea8e
