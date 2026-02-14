"""API endpoint tests for IPAI Control Plane server."""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


class TestHealthCheck:
    """Health check endpoint tests."""

    def test_health_check_returns_200(self):
        """Health check should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestProjectDiscovery:
    """Project discovery endpoint tests."""

    def test_list_projects(self):
        """Should list discovered projects."""
        response = client.get("/projects")
        assert response.status_code == 200

        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)

    def test_get_project_details(self):
        """Should get project details."""
        # First list projects
        list_response = client.get("/projects")
        projects = list_response.json()["projects"]

        if projects:
            project_id = projects[0]["id"]
            response = client.get(f"/projects/{project_id}")
            assert response.status_code == 200

            data = response.json()
            assert "id" in data
            assert "environments" in data


class TestOperationPlanAPI:
    """Operation planning endpoint tests."""

    def test_plan_install_modules_success(self):
        """Should plan module installation with diffs and validation."""
        response = client.post("/v1/ops/plan", json={
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale", "account"],
            "project_id": "test-project"
        })

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "op_id" in data
        assert "status" in data
        assert "diffs" in data
        assert "checks" in data

        # Status should be planned or validation_failed
        assert data["status"] in ["planned", "validation_failed"]

        # Diffs should be present
        assert isinstance(data["diffs"], list)

        # Checks should be present
        assert isinstance(data["checks"], list)

    def test_plan_with_ee_modules_fails_validation(self):
        """Should fail validation when EE modules detected."""
        response = client.post("/v1/ops/plan", json={
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale", "web_studio"],  # web_studio is EE-only
            "project_id": "test-project"
        })

        assert response.status_code == 200
        data = response.json()

        # Should have validation failure
        assert data["status"] == "validation_failed"

        # Should have at least one failed check
        failed_checks = [c for c in data["checks"] if c["status"] == "fail"]
        assert len(failed_checks) > 0

    def test_plan_missing_required_fields(self):
        """Should reject plan requests with missing fields."""
        response = client.post("/v1/ops/plan", json={
            "type": "install_modules"
            # Missing environment, modules, project_id
        })

        # Should return 422 Unprocessable Entity or handle gracefully
        assert response.status_code in [422, 400, 500]


class TestOperationExecutionAPI:
    """Operation execution endpoint tests."""

    def test_execute_operation_success(self):
        """Should execute a planned operation."""
        # First plan an operation
        plan_response = client.post("/v1/ops/plan", json={
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale"],
            "project_id": "test-project"
        })

        assert plan_response.status_code == 200
        plan_data = plan_response.json()

        # Only execute if validation passed
        if plan_data["status"] == "planned":
            op_id = plan_data["op_id"]

            # Execute the operation
            exec_response = client.post("/v1/ops/execute", json={"op_id": op_id})

            assert exec_response.status_code == 200
            exec_data = exec_response.json()

            assert exec_data["op_id"] == op_id
            assert "bundle_id" in exec_data
            assert exec_data["status"] in ["succeeded", "running", "failed"]

    def test_execute_nonexistent_operation(self):
        """Should reject execution of non-existent operation."""
        response = client.post("/v1/ops/execute", json={
            "op_id": "nonexistent-op-id-12345"
        })

        # Should return error
        assert response.status_code in [404, 400, 500]


class TestOperationStatusAPI:
    """Operation status endpoint tests."""

    def test_get_operation_status(self):
        """Should get operation status."""
        # First create an operation
        plan_response = client.post("/v1/ops/plan", json={
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale"],
            "project_id": "test-project"
        })

        assert plan_response.status_code == 200
        op_id = plan_response.json()["op_id"]

        # Get status
        status_response = client.get(f"/v1/ops/{op_id}")

        assert status_response.status_code == 200
        data = status_response.json()

        assert data["op_id"] == op_id
        assert "status" in data
        assert data["status"] in ["planned", "running", "succeeded", "failed", "validation_failed"]

    def test_get_nonexistent_operation_status(self):
        """Should return 404 for non-existent operation."""
        response = client.get("/v1/ops/nonexistent-op-id-12345")
        assert response.status_code in [404, 500]


class TestEvidenceBundlesAPI:
    """Evidence bundles endpoint tests."""

    def test_list_evidence_bundles(self):
        """Should list evidence bundles."""
        response = client.get("/evidence/test-project")

        assert response.status_code == 200
        data = response.json()

        assert "bundles" in data
        assert isinstance(data["bundles"], list)

    def test_get_evidence_bundle(self):
        """Should get specific evidence bundle."""
        # First create an operation to generate evidence
        plan_response = client.post("/v1/ops/plan", json={
            "type": "install_modules",
            "environment": "dev",
            "modules": ["sale"],
            "project_id": "test-project"
        })

        assert plan_response.status_code == 200

        if plan_response.json()["status"] == "planned":
            op_id = plan_response.json()["op_id"]

            exec_response = client.post("/v1/ops/execute", json={"op_id": op_id})

            if exec_response.status_code == 200:
                bundle_id = exec_response.json().get("bundle_id")

                if bundle_id:
                    bundle_response = client.get(f"/evidence/{bundle_id}")

                    # Should either succeed or indicate bundle not found yet
                    assert bundle_response.status_code in [200, 404]
