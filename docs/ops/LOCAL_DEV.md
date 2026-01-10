# Local Dev (Docker Compose)

## Bring up stack
```bash
cd odoo-ce
docker compose -f docker-compose.prod.yml --env-file .env up -d
docker compose -f docker-compose.prod.yml ps
```

## Logs

```bash
docker compose -f docker-compose.prod.yml logs -f --tail=200 odoo
```

## Smoke checks

```bash
curl -fsS http://localhost:8069/web/login | head -50
curl -I http://localhost:8069/web/assets/ | head -20
```

## Install/Update the shipped bundle (example)

```bash
# run from inside container if you have odoo-bin available there
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "odoo --stop-after-init -d odoo_core -i ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr"
```

## AIUX verification scripts

```bash
bash scripts/aiux/verify_install.sh
bash scripts/aiux/verify_assets.sh
```
