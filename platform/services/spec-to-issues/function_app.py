"""Azure Functions v2 — Spec-to-Issues Bridge.

Parses spec kit tasks.md files and creates GitHub Issues for unchecked tasks.
Optionally assigns issues to Copilot coding agent.

Triggers:
  HTTP POST /api/spec-to-issues  (called by Azure Pipeline or manual)

Env vars:
  GITHUB_TOKEN       — PAT or GitHub App token with issues:write scope
  GITHUB_REPO        — owner/repo (default: Insightpulseai/odoo)
  COPILOT_ASSIGNEE   — set to "copilot" to auto-assign coding agent
"""

import json
import logging
import os
import re

import azure.functions as func
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
logger = logging.getLogger("spec_to_issues")

GITHUB_API = "https://api.github.com"
DEFAULT_REPO = "Insightpulseai/odoo"


def parse_tasks_md(content: str, spec_name: str) -> list[dict]:
    """Parse a spec tasks.md into structured task dicts.

    Returns list of dicts with keys: id, title, phase, done, spec.
    Only returns unchecked ([ ]) tasks.
    """
    tasks = []
    current_phase = ""

    for line in content.splitlines():
        # Phase headers: ## Phase N: Title
        phase_match = re.match(r"^##\s+(.+)", line)
        if phase_match:
            current_phase = phase_match.group(1).strip()
            continue

        # Task lines: - [ ] **T1.1** Description
        # or: - [x] **T1.1** Description (completed, skip)
        task_match = re.match(
            r"^-\s+\[([ x])\]\s+\*\*([^*]+)\*\*\s*(.*)", line
        )
        if task_match:
            done = task_match.group(1) == "x"
            task_id = task_match.group(2).strip()
            title = task_match.group(3).strip()

            if not done:
                tasks.append({
                    "id": task_id,
                    "title": title,
                    "phase": current_phase,
                    "spec": spec_name,
                })

    return tasks


def create_github_issue(
    token: str,
    repo: str,
    task: dict,
    assignee: str | None = None,
    labels: list[str] | None = None,
) -> dict:
    """Create a GitHub Issue from a parsed spec task."""
    issue_title = f"[{task['spec']}] {task['id']}: {task['title']}"
    issue_body = (
        f"## Spec Task\n\n"
        f"- **Spec:** `spec/{task['spec']}/`\n"
        f"- **Task ID:** {task['id']}\n"
        f"- **Phase:** {task['phase']}\n\n"
        f"## Description\n\n"
        f"{task['title']}\n\n"
        f"---\n"
        f"*Auto-created by spec-to-issues bridge from `spec/{task['spec']}/tasks.md`*"
    )

    payload = {
        "title": issue_title,
        "body": issue_body,
        "labels": labels or ["spec-task", f"spec:{task['spec']}"],
    }
    if assignee:
        payload["assignees"] = [assignee]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(
        f"{GITHUB_API}/repos/{repo}/issues",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def find_existing_issues(token: str, repo: str, spec_name: str) -> set[str]:
    """Find existing issues for a spec to avoid duplicates. Returns set of task IDs."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    existing = set()
    page = 1
    while True:
        resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/issues",
            headers=headers,
            params={
                "labels": f"spec:{spec_name}",
                "state": "all",
                "per_page": 100,
                "page": page,
            },
            timeout=30,
        )
        issues = resp.json()
        if not issues:
            break
        for issue in issues:
            # Extract task ID from title: [spec] T1.1: ...
            m = re.search(r"\]\s+(T[\d.]+):", issue.get("title", ""))
            if m:
                existing.add(m.group(1))
        page += 1
    return existing


@app.route(route="spec-to-issues", methods=["POST"])
def spec_to_issues(req: func.HttpRequest) -> func.HttpResponse:
    """Parse spec tasks.md and create GitHub Issues for open tasks.

    JSON body:
      spec_name:  required — name of spec bundle (e.g. "finance-unified")
      tasks_md:   required — raw content of tasks.md
      dry_run:    optional — if true, return tasks without creating issues
      assignee:   optional — GitHub username to assign (e.g. "copilot")
      labels:     optional — list of extra labels
    """
    logger.info("spec_to_issues: request received")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "JSON body required"}),
            status_code=400,
            mimetype="application/json",
        )

    spec_name = body.get("spec_name", "")
    tasks_md = body.get("tasks_md", "")
    dry_run = body.get("dry_run", False)
    assignee = body.get("assignee") or os.environ.get("COPILOT_ASSIGNEE")
    extra_labels = body.get("labels", [])

    if not spec_name or not tasks_md:
        return func.HttpResponse(
            json.dumps({"error": "spec_name and tasks_md are required"}),
            status_code=400,
            mimetype="application/json",
        )

    # Parse tasks
    tasks = parse_tasks_md(tasks_md, spec_name)
    if not tasks:
        return func.HttpResponse(
            json.dumps({"spec": spec_name, "tasks_found": 0, "message": "No open tasks found"}),
            status_code=200,
            mimetype="application/json",
        )

    if dry_run:
        return func.HttpResponse(
            json.dumps({
                "spec": spec_name,
                "dry_run": True,
                "tasks_found": len(tasks),
                "tasks": tasks,
            }),
            status_code=200,
            mimetype="application/json",
        )

    # Create issues
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        return func.HttpResponse(
            json.dumps({"error": "GITHUB_TOKEN env var required"}),
            status_code=500,
            mimetype="application/json",
        )

    repo = os.environ.get("GITHUB_REPO", DEFAULT_REPO)
    labels = ["spec-task", f"spec:{spec_name}"] + extra_labels

    # Check for existing issues to avoid duplicates
    existing_ids = find_existing_issues(gh_token, repo, spec_name)
    logger.info("Found %d existing issues for spec=%s", len(existing_ids), spec_name)

    created = []
    skipped = []
    errors = []

    for task in tasks:
        if task["id"] in existing_ids:
            skipped.append(task["id"])
            continue

        try:
            issue = create_github_issue(gh_token, repo, task, assignee, labels)
            created.append({
                "task_id": task["id"],
                "issue_number": issue["number"],
                "url": issue["html_url"],
            })
            logger.info("Created issue #%d for %s", issue["number"], task["id"])
        except Exception as exc:
            errors.append({"task_id": task["id"], "error": str(exc)})
            logger.error("Failed to create issue for %s: %s", task["id"], exc)

    result = {
        "spec": spec_name,
        "tasks_found": len(tasks),
        "created": len(created),
        "skipped": len(skipped),
        "errors": len(errors),
        "issues": created,
        "skipped_ids": skipped,
        "error_details": errors,
    }

    status_code = 200 if not errors else 207
    return func.HttpResponse(
        json.dumps(result),
        status_code=status_code,
        mimetype="application/json",
    )
