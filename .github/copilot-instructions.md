# Copilot Instructions for InsightPulse Odoo CE

## Project Architecture
- **Odoo CE + OCA stack**: Self-hosted ERP for expense management and equipment booking. No Odoo Enterprise/IAP modules; all customizations are in `addons/`.
- **Custom modules**:
  - `ipai_expense`: PH expense/travel workflows, receipt attachments, GL posting, project codes.
  - `ipai_equipment`: Asset catalog, booking, check-in/out, incident tracking.
  - `ipai_ce_cleaner`: Removes Enterprise/IAP upsells, rewires help links.
- **OCA modules**: Added as git submodules in `oca/`. Update `odoo.conf` `addons_path` when adding.
- **OCR Integration**: `ocr-adapter/` bridges Odoo expense form to external OCR (FastAPI, PaddleOCR-VL + OpenAI). Response normalized in `main.py:normalize_ocr_response()`.

## Developer Workflows
- **Deployment**:
  - One-shot: Run `deploy_m1.sh` for DigitalOcean Ubuntu droplets. Handles Docker, Nginx, SSL, backups, secrets.
  - Manual: Use `docker compose up -d` in `deploy/`. Nginx config in `deploy/nginx/`.
- **CI/CD**: GitHub Actions (`.github/workflows/ci-odoo-ce.yml`) enforces CE/OCA-only policy. Build fails on Enterprise references or `odoo.com` links.
- **Local Testing**: `docker compose up` in `deploy/`. Logs: `docker compose logs -f odoo`.
- **OCR Adapter Testing**: Use `curl` with sample receipts and API key. See `ocr-adapter/README.md` for patterns and troubleshooting.

## Conventions & Patterns
- **Expense/Equipment flows**: Custom modules follow Odoo's model/view/security structure. See `addons/ipai_expense/` and `addons/ipai_equipment/` for examples.
- **No Enterprise/IAP**: All upsell code removed/hidden. Use `ipai_ce_cleaner` for guardrails.
- **External API contracts**: OCR adapter expects/returns specific JSON fields (`merchant_name`, `invoice_date`, `currency`, `total_amount`). Normalize upstream responses in `main.py`.
- **Secrets**: Auto-generated and stored in `/opt/odoo-ce/deploy/.env` during deployment.

## Key Files & Directories
- `addons/`: Custom modules (expense, equipment, cleaner)
- `oca/`: OCA community modules (submodules)
- `deploy/`: Docker, Nginx, Odoo config
- `ocr-adapter/`: FastAPI OCR bridge, normalization logic
- `.github/workflows/ci-odoo-ce.yml`: CI/CD guardrails
- `spec.md`, `plan.md`, `tasks.md`: Specs, plans, checklists

## Examples
- **Add OCA module**:
  ```bash
  git submodule add https://github.com/OCA/account-financial-tools.git oca/account-financial-tools
  docker compose restart odoo
  ```
- **OCR adapter normalization**:
  ```python
  def normalize_ocr_response(raw: dict) -> dict:
      return {
          "merchant_name": raw.get("merchant", "Unknown"),
          "invoice_date": raw.get("date"),
          "currency": "PHP",
          "total_amount": float(raw.get("total", 0.0))
      }
  ```
- **CI/CD failure triggers**:
  - Enterprise module detected in `addons/` or `oca/`
  - `odoo.com` links in user-facing code

---
For unclear or missing conventions, review `README.md`, `ocr-adapter/README.md`, and `.github/workflows/ci-odoo-ce.yml`. Ask the team for undocumented patterns.
