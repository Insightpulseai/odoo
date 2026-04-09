"""Tests for finance copilot tools — mocked Databricks connection."""

import json
from unittest.mock import MagicMock, patch

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools import get_portfolio_health, get_project_profitability


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.description = [
        ("project_name",), ("revenue",), ("cost",), ("margin_pct",),
    ]
    cursor.fetchall.return_value = [
        ("Alpha", 500000.0, 350000.0, 30.0),
        ("Beta", 200000.0, 180000.0, 10.0),
    ]
    return cursor


@pytest.fixture
def mock_portfolio_cursor():
    cursor = MagicMock()
    cursor.description = [
        ("portfolio_name",), ("health_score",), ("budget_utilization",), ("risk_level",),
    ]
    cursor.fetchall.return_value = [
        ("Finance Ops", 92.5, 0.78, "low"),
        ("Engineering", 71.0, 0.95, "medium"),
    ]
    return cursor


@patch("tools._get_connection")
def test_get_project_profitability_all(mock_conn, mock_cursor):
    mock_conn.return_value.cursor.return_value = mock_cursor
    result = json.loads(get_project_profitability())
    assert len(result) == 2
    assert result[0]["project_name"] == "Alpha"
    assert result[0]["revenue"] == 500000.0
    assert result[0]["margin_pct"] == 30.0


@patch("tools._get_connection")
def test_get_project_profitability_filtered(mock_conn, mock_cursor):
    mock_conn.return_value.cursor.return_value = mock_cursor
    result = json.loads(get_project_profitability(project_name="Alpha"))
    assert isinstance(result, list)
    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "WHERE project_name = 'Alpha'" in sql


@patch("tools._get_connection")
def test_get_portfolio_health_all(mock_conn, mock_portfolio_cursor):
    mock_conn.return_value.cursor.return_value = mock_portfolio_cursor
    result = json.loads(get_portfolio_health())
    assert len(result) == 2
    assert result[0]["portfolio_name"] == "Finance Ops"
    assert result[0]["health_score"] == 92.5


@patch("tools._get_connection")
def test_get_portfolio_health_filtered(mock_conn, mock_portfolio_cursor):
    mock_conn.return_value.cursor.return_value = mock_portfolio_cursor
    result = json.loads(get_portfolio_health(portfolio_name="Finance Ops"))
    assert isinstance(result, list)
    sql = mock_portfolio_cursor.execute.call_args[0][0]
    assert "WHERE portfolio_name = 'Finance Ops'" in sql


@patch("tools._get_connection")
def test_project_profitability_returns_valid_json(mock_conn, mock_cursor):
    mock_conn.return_value.cursor.return_value = mock_cursor
    raw = get_project_profitability()
    parsed = json.loads(raw)
    assert all(
        key in parsed[0] for key in ("project_name", "revenue", "cost", "margin_pct")
    )


@patch("tools._get_connection")
def test_portfolio_health_returns_valid_json(mock_conn, mock_portfolio_cursor):
    mock_conn.return_value.cursor.return_value = mock_portfolio_cursor
    raw = get_portfolio_health()
    parsed = json.loads(raw)
    assert all(
        key in parsed[0]
        for key in ("portfolio_name", "health_score", "budget_utilization", "risk_level")
    )
