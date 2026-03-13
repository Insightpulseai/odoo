# Constitution: Odoo App Agent Skills

## Non-Negotiable Rules

1. **Skills are declarative**. Each skill is a YAML definition with intents, tools, workflow, and schemas. No imperative code in skill files.

2. **Config → OCA → Delta**. Skills must recommend built-in Odoo config first, OCA modules second, custom ipai_* modules only when necessary.

3. **CE only**. No skill may recommend or depend on Odoo Enterprise modules.

4. **Self-hosted first**. Cost analyses and architecture recommendations prefer self-hosted (DigitalOcean) over managed cloud services.

5. **Security by design**. Skills never request, store, or log secrets. All credentials via env vars or ir.config_parameter.

6. **Evidence required**. Every skill execution that modifies state must produce verifiable evidence in docs/evidence/.

7. **Idempotent workflows**. Skill tool sequences must be safe to re-run without side effects.

8. **OCA coding standards**. All generated code must pass pre-commit (black, isort, flake8).
