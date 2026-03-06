"""GitHub REST API connector.

Incremental extraction of repos, issues, PRs, commits, and
workflow_runs using updated_at / since cursors.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator

import httpx

from workbench.config.settings import get_settings
from workbench.connectors.base import BaseConnector
from workbench.connectors.registry import register_connector
from workbench.connectors.retry import RetryPolicy
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    SyncMode,
    SyncOp,
    TableDef,
)

logger = logging.getLogger(__name__)


@register_connector("github", name="GitHub")
class GitHubConnector(BaseConnector):
    """Connector for GitHub REST API.

    Config keys:
        github_token: Personal access token
        org: GitHub organization
        repos: Optional list of repo names (defaults to all org repos)
    """

    BASE_URL = "https://api.github.com"
    retry_policy = RetryPolicy(
        max_retries=5,
        base_delay=2.0,
        retryable_exceptions=(httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException),
    )
    rate_limit = 3.0  # 5000/hr authenticated ≈ ~1.4/s, use 3/s with bursts

    def __init__(self, config: dict) -> None:  # type: ignore[type-arg]
        super().__init__(config)
        settings = get_settings()
        self.token = config.get("github_token") or settings.github_token
        self.org = config.get("org") or settings.github_org
        self.repos: list[str] = list(config.get("repos", []))
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        self.client.close()

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Verify token by fetching authenticated user."""
        resp = self.client.get("/user")
        resp.raise_for_status()
        return True

    def schema(self) -> list[TableDef]:
        """Declare GitHub entity tables."""
        return [
            TableDef(
                name="github_repos",
                columns=(
                    ColumnDef("repo_id", "LONG"),
                    ColumnDef("full_name", "STRING"),
                    ColumnDef("name", "STRING"),
                    ColumnDef("description", "STRING"),
                    ColumnDef("language", "STRING"),
                    ColumnDef("default_branch", "STRING"),
                    ColumnDef("stargazers_count", "INT"),
                    ColumnDef("forks_count", "INT"),
                    ColumnDef("open_issues_count", "INT"),
                    ColumnDef("created_at", "TIMESTAMP"),
                    ColumnDef("updated_at", "TIMESTAMP"),
                    ColumnDef("pushed_at", "TIMESTAMP"),
                    ColumnDef("raw_payload", "STRING"),
                ),
                primary_key=("repo_id",),
                sync_mode=SyncMode.INCREMENTAL,
                description="GitHub repositories",
            ),
            TableDef(
                name="github_issues",
                columns=(
                    ColumnDef("issue_id", "LONG"),
                    ColumnDef("repo_full_name", "STRING"),
                    ColumnDef("number", "INT"),
                    ColumnDef("title", "STRING"),
                    ColumnDef("state", "STRING"),
                    ColumnDef("author", "STRING"),
                    ColumnDef("labels", "STRING"),
                    ColumnDef("created_at", "TIMESTAMP"),
                    ColumnDef("updated_at", "TIMESTAMP"),
                    ColumnDef("closed_at", "TIMESTAMP"),
                    ColumnDef("raw_payload", "STRING"),
                ),
                primary_key=("issue_id",),
                sync_mode=SyncMode.INCREMENTAL,
                description="GitHub issues (includes PRs)",
            ),
            TableDef(
                name="github_pull_requests",
                columns=(
                    ColumnDef("pr_id", "LONG"),
                    ColumnDef("repo_full_name", "STRING"),
                    ColumnDef("number", "INT"),
                    ColumnDef("title", "STRING"),
                    ColumnDef("state", "STRING"),
                    ColumnDef("author", "STRING"),
                    ColumnDef("merged", "BOOLEAN"),
                    ColumnDef("merged_at", "TIMESTAMP"),
                    ColumnDef("additions", "INT"),
                    ColumnDef("deletions", "INT"),
                    ColumnDef("created_at", "TIMESTAMP"),
                    ColumnDef("updated_at", "TIMESTAMP"),
                    ColumnDef("raw_payload", "STRING"),
                ),
                primary_key=("pr_id",),
                sync_mode=SyncMode.INCREMENTAL,
                description="GitHub pull requests",
            ),
            TableDef(
                name="github_commits",
                columns=(
                    ColumnDef("sha", "STRING"),
                    ColumnDef("repo_full_name", "STRING"),
                    ColumnDef("message", "STRING"),
                    ColumnDef("author_name", "STRING"),
                    ColumnDef("author_email", "STRING"),
                    ColumnDef("committed_at", "TIMESTAMP"),
                    ColumnDef("raw_payload", "STRING"),
                ),
                primary_key=("sha",),
                sync_mode=SyncMode.INCREMENTAL,
                description="GitHub commits",
            ),
            TableDef(
                name="github_workflow_runs",
                columns=(
                    ColumnDef("run_id", "LONG"),
                    ColumnDef("repo_full_name", "STRING"),
                    ColumnDef("workflow_name", "STRING"),
                    ColumnDef("status", "STRING"),
                    ColumnDef("conclusion", "STRING"),
                    ColumnDef("event", "STRING"),
                    ColumnDef("branch", "STRING"),
                    ColumnDef("created_at", "TIMESTAMP"),
                    ColumnDef("updated_at", "TIMESTAMP"),
                    ColumnDef("run_started_at", "TIMESTAMP"),
                    ColumnDef("raw_payload", "STRING"),
                ),
                primary_key=("run_id",),
                sync_mode=SyncMode.INCREMENTAL,
                description="GitHub Actions workflow runs",
            ),
        ]

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        """Incrementally sync GitHub data across all repos."""
        cursors: dict[str, dict[str, str]] = state.cursor.get("github", {})

        # Resolve repo list
        repos = self.repos or self._list_org_repos()

        for repo in repos:
            full_name = f"{self.org}/{repo}" if "/" not in repo else repo
            repo_cursors = cursors.get(full_name, {})

            yield from self._sync_repo_metadata(full_name)
            yield from self._sync_issues(full_name, repo_cursors)
            yield from self._sync_pulls(full_name, repo_cursors)
            yield from self._sync_commits(full_name, repo_cursors)
            yield from self._sync_workflow_runs(full_name, repo_cursors)

            cursors[full_name] = repo_cursors

        yield SyncOp(
            op_type=OpType.CHECKPOINT,
            table="",
            cursor={"github": cursors},
        )

    # ------------------------------------------------------------------
    # Entity sync methods
    # ------------------------------------------------------------------

    def _sync_repo_metadata(self, full_name: str) -> Iterator[SyncOp]:
        resp = self.client.get(f"/repos/{full_name}")
        resp.raise_for_status()
        repo = resp.json()
        yield SyncOp(
            op_type=OpType.UPSERT,
            table="github_repos",
            data={
                "repo_id": repo["id"],
                "full_name": repo["full_name"],
                "name": repo["name"],
                "description": repo.get("description") or "",
                "language": repo.get("language") or "",
                "default_branch": repo.get("default_branch", "main"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "pushed_at": repo.get("pushed_at"),
                "raw_payload": json.dumps(repo),
            },
        )

    def _sync_issues(self, full_name: str, cursors: dict[str, str]) -> Iterator[SyncOp]:
        since = cursors.get("issues_updated_at")
        params: dict[str, Any] = {
            "state": "all",
            "sort": "updated",
            "direction": "asc",
            "per_page": 100,
        }
        if since:
            params["since"] = since

        max_updated = since
        for issue in self._paginate(f"/repos/{full_name}/issues", params):
            if issue.get("pull_request"):
                continue  # Skip PRs in issues endpoint
            updated = issue.get("updated_at", "")
            if not max_updated or updated > max_updated:
                max_updated = updated

            labels = json.dumps([l["name"] for l in issue.get("labels", [])])
            yield SyncOp(
                op_type=OpType.UPSERT,
                table="github_issues",
                data={
                    "issue_id": issue["id"],
                    "repo_full_name": full_name,
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "author": issue.get("user", {}).get("login", ""),
                    "labels": labels,
                    "created_at": issue["created_at"],
                    "updated_at": updated,
                    "closed_at": issue.get("closed_at"),
                    "raw_payload": json.dumps(issue),
                },
            )

        if max_updated:
            cursors["issues_updated_at"] = max_updated

    def _sync_pulls(self, full_name: str, cursors: dict[str, str]) -> Iterator[SyncOp]:
        since = cursors.get("pulls_updated_at")
        params: dict[str, Any] = {
            "state": "all",
            "sort": "updated",
            "direction": "asc",
            "per_page": 100,
        }

        max_updated = since
        for pr in self._paginate(f"/repos/{full_name}/pulls", params):
            updated = pr.get("updated_at", "")
            if since and updated <= since:
                continue
            if not max_updated or updated > max_updated:
                max_updated = updated

            yield SyncOp(
                op_type=OpType.UPSERT,
                table="github_pull_requests",
                data={
                    "pr_id": pr["id"],
                    "repo_full_name": full_name,
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "author": pr.get("user", {}).get("login", ""),
                    "merged": pr.get("merged_at") is not None,
                    "merged_at": pr.get("merged_at"),
                    "additions": pr.get("additions", 0),
                    "deletions": pr.get("deletions", 0),
                    "created_at": pr["created_at"],
                    "updated_at": updated,
                    "raw_payload": json.dumps(pr),
                },
            )

        if max_updated:
            cursors["pulls_updated_at"] = max_updated

    def _sync_commits(self, full_name: str, cursors: dict[str, str]) -> Iterator[SyncOp]:
        since = cursors.get("commits_since")
        params: dict[str, Any] = {"per_page": 100}
        if since:
            params["since"] = since

        max_date = since
        for commit in self._paginate(f"/repos/{full_name}/commits", params):
            commit_data = commit.get("commit", {})
            author = commit_data.get("author", {})
            committed_at = author.get("date", "")
            if not max_date or committed_at > max_date:
                max_date = committed_at

            yield SyncOp(
                op_type=OpType.UPSERT,
                table="github_commits",
                data={
                    "sha": commit["sha"],
                    "repo_full_name": full_name,
                    "message": commit_data.get("message", ""),
                    "author_name": author.get("name", ""),
                    "author_email": author.get("email", ""),
                    "committed_at": committed_at,
                    "raw_payload": json.dumps(commit),
                },
            )

        if max_date:
            cursors["commits_since"] = max_date

    def _sync_workflow_runs(self, full_name: str, cursors: dict[str, str]) -> Iterator[SyncOp]:
        since = cursors.get("workflow_runs_created")
        params: dict[str, Any] = {"per_page": 100}
        if since:
            params["created"] = f">={since}"

        max_created = since
        resp = self.client.get(f"/repos/{full_name}/actions/runs", params=params)
        resp.raise_for_status()
        runs = resp.json().get("workflow_runs", [])

        for run in runs:
            created = run.get("created_at", "")
            if not max_created or created > max_created:
                max_created = created

            yield SyncOp(
                op_type=OpType.UPSERT,
                table="github_workflow_runs",
                data={
                    "run_id": run["id"],
                    "repo_full_name": full_name,
                    "workflow_name": run.get("name", ""),
                    "status": run.get("status", ""),
                    "conclusion": run.get("conclusion") or "",
                    "event": run.get("event", ""),
                    "branch": run.get("head_branch", ""),
                    "created_at": created,
                    "updated_at": run.get("updated_at", ""),
                    "run_started_at": run.get("run_started_at", ""),
                    "raw_payload": json.dumps(run),
                },
            )

        if max_created:
            cursors["workflow_runs_created"] = max_created

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _list_org_repos(self) -> list[str]:
        """List all repositories in the configured org."""
        repos: list[str] = []
        for repo in self._paginate(f"/orgs/{self.org}/repos", {"per_page": 100}):
            repos.append(repo["name"])
        return repos

    def _paginate(self, url: str, params: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """Follow GitHub link-header pagination."""
        page_params = dict(params)
        while True:
            resp = self.client.get(url, params=page_params)
            resp.raise_for_status()
            items = resp.json()
            if isinstance(items, list):
                yield from items
            else:
                break

            # Check for next page via Link header
            link = resp.headers.get("link", "")
            if 'rel="next"' not in link:
                break

            # Extract next URL
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip(" <>")
                    # Parse query params from next URL
                    if "?" in next_url:
                        from urllib.parse import parse_qs, urlparse

                        parsed = urlparse(next_url)
                        page_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
                    break
