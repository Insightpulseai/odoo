# -*- coding: utf-8 -*-
"""
IPAI AI Studio Run Model.

Orchestrates the complete workflow:
1. Prompt → Spec JSON (via LLM)
2. Spec JSON → Generated Addon Files
3. Validation (static checks)
4. Apply (filesystem or git commit)
5. Optional: Install/Upgrade on DB
"""
import json
import os
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from .generator import render_addon_from_spec
from .validator import validate_generated_addon
from .llm_client import draft_spec_json
from .git_ops import commit_generated_module


SAFE_MOD_RE = re.compile(r"^ipai_[a-z0-9_]+$")


class IpaiAiStudioRun(models.Model):
    _name = "ipai.ai_studio.run"
    _description = "IPAI AI Studio Run"
    _order = "create_date desc"

    name = fields.Char(default=lambda self: _("AI Studio Run"), required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("validated", "Validated"),
            ("failed", "Failed"),
            ("applied", "Applied"),
        ],
        default="draft",
        required=True,
    )

    prompt = fields.Text(string="Request (Chat Input)")
    spec_json = fields.Text(string="Spec JSON")
    module_name = fields.Char(string="Module Technical Name", readonly=False)
    workspace_path = fields.Char(string="Workspace Path", readonly=True)

    validation_ok = fields.Boolean(string="Validation OK", default=False, readonly=True)
    validation_report = fields.Text(string="Validation Report", readonly=True)

    generated_files_json = fields.Text(string="Generated Files (JSON)", readonly=True)

    # -------------------------------------------------------------------------
    # LLM Configuration
    # -------------------------------------------------------------------------

    def _llm_config(self):
        """
        Config via system params (preferred):
          - ipai_ai_studio.llm_base_url
          - ipai_ai_studio.llm_api_key
          - ipai_ai_studio.llm_model
          - ipai_ai_studio.llm_timeout_s

        Fallback to existing Ask AI keys if present:
          - ipai_copilot.api_url
          - ipai_copilot.api_key
          - ipai_copilot.model
        """
        icp = self.env["ir.config_parameter"].sudo()

        base_url = (
            icp.get_param("ipai_ai_studio.llm_base_url")
            or icp.get_param("ipai_copilot.api_url")
            or ""
        )
        api_key = (
            icp.get_param("ipai_ai_studio.llm_api_key")
            or icp.get_param("ipai_copilot.api_key")
            or ""
        )
        model = (
            icp.get_param("ipai_ai_studio.llm_model")
            or icp.get_param("ipai_copilot.model")
            or "gpt-4o-mini"
        )
        timeout = int(icp.get_param("ipai_ai_studio.llm_timeout_s") or "60")

        if not base_url:
            raise UserError(
                _(
                    "Missing LLM base URL. Set system param "
                    "ipai_ai_studio.llm_base_url (or ipai_copilot.api_url)."
                )
            )

        return base_url, api_key, model, timeout

    # -------------------------------------------------------------------------
    # Addons Path Resolution
    # -------------------------------------------------------------------------

    def _addons_root_candidates(self):
        """
        Best-effort: pick a writable addons root from common self-hosted layouts.
        You can hard-pin via system parameter: ipai_ai_studio.addons_root
        """
        icp = self.env["ir.config_parameter"].sudo()
        pinned = icp.get_param("ipai_ai_studio.addons_root")
        if pinned:
            return [pinned]

        return [
            "/mnt/extra-addons",                 # common docker mount
            "/opt/odoo/custom-addons",           # common custom
            "/home/user/odoo-ce/addons",         # your observed layout
            "/workspace/addons",                 # CI-ish
        ]

    def _resolve_addons_root(self):
        for p in self._addons_root_candidates():
            if p and os.path.isdir(p) and os.access(p, os.W_OK):
                return p
        raise UserError(
            _(
                "No writable addons root found. Set system parameter "
                "ipai_ai_studio.addons_root to a writable path."
            )
        )

    def _generated_base_dir(self):
        addons_root = self._resolve_addons_root()
        gen = os.path.join(addons_root, "generated")
        os.makedirs(gen, exist_ok=True)
        return gen

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_draft_spec_from_prompt(self):
        """Draft spec JSON from prompt using LLM."""
        for rec in self:
            if not rec.prompt:
                raise UserError(_("Prompt is empty. Fill the Request tab first."))

            base_url, api_key, model, timeout = rec._llm_config()

            try:
                spec_str = draft_spec_json(
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    user_prompt=rec.prompt,
                    timeout_s=timeout,
                )
            except Exception as e:
                raise UserError(_("Spec draft failed: %s") % str(e))

            rec.spec_json = spec_str
            rec.state = "draft"

            # Auto-populate module_name from spec if available
            try:
                spec = json.loads(spec_str)
                if spec.get("module_name"):
                    rec.module_name = spec["module_name"]
            except Exception:
                pass

        return True

    def action_generate_from_spec(self):
        """Generate addon files from spec JSON."""
        for rec in self:
            spec = rec._load_spec()
            mod = spec.get("module_name") or rec.module_name
            if not mod or not SAFE_MOD_RE.match(mod):
                raise UserError(
                    _("Invalid module_name. Must match: ipai_[a-z0-9_]+")
                )

            rec.module_name = mod

            out_dir = os.path.join(rec._generated_base_dir(), mod)

            try:
                files = render_addon_from_spec(self.env, spec)
            except ValueError as e:
                # Dependency guardrail failure
                raise UserError(_("Generation blocked: %s") % str(e))

            # Write files
            for rel_path, content in files.items():
                abs_path = os.path.join(out_dir, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content)

            rec.workspace_path = out_dir
            rec.generated_files_json = json.dumps(sorted(list(files.keys())), indent=2)
            rec.state = "generated"
            rec.validation_ok = False
            rec.validation_report = False

        return True

    def action_validate(self):
        """Run static validation on generated addon."""
        for rec in self:
            if not rec.workspace_path:
                raise UserError(_("Nothing to validate. Generate first."))

            ok, report = validate_generated_addon(rec.workspace_path)
            rec.validation_ok = bool(ok)
            rec.validation_report = report
            rec.state = "validated" if ok else "failed"

        return True

    def action_apply(self):
        """
        Apply generated module.

        Modes (via ipai_ai_studio.apply_mode system param):
        - filesystem (default): Files already written to addons root, just mark applied
        - git_commit: Create a new git branch and commit the generated files
        """
        for rec in self:
            if not rec.workspace_path:
                raise UserError(_("Nothing to apply. Generate first."))
            if not rec.validation_ok:
                raise UserError(_("Validation must pass before applying."))

            icp = self.env["ir.config_parameter"].sudo()
            mode = (icp.get_param("ipai_ai_studio.apply_mode") or "filesystem").strip().lower()

            if mode == "git_commit":
                repo_root = icp.get_param("ipai_ai_studio.repo_root") or "/home/user/odoo-ce"
                if not os.path.isdir(repo_root):
                    raise UserError(
                        _("Repo root not found. Set ipai_ai_studio.repo_root.")
                    )

                module_rel = os.path.relpath(rec.workspace_path, repo_root)

                try:
                    branch, out = commit_generated_module(
                        repo_root, module_rel, rec.module_name
                    )
                    rec.validation_report = (
                        (rec.validation_report or "") + "\n\n[GIT]\n" + out
                    )
                    rec.workspace_path = f"{rec.workspace_path} (git:{branch})"
                except Exception as e:
                    raise UserError(_("Git apply failed: %s") % str(e))

            rec.state = "applied"
        return True

    def action_install_on_db(self):
        """
        Optional: install generated module on current DB using Odoo's module API.
        This will mutate the DB; use only in dev/stage.
        """
        for rec in self:
            if not rec.module_name:
                raise UserError(_("No module_name set."))
            if not rec.validation_ok:
                raise UserError(_("Validation must pass before install."))

            mod = (
                self.env["ir.module.module"]
                .sudo()
                .search([("name", "=", rec.module_name)], limit=1)
            )
            if not mod:
                raise UserError(
                    _(
                        "Module not found in Apps registry yet. "
                        "Update Apps List then retry (Apps > Update Apps List)."
                    )
                )

            if mod.state in ("installed", "to upgrade"):
                mod.button_immediate_upgrade()
            else:
                mod.button_immediate_install()

        return True

    def _load_spec(self):
        """Parse and return spec JSON."""
        for rec in self:
            if not rec.spec_json:
                raise UserError(_("Spec JSON is empty. Paste spec JSON first."))
            try:
                return json.loads(rec.spec_json)
            except Exception as e:
                raise UserError(_("Invalid JSON spec: %s") % str(e))
