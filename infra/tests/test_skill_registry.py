import yaml
import pathlib
import pytest


def test_deploy_skill_registered():
    # Use absolute path relative to repo root
    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    assert p.exists(), f"Registry file not found at {p}"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    ids = [s["id"] for s in skills]

    assert "deploy-odoo-modules-git" in ids, "deploy-odoo-modules-git skill not found in registry"

    # Verify guardrails
    skill = next(s for s in skills if s["id"] == "deploy-odoo-modules-git")
    guardrails = skill.get("guardrails", {})
    assert guardrails.get("prod_requires_staging_success") is True
    assert guardrails.get("forbid_enterprise_modules") is True


def test_fullstack_skill_registered():
    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    ids = [s["id"] for s in skills]

    assert "odoo-fullstack-ai-dev" in ids, "odoo-fullstack-ai-dev skill not found in registry"
    assert "odoo-studio-mastery" not in ids, "odoo-studio-mastery skill should be removed"

    skill = next(s for s in skills if s["id"] == "odoo-fullstack-ai-dev")
    assert skill["type"] == "knowledge"
    assert "ai" in skill["domains"]
    assert "fullstack" in skill["domains"]


def test_backup_skill_registered():
    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    by_id = {s["id"]: s for s in skills}

    assert "backup-odoo-environment" in by_id, "backup-odoo-environment skill not found in registry"

    skill = by_id["backup-odoo-environment"]
    guardrails = skill.get("guardrails", {})

    assert guardrails.get("integrity_checks_required") is True
    assert guardrails.get("redact_secrets_in_evidence") is True
    assert guardrails.get("redact_secrets_in_evidence") is True
    assert guardrails.get("retention_policy_default") == {"daily": 7, "weekly": 4, "monthly": 3}


def test_restore_skill_registered():
    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    by_id = {s["id"]: s for s in skills}

    assert "restore-odoo-environment" in by_id, (
        "restore-odoo-environment skill not found in registry"
    )

    skill = by_id["restore-odoo-environment"]
    guardrails = skill.get("guardrails", {})

    # Validate all 6 mandatory guardrails
    assert guardrails.get("forbid_parallel_deploy_restore") is True
    assert guardrails.get("prod_requires_human_confirmation") is True
    assert guardrails.get("pre_restore_backup_mandatory") is True
    assert guardrails.get("redact_secrets_in_evidence") is True
    assert guardrails.get("integrity_checks_required") is True
    assert guardrails.get("rollback_on_failure_default") is True


def test_refresh_kb_skill_registered():
    import yaml
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    by_id = {s["id"]: s for s in skills}

    assert "refresh-odoo19-kb" in by_id, "refresh-odoo19-kb skill not found in registry"

    skill = by_id["refresh-odoo19-kb"]
    guardrails = skill.get("guardrails", {})

    assert guardrails.get("integrity_checks_required") is True
    assert "docs" in skill["domains"]


def test_promote_skill_registered():
    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    skills = data.get("skills", [])
    by_id = {s["id"]: s for s in skills}

    assert "promote-staging-to-prod" in by_id, "promote-staging-to-prod skill not found in registry"

    skill = by_id["promote-staging-to-prod"]
    guardrails = skill.get("guardrails", {})

    # Validate mandatory guardrails
    assert guardrails.get("prod_requires_staging_success") is True
    assert guardrails.get("forbid_enterprise_modules") is True
    assert guardrails.get("rollback_default") is True
    assert guardrails.get("evidence_required") is True

    # Validate dependencies include restore-odoo-environment
    requires = skill.get("requires", [])
    assert "restore-odoo-environment" in requires, "promote skill must depend on restore-odoo-environment"
    assert "backup-odoo-environment" in requires, "promote skill must depend on backup-odoo-environment"


def test_validate_module_skill_registered():
    import yaml
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    by_id = {s["id"]: s for s in data.get("skills", [])}

    assert "validate-odoo-module-against-kb" in by_id
    skill = by_id["validate-odoo-module-against-kb"]

    assert skill["type"] == "procedural"
    assert skill["kb"]["namespace"] == "docs/kb/odoo19"
    assert skill["guardrails"]["forbid_enterprise_modules"] is True


def test_generate_skill_registered():
    import yaml
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent
    p = repo_root / "agents/registry/odoo_skills.yaml"

    data = yaml.safe_load(p.read_text())
    by_id = {s["id"]: s for s in data.get("skills", [])}

    assert "generate-odoo-skill-from-kb" in by_id
    skill = by_id["generate-odoo-skill-from-kb"]

    assert skill["type"] == "procedural"
    assert "meta" in skill["domains"]
    assert skill["routing"]["default_tier"] == "remote"
