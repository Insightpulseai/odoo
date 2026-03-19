#!/usr/bin/env python3
"""
API Contract Tests for IPAI Skill API

Tests the REST API endpoints against expected contracts.
Run with: pytest tests/api/test_skill_api_contract.py -v

Requires:
- Running Odoo instance with ipai_skill_api installed
- ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD env vars
"""

import json
import os
import pytest
import requests
from urllib.parse import urljoin

# Configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")


@pytest.fixture(scope="module")
def session():
    """Create authenticated session."""
    s = requests.Session()

    # Authenticate via web login
    login_url = urljoin(ODOO_URL, "/web/session/authenticate")
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_USER,
            "password": ODOO_PASSWORD,
        },
        "id": 1,
    }

    response = s.post(login_url, json=payload)
    response.raise_for_status()

    result = response.json()
    if result.get("error"):
        pytest.skip(f"Authentication failed: {result['error']}")

    return s


class TestHealthEndpoint:
    """Tests for /api/v1/health endpoint."""

    def test_health_returns_ok(self):
        """Health check should return 200 with status ok."""
        response = requests.get(urljoin(ODOO_URL, "/api/v1/health"))

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ipai_skill_api"
        assert "version" in data


class TestSkillsEndpoint:
    """Tests for /api/v1/skills endpoints."""

    def test_list_skills_requires_auth(self):
        """Skills list should require authentication."""
        response = requests.get(urljoin(ODOO_URL, "/api/v1/skills"))

        # Should redirect to login or return auth error
        assert response.status_code in [401, 403, 303]

    def test_list_skills_with_auth(self, session):
        """Skills list should return skills array."""
        response = session.get(urljoin(ODOO_URL, "/api/v1/skills"))

        assert response.status_code == 200
        data = response.json()

        assert "skills" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["skills"], list)

    def test_list_skills_pagination(self, session):
        """Skills list should support pagination."""
        response = session.get(
            urljoin(ODOO_URL, "/api/v1/skills"),
            params={"limit": 5, "offset": 0}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["limit"] == 5
        assert data["offset"] == 0
        assert len(data["skills"]) <= 5

    def test_list_skills_search(self, session):
        """Skills list should support search."""
        response = session.get(
            urljoin(ODOO_URL, "/api/v1/skills"),
            params={"search": "test"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "skills" in data

    def test_skill_structure(self, session):
        """Skills should have expected structure."""
        response = session.get(urljoin(ODOO_URL, "/api/v1/skills"))

        assert response.status_code == 200
        data = response.json()

        if data["skills"]:
            skill = data["skills"][0]
            assert "id" in skill
            assert "key" in skill
            assert "name" in skill
            assert "version" in skill
            assert "is_active" in skill

    def test_get_skill_not_found(self, session):
        """Getting non-existent skill should return 404."""
        response = session.get(
            urljoin(ODOO_URL, "/api/v1/skills/nonexistent.skill.key")
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestRunsEndpoint:
    """Tests for /api/v1/runs endpoints."""

    def test_create_run_requires_auth(self):
        """Run creation should require authentication."""
        response = requests.post(
            urljoin(ODOO_URL, "/api/v1/runs"),
            json={"skill_key": "test.skill"}
        )

        assert response.status_code in [401, 403, 303]

    def test_create_run_requires_skill_key(self, session):
        """Run creation should require skill_key."""
        response = session.post(
            urljoin(ODOO_URL, "/api/v1/runs"),
            json={},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "skill_key" in data["error"].lower()

    def test_create_run_invalid_skill(self, session):
        """Run creation with invalid skill should return 404."""
        response = session.post(
            urljoin(ODOO_URL, "/api/v1/runs"),
            json={"skill_key": "nonexistent.skill.key"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_get_run_not_found(self, session):
        """Getting non-existent run should return 404."""
        response = session.get(urljoin(ODOO_URL, "/api/v1/runs/999999"))

        assert response.status_code == 404


class TestAPIContract:
    """General API contract tests."""

    def test_api_returns_json(self, session):
        """API should return JSON content type."""
        response = session.get(urljoin(ODOO_URL, "/api/v1/health"))

        assert "application/json" in response.headers.get("Content-Type", "")

    def test_error_responses_are_json(self, session):
        """Error responses should be JSON."""
        response = session.get(
            urljoin(ODOO_URL, "/api/v1/skills/nonexistent")
        )

        assert response.status_code == 404
        assert "application/json" in response.headers.get("Content-Type", "")

        data = response.json()
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
