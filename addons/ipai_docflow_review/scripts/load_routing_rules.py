# Usage:
#   ./odoo-bin shell -d <DB> -c <conf> -i ipai_docflow_review < addons/ipai_docflow_review/scripts/load_routing_rules.py
#
# Env:
#   DOCFLOW_RULES_YAML=path/to/routing_rules.yaml (default: config/docflow/routing_rules.yaml)

import os
import sys

PATH = os.environ.get("DOCFLOW_RULES_YAML", "config/docflow/routing_rules.yaml")

try:
    import yaml  # pyyaml
except Exception as e:
    raise SystemExit(
        "Missing dependency: pyyaml. Install it in the Odoo python env: pip install pyyaml"
    ) from e


def _find_company(env, name):
    if not name:
        return None
    c = env["res.company"].search([("name", "=", name)], limit=1)
    if not c:
        raise ValueError(f"Company not found: {name}")
    return c


def _find_currency(env, name):
    if not name:
        return None
    cur = env["res.currency"].search([("name", "=", name)], limit=1)
    if not cur:
        raise ValueError(f"Currency not found: {name}")
    return cur


def _find_journal(env, name, company_id=None):
    if not name:
        return None
    domain = [("name", "=", name)]
    if company_id:
        domain.append(("company_id", "=", company_id))
    j = env["account.journal"].search(domain, limit=1)
    if not j:
        # fallback without company filter
        j = env["account.journal"].search([("name", "=", name)], limit=1)
    if not j:
        raise ValueError(f"Journal not found: {name} (company_id={company_id})")
    return j


def _find_user(env, ident):
    if not ident:
        return None
    # prefer login match
    u = env["res.users"].search([("login", "=", ident)], limit=1)
    if u:
        return u
    # fallback: name match
    u = env["res.users"].search([("name", "=", ident)], limit=1)
    if not u:
        raise ValueError(f"User not found (login or name): {ident}")
    return u


def _find_group(env, name):
    if not name:
        return None
    g = env["res.groups"].search([("name", "=", name)], limit=1)
    if not g:
        raise ValueError(f"Group not found: {name}")
    return g


def load_rules(env, path):
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    rules = doc.get("rules") or []
    if not isinstance(rules, list):
        raise ValueError("routing_rules.yaml: rules must be a list")

    Rule = env["docflow.routing.rule"].sudo()

    created = 0
    updated = 0

    for r in rules:
        name = (r.get("name") or "").strip()
        if not name:
            raise ValueError("Rule missing name")

        company = _find_company(env, r.get("company"))
        currency = _find_currency(env, r.get("currency"))
        journal = _find_journal(env, r.get("journal"), company_id=company.id if company else None)
        user = _find_user(env, r.get("assign_user"))
        group = _find_group(env, r.get("assign_group"))

        vals = {
            "name": name,
            "active": bool(r.get("active", True)),
            "sequence": int(r.get("sequence", 10)),
            "doc_type": r.get("doc_type"),
            "source": r.get("source") or False,
            "company_id": company.id if company else False,
            "journal_id": journal.id if journal else False,
            "currency_id": currency.id if currency else False,
            "vendor_name_contains": r.get("vendor_name_contains") or False,
            "bank_account_contains": r.get("bank_account_contains") or False,
            "min_confidence": float(r.get("min_confidence") or 0.0),
            "assign_user_id": user.id if user else False,
            "assign_group_id": group.id if group else False,
        }

        existing = Rule.search([("name", "=", name)], limit=1)
        if existing:
            existing.write(vals)
            updated += 1
        else:
            Rule.create(vals)
            created += 1

    return created, updated


created, updated = load_rules(env, PATH)
print(f"DocFlow routing rules loaded from {PATH}: created={created} updated={updated}")
