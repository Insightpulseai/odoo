"""
Project Registry

Discovers Odoo projects and environments using workspace markers and conventions.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional


class ProjectRegistry:
    """
    Project discovery and environment management.

    Discovery priority:
    1. odoo.code-workspace (explicit workspace file)
    2. spec/ directory (Spec Kit marker)
    3. addons/ directories (Odoo convention)
    """

    def __init__(self, search_root: Optional[Path] = None):
        self.search_root = search_root or Path.cwd()
        self._project_cache: Dict[str, Dict] = {}

    def discover_projects(self) -> List[Dict]:
        """
        Discover all Odoo projects in search root.

        Returns list of projects with:
        - id: project identifier
        - repo_root: absolute path to repo root
        - environments: list of environment names
        - spec_bundles: list of spec bundle paths
        """
        projects = []

        # Look for workspace file
        workspace_file = self._find_workspace_file()
        if workspace_file:
            project = self._load_from_workspace(workspace_file)
            projects.append(project)
            self._project_cache[project['id']] = project
            return projects

        # Fallback: look for spec/ directory
        spec_dir = self.search_root / 'spec'
        if spec_dir.exists():
            project = self._discover_from_spec_dir()
            projects.append(project)
            self._project_cache[project['id']] = project
            return projects

        # Fallback: look for addons/ directory
        addons_dir = self.search_root / 'addons'
        if addons_dir.exists():
            project = self._discover_from_addons_dir()
            projects.append(project)
            self._project_cache[project['id']] = project

        return projects

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        if project_id in self._project_cache:
            return self._project_cache[project_id]

        # Re-discover if not in cache
        projects = self.discover_projects()
        for project in projects:
            if project['id'] == project_id:
                return project

        return None

    def get_environments(self, project_id: str) -> List[Dict]:
        """
        Get environments for a project.

        Environment detection:
        1. Docker Compose services (odoo-dev, odoo-stage, odoo-prod)
        2. Database names (odoo, odoo_dev, odoo_stage, odoo_prod)
        3. Convention: always provide dev/stage/prod
        """
        project = self.get_project(project_id)
        if not project:
            return []

        # Default environments (convention)
        environments = [
            {
                'name': 'dev',
                'db_name': 'odoo_dev',
                'odoo_version': self._detect_odoo_version(project),
                'modules_installed': [],
                'schema_hash': '',
                'last_deploy': '',
                'health': 'unknown',
                'pending_migrations': []
            },
            {
                'name': 'stage',
                'db_name': 'odoo_stage',
                'odoo_version': self._detect_odoo_version(project),
                'modules_installed': [],
                'schema_hash': '',
                'last_deploy': '',
                'health': 'unknown',
                'pending_migrations': []
            },
            {
                'name': 'prod',
                'db_name': 'odoo',
                'odoo_version': self._detect_odoo_version(project),
                'modules_installed': [],
                'schema_hash': '',
                'last_deploy': '',
                'health': 'unknown',
                'pending_migrations': []
            }
        ]

        return environments

    def get_environment_status(self, project_id: str, env_name: str) -> Optional[Dict]:
        """Get detailed status for a specific environment."""
        environments = self.get_environments(project_id)

        for env in environments:
            if env['name'] == env_name:
                # Enhance with real-time status checks (TODO: implement)
                return env

        return None

    def _find_workspace_file(self) -> Optional[Path]:
        """Find odoo.code-workspace file."""
        workspace_files = list(self.search_root.glob('*.code-workspace'))
        if workspace_files:
            return workspace_files[0]
        return None

    def _load_from_workspace(self, workspace_file: Path) -> Dict:
        """Load project from workspace file."""
        try:
            with open(workspace_file) as f:
                workspace_data = json.load(f)

            # Extract project ID from workspace file name
            project_id = workspace_file.stem.replace('.code-workspace', '')

            return {
                'id': project_id,
                'repo_root': str(workspace_file.parent.absolute()),
                'environments': [],
                'spec_bundles': self._discover_spec_bundles(workspace_file.parent)
            }
        except Exception as e:
            # Fallback to directory-based discovery
            return self._discover_from_spec_dir()

    def _discover_from_spec_dir(self) -> Dict:
        """Discover project from spec/ directory."""
        project_id = self.search_root.name

        return {
            'id': project_id,
            'repo_root': str(self.search_root.absolute()),
            'environments': [],
            'spec_bundles': self._discover_spec_bundles(self.search_root)
        }

    def _discover_from_addons_dir(self) -> Dict:
        """Discover project from addons/ directory."""
        project_id = self.search_root.name

        return {
            'id': project_id,
            'repo_root': str(self.search_root.absolute()),
            'environments': [],
            'spec_bundles': []
        }

    def _discover_spec_bundles(self, root: Path) -> List[str]:
        """Discover Spec Kit bundles in project."""
        spec_dir = root / 'spec'
        if not spec_dir.exists():
            return []

        bundles = []
        for item in spec_dir.iterdir():
            if item.is_dir():
                # Check for required Spec Kit files
                if (item / 'prd.md').exists() or (item / 'constitution.md').exists():
                    bundles.append(str(item.relative_to(root)))

        return bundles

    def _detect_odoo_version(self, project: Dict) -> str:
        """
        Detect Odoo version from project.

        Detection logic:
        1. Check odoo/release.py
        2. Check requirements.txt
        3. Default to 19.0
        """
        repo_root = Path(project['repo_root'])

        # Check odoo/release.py
        release_file = repo_root / 'odoo' / 'release.py'
        if release_file.exists():
            try:
                content = release_file.read_text()
                # Look for version = "19.0"
                for line in content.split('\n'):
                    if 'version' in line and '=' in line:
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        return version
            except Exception:
                pass

        # Default to 19.0 (IPAI standard)
        return '19.0'
