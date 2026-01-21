# -*- coding: utf-8 -*-
"""
Production Readiness Gating for Odoo Modules

Extends ir.module.module with:
- Risk stage computation (stable, beta, experimental, deprecated)
- Risk score calculation (0-100)
- Install/upgrade blocking for high-risk modules
- Dependency health checks
- Odoo 18 compatibility detection
"""
import base64
import csv
import io
import logging
import os
import re
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)

# Odoo server major version
ODOO_MAJOR_VERSION = 18

# Known issue signatures - modules with specific dependency requirements
KNOWN_DEPENDENCY_RULES = {
    "ipai_theme_tbwa_backend": {
        "required": ["ipai_platform_theme"],
        "reason": "Theme backend requires ipai_platform_theme tokens module",
        "block": True,
    },
    "ipai_ocr_expense": {
        "optional": ["hr_expense"],
        "reason": "OCR expense works best with hr_expense module",
        "block": False,
    },
}

# Patterns indicating deprecated/backup modules
DEPRECATED_PATTERNS = [
    r"\.backup$",
    r"_backup$",
    r"_deprecated$",
    r"_retired$",
    r"_old$",
    r"^backup_",
]

# Patterns indicating experimental modules
EXPERIMENTAL_PATTERNS = [
    r"_experimental$",
    r"_wip$",
    r"_dev$",
    r"_test$",
]


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    # Risk assessment fields
    x_risk_stage = fields.Selection(
        selection=[
            ("stable", "Stable ✅"),
            ("beta", "Beta ⚠️"),
            ("experimental", "Experimental 🧪"),
            ("deprecated", "Deprecated ☠️"),
        ],
        string="Risk Stage",
        compute="_compute_x_risk_fields",
        store=True,
        help="Production readiness stage based on risk assessment",
    )
    x_risk_score = fields.Integer(
        string="Risk Score",
        compute="_compute_x_risk_fields",
        store=True,
        help="Risk score from 0 (safe) to 100 (high risk)",
    )
    x_risk_reasons = fields.Text(
        string="Risk Reasons",
        compute="_compute_x_risk_fields",
        store=True,
        help="Detailed reasons for the assigned risk stage",
    )
    x_block_install = fields.Boolean(
        string="Block Install/Upgrade",
        compute="_compute_x_risk_fields",
        store=True,
        help="If True, install/upgrade is blocked unless explicitly overridden",
    )
    x_block_override = fields.Boolean(
        string="Override Block",
        default=False,
        help="Admin override to allow install/upgrade despite blocking",
    )
    x_deps_missing = fields.Char(
        string="Missing Dependencies",
        compute="_compute_x_risk_fields",
        store=True,
        help="List of missing dependency modules",
    )
    x_last_risk_check = fields.Datetime(
        string="Last Risk Check",
        compute="_compute_x_risk_fields",
        store=True,
    )
    x_v18_compat_required = fields.Boolean(
        string="V18 Compat Required",
        compute="_compute_x_risk_fields",
        store=True,
        help="Module likely contains tree/list view mode issues requiring ipai_v18_compat",
    )

    @api.depends("name", "state", "installed_version", "dependencies_id")
    def _compute_x_risk_fields(self):
        """Compute all risk-related fields for modules."""
        for module in self:
            stage, score, reasons, block, deps_missing, v18_compat = (
                module._compute_risk_for_one()
            )
            module.x_risk_stage = stage
            module.x_risk_score = score
            module.x_risk_reasons = reasons
            module.x_block_install = block
            module.x_deps_missing = deps_missing
            module.x_v18_compat_required = v18_compat
            module.x_last_risk_check = fields.Datetime.now()

    def _compute_risk_for_one(self):
        """
        Compute risk assessment for a single module.

        Returns:
            tuple: (stage, score, reasons, block, deps_missing, v18_compat_required)
        """
        self.ensure_one()

        score = 0
        reasons = []
        stage = "stable"
        block = False
        v18_compat_required = False

        # Get missing dependencies
        missing_deps = self._get_deps_not_installed()
        deps_missing = ", ".join(missing_deps) if missing_deps else ""

        # Check 1: Version major mismatch
        version_mismatch = self._check_version_mismatch()
        if version_mismatch:
            score += version_mismatch["score"]
            reasons.append(version_mismatch["reason"])
            if version_mismatch["stage_override"]:
                stage = version_mismatch["stage_override"]
            if version_mismatch.get("block"):
                block = True

        # Check 2: Deprecated patterns in name
        deprecated_match = self._check_deprecated_patterns()
        if deprecated_match:
            score += 80
            reasons.append(
                f"Module name matches deprecated pattern: {deprecated_match}"
            )
            stage = "deprecated"
            block = True

        # Check 3: Experimental patterns in name
        experimental_match = self._check_experimental_patterns()
        if experimental_match and stage != "deprecated":
            score += 40
            reasons.append(
                f"Module name matches experimental pattern: {experimental_match}"
            )
            stage = "experimental"

        # Check 4: Missing dependencies (for installed modules)
        if missing_deps and self.state == "installed":
            score += 50
            reasons.append(f"Installed but missing deps: {', '.join(missing_deps)}")
            if stage not in ("deprecated",):
                stage = "beta"
            block = True
        elif missing_deps and self.state != "installed":
            score += 20
            reasons.append(f"Unmet dependencies: {', '.join(missing_deps)}")

        # Check 5: Known dependency rules
        known_issue = self._check_known_dependency_rules(missing_deps)
        if known_issue:
            score += known_issue["score"]
            reasons.append(known_issue["reason"])
            if known_issue.get("stage_override") and stage not in ("deprecated",):
                stage = known_issue["stage_override"]
            if known_issue.get("block"):
                block = True

        # Check 6: Odoo 18 tree→list compatibility
        v18_issue = self._check_v18_tree_list_compat()
        if v18_issue:
            score += v18_issue["score"]
            reasons.append(v18_issue["reason"])
            v18_compat_required = True
            if stage == "stable":
                stage = "beta"

        # Check 7: IPAI module without proper prefix
        ipai_check = self._check_ipai_naming()
        if ipai_check:
            score += ipai_check["score"]
            reasons.append(ipai_check["reason"])

        # Normalize score to 0-100
        score = min(100, max(0, score))

        # Determine stage based on score if not already set by rules
        if stage == "stable":
            if score >= 60:
                stage = "experimental"
            elif score >= 30:
                stage = "beta"

        # Auto-block experimental modules if enabled
        if stage == "experimental" and self._should_block_experimental():
            block = True

        reasons_text = "\n".join(reasons) if reasons else "No issues detected"

        return stage, score, reasons_text, block, deps_missing, v18_compat_required

    def _get_deps_not_installed(self):
        """Get list of dependencies that are not installed."""
        self.ensure_one()
        deps = self.dependencies_id.mapped("name")
        if not deps:
            return []
        installed = (
            self.env["ir.module.module"]
            .search(
                [
                    ("name", "in", deps),
                    ("state", "=", "installed"),
                ]
            )
            .mapped("name")
        )
        return sorted(set(deps) - set(installed))

    def _get_deps_not_found(self):
        """Get list of dependencies that don't exist in the system."""
        self.ensure_one()
        deps = self.dependencies_id.mapped("name")
        if not deps:
            return []
        available = (
            self.env["ir.module.module"]
            .search(
                [
                    ("name", "in", deps),
                ]
            )
            .mapped("name")
        )
        return sorted(set(deps) - set(available))

    def _check_version_mismatch(self):
        """Check for version major mismatch with Odoo server."""
        self.ensure_one()
        if not self.installed_version:
            # Not installed, check manifest version if available
            if hasattr(self, "latest_version") and self.latest_version:
                version = self.latest_version
            else:
                return None
        else:
            version = self.installed_version

        # Parse major version (e.g., "18.0.1.0.0" -> 18)
        try:
            major = int(version.split(".")[0])
        except (ValueError, IndexError):
            return {
                "score": 30,
                "reason": f"Invalid version format: {version}",
                "stage_override": "beta",
                "block": False,
            }

        if major != ODOO_MAJOR_VERSION:
            if major > ODOO_MAJOR_VERSION:
                return {
                    "score": 60,
                    "reason": f"Module version {major}.x requires Odoo {major}, server is {ODOO_MAJOR_VERSION}",
                    "stage_override": "experimental",
                    "block": True,
                }
            else:
                return {
                    "score": 40,
                    "reason": f"Module version {major}.x may need migration to Odoo {ODOO_MAJOR_VERSION}",
                    "stage_override": "beta",
                    "block": False,
                }
        return None

    def _check_deprecated_patterns(self):
        """Check if module name matches deprecated patterns."""
        self.ensure_one()
        for pattern in DEPRECATED_PATTERNS:
            if re.search(pattern, self.name, re.IGNORECASE):
                return pattern
        return None

    def _check_experimental_patterns(self):
        """Check if module name matches experimental patterns."""
        self.ensure_one()
        for pattern in EXPERIMENTAL_PATTERNS:
            if re.search(pattern, self.name, re.IGNORECASE):
                return pattern
        return None

    def _check_known_dependency_rules(self, missing_deps):
        """Check against known dependency rules."""
        self.ensure_one()
        rule = KNOWN_DEPENDENCY_RULES.get(self.name)
        if not rule:
            return None

        # Check required dependencies
        required = rule.get("required", [])
        missing_required = set(required) & set(missing_deps)
        if missing_required:
            return {
                "score": 40,
                "reason": rule["reason"],
                "stage_override": "beta",
                "block": rule.get("block", False),
            }

        # Check optional dependencies (warning only)
        optional = rule.get("optional", [])
        missing_optional = set(optional) & set(missing_deps)
        if missing_optional:
            return {
                "score": 10,
                "reason": f"Optional: {rule['reason']}",
                "stage_override": None,
                "block": False,
            }

        return None

    def _check_v18_tree_list_compat(self):
        """Check if module might have tree→list view mode issues."""
        self.ensure_one()

        # Only check if ipai_v18_compat is NOT installed
        if self._is_v18_compat_installed():
            return None

        # Only check installed IPAI modules
        if self.state != "installed" or not self.name.startswith("ipai_"):
            return None

        # Check module's XML files for tree view patterns
        has_tree_pattern = self._scan_for_tree_patterns()
        if has_tree_pattern:
            return {
                "score": 25,
                "reason": "Module may contain 'tree' view patterns; ipai_v18_compat recommended",
            }
        return None

    def _is_v18_compat_installed(self):
        """Check if ipai_v18_compat module is installed."""
        return bool(
            self.env["ir.module.module"].search_count(
                [
                    ("name", "=", "ipai_v18_compat"),
                    ("state", "=", "installed"),
                ]
            )
        )

    def _scan_for_tree_patterns(self):
        """Scan module's XML files for tree view patterns."""
        self.ensure_one()

        # Get addons paths from config
        addons_paths = config.get("addons_path", "").split(",")

        for addons_path in addons_paths:
            module_path = os.path.join(addons_path.strip(), self.name)
            if os.path.isdir(module_path):
                # Scan XML files
                for root, _, files in os.walk(module_path):
                    for filename in files:
                        if filename.endswith(".xml"):
                            filepath = os.path.join(root, filename)
                            try:
                                with open(filepath, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    # Check for tree view patterns
                                    if re.search(r"<tree\b", content) or re.search(
                                        r"view_mode.*tree", content
                                    ):
                                        return True
                            except (IOError, OSError):
                                continue
        return False

    def _check_ipai_naming(self):
        """Check IPAI module naming conventions."""
        self.ensure_one()
        if not self.name.startswith("ipai_"):
            return None

        # Check for proper domain prefix
        valid_prefixes = [
            "ipai_finance_",
            "ipai_platform_",
            "ipai_workspace_",
            "ipai_dev_studio_",
            "ipai_studio_",
            "ipai_industry_",
            "ipai_workos_",
            "ipai_theme_",
            "ipai_web_theme_",
            "ipai_ce_",
            "ipai_v18_",
            "ipai_master_",
            "ipai_agent_",
            "ipai_ask_",
            "ipai_ai_",
            "ipai_bir_",
            "ipai_ocr_",
            "ipai_ppm_",
            "ipai_project_",
            "ipai_srm_",
            "ipai_superset_",
            "ipai_portal_",
            "ipai_default_",
            "ipai_auth_",
            "ipai_close_",
            "ipai_expense_",
            "ipai_equipment_",
            "ipai_assets_",
            "ipai_advisor_",
            "ipai_clarity_",
            "ipai_custom_",
            "ipai_chatgpt_",
            "ipai_marketing_",
            "ipai_module_",
            "ipai_test_",
        ]

        if not any(self.name.startswith(prefix) for prefix in valid_prefixes):
            return {
                "score": 5,
                "reason": f"IPAI module '{self.name}' doesn't match known domain prefixes",
            }
        return None

    def _should_block_experimental(self):
        """Check if experimental modules should be blocked."""
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_module_gating.block_experimental", "1")
        )
        return param == "1"

    def _is_auto_block_enabled(self):
        """Check if automatic blocking is enabled."""
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_module_gating.auto_block", "1")
        )
        return param == "1"

    # ========================================================================
    # ACTIONS
    # ========================================================================

    def action_recompute_module_risk(self):
        """Recompute risk for all selected modules."""
        self._compute_x_risk_fields()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Risk Recomputed"),
                "message": _("Recomputed risk for %d modules") % len(self),
                "type": "success",
            },
        }

    def action_override_block(self):
        """Admin override to allow blocked install."""
        self.ensure_one()
        self.x_block_override = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Block Override"),
                "message": _("Install/upgrade block overridden for '%s'") % self.name,
                "type": "warning",
            },
        }

    def action_clear_override(self):
        """Clear admin override."""
        self.ensure_one()
        self.x_block_override = False
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Override Cleared"),
                "message": _("Block override cleared for '%s'") % self.name,
                "type": "info",
            },
        }

    def action_export_health_report(self):
        """Export module health report as CSV."""
        modules = self.search([])
        return modules._generate_health_report()

    def _generate_health_report(self):
        """Generate CSV health report for modules."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Technical Name",
                "Display Name",
                "Stage",
                "Risk Score",
                "Blocked",
                "Override",
                "State",
                "Version",
                "Missing Deps",
                "V18 Compat Required",
                "Reasons",
            ]
        )

        # Data rows
        for mod in self.sorted(key=lambda m: (m.x_risk_score or 0), reverse=True):
            writer.writerow(
                [
                    mod.name,
                    mod.shortdesc or mod.name,
                    mod.x_risk_stage or "unknown",
                    mod.x_risk_score or 0,
                    "Yes" if mod.x_block_install else "No",
                    "Yes" if mod.x_block_override else "No",
                    mod.state or "unknown",
                    mod.installed_version or mod.latest_version or "N/A",
                    mod.x_deps_missing or "",
                    "Yes" if mod.x_v18_compat_required else "No",
                    (mod.x_risk_reasons or "").replace("\n", " | "),
                ]
            )

        csv_content = output.getvalue()
        output.close()

        # Create attachment
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"module_health_report_{timestamp}.csv",
                "type": "binary",
                "datas": base64.b64encode(csv_content.encode("utf-8")),
                "mimetype": "text/csv",
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    def action_generate_markdown_report(self):
        """Generate markdown health report."""
        modules = self.search([])
        return modules._generate_markdown_report()

    def _generate_markdown_report(self):
        """Generate markdown report for modules."""
        lines = [
            "# Module Production Readiness Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
        ]

        # Summary stats
        stable = self.filtered(lambda m: m.x_risk_stage == "stable")
        beta = self.filtered(lambda m: m.x_risk_stage == "beta")
        experimental = self.filtered(lambda m: m.x_risk_stage == "experimental")
        deprecated = self.filtered(lambda m: m.x_risk_stage == "deprecated")
        blocked = self.filtered(lambda m: m.x_block_install)

        lines.extend(
            [
                f"| Stage | Count |",
                f"|-------|-------|",
                f"| Stable ✅ | {len(stable)} |",
                f"| Beta ⚠️ | {len(beta)} |",
                f"| Experimental 🧪 | {len(experimental)} |",
                f"| Deprecated ☠️ | {len(deprecated)} |",
                f"| **Blocked** | {len(blocked)} |",
                "",
            ]
        )

        # High-risk modules
        high_risk = self.filtered(lambda m: (m.x_risk_score or 0) >= 40).sorted(
            key=lambda m: m.x_risk_score, reverse=True
        )

        if high_risk:
            lines.extend(
                [
                    "## High-Risk Modules",
                    "",
                    "| Module | Stage | Score | Blocked | Issues |",
                    "|--------|-------|-------|---------|--------|",
                ]
            )
            for mod in high_risk[:20]:  # Top 20
                reasons = (mod.x_risk_reasons or "").replace("\n", "; ")[:100]
                lines.append(
                    f"| `{mod.name}` | {mod.x_risk_stage} | {mod.x_risk_score} | "
                    f"{'🚫' if mod.x_block_install else '✓'} | {reasons} |"
                )
            lines.append("")

        # Blocked modules
        if blocked:
            lines.extend(
                [
                    "## Blocked Modules",
                    "",
                ]
            )
            for mod in blocked:
                override_status = " (override active)" if mod.x_block_override else ""
                lines.append(f"- `{mod.name}`: {mod.x_risk_reasons}{override_status}")
            lines.append("")

        # V18 compat required
        v18_needed = self.filtered(lambda m: m.x_v18_compat_required)
        if v18_needed:
            lines.extend(
                [
                    "## Modules Requiring V18 Compatibility",
                    "",
                    "These modules may need `ipai_v18_compat` for tree→list view fixes:",
                    "",
                ]
            )
            for mod in v18_needed:
                lines.append(f"- `{mod.name}`")
            lines.append("")

        md_content = "\n".join(lines)

        # Create attachment
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"module_health_report_{timestamp}.md",
                "type": "binary",
                "datas": base64.b64encode(md_content.encode("utf-8")),
                "mimetype": "text/markdown",
            }
        )

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    # ========================================================================
    # INSTALL/UPGRADE BLOCKING
    # ========================================================================

    def button_install(self):
        """Override install to check risk blocking."""
        self._check_install_allowed()
        return super().button_install()

    def button_immediate_install(self):
        """Override immediate install to check risk blocking."""
        self._check_install_allowed()
        return super().button_immediate_install()

    def button_upgrade(self):
        """Override upgrade to check risk blocking."""
        self._check_install_allowed()
        return super().button_upgrade()

    def button_immediate_upgrade(self):
        """Override immediate upgrade to check risk blocking."""
        self._check_install_allowed()
        return super().button_immediate_upgrade()

    def _check_install_allowed(self):
        """Check if install/upgrade is allowed based on risk assessment."""
        if not self._is_auto_block_enabled():
            return True

        # Check if allow_override is enabled and user has override
        allow_override = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_module_gating.allow_override", "1")
        )

        for module in self:
            if module.x_block_install and not module.x_block_override:
                if allow_override != "1":
                    raise UserError(
                        _(
                            "Module '%s' is blocked from install/upgrade.\n\n"
                            "Risk Stage: %s\n"
                            "Risk Score: %d\n"
                            "Reasons:\n%s\n\n"
                            "Contact your administrator to resolve the blocking issues."
                        )
                        % (
                            module.name,
                            module.x_risk_stage or "Unknown",
                            module.x_risk_score or 0,
                            module.x_risk_reasons or "Unknown",
                        )
                    )
                else:
                    # Allow but warn - admin can override
                    _logger.warning(
                        "Installing blocked module '%s' (score=%d, stage=%s). "
                        "Set x_block_override=True to suppress this warning.",
                        module.name,
                        module.x_risk_score,
                        module.x_risk_stage,
                    )
        return True

    # ========================================================================
    # SCHEDULED ACTIONS
    # ========================================================================

    @api.model
    def _cron_recompute_all_risk(self):
        """Scheduled action to recompute risk for all modules."""
        _logger.info("Starting scheduled module risk recomputation...")
        modules = self.search([])
        modules._compute_x_risk_fields()
        _logger.info("Completed risk recomputation for %d modules", len(modules))
        return True

    # ========================================================================
    # JSON EXPORT FOR CI
    # ========================================================================

    def _export_status_json(self):
        """Export module status as JSON for CI integration."""
        import json

        data = {
            "generated_at": datetime.now().isoformat(),
            "odoo_version": ODOO_MAJOR_VERSION,
            "modules": {},
        }

        for mod in self:
            data["modules"][mod.name] = {
                "stage": mod.x_risk_stage,
                "score": mod.x_risk_score,
                "blocked": mod.x_block_install,
                "override": mod.x_block_override,
                "state": mod.state,
                "version": mod.installed_version or mod.latest_version,
                "deps_missing": mod.x_deps_missing,
                "v18_compat_required": mod.x_v18_compat_required,
                "reasons": mod.x_risk_reasons,
            }

        return json.dumps(data, indent=2)
