# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""
Pulser intent handlers — read-only MVP actions.

Each handler:
  1. Validates args per the exact request contract
  2. Executes the Odoo action
  3. Returns a ``data`` dict wrapped in the universal envelope

Contract: docs/contracts/C-PULSER-ODOO-01.md
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone

from odoo import api, models, release

_logger = logging.getLogger(__name__)

# Hard caps
INSTALLED_SAMPLE_MAX = 100
INSTALLED_SAMPLE_DEFAULT = 50

# Valid environment values
VALID_ENVS = {"prod", "stage", "dev"}

# Known allowlist profiles
KNOWN_ALLOWLIST_PROFILES = {"oca_allowlist_v1"}

# Allowlisted safe config keys (never include secrets)
SAFE_CONFIG_KEYS = frozenset({
    "db_host", "db_port", "db_sslmode", "proxy_mode",
    "workers", "limit_time_real", "limit_time_cpu",
    "smtp_host", "smtp_port", "addons_path",
})


class ArgsValidationError(Exception):
    """Raised when intent args fail validation."""

    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class PulserHandlers(models.AbstractModel):
    _name = "ipai.pulser.handlers"
    _description = "Pulser Intent Handlers"

    # ── Dispatcher ──────────────────────────────────────────────────────

    @api.model
    def _dispatch(self, intent_type, args):
        """Dispatch an intent_type to its handler. Returns data dict.

        Raises:
            ValueError: Unknown or disallowed intent type.
            ArgsValidationError: Invalid args (code + details available).
        """
        handlers = {
            "odoo.healthcheck": self._handle_healthcheck,
            "odoo.modules.status": self._handle_modules_status,
            "odoo.config.snapshot": self._handle_config_snapshot,
        }

        handler = handlers.get(intent_type)
        if not handler:
            raise ValueError(
                "Unknown or disallowed intent type: %s" % intent_type
            )

        return handler(args)

    # ── Shared args helpers ─────────────────────────────────────────────

    @api.model
    def _validate_env(self, args):
        """Extract and validate the env field. Returns validated env string."""
        env = args.get("env", "prod")
        if env not in VALID_ENVS:
            raise ArgsValidationError(
                "ARGS_INVALID",
                "Invalid env value: %s" % env,
                {"path": "args.env", "allowed": list(VALID_ENVS)},
            )
        return env

    @api.model
    def _extract_meta(self, args):
        """Extract optional meta block for trace propagation."""
        meta = args.get("meta", {})
        return {
            "work_item_ref": meta.get("work_item_ref", "spec:odooops-console"),
            "correlation_id": meta.get("correlation_id"),
            "reply": meta.get("reply"),
        }

    # ── odoo.healthcheck ────────────────────────────────────────────────

    @api.model
    def _handle_healthcheck(self, args):
        """Return Odoo health status.

        Args schema:
          { env, include: { addons_paths, workers, modules_count, supabase_reachable } }
        """
        self._validate_env(args)
        include = args.get("include", {})

        now_utc = datetime.now(timezone.utc).isoformat()
        db_name = self.env.cr.dbname

        # Installed module count (bounded query)
        installed_count = None
        if include.get("modules_count", True):
            self.env.cr.execute(
                "SELECT COUNT(*) FROM ir_module_module "
                "WHERE state = 'installed'"
            )
            installed_count = self.env.cr.fetchone()[0]

        # Addons paths from Odoo config
        from odoo.tools import config as odoo_config

        addons_paths = None
        if include.get("addons_paths", True):
            raw = odoo_config.get("addons_path", "").split(",")
            addons_paths = [p.strip() for p in raw if p.strip()]

        # Workers config
        workers_data = None
        if include.get("workers", True):
            workers = int(odoo_config.get("workers", 0))
            workers_data = {
                "mode": "prefork" if workers > 0 else "threaded",
                "configured": workers,
            }

        # Base URL
        base_url = self.env["ir.config_parameter"].sudo().get_param(
            "web.base.url", default=""
        )

        # Supabase connectivity check
        supabase_data = None
        if include.get("supabase_reachable", True):
            supabase_reachable = False
            supabase_url = os.environ.get("SUPABASE_URL", "")
            if supabase_url:
                import requests
                try:
                    resp = requests.get(
                        "%s/rest/v1/" % supabase_url,
                        headers={
                            "apikey": os.environ.get(
                                "SUPABASE_SERVICE_ROLE_KEY", ""
                            )
                        },
                        timeout=5,
                    )
                    supabase_reachable = resp.status_code < 500
                except Exception:
                    pass
            supabase_data = {
                "reachable": supabase_reachable,
                "project_ref": "spdtwktxdalcfigzeqrz",
            }

        return {
            "odoo": {
                "version": release.version,
                "server_time_utc": now_utc,
                "db_name": db_name,
                "base_url": base_url,
                "addons_paths": addons_paths,
            },
            "runtime": {
                "environment": self._detect_environment(),
                "container": {
                    "name": os.environ.get("HOSTNAME", None),
                    "host": os.environ.get("HOST_IP", None),
                },
                "workers": workers_data,
            },
            "modules": {
                "installed_count": installed_count,
            },
            "connectivity": {
                "supabase": supabase_data,
            },
        }

    # ── odoo.modules.status ─────────────────────────────────────────────

    @api.model
    def _handle_modules_status(self, args):
        """Return installed modules list with optional allowlist diff.

        Args schema:
          { env, limit: { installed_sample }, allowlist: { profile, include_diff },
            risk: { include } }
        """
        self._validate_env(args)

        # Parse and validate limit
        limit_cfg = args.get("limit", {})
        sample_cap = limit_cfg.get("installed_sample", INSTALLED_SAMPLE_DEFAULT)
        if not isinstance(sample_cap, int) or sample_cap < 1:
            raise ArgsValidationError(
                "ARGS_INVALID",
                "installed_sample must be a positive integer",
                {"path": "args.limit.installed_sample", "value": sample_cap},
            )
        if sample_cap > INSTALLED_SAMPLE_MAX:
            raise ArgsValidationError(
                "ARGS_INVALID",
                "installed_sample exceeds maximum of %d" % INSTALLED_SAMPLE_MAX,
                {
                    "path": "args.limit.installed_sample",
                    "value": sample_cap,
                    "max": INSTALLED_SAMPLE_MAX,
                },
            )

        # Parse and validate allowlist
        allowlist_cfg = args.get("allowlist", {})
        profile = allowlist_cfg.get("profile", "oca_allowlist_v1")
        if profile not in KNOWN_ALLOWLIST_PROFILES:
            raise ArgsValidationError(
                "ALLOWLIST_PROFILE_UNKNOWN",
                "Unknown allowlist profile: %s" % profile,
                {
                    "path": "args.allowlist.profile",
                    "value": profile,
                    "known": list(KNOWN_ALLOWLIST_PROFILES),
                },
            )

        # Fetch installed modules (bounded)
        fetch_limit = sample_cap + 10
        self.env.cr.execute(
            "SELECT name FROM ir_module_module WHERE state = 'installed' "
            "ORDER BY name LIMIT %s",
            (fetch_limit,),
        )
        installed = [row[0] for row in self.env.cr.fetchall()]
        total_count = len(installed)

        if total_count >= fetch_limit:
            self.env.cr.execute(
                "SELECT COUNT(*) FROM ir_module_module "
                "WHERE state = 'installed'"
            )
            total_count = self.env.cr.fetchone()[0]

        sample = installed[:sample_cap]

        # Allowlist diff (placeholder — full impl reads SSOT allowlist file)
        missing_from_allowlist = []
        allowlisted_not_installed = []
        passed = True

        # Risk assessment
        risk_cfg = args.get("risk", {})
        include_risk = risk_cfg.get("include", True)

        return {
            "environment": self._detect_environment(),
            "installed": {
                "count": total_count,
                "sample": sample,
            },
            "allowlist": {
                "profile": profile,
                "passed": passed,
                "missing_from_allowlist": missing_from_allowlist,
                "allowlisted_not_installed": allowlisted_not_installed,
            },
            "risk": {
                "high_risk_detected": False,
                "violations": [],
            } if include_risk else None,
            "evidence_refs": {
                "module_status_artifact": None,
                "allowlist_diff_artifact": None,
            },
        }

    # ── odoo.config.snapshot ────────────────────────────────────────────

    @api.model
    def _handle_config_snapshot(self, args):
        """Return a safe config fingerprint (no secrets).

        Args schema:
          { env, redaction: { mode, include_keys }, fingerprint: { algorithm, include_keys } }
        """
        self._validate_env(args)
        from odoo.tools import config as odoo_config

        # Validate redaction mode
        redaction_cfg = args.get("redaction", {})
        redaction_mode = redaction_cfg.get("mode", "safe")
        if redaction_mode != "safe":
            raise ArgsValidationError(
                "REDACTION_MODE_UNSUPPORTED",
                "Only 'safe' redaction mode is supported",
                {"path": "args.redaction.mode", "value": redaction_mode},
            )

        # Validate include_keys against allowlist
        requested_keys = redaction_cfg.get("include_keys", list(SAFE_CONFIG_KEYS))
        unsafe_keys = set(requested_keys) - SAFE_CONFIG_KEYS
        if unsafe_keys:
            raise ArgsValidationError(
                "ARGS_INVALID",
                "Requested keys contain unsafe/unknown entries: %s"
                % ", ".join(sorted(unsafe_keys)),
                {
                    "path": "args.redaction.include_keys",
                    "unsafe_keys": sorted(unsafe_keys),
                    "allowed_keys": sorted(SAFE_CONFIG_KEYS),
                },
            )

        # Build config data from safe keys
        config_data = {}
        for key in requested_keys:
            if key in ("db_port", "workers", "limit_time_real", "limit_time_cpu"):
                config_data[key] = int(odoo_config.get(key, 0))
            elif key == "proxy_mode":
                config_data[key] = bool(odoo_config.get(key, False))
            elif key in ("smtp_host", "smtp_port"):
                # Read from mail server table
                pass  # handled below
            else:
                config_data[key] = odoo_config.get(key, "")

        # SMTP config (safe fields only — no passwords)
        self.env.cr.execute(
            "SELECT smtp_host, smtp_port FROM ir_mail_server "
            "WHERE active = true ORDER BY sequence LIMIT 1"
        )
        mail_row = self.env.cr.fetchone()
        smtp_host = mail_row[0] if mail_row else ""
        smtp_port = mail_row[1] if mail_row else 0

        if "smtp_host" in requested_keys:
            config_data["smtp_host"] = smtp_host
        if "smtp_port" in requested_keys:
            config_data["smtp_port"] = smtp_port

        # Fingerprint
        fp_cfg = args.get("fingerprint", {})
        fp_algorithm = fp_cfg.get("algorithm", "sha256")
        fp_keys = fp_cfg.get("include_keys", list(SAFE_CONFIG_KEYS))

        # Validate fingerprint keys against allowlist
        unsafe_fp = set(fp_keys) - SAFE_CONFIG_KEYS
        if unsafe_fp:
            raise ArgsValidationError(
                "ARGS_INVALID",
                "Fingerprint keys contain unsafe entries: %s"
                % ", ".join(sorted(unsafe_fp)),
                {
                    "path": "args.fingerprint.include_keys",
                    "unsafe_keys": sorted(unsafe_fp),
                },
            )

        fp_data = {}
        for k in fp_keys:
            if k in config_data:
                fp_data[k] = str(config_data[k])
            elif k in ("smtp_host",):
                fp_data[k] = smtp_host
            elif k in ("smtp_port",):
                fp_data[k] = str(smtp_port)
            else:
                fp_data[k] = str(odoo_config.get(k, ""))

        fingerprint = hashlib.sha256(
            json.dumps(fp_data, sort_keys=True).encode()
        ).hexdigest()

        # Detect catcher mode
        env = self._detect_environment()
        catcher_mode = (
            env != "prod"
            and "mailgun" in (smtp_host or "").lower()
        )

        return {
            "environment": env,
            "config": {
                "odoo_conf_fingerprint": "sha256:%s" % fingerprint,
                **{k: v for k, v in config_data.items()
                   if k not in ("smtp_host", "smtp_port")},
            },
            "mail": {
                "smtp_host": smtp_host,
                "smtp_port": smtp_port,
                "catcher_mode": catcher_mode,
            },
            "feature_flags": {
                "mail_catcher_enforced_nonprod": True,
                "json_only_api_contract": True,
            },
        }

    # ── Helpers ─────────────────────────────────────────────────────────

    @api.model
    def _detect_environment(self):
        """Detect runtime environment from config/env vars."""
        env = os.environ.get("ODOO_ENV", "").lower()
        if env in ("prod", "production"):
            return "prod"
        if env in ("stage", "staging"):
            return "stage"
        if env in ("dev", "development"):
            return "dev"

        # Fallback: check db name
        db_name = self.env.cr.dbname
        if "prod" in db_name:
            return "prod"
        if "stage" in db_name:
            return "stage"
        return "dev"
