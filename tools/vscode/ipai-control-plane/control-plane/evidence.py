"""
Evidence Bundle Generator

Creates immutable audit trails for all control plane operations.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class EvidenceBundler:
    """
    Evidence bundle management.

    Bundle structure:
    docs/evidence/YYYYMMDD-HHMM-<operation>/
    ├── plan.md                    # Human-readable summary
    ├── operation.json             # Machine-readable metadata
    ├── diffs/
    │   ├── schema.sql
    │   ├── orm.diff
    │   └── files/
    ├── validation/
    │   ├── manifest.json
    │   ├── xml.json
    │   └── summary.json
    ├── logs/
    │   └── operation.log
    └── artifacts/
        └── checksums.txt
    """

    def __init__(self, evidence_root: Path):
        self.evidence_root = evidence_root
        self.evidence_root.mkdir(parents=True, exist_ok=True)

    def create_bundle(self, operation: Dict) -> Dict:
        """
        Create new evidence bundle.

        Args:
            operation: Operation metadata
                - type: operation type (install_modules, migrate, upgrade, etc.)
                - target_env: target environment
                - project_id: project identifier
                - modules: list of modules (for install operations)

        Returns:
            Evidence bundle metadata with path
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        operation_type = operation.get('type', 'unknown')
        bundle_name = f"{timestamp}-{operation_type}"

        bundle_path = self.evidence_root / bundle_name
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (bundle_path / 'diffs').mkdir(exist_ok=True)
        (bundle_path / 'validation').mkdir(exist_ok=True)
        (bundle_path / 'logs').mkdir(exist_ok=True)
        (bundle_path / 'artifacts').mkdir(exist_ok=True)

        # Write operation metadata
        metadata = {
            'timestamp': timestamp,
            'operation': operation_type,
            'target_env': operation.get('target_env'),
            'project_id': operation.get('project_id'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        # Add operation-specific metadata
        if operation_type == 'install_modules':
            metadata['modules'] = operation.get('modules', [])

        operation_file = bundle_path / 'operation.json'
        with open(operation_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Write plan.md
        self._write_plan(bundle_path, operation, metadata)

        return {
            'path': bundle_path,
            'metadata': metadata,
            'bundle_id': bundle_name
        }

    def finalize_bundle(self, bundle_id: str, result: Dict):
        """
        Finalize bundle with operation results.

        Args:
            bundle_id: Evidence bundle identifier
            result: Operation result data
        """
        bundle_path = self.evidence_root / bundle_id
        if not bundle_path.exists():
            raise ValueError(f"Bundle not found: {bundle_id}")

        # Update metadata
        operation_file = bundle_path / 'operation.json'
        with open(operation_file, 'r') as f:
            metadata = json.load(f)

        metadata['status'] = result.get('status', 'failed')
        metadata['completed_at'] = datetime.now().isoformat()

        with open(operation_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Write logs if provided
        if 'logs' in result:
            log_file = bundle_path / 'logs' / 'operation.log'
            with open(log_file, 'w') as f:
                f.write(result['logs'])

    def list_bundles(self, project_id: Optional[str] = None) -> List[Dict]:
        """
        List evidence bundles.

        Args:
            project_id: Optional project filter

        Returns:
            List of evidence bundle summaries
        """
        bundles = []

        for bundle_path in sorted(self.evidence_root.iterdir(), reverse=True):
            if not bundle_path.is_dir():
                continue

            operation_file = bundle_path / 'operation.json'
            if not operation_file.exists():
                continue

            try:
                with open(operation_file, 'r') as f:
                    metadata = json.load(f)

                # Filter by project if specified
                if project_id and metadata.get('project_id') != project_id:
                    continue

                bundles.append({
                    'bundle_id': bundle_path.name,
                    'timestamp': metadata.get('timestamp'),
                    'operation': metadata.get('operation'),
                    'target_env': metadata.get('target_env'),
                    'status': metadata.get('status'),
                    'path': str(bundle_path)
                })
            except Exception:
                continue

        return bundles

    def get_bundle(self, bundle_id: str) -> Optional[Dict]:
        """Get detailed information for a specific bundle."""
        bundle_path = self.evidence_root / bundle_id
        if not bundle_path.exists():
            return None

        operation_file = bundle_path / 'operation.json'
        if not operation_file.exists():
            return None

        try:
            with open(operation_file, 'r') as f:
                metadata = json.load(f)

            # Read plan if exists
            plan_file = bundle_path / 'plan.md'
            plan_content = ''
            if plan_file.exists():
                plan_content = plan_file.read_text()

            return {
                'bundle_id': bundle_id,
                'metadata': metadata,
                'plan': plan_content,
                'path': str(bundle_path)
            }
        except Exception:
            return None

    def _write_plan(self, bundle_path: Path, operation: Dict, metadata: Dict):
        """Write human-readable plan.md."""
        operation_type = operation.get('type', 'unknown')
        target_env = operation.get('target_env', 'N/A')

        plan_content = f"""# Operation Plan

**Type**: {operation_type}
**Target Environment**: {target_env}
**Timestamp**: {metadata['created_at']}
**Project**: {operation.get('project_id', 'N/A')}

## Operation Details

"""

        # Add operation-specific details
        if operation_type == 'install_modules':
            modules = operation.get('modules', [])
            plan_content += f"""### Modules to Install

{chr(10).join(f'- {m}' for m in modules)}

"""

        plan_content += """## Validation

(Validation results will be added here)

## Changes

(Diffs will be added here)

## Rollback Plan

(Rollback instructions will be added here)
"""

        plan_file = bundle_path / 'plan.md'
        plan_file.write_text(plan_content)
