# Skill: ocr.bridge.configure

## Reasoning Strategy

1. **Read SSOT state**: Load `ssot/runtime/prod_settings.yaml` → `ocr:` section
2. **Verify canonical URL**: Check `docs/architecture/CANONICAL_URLS.md` includes the OCR endpoint
3. **Apply configuration**: Ensure the OCR base URL and health endpoint match SSOT declarations
4. **Health check**: If network is available, hit `/health` on the OCR service
5. **Produce evidence**: Write verification results to evidence directory

## Edge Cases

- **OCR service down**: The health check may fail if the PaddleOCR microservice is not running.
  This is NOT a configuration error — report the health check failure separately from config validation.
- **URL mismatch**: If `ocr.base_url` in prod_settings doesn't match `CANONICAL_URLS.md`,
  the canonical URL list is authoritative. Update prod_settings to match.
- **No secrets needed**: Unlike mail, the OCR bridge currently requires no secrets.
  The `requires.secrets` list is intentionally empty. If a future version adds auth tokens,
  they must be registered in `ssot/secrets/registry.yaml` first.

## SSOT Anchoring

| What | Where |
|------|-------|
| OCR endpoint config | `ssot/runtime/prod_settings.yaml` → `ocr:` section |
| Canonical URLs | `docs/architecture/CANONICAL_URLS.md` → Production Services |
| DNS record | `infra/dns/subdomain-registry.yaml` → `ocr` entry |
| Health check contract | `ssot/runtime/prod_settings.yaml` → `ocr.health_endpoint` |
