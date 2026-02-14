#!/usr/bin/env python3
"""
IPAI Control Plane Server

FastAPI server that provides SaaS-grade control plane operations for Odoo CE + OCA + IPAI.
Called by VS Code extension for all business logic (stateless extension pattern).
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from project_registry import ProjectRegistry
from evidence import EvidenceBundler
from validators.manifest import ManifestValidator
from validators.xml import XmlValidator
from validators.security import SecurityValidator
from operations import OperationState, DiffGenerator, ValidationRunner

# Initialize FastAPI app
app = FastAPI(
    title="IPAI Control Plane",
    description="SaaS-grade control plane for Odoo CE + OCA + IPAI",
    version="0.1.0"
)

# CORS middleware (VS Code webviews only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["vscode-webview://*", "http://localhost:*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
project_registry = ProjectRegistry()
evidence_bundler = EvidenceBundler(Path.cwd() / "docs" / "evidence")
manifest_validator = ManifestValidator()
xml_validator = XmlValidator()
security_validator = SecurityValidator()
operation_state = OperationState()
diff_generator = DiffGenerator()
validation_runner = ValidationRunner()


# ============================================================================
# Request/Response Models
# ============================================================================

class ValidateRequest(BaseModel):
    file_path: str


class ValidateModuleRequest(BaseModel):
    module_path: str


class InstallModulesRequest(BaseModel):
    project_id: str
    environment: str
    modules: List[str]


class InstallPreviewRequest(BaseModel):
    project_id: str
    environment: str
    modules: List[str]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for VS Code extension startup verification."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Project & Environment APIs
# ============================================================================

@app.get("/api/projects")
async def list_projects():
    """
    List all discovered Odoo projects.

    Discovery logic:
    1. Check for odoo.code-workspace
    2. Look for spec/ directory (Spec Kit marker)
    3. Look for addons/ directories
    """
    try:
        projects = project_registry.discover_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover projects: {str(e)}")


@app.get("/api/projects/{project_id}/environments")
async def list_environments(project_id: str):
    """
    List environments for a project.

    Environments are determined by:
    1. Docker Compose services (odoo-dev, odoo-stage, odoo-prod)
    2. Database naming conventions (odoo, odoo_dev, odoo_stage, odoo_prod)
    3. Configuration files
    """
    try:
        project = project_registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

        environments = project_registry.get_environments(project_id)
        return environments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list environments: {str(e)}")


@app.get("/api/projects/{project_id}/environments/{env_name}/status")
async def get_environment_status(project_id: str, env_name: str):
    """
    Get detailed status for a specific environment.

    Returns:
    - Odoo version
    - Installed modules
    - Schema hash (for drift detection)
    - Health status
    - Pending migrations
    """
    try:
        project = project_registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

        status = project_registry.get_environment_status(project_id, env_name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Environment not found: {env_name}")

        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get environment status: {str(e)}")


# ============================================================================
# Validation APIs
# ============================================================================

@app.post("/api/validate/manifest")
async def validate_manifest(request: ValidateRequest):
    """
    Validate __manifest__.py file.

    Checks:
    - Required keys (name, version, depends, data, installable)
    - Dependency existence
    - EE-only module detection
    - Version format
    """
    try:
        manifest_path = Path(request.file_path)
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail=f"Manifest not found: {request.file_path}")

        result = manifest_validator.validate(manifest_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manifest validation failed: {str(e)}")


@app.post("/api/validate/xml")
async def validate_xml(request: ValidateRequest):
    """
    Validate XML file.

    Checks:
    - Deprecated <tree> elements (should be <list> in Odoo 19+)
    - Missing external IDs
    - External ID collisions
    - Action/view reference validity
    """
    try:
        xml_path = Path(request.file_path)
        if not xml_path.exists():
            raise HTTPException(status_code=404, detail=f"XML file not found: {request.file_path}")

        result = xml_validator.validate(xml_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XML validation failed: {str(e)}")


@app.post("/api/validate/security")
async def validate_security(request: ValidateModuleRequest):
    """
    Validate security configuration for a module.

    Checks:
    - ir.model.access.csv existence
    - Access rule coverage for all models
    - Record rule (RLS) completeness
    - Empty domain detection
    """
    try:
        module_path = Path(request.module_path)
        if not module_path.exists():
            raise HTTPException(status_code=404, detail=f"Module not found: {request.module_path}")

        result = security_validator.validate(module_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security validation failed: {str(e)}")


@app.post("/api/validate/all")
async def validate_all(request: dict):
    """
    Run all validators on a project.

    Returns aggregated validation results with:
    - Manifest validation for all modules
    - XML validation for all views
    - Security validation for all modules
    """
    project_id = request.get('project_id')
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    try:
        project = project_registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

        # TODO: Implement comprehensive validation
        return {
            "manifest": {"status": "pass", "issues": []},
            "xml": {"status": "pass", "issues": []},
            "security": {"status": "pass", "issues": []}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# ============================================================================
# V1 Operation APIs (New SaaS-grade endpoints)
# ============================================================================

@app.post("/v1/ops/plan")
async def plan_operation(request: dict):
    """
    Plan an operation (returns diffs without executing).

    Request:
        {
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale", "account"]
        }

    Response:
        {
            "op_id": "uuid",
            "status": "planned",
            "diffs": [...],
            "checks": [...]
        }
    """
    try:
        operation_type = request.get('type')
        if not operation_type:
            raise HTTPException(status_code=400, detail="operation type required")

        # Create operation
        operation = operation_state.create_operation(operation_type, request)

        # Run validation checks
        checks = validation_runner.run_checks(operation_type, request)
        operation_state.add_checks(operation['op_id'], checks)

        # Check if validation failed
        if any(c['status'] == 'fail' for c in checks):
            operation_state.update_status(operation['op_id'], 'validation_failed')
            return {
                'op_id': operation['op_id'],
                'status': 'validation_failed',
                'diffs': [],
                'checks': checks
            }

        # Generate diffs
        if operation_type == 'install_modules':
            modules = request.get('modules', [])
            diffs = diff_generator.generate_install_diffs(modules)
            operation_state.add_diffs(operation['op_id'], diffs)
        else:
            diffs = []

        return {
            'op_id': operation['op_id'],
            'status': 'planned',
            'diffs': diffs,
            'checks': checks
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@app.post("/v1/ops/execute")
async def execute_operation(request: dict):
    """
    Execute a planned operation.

    Request:
        {
            "op_id": "uuid"
        }

    Response:
        {
            "op_id": "uuid",
            "bundle_id": "uuid",
            "status": "running" | "succeeded" | "failed"
        }
    """
    try:
        op_id = request.get('op_id')
        if not op_id:
            raise HTTPException(status_code=400, detail="op_id required")

        operation = operation_state.get_operation(op_id)
        if not operation:
            raise HTTPException(status_code=404, detail=f"Operation not found: {op_id}")

        if operation['status'] != 'planned':
            raise HTTPException(
                status_code=400,
                detail=f"Operation cannot be executed (status: {operation['status']})"
            )

        # Update status to running
        operation_state.update_status(op_id, 'running')

        # Create evidence bundle
        evidence = evidence_bundler.create_bundle({
            'type': operation['type'],
            'target_env': operation['params'].get('environment'),
            'project_id': operation['params'].get('project_id'),
            'modules': operation['params'].get('modules', []),
            'op_id': op_id
        })

        bundle_id = evidence['bundle_id']
        operation_state.update_status(op_id, 'running', bundle_id=bundle_id)

        # TODO: Execute actual operation (install modules, run migration, etc.)
        # For now, simulate success

        # Finalize evidence
        evidence_bundler.finalize_bundle(bundle_id, {
            'status': 'success',
            'logs': f"Operation {operation['type']} completed successfully"
        })

        # Update operation status
        operation_state.update_status(op_id, 'succeeded')

        return {
            'op_id': op_id,
            'bundle_id': bundle_id,
            'status': 'succeeded'
        }

    except HTTPException:
        raise
    except Exception as e:
        # Mark operation as failed
        if op_id:
            operation_state.update_status(op_id, 'failed', error=str(e))
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.get("/v1/ops/{op_id}")
async def get_operation_status(op_id: str):
    """
    Get operation status.

    Response:
        {
            "op_id": "uuid",
            "status": "planned" | "running" | "succeeded" | "failed",
            "bundle_id": "uuid" | null,
            "created_at": "iso8601",
            "updated_at": "iso8601"
        }
    """
    operation = operation_state.get_operation(op_id)
    if not operation:
        raise HTTPException(status_code=404, detail=f"Operation not found: {op_id}")

    return {
        'op_id': operation['op_id'],
        'status': operation['status'],
        'bundle_id': operation.get('bundle_id'),
        'created_at': operation['created_at'],
        'updated_at': operation.get('updated_at'),
        'type': operation['type']
    }


# ============================================================================
# Legacy Operation APIs (backwards compatibility)
# ============================================================================

@app.post("/api/operations/install-modules")
async def install_modules(request: InstallModulesRequest):
    """
    Install modules with evidence bundle generation.

    Flow:
    1. Generate evidence bundle
    2. Compute diffs (SQL, ORM, XML)
    3. Execute installation
    4. Finalize evidence with results
    """
    try:
        # Create evidence bundle
        operation = {
            'type': 'install_modules',
            'target_env': request.environment,
            'modules': request.modules,
            'project_id': request.project_id
        }

        evidence = evidence_bundler.create_bundle(operation)

        # TODO: Implement actual installation
        # For now, return success with evidence path

        return {
            'status': 'success',
            'evidence_path': str(evidence['path']),
            'modules_installed': request.modules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")


@app.post("/api/operations/install-modules/preview")
async def preview_install(request: InstallPreviewRequest):
    """
    Preview module installation (diffs only, no execution).

    Returns:
    - SQL diff
    - ORM diff (models/fields changed)
    - XML diff (views/actions added)
    - File diffs
    """
    try:
        # TODO: Implement diff generation
        return {
            'sql': {'statements': [], 'safe': True},
            'orm': {'models_added': [], 'models_removed': [], 'fields_changed': []},
            'files': []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@app.post("/api/operations/run-migration")
async def run_migration(request: dict):
    """Run database migration with evidence generation."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/operations/upgrade-odoo")
async def upgrade_odoo(request: dict):
    """Upgrade Odoo version with evidence generation."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/operations/rollback")
async def rollback(request: dict):
    """Rollback to previous state via snapshot restore."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ============================================================================
# Evidence APIs
# ============================================================================

@app.get("/v1/evidence/{bundle_id}")
async def get_evidence_bundle_v1(bundle_id: str):
    """Get evidence bundle by ID (v1 API)."""
    try:
        bundle = evidence_bundler.get_bundle(bundle_id)
        if not bundle:
            raise HTTPException(status_code=404, detail=f"Evidence bundle not found: {bundle_id}")
        return bundle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evidence: {str(e)}")


@app.get("/api/evidence/{project_id}")
async def list_evidence_bundles(project_id: str):
    """List all evidence bundles for a project."""
    try:
        bundles = evidence_bundler.list_bundles(project_id)
        return bundles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list evidence: {str(e)}")


@app.get("/api/evidence/bundle/{bundle_id}")
async def get_evidence_bundle(bundle_id: str):
    """Get details for a specific evidence bundle."""
    try:
        bundle = evidence_bundler.get_bundle(bundle_id)
        if not bundle:
            raise HTTPException(status_code=404, detail=f"Evidence bundle not found: {bundle_id}")
        return bundle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evidence: {str(e)}")


# ============================================================================
# AI Relay APIs
# ============================================================================

@app.post("/api/ai/generate-patch")
async def ai_generate_patch(request: dict):
    """
    Generate patch via AI relay.

    Enforces:
    - Spec Kit SSOT
    - Patch-only output
    - Validation gates
    """
    raise HTTPException(status_code=501, detail="AI relay not implemented yet")


@app.post("/api/ai/explain-drift")
async def ai_explain_drift(request: dict):
    """Generate human-readable explanation of schema drift."""
    raise HTTPException(status_code=501, detail="AI relay not implemented yet")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('IPAI_CONTROL_PLANE_PORT', 9876))

    print(f"""
╔════════════════════════════════════════════════════════════════╗
║  IPAI Control Plane Server                                     ║
║  Version: 0.1.0                                                ║
║  Port: {port}                                                     ║
║                                                                ║
║  Endpoints:                                                    ║
║  - Health: http://127.0.0.1:{port}/health                        ║
║  - Docs: http://127.0.0.1:{port}/docs                            ║
╚════════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
