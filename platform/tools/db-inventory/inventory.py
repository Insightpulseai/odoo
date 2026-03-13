#!/usr/bin/env python3
"""
Database Instance Inventory Scanner

Scans a repository for all database/datastore references and produces
a comprehensive inventory with redacted secrets.

Supports: PostgreSQL, MySQL, MSSQL, SQLite, Redis, MongoDB, ClickHouse,
Elasticsearch, OpenSearch, Supabase, and various ORM/driver configurations.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Optional YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Constants
VERSION = "1.0.0"
REDACTED = "***REDACTED***"

DEFAULT_EXCLUDE_DIRS = {
    ".git", "node_modules", "dist", "build", ".venv", "__pycache__",
    ".next", ".nuxt", "vendor", ".tox", "eggs", "*.egg-info",
    ".mypy_cache", ".pytest_cache", ".coverage", "htmlcov",
    ".terraform", ".serverless"
}

SECRET_PATTERNS = [
    r"password", r"passwd", r"pwd", r"secret", r"token", r"apikey",
    r"api_key", r"api-key", r"private_key", r"privatekey", r"credential",
    r"auth", r"service_role", r"anon_key", r"jwt", r"bearer"
]

# URL patterns for various datastores
URL_PATTERNS = {
    "postgres": [
        r"postgres(?:ql)?://[^\s\"'`]+",
        r"jdbc:postgresql://[^\s\"'`]+",
    ],
    "mysql": [
        r"mysql://[^\s\"'`]+",
        r"mysql\+pymysql://[^\s\"'`]+",
        r"jdbc:mysql://[^\s\"'`]+",
    ],
    "mssql": [
        r"mssql://[^\s\"'`]+",
        r"mssql\+pymssql://[^\s\"'`]+",
        r"jdbc:sqlserver://[^\s\"'`]+",
    ],
    "sqlite": [
        r"sqlite(?:3)?://[^\s\"'`]+",
        r"sqlite:///[^\s\"'`]+",
    ],
    "redis": [
        r"redis(?:s)?://[^\s\"'`]+",
        r"redis-sentinel://[^\s\"'`]+",
    ],
    "mongodb": [
        r"mongodb(?:\+srv)?://[^\s\"'`]+",
    ],
    "clickhouse": [
        r"clickhouse://[^\s\"'`]+",
        r"clickhouse\+native://[^\s\"'`]+",
    ],
    "elasticsearch": [
        r"(?:https?://)?[^\s\"'`]*elastic[^\s\"'`]*:\d+",
    ],
    "opensearch": [
        r"(?:https?://)?[^\s\"'`]*opensearch[^\s\"'`]*:\d+",
    ],
}

# Environment variable patterns
ENV_VAR_PATTERNS = {
    "postgres": [
        r"(?:POSTGRES|PG|DATABASE)_(?:URL|URI|HOST|PORT|NAME|USER|PASSWORD|DB)",
        r"PGHOST", r"PGPORT", r"PGDATABASE", r"PGUSER", r"PGPASSWORD",
        r"DB_(?:HOST|PORT|NAME|USER|PASSWORD|DATABASE)",
    ],
    "mysql": [
        r"MYSQL_(?:URL|URI|HOST|PORT|DATABASE|USER|PASSWORD|ROOT_PASSWORD)",
    ],
    "redis": [
        r"REDIS_(?:URL|URI|HOST|PORT|PASSWORD|DB)",
    ],
    "mongodb": [
        r"MONGO(?:DB)?_(?:URL|URI|HOST|PORT|DATABASE|USER|PASSWORD)",
    ],
    "supabase": [
        r"SUPABASE_(?:URL|KEY|ANON_KEY|SERVICE_ROLE_KEY|DB_URL|JWT_SECRET)",
        r"NEXT_PUBLIC_SUPABASE_(?:URL|ANON_KEY)",
    ],
    "clickhouse": [
        r"CLICKHOUSE_(?:URL|HOST|PORT|DATABASE|USER|PASSWORD)",
    ],
    "elasticsearch": [
        r"ELASTIC(?:SEARCH)?_(?:URL|HOST|PORT|USER|PASSWORD)",
        r"ES_(?:URL|HOST|PORT|USER|PASSWORD)",
    ],
}

# Odoo-specific patterns
ODOO_PATTERNS = [
    r"db_host\s*=",
    r"db_port\s*=",
    r"db_user\s*=",
    r"db_password\s*=",
    r"db_name\s*=",
    r"db_template\s*=",
]


class Finding:
    """Represents a database instance finding."""

    def __init__(
        self,
        datastore_type: str,
        instance_name: str = "",
        host: str = "",
        port: str = "",
        database: str = "",
        user: str = "",
        ssl_mode: str = "",
        url_redacted: str = "",
        secrets_present: bool = False,
        secret_fields: List[str] = None,
        file_path: str = "",
        line_start: int = 0,
        line_end: int = 0,
        snippet_redacted: str = "",
        detector: str = "",
        tags: List[str] = None,
    ):
        self.datastore_type = datastore_type
        self.instance_name = instance_name
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.ssl_mode = ssl_mode
        self.url_redacted = url_redacted
        self.secrets_present = secrets_present
        self.secret_fields = secret_fields or []
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.snippet_redacted = snippet_redacted
        self.detector = detector
        self.tags = tags or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with stable ID."""
        # Create stable ID from normalized fields
        id_string = f"{self.datastore_type}|{self.host}|{self.port}|{self.database}|{self.file_path}|{self.line_start}"
        finding_id = hashlib.sha256(id_string.encode()).hexdigest()[:16]

        return {
            "id": finding_id,
            "datastore_type": self.datastore_type,
            "instance_name": self.instance_name,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "ssl_mode": self.ssl_mode,
            "url_redacted": self.url_redacted,
            "secrets_present": self.secrets_present,
            "secret_fields": self.secret_fields,
            "source": {
                "file_path": self.file_path,
                "line_start": self.line_start,
                "line_end": self.line_end,
                "snippet_redacted": self.snippet_redacted,
                "detector": self.detector,
            },
            "tags": self.tags,
        }


def redact_secret(value: str) -> Tuple[str, bool]:
    """Redact secrets from a value. Returns (redacted_value, was_redacted)."""
    if not value:
        return value, False

    # Check for JWT tokens (eyJ...)
    if re.search(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", value):
        return REDACTED, True

    # Check for common secret patterns
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return REDACTED, True

    # Check for long base64-like strings (likely keys/tokens)
    if re.search(r"[A-Za-z0-9+/=]{32,}", value):
        # But not if it looks like a hash or UUID
        if not re.match(r"^[0-9a-f-]{32,}$", value, re.IGNORECASE):
            return REDACTED, True

    return value, False


def redact_url(url: str) -> Tuple[str, bool, List[str]]:
    """Redact secrets from a database URL. Returns (redacted_url, has_secrets, secret_fields)."""
    if not url:
        return url, False, []

    secret_fields = []
    has_secrets = False

    # Parse URL and redact password
    # Format: scheme://user:password@host:port/database
    url_pattern = r"^([a-z+]+)://(?:([^:@]+)(?::([^@]+))?@)?([^:/]+)(?::(\d+))?(?:/(.*))?$"
    match = re.match(url_pattern, url, re.IGNORECASE)

    if match:
        scheme, user, password, host, port, path = match.groups()

        if password:
            has_secrets = True
            secret_fields.append("password")
            password = REDACTED

        # Rebuild URL
        redacted = f"{scheme}://"
        if user:
            redacted += user
            if password:
                redacted += f":{password}"
            redacted += "@"
        redacted += host
        if port:
            redacted += f":{port}"
        if path:
            # Check for secrets in query params
            if "?" in path:
                base_path, query = path.split("?", 1)
                redacted_params = []
                for param in query.split("&"):
                    if "=" in param:
                        key, val = param.split("=", 1)
                        if any(re.search(p, key, re.IGNORECASE) for p in SECRET_PATTERNS):
                            redacted_params.append(f"{key}={REDACTED}")
                            has_secrets = True
                            secret_fields.append(key)
                        else:
                            redacted_params.append(param)
                    else:
                        redacted_params.append(param)
                path = f"{base_path}?{'&'.join(redacted_params)}"
            redacted += f"/{path}"

        return redacted, has_secrets, secret_fields

    # Fallback: simple password redaction
    redacted = re.sub(r":([^:@]+)@", f":{REDACTED}@", url)
    if redacted != url:
        has_secrets = True
        secret_fields.append("password")

    return redacted, has_secrets, secret_fields


def redact_snippet(text: str, max_length: int = 200) -> str:
    """Redact secrets from a code snippet."""
    if not text:
        return text

    # Redact password values
    text = re.sub(
        r"(password|passwd|pwd|secret|token|apikey|api_key|private_key)\s*[=:]\s*[\"']?([^\"'\s\n]+)[\"']?",
        rf"\1={REDACTED}",
        text,
        flags=re.IGNORECASE
    )

    # Redact JWT tokens
    text = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*", REDACTED, text)

    # Redact URLs with credentials
    text = re.sub(r":([^:/@\s]{8,})@", f":{REDACTED}@", text)

    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text.strip()


def infer_tags(file_path: str, content: str = "") -> List[str]:
    """Infer tags from file path and content."""
    tags = []
    path_lower = file_path.lower()
    content_lower = content.lower() if content else ""

    # Environment-based tags
    if "prod" in path_lower or "production" in path_lower:
        tags.append("prod")
    elif "stag" in path_lower or "staging" in path_lower:
        tags.append("staging")
    elif "dev" in path_lower or "development" in path_lower:
        tags.append("dev")
    elif "test" in path_lower:
        tags.append("test")
    elif "local" in path_lower:
        tags.append("local")

    # Tool-based tags
    if "odoo" in path_lower or "odoo" in content_lower:
        tags.append("odoo")
    if "superset" in path_lower or "superset" in content_lower:
        tags.append("superset")
    if "supabase" in path_lower or "supabase" in content_lower:
        tags.append("supabase")
    if "n8n" in path_lower or "n8n" in content_lower:
        tags.append("n8n")
    if "mattermost" in path_lower or "mattermost" in content_lower:
        tags.append("mattermost")

    # Infrastructure tags
    if "docker" in path_lower or "compose" in path_lower:
        tags.append("docker")
    if "k8s" in path_lower or "kubernetes" in path_lower:
        tags.append("k8s")
    if ".github" in path_lower or "ci" in path_lower:
        tags.append("ci")
    if "terraform" in path_lower or ".tf" in path_lower:
        tags.append("terraform")
    if "ansible" in path_lower:
        tags.append("ansible")
    if "helm" in path_lower:
        tags.append("helm")

    return list(set(tags))


def parse_url(url: str) -> Dict[str, str]:
    """Parse a database URL into components."""
    result = {
        "host": "",
        "port": "",
        "database": "",
        "user": "",
        "ssl_mode": "",
    }

    # Parse URL format: scheme://user:password@host:port/database?params
    pattern = r"^[a-z+]+://(?:([^:@]+)(?::[^@]+)?@)?([^:/]+)(?::(\d+))?(?:/([^?]+))?(?:\?(.+))?$"
    match = re.match(pattern, url, re.IGNORECASE)

    if match:
        user, host, port, database, params = match.groups()
        result["user"] = user or ""
        result["host"] = host or ""
        result["port"] = port or ""
        result["database"] = database or ""

        if params:
            for param in params.split("&"):
                if "=" in param:
                    key, val = param.split("=", 1)
                    if key.lower() in ("sslmode", "ssl_mode", "ssl"):
                        result["ssl_mode"] = val

    return result


class InventoryScanner:
    """Main scanner class."""

    def __init__(
        self,
        root: Path,
        exclude_dirs: Set[str] = None,
        include_datastores: Set[str] = None,
        max_file_mb: float = 5.0,
        verbose: bool = False,
    ):
        self.root = root.resolve()
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.include_datastores = include_datastores
        self.max_file_bytes = int(max_file_mb * 1024 * 1024)
        self.verbose = verbose
        self.findings: List[Finding] = []
        self.errors: List[str] = []

    def log(self, msg: str):
        """Log verbose message."""
        if self.verbose:
            print(f"[INFO] {msg}", file=sys.stderr)

    def error(self, msg: str):
        """Log error message."""
        self.errors.append(msg)
        print(f"[ERROR] {msg}", file=sys.stderr)

    def should_skip_dir(self, dir_name: str) -> bool:
        """Check if directory should be skipped."""
        return dir_name in self.exclude_dirs or dir_name.startswith(".")

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Check size
        try:
            if file_path.stat().st_size > self.max_file_bytes:
                self.log(f"Skipping large file: {file_path}")
                return False
        except OSError:
            return False

        # Check extension
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        # Files to process
        processable = {
            ".env", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
            ".py", ".ts", ".js", ".mjs", ".cjs", ".tsx", ".jsx",
            ".conf", ".config", ".tf", ".prisma", ".md", ".txt",
            ".sh", ".bash", ".zsh", ".properties",
        }

        # Also process dotfiles like .env.local
        if name.startswith(".env") or name.endswith(".env"):
            return True
        if name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            return True
        if name.endswith(".conf") or name.endswith(".config"):
            return True

        return suffix in processable

    def scan(self):
        """Scan the repository."""
        self.log(f"Scanning repository: {self.root}")

        for dirpath, dirnames, filenames in os.walk(self.root):
            # Filter directories
            dirnames[:] = [d for d in dirnames if not self.should_skip_dir(d)]

            for filename in filenames:
                file_path = Path(dirpath) / filename

                if self.should_process_file(file_path):
                    try:
                        self.scan_file(file_path)
                    except Exception as e:
                        self.error(f"Error scanning {file_path}: {e}")

        # Sort findings
        self.findings.sort(key=lambda f: (
            f.datastore_type,
            f.host,
            f.database,
            f.file_path,
        ))

        self.log(f"Found {len(self.findings)} database references")

    def scan_file(self, file_path: Path):
        """Scan a single file for database references."""
        self.log(f"Scanning: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.error(f"Cannot read {file_path}: {e}")
            return

        lines = content.split("\n")
        rel_path = str(file_path.relative_to(self.root))

        # Determine detector based on file type
        detector = self.detect_file_type(file_path)

        # Scan for URL patterns
        self.scan_urls(rel_path, lines, detector)

        # Scan for env var patterns
        self.scan_env_vars(rel_path, lines, detector)

        # Scan for Odoo config
        self.scan_odoo_config(rel_path, lines, detector)

        # Scan Docker Compose
        if detector == "docker_compose":
            self.scan_docker_compose(rel_path, content, lines)

        # Scan Prisma schema
        if file_path.suffix == ".prisma":
            self.scan_prisma(rel_path, content, lines)

    def detect_file_type(self, file_path: Path) -> str:
        """Detect the type of configuration file."""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        if name.startswith(".env") or name.endswith(".env"):
            return "env_file"
        if "docker-compose" in name or "compose" in name:
            return "docker_compose"
        if suffix == ".prisma":
            return "prisma_schema"
        if suffix == ".tf":
            return "terraform"
        if "k8s" in str(file_path) or "kubernetes" in str(file_path):
            return "k8s_manifest"
        if suffix in (".yaml", ".yml"):
            if "ansible" in str(file_path):
                return "ansible"
            if "helm" in str(file_path):
                return "helm_chart"
            return "yaml_config"
        if suffix == ".py":
            return "python_config"
        if suffix in (".ts", ".js", ".mjs", ".cjs", ".tsx", ".jsx"):
            return "js_config"
        if suffix == ".json":
            return "json_config"
        if suffix == ".conf":
            if "odoo" in name:
                return "odoo_conf"
            return "conf_file"
        if suffix == ".md":
            return "docs"

        return "unknown"

    def scan_urls(self, file_path: str, lines: List[str], detector: str):
        """Scan for database URLs."""
        for ds_type, patterns in URL_PATTERNS.items():
            if self.include_datastores and ds_type not in self.include_datastores:
                continue

            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                for i, line in enumerate(lines):
                    for match in regex.finditer(line):
                        url = match.group(0)
                        self.add_url_finding(
                            url, ds_type, file_path, i + 1, line, detector
                        )

    def scan_env_vars(self, file_path: str, lines: List[str], detector: str):
        """Scan for environment variable definitions."""
        for ds_type, patterns in ENV_VAR_PATTERNS.items():
            if self.include_datastores and ds_type not in self.include_datastores:
                continue

            for pattern in patterns:
                regex = re.compile(rf"({pattern})\s*[=:]\s*(.+)", re.IGNORECASE)
                for i, line in enumerate(lines):
                    match = regex.search(line)
                    if match:
                        var_name = match.group(1)
                        var_value = match.group(2).strip().strip("\"'")

                        # Check if it's a URL
                        if any(scheme in var_value.lower() for scheme in
                               ["://", "postgres", "mysql", "redis", "mongo"]):
                            self.add_url_finding(
                                var_value, ds_type, file_path, i + 1, line, detector
                            )
                        else:
                            self.add_env_finding(
                                var_name, var_value, ds_type, file_path, i + 1, line, detector
                            )

    def scan_odoo_config(self, file_path: str, lines: List[str], detector: str):
        """Scan for Odoo database configuration."""
        if detector not in ("odoo_conf", "env_file", "docker_compose", "python_config"):
            if "odoo" not in file_path.lower():
                return

        odoo_config = {}
        line_range = [None, None]

        for i, line in enumerate(lines):
            for pattern in ODOO_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    match = re.search(r"(db_\w+)\s*[=:]\s*(.+)", line, re.IGNORECASE)
                    if match:
                        key = match.group(1).lower()
                        value = match.group(2).strip().strip("\"'")
                        odoo_config[key] = value
                        if line_range[0] is None:
                            line_range[0] = i + 1
                        line_range[1] = i + 1

        if odoo_config:
            secrets_present = False
            secret_fields = []

            # Check for password
            if odoo_config.get("db_password"):
                secrets_present = True
                secret_fields.append("db_password")

            snippet = "; ".join(f"{k}={v if k != 'db_password' else REDACTED}"
                               for k, v in odoo_config.items())

            finding = Finding(
                datastore_type="postgres",
                instance_name="odoo",
                host=odoo_config.get("db_host", ""),
                port=odoo_config.get("db_port", ""),
                database=odoo_config.get("db_name", ""),
                user=odoo_config.get("db_user", ""),
                secrets_present=secrets_present,
                secret_fields=secret_fields,
                file_path=file_path,
                line_start=line_range[0] or 0,
                line_end=line_range[1] or 0,
                snippet_redacted=redact_snippet(snippet),
                detector=detector,
                tags=infer_tags(file_path, "odoo"),
            )
            self.findings.append(finding)

    def scan_docker_compose(self, file_path: str, content: str, lines: List[str]):
        """Scan Docker Compose files."""
        if not HAS_YAML:
            # Fallback to regex-based parsing
            self.log("YAML not available, using regex parsing for Docker Compose")
            return

        try:
            data = yaml.safe_load(content)
        except Exception as e:
            self.error(f"Cannot parse YAML {file_path}: {e}")
            return

        if not isinstance(data, dict):
            return

        services = data.get("services", {})
        if not isinstance(services, dict):
            return

        for svc_name, svc_config in services.items():
            if not isinstance(svc_config, dict):
                continue

            image = svc_config.get("image", "")
            env = svc_config.get("environment", {})

            # Convert list format to dict
            if isinstance(env, list):
                env_dict = {}
                for item in env:
                    if "=" in str(item):
                        k, v = str(item).split("=", 1)
                        env_dict[k] = v
                    elif isinstance(item, dict):
                        env_dict.update(item)
                env = env_dict

            # Detect database type from image
            ds_type = None
            if "postgres" in image.lower():
                ds_type = "postgres"
            elif "mysql" in image.lower() or "mariadb" in image.lower():
                ds_type = "mysql"
            elif "redis" in image.lower():
                ds_type = "redis"
            elif "mongo" in image.lower():
                ds_type = "mongodb"
            elif "clickhouse" in image.lower():
                ds_type = "clickhouse"
            elif "elasticsearch" in image.lower() or "elastic" in image.lower():
                ds_type = "elasticsearch"
            elif "opensearch" in image.lower():
                ds_type = "opensearch"
            elif "mssql" in image.lower() or "sqlserver" in image.lower():
                ds_type = "mssql"

            if ds_type and (not self.include_datastores or ds_type in self.include_datastores):
                # Extract connection info from environment
                host = svc_name  # Service name is the host in Docker network
                port = ""
                database = ""
                user = ""
                secrets_present = False
                secret_fields = []

                for key, val in env.items():
                    key_lower = key.lower()
                    val_str = str(val) if val else ""

                    if "host" in key_lower:
                        host = val_str
                    elif "port" in key_lower:
                        port = val_str
                    elif "database" in key_lower or "db" in key_lower or "name" in key_lower:
                        database = val_str
                    elif "user" in key_lower and "password" not in key_lower:
                        user = val_str
                    elif "password" in key_lower or "secret" in key_lower:
                        secrets_present = True
                        secret_fields.append(key)

                # Find line numbers
                line_start = 1
                for i, line in enumerate(lines):
                    if svc_name in line and ":" in line:
                        line_start = i + 1
                        break

                finding = Finding(
                    datastore_type=ds_type,
                    instance_name=svc_name,
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    secrets_present=secrets_present,
                    secret_fields=secret_fields,
                    file_path=file_path,
                    line_start=line_start,
                    line_end=line_start,
                    snippet_redacted=f"service: {svc_name}, image: {image}",
                    detector="docker_compose",
                    tags=infer_tags(file_path, content),
                )
                self.findings.append(finding)

    def scan_prisma(self, file_path: str, content: str, lines: List[str]):
        """Scan Prisma schema files."""
        # Look for datasource block
        ds_match = re.search(
            r'datasource\s+\w+\s*\{([^}]+)\}',
            content,
            re.DOTALL
        )

        if not ds_match:
            return

        ds_block = ds_match.group(1)

        # Extract provider
        provider_match = re.search(r'provider\s*=\s*"(\w+)"', ds_block)
        provider = provider_match.group(1) if provider_match else "unknown"

        ds_type_map = {
            "postgresql": "postgres",
            "postgres": "postgres",
            "mysql": "mysql",
            "sqlite": "sqlite",
            "sqlserver": "mssql",
            "mongodb": "mongodb",
        }
        ds_type = ds_type_map.get(provider.lower(), "unknown")

        if self.include_datastores and ds_type not in self.include_datastores:
            return

        # Extract URL
        url_match = re.search(r'url\s*=\s*env\("([^"]+)"\)', ds_block)
        env_var = url_match.group(1) if url_match else ""

        # Find line numbers
        line_start = 1
        for i, line in enumerate(lines):
            if "datasource" in line:
                line_start = i + 1
                break

        finding = Finding(
            datastore_type=ds_type,
            instance_name="prisma",
            secrets_present=True,  # Assume URL contains secrets
            secret_fields=["url"],
            file_path=file_path,
            line_start=line_start,
            line_end=line_start + ds_block.count("\n"),
            snippet_redacted=f'provider="{provider}", url=env("{env_var}")',
            detector="prisma_schema",
            tags=infer_tags(file_path),
        )
        self.findings.append(finding)

    def add_url_finding(
        self,
        url: str,
        ds_type: str,
        file_path: str,
        line_num: int,
        line: str,
        detector: str,
    ):
        """Add a finding from a URL."""
        if self.include_datastores and ds_type not in self.include_datastores:
            return

        url_redacted, has_secrets, secret_fields = redact_url(url)
        parsed = parse_url(url)

        finding = Finding(
            datastore_type=ds_type,
            instance_name=infer_instance_name(file_path, ds_type),
            host=parsed["host"],
            port=parsed["port"],
            database=parsed["database"],
            user=parsed["user"],
            ssl_mode=parsed["ssl_mode"],
            url_redacted=url_redacted,
            secrets_present=has_secrets,
            secret_fields=secret_fields,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num,
            snippet_redacted=redact_snippet(line),
            detector=detector,
            tags=infer_tags(file_path, line),
        )
        self.findings.append(finding)

    def add_env_finding(
        self,
        var_name: str,
        var_value: str,
        ds_type: str,
        file_path: str,
        line_num: int,
        line: str,
        detector: str,
    ):
        """Add a finding from an environment variable."""
        if self.include_datastores and ds_type not in self.include_datastores:
            return

        # Determine what this variable represents
        var_lower = var_name.lower()

        host = ""
        port = ""
        database = ""
        user = ""
        secrets_present = False
        secret_fields = []

        value_redacted, was_redacted = redact_secret(var_value)
        if was_redacted:
            secrets_present = True
            secret_fields.append(var_name)

        if "host" in var_lower:
            host = var_value
        elif "port" in var_lower:
            port = var_value
        elif "database" in var_lower or "name" in var_lower or "db" in var_lower:
            database = var_value
        elif "user" in var_lower and "password" not in var_lower:
            user = var_value
        elif "password" in var_lower or "secret" in var_lower or "key" in var_lower:
            secrets_present = True
            secret_fields.append(var_name)

        finding = Finding(
            datastore_type=ds_type,
            instance_name=infer_instance_name(file_path, ds_type),
            host=host,
            port=port,
            database=database,
            user=user,
            secrets_present=secrets_present,
            secret_fields=secret_fields,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num,
            snippet_redacted=f"{var_name}={value_redacted}",
            detector=detector,
            tags=infer_tags(file_path, line),
        )
        self.findings.append(finding)


def infer_instance_name(file_path: str, ds_type: str) -> str:
    """Infer an instance name from file path."""
    path_lower = file_path.lower()

    # Check for common service names
    if "odoo" in path_lower:
        return "odoo"
    if "superset" in path_lower:
        return "superset"
    if "n8n" in path_lower:
        return "n8n"
    if "mattermost" in path_lower:
        return "mattermost"
    if "supabase" in path_lower:
        return "supabase"

    # Use filename as fallback
    filename = Path(file_path).stem
    return f"{ds_type}_{filename}"


def generate_json(findings: List[Finding], root: Path, output_path: Path):
    """Generate JSON output."""
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "total_findings": len(findings),
        "findings": [f.to_dict() for f in findings],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)


def generate_csv(findings: List[Finding], output_path: Path):
    """Generate CSV output."""
    fieldnames = [
        "id", "datastore_type", "instance_name", "host", "port",
        "database", "user", "ssl_mode", "secrets_present",
        "file_path", "line_start", "detector", "tags"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for finding in findings:
            row = finding.to_dict()
            flat_row = {
                "id": row["id"],
                "datastore_type": row["datastore_type"],
                "instance_name": row["instance_name"],
                "host": row["host"],
                "port": row["port"],
                "database": row["database"],
                "user": row["user"],
                "ssl_mode": row["ssl_mode"],
                "secrets_present": row["secrets_present"],
                "file_path": row["source"]["file_path"],
                "line_start": row["source"]["line_start"],
                "detector": row["source"]["detector"],
                "tags": ",".join(row["tags"]),
            }
            writer.writerow(flat_row)


def generate_markdown(findings: List[Finding], root: Path, output_path: Path):
    """Generate detailed Markdown report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Database Instance Inventory\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write(f"**Repository:** `{root}`\n\n")
        f.write(f"**Total Findings:** {len(findings)}\n\n")
        f.write("---\n\n")

        # Group by datastore type
        by_type: Dict[str, List[Finding]] = {}
        for finding in findings:
            ds_type = finding.datastore_type
            if ds_type not in by_type:
                by_type[ds_type] = []
            by_type[ds_type].append(finding)

        for ds_type in sorted(by_type.keys()):
            type_findings = by_type[ds_type]
            f.write(f"## {ds_type.upper()} ({len(type_findings)} found)\n\n")

            for finding in type_findings:
                d = finding.to_dict()
                f.write(f"### {d['instance_name'] or 'unnamed'}\n\n")
                f.write(f"- **Host:** `{d['host'] or 'N/A'}`\n")
                f.write(f"- **Port:** `{d['port'] or 'N/A'}`\n")
                f.write(f"- **Database:** `{d['database'] or 'N/A'}`\n")
                f.write(f"- **User:** `{d['user'] or 'N/A'}`\n")
                if d['ssl_mode']:
                    f.write(f"- **SSL Mode:** `{d['ssl_mode']}`\n")
                f.write(f"- **Secrets Present:** {'Yes' if d['secrets_present'] else 'No'}\n")
                if d['secret_fields']:
                    f.write(f"- **Redacted Fields:** {', '.join(d['secret_fields'])}\n")
                if d['url_redacted']:
                    f.write(f"- **URL:** `{d['url_redacted']}`\n")
                f.write(f"- **Source:** `{d['source']['file_path']}:{d['source']['line_start']}`\n")
                f.write(f"- **Detector:** {d['source']['detector']}\n")
                if d['tags']:
                    f.write(f"- **Tags:** {', '.join(d['tags'])}\n")
                f.write(f"\n```\n{d['source']['snippet_redacted']}\n```\n\n")

            f.write("---\n\n")


def generate_summary(findings: List[Finding], root: Path, errors: List[str], output_path: Path):
    """Generate summary Markdown report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Database Inventory Summary\n\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n")
        f.write(f"**Repository:** `{root}`\n\n")

        # Stats by type
        by_type: Dict[str, int] = {}
        by_detector: Dict[str, int] = {}
        secrets_count = 0

        for finding in findings:
            ds_type = finding.datastore_type
            detector = finding.detector
            by_type[ds_type] = by_type.get(ds_type, 0) + 1
            by_detector[detector] = by_detector.get(detector, 0) + 1
            if finding.secrets_present:
                secrets_count += 1

        f.write("## Overview\n\n")
        f.write(f"| Metric | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Findings | {len(findings)} |\n")
        f.write(f"| Findings with Secrets | {secrets_count} |\n")
        f.write(f"| Datastore Types | {len(by_type)} |\n")
        f.write(f"| Scan Errors | {len(errors)} |\n")
        f.write("\n")

        f.write("## By Datastore Type\n\n")
        f.write("| Type | Count |\n")
        f.write("|------|-------|\n")
        for ds_type, count in sorted(by_type.items()):
            f.write(f"| {ds_type} | {count} |\n")
        f.write("\n")

        f.write("## By Detector\n\n")
        f.write("| Detector | Count |\n")
        f.write("|----------|-------|\n")
        for detector, count in sorted(by_detector.items()):
            f.write(f"| {detector} | {count} |\n")
        f.write("\n")

        if errors:
            f.write("## Errors\n\n")
            for error in errors[:20]:  # Limit to first 20
                f.write(f"- {error}\n")
            if len(errors) > 20:
                f.write(f"\n... and {len(errors) - 20} more errors\n")
            f.write("\n")

        # Unique hosts
        hosts = set(f.host for f in findings if f.host)
        if hosts:
            f.write("## Unique Hosts\n\n")
            for host in sorted(hosts):
                f.write(f"- `{host}`\n")
            f.write("\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database Instance Inventory Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inventory.py --root /path/to/repo
  python inventory.py --verbose --format json,md
  python inventory.py --include-datastores postgres,mysql
        """
    )

    parser.add_argument(
        "--root", "-r",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--out", "-o",
        type=Path,
        default=None,
        help="Output directory (default: tools/db-inventory/output)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        default="json,csv,md",
        help="Output formats: json,csv,md (default: all)"
    )
    parser.add_argument(
        "--include-datastores",
        type=str,
        default=None,
        help="Only include these datastores (comma-separated)"
    )
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        default=None,
        help="Directories to exclude (comma-separated, adds to defaults)"
    )
    parser.add_argument(
        "--max-file-mb",
        type=float,
        default=5.0,
        help="Maximum file size in MB to scan (default: 5)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"db-inventory {VERSION}"
    )

    args = parser.parse_args()

    # Resolve paths
    root = args.root.resolve()
    if args.out:
        output_dir = args.out.resolve()
    else:
        output_dir = root / "tools" / "db-inventory" / "output"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse options
    formats = set(args.format.lower().split(","))
    include_datastores = None
    if args.include_datastores:
        include_datastores = set(args.include_datastores.lower().split(","))

    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if args.exclude_dirs:
        exclude_dirs.update(args.exclude_dirs.split(","))

    # Run scanner
    scanner = InventoryScanner(
        root=root,
        exclude_dirs=exclude_dirs,
        include_datastores=include_datastores,
        max_file_mb=args.max_file_mb,
        verbose=args.verbose,
    )

    scanner.scan()

    # Generate outputs
    if "json" in formats:
        json_path = output_dir / "db_inventory.json"
        generate_json(scanner.findings, root, json_path)
        print(f"Generated: {json_path}")

    if "csv" in formats:
        csv_path = output_dir / "db_inventory.csv"
        generate_csv(scanner.findings, csv_path)
        print(f"Generated: {csv_path}")

    if "md" in formats:
        md_path = output_dir / "db_inventory.md"
        generate_markdown(scanner.findings, root, md_path)
        print(f"Generated: {md_path}")

        summary_path = output_dir / "db_inventory_summary.md"
        generate_summary(scanner.findings, root, scanner.errors, summary_path)
        print(f"Generated: {summary_path}")

    print(f"\nTotal findings: {len(scanner.findings)}")
    if scanner.errors:
        print(f"Errors: {len(scanner.errors)}")

    return 0 if not scanner.errors else 1


if __name__ == "__main__":
    sys.exit(main())
