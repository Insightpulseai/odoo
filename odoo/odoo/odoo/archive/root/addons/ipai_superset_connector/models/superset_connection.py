# -*- coding: utf-8 -*-
"""
Superset Connection Model

Manages connections to Apache Superset instances.
Handles authentication, API calls, and connection pooling.
"""
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from odoo.exceptions import UserError, ValidationError

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SupersetConnection(models.Model):
    _name = "superset.connection"
    _description = "Superset Connection"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Connection Name",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    # Connection Settings
    base_url = fields.Char(
        string="Superset URL",
        required=True,
        help="Base URL of your Superset instance (e.g., https://superset.company.com)",
        tracking=True,
    )

    # Authentication
    auth_method = fields.Selection(
        [
            ("basic", "Username/Password"),
            ("ldap", "LDAP"),
            ("oauth", "OAuth2"),
            ("api_key", "API Key"),
        ],
        string="Auth Method",
        default="basic",
        required=True,
    )

    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    api_key = fields.Char(string="API Key")

    # Token Management
    access_token = fields.Char(string="Access Token", readonly=True)
    refresh_token = fields.Char(string="Refresh Token", readonly=True)
    token_expiry = fields.Datetime(string="Token Expiry", readonly=True)
    csrf_token = fields.Char(string="CSRF Token", readonly=True)

    # Database Connection (for Odoo's PostgreSQL)
    db_connection_id = fields.Integer(
        string="Superset Database ID",
        help="ID of the database connection in Superset",
        readonly=True,
    )
    db_connection_name = fields.Char(
        string="Database Name in Superset",
        default="Odoo Production",
    )

    # PostgreSQL Connection Details (for Superset to connect to Odoo's DB)
    pg_host = fields.Char(
        string="PostgreSQL Host",
        default="localhost",
        help="Hostname of Odoo PostgreSQL server (use read replica if available)",
    )
    pg_port = fields.Integer(
        string="PostgreSQL Port",
        default=5432,
    )
    pg_database = fields.Char(
        string="PostgreSQL Database",
        help="Odoo database name",
    )
    pg_username = fields.Char(
        string="PostgreSQL Username",
        help="Read-only user recommended",
    )
    pg_password = fields.Char(
        string="PostgreSQL Password",
    )
    pg_schema = fields.Char(
        string="PostgreSQL Schema",
        default="public",
    )
    use_ssl = fields.Boolean(
        string="Use SSL",
        default=True,
    )

    # Status
    state = fields.Selection(
        [
            ("draft", "Not Connected"),
            ("connected", "Connected"),
            ("error", "Connection Error"),
        ],
        string="Status",
        default="draft",
        readonly=True,
        tracking=True,
    )

    last_sync = fields.Datetime(string="Last Sync", readonly=True)
    last_error = fields.Text(string="Last Error", readonly=True)

    # Related
    dataset_ids = fields.One2many(
        "superset.dataset",
        "connection_id",
        string="Datasets",
    )
    dataset_count = fields.Integer(
        string="Dataset Count",
        compute="_compute_dataset_count",
    )

    @api.depends("dataset_ids")
    def _compute_dataset_count(self):
        for rec in self:
            rec.dataset_count = len(rec.dataset_ids)

    # =========================================================================
    # API CLIENT METHODS
    # =========================================================================

    def _get_session(self):
        """Get requests session with authentication"""
        self.ensure_one()
        session = requests.Session()
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Check if token is still valid
        if self.access_token and self.token_expiry:
            if fields.Datetime.now() < self.token_expiry:
                session.headers["Authorization"] = f"Bearer {self.access_token}"
                if self.csrf_token:
                    session.headers["X-CSRFToken"] = self.csrf_token
                return session

        # Authenticate
        self._authenticate(session)
        return session

    def _authenticate(self, session):
        """Authenticate with Superset and get tokens"""
        self.ensure_one()

        if self.auth_method == "api_key":
            session.headers["Authorization"] = f"Bearer {self.api_key}"
            self.write(
                {
                    "access_token": self.api_key,
                    "token_expiry": fields.Datetime.now() + timedelta(days=365),
                }
            )
            return

        # Username/Password authentication
        auth_url = urljoin(self.base_url, "/api/v1/security/login")
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db" if self.auth_method == "basic" else "ldap",
            "refresh": True,
        }

        try:
            response = session.post(auth_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")

            if not access_token:
                raise UserError(_("Authentication failed: No access token returned"))

            # Get CSRF token
            csrf_url = urljoin(self.base_url, "/api/v1/security/csrf_token/")
            session.headers["Authorization"] = f"Bearer {access_token}"
            csrf_response = session.get(csrf_url, timeout=30)
            csrf_token = (
                csrf_response.json().get("result") if csrf_response.ok else None
            )

            self.write(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "csrf_token": csrf_token,
                    "token_expiry": fields.Datetime.now() + timedelta(hours=1),
                    "state": "connected",
                    "last_error": False,
                }
            )

            session.headers["Authorization"] = f"Bearer {access_token}"
            if csrf_token:
                session.headers["X-CSRFToken"] = csrf_token

        except requests.RequestException as e:
            self.write(
                {
                    "state": "error",
                    "last_error": str(e),
                }
            )
            raise UserError(_("Superset authentication failed: %s") % str(e))

    def _api_call(self, method, endpoint, data=None, params=None):
        """Make authenticated API call to Superset"""
        self.ensure_one()
        session = self._get_session()
        url = urljoin(self.base_url, endpoint)

        try:
            if method.upper() == "GET":
                response = session.get(url, params=params, timeout=60)
            elif method.upper() == "POST":
                response = session.post(url, json=data, timeout=60)
            elif method.upper() == "PUT":
                response = session.put(url, json=data, timeout=60)
            elif method.upper() == "DELETE":
                response = session.delete(url, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.RequestException as e:
            _logger.error("Superset API error: %s %s - %s", method, endpoint, str(e))
            self.write(
                {
                    "state": "error",
                    "last_error": f"{method} {endpoint}: {str(e)}",
                }
            )
            raise UserError(_("Superset API error: %s") % str(e))

    # =========================================================================
    # CONNECTION ACTIONS
    # =========================================================================

    def action_test_connection(self):
        """Test connection to Superset"""
        self.ensure_one()
        try:
            # Test authentication
            result = self._api_call("GET", "/api/v1/me/")

            self.write(
                {
                    "state": "connected",
                    "last_error": False,
                }
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Successful"),
                    "message": _("Connected as: %s")
                    % result.get("result", {}).get("username", "Unknown"),
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Failed"),
                    "message": str(e),
                    "type": "danger",
                    "sticky": True,
                },
            }

    def action_create_database_connection(self):
        """Create database connection in Superset for Odoo's PostgreSQL"""
        self.ensure_one()

        if not all(
            [self.pg_host, self.pg_database, self.pg_username, self.pg_password]
        ):
            raise UserError(_("Please fill all PostgreSQL connection details"))

        # Build SQLAlchemy URI
        ssl_params = "?sslmode=require" if self.use_ssl else ""
        sqlalchemy_uri = (
            f"postgresql://{self.pg_username}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_database}{ssl_params}"
        )

        # Check if database already exists
        existing = self._api_call(
            "GET",
            "/api/v1/database/",
            params={
                "q": json.dumps(
                    {
                        "filters": [
                            {
                                "col": "database_name",
                                "opr": "eq",
                                "value": self.db_connection_name,
                            }
                        ]
                    }
                )
            },
        )

        if existing.get("count", 0) > 0:
            db_id = existing["result"][0]["id"]
            # Update existing
            self._api_call(
                "PUT",
                f"/api/v1/database/{db_id}",
                data={
                    "database_name": self.db_connection_name,
                    "sqlalchemy_uri": sqlalchemy_uri,
                    "expose_in_sqllab": True,
                    "allow_ctas": False,
                    "allow_cvas": False,
                    "allow_dml": False,
                    "allow_run_async": True,
                    "cache_timeout": 300,
                    "extra": json.dumps(
                        {
                            "metadata_params": {},
                            "engine_params": {
                                "connect_args": {
                                    "options": f"-c search_path={self.pg_schema}"
                                }
                            },
                            "metadata_cache_timeout": {},
                            "schemas_allowed_for_file_upload": [],
                        }
                    ),
                },
            )
        else:
            # Create new
            result = self._api_call(
                "POST",
                "/api/v1/database/",
                data={
                    "database_name": self.db_connection_name,
                    "sqlalchemy_uri": sqlalchemy_uri,
                    "expose_in_sqllab": True,
                    "allow_ctas": False,
                    "allow_cvas": False,
                    "allow_dml": False,
                    "allow_run_async": True,
                    "cache_timeout": 300,
                    "extra": json.dumps(
                        {
                            "metadata_params": {},
                            "engine_params": {
                                "connect_args": {
                                    "options": f"-c search_path={self.pg_schema}"
                                }
                            },
                        }
                    ),
                },
            )
            db_id = result.get("id")

        self.write(
            {
                "db_connection_id": db_id,
                "last_sync": fields.Datetime.now(),
            }
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Database Connection Created"),
                "message": _("Superset can now query Odoo database (ID: %s)") % db_id,
                "type": "success",
                "sticky": False,
            },
        }

    def action_sync_all_datasets(self):
        """Sync all datasets to Superset"""
        self.ensure_one()
        synced = 0
        errors = []

        for dataset in self.dataset_ids.filtered(lambda d: d.active):
            try:
                dataset.action_sync_to_superset()
                synced += 1
            except Exception as e:
                errors.append(f"{dataset.name}: {str(e)}")

        self.last_sync = fields.Datetime.now()

        message = _("%d datasets synced successfully.") % synced
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Sync Complete"),
                "message": message,
                "type": "warning" if errors else "success",
                "sticky": bool(errors),
            },
        }

    # =========================================================================
    # SUPERSET API WRAPPERS
    # =========================================================================

    def get_databases(self):
        """List all databases in Superset"""
        return self._api_call("GET", "/api/v1/database/")

    def get_datasets(self):
        """List all datasets in Superset"""
        return self._api_call("GET", "/api/v1/dataset/")

    def create_dataset(self, table_name, schema="public", database_id=None):
        """Create a dataset in Superset"""
        return self._api_call(
            "POST",
            "/api/v1/dataset/",
            data={
                "database": database_id or self.db_connection_id,
                "schema": schema,
                "table_name": table_name,
            },
        )

    def refresh_dataset(self, dataset_id):
        """Refresh dataset metadata"""
        return self._api_call("PUT", f"/api/v1/dataset/{dataset_id}/refresh")

    def get_schemas(self, database_id=None):
        """Get available schemas"""
        db_id = database_id or self.db_connection_id
        return self._api_call("GET", f"/api/v1/database/{db_id}/schemas/")

    def get_tables(self, schema="public", database_id=None):
        """Get tables in a schema"""
        db_id = database_id or self.db_connection_id
        return self._api_call(
            "GET", f"/api/v1/database/{db_id}/tables/", params={"schema_name": schema}
        )
