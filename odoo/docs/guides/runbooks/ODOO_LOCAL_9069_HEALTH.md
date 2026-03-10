# Odoo Local 9069 Health Policy

Local dev Odoo on `http://localhost:9069` is considered **healthy** if:

1. `/web/login` returns HTTP 200 and contains `meta name="generator" content="Odoo"`.
2. Main frontend CSS (e.g. `/web/assets/1/877a298/web.assets_frontend.min.css`) returns HTTP 200 and is non-empty.

Use:

```bash
scripts/health/odoo_local_9069.sh
```

## IMPORTANT BEHAVIOR

* If the health script passes:

  * DO NOT restart Docker.
  * DO NOT restart Odoo.
  * Any visual issues in the browser are treated as **cache / theme rendering**, not infra failure.
* If the health script fails:

  * Only then proceed to Docker/Odoo restart or deeper diagnostics.

This prevents false positives where browser cache or stale assets cause confusion while Odoo is actually healthy.
