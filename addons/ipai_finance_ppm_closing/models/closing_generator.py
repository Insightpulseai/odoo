# -*- coding: utf-8 -*-
"""
Month-End Close + BIR Task Generator

Implements the generator contract for creating Odoo tasks from seed JSON
with idempotent upserts and completeness reporting.

Key features:
- Deterministic external keys for idempotency
- SHA256 hashing for change detection
- Audit trail via generation runs
- Completeness status (PASS/WARN/FAIL)
- Asia/Manila timezone for deadline calculations
- Fallback assignee for unmapped employee codes
"""
import hashlib
import json
import logging
from datetime import date, datetime, timedelta

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Default timezone for deadline calculations
DEFAULT_TIMEZONE = "Asia/Manila"


def _sha256(obj) -> str:
    """Generate SHA256 hash of a JSON-serializable object."""
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _parse_iso(d: str) -> date:
    """Parse ISO date string to date object."""
    return datetime.strptime(d, "%Y-%m-%d").date()


class ClosingTaskGenerator(models.AbstractModel):
    """
    Month-End Close + BIR Task Generator

    Abstract model providing the core generation logic. Can be invoked via:
    - Server action
    - Scheduled cron
    - Direct API call: env['ipai.close.generator'].run(seed, cycle_code)
    """

    _name = "ipai.close.generator"
    _description = "Month-End Close + BIR Task Generator"

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    @api.model
    def run(
        self,
        seed: dict,
        cycle_code: str,
        cycle_key: str | None = None,
        dry_run: bool = False,
    ) -> dict:
        """
        Generate tasks for a closing cycle from seed JSON.

        Args:
            seed: The seed JSON document conforming to schema v1.1.0
            cycle_code: Cycle to generate (e.g., 'MONTH_END_CLOSE')
            cycle_key: Optional specific instance (e.g., 'MONTH_END_CLOSE|2025-11')
                      If None, generates for current month.
            dry_run: If True, report what would change without persisting.

        Returns:
            dict: Generation report with counts, errors, warnings, and status.

        Raises:
            UserError: If seed is invalid or cycle not found.
        """
        self._validate_seed(seed)

        cycle = self._find_cycle(seed, cycle_code)
        if not cycle:
            raise UserError(f"Cycle not found: {cycle_code}")

        # If no cycle_key specified, generate for current month
        # Use timezone from seed for date calculations
        if not cycle_key:
            today = self._get_today_in_timezone(seed.get("timezone", DEFAULT_TIMEZONE))
            cycle_key = f"{cycle_code}|{today.strftime('%Y-%m')}"

        # Create audit run record
        run_rec = self.env["ipai.close.generation.run"].create(
            {
                "seed_id": seed["seed_id"],
                "cycle_code": cycle_code,
                "cycle_key": cycle_key,
                "dry_run": dry_run,
                "status": "pass",
                "report_json": {},
            }
        )

        # Initialize report
        report = {
            "seed_id": seed["seed_id"],
            "cycle_code": cycle_code,
            "cycle_key": cycle_key,
            "dry_run": dry_run,
            "errors": [],
            "warnings": [],
            "counts": {
                "created": 0,
                "updated": 0,
                "unchanged": 0,
                "obsolete_marked": 0,
            },
            "unresolved_assignees": [],
            "missing_deadlines": [],
            "duplicates": [],
        }

        # Ensure project exists
        project = self._ensure_project(cycle)

        # Flatten templates from hierarchy
        templates = self._flatten_templates(cycle)

        # Get instance-specific date overrides
        override_map = self._instance_override_map(cycle, cycle_key)

        # Track expected keys for obsolescence detection
        expected_step_keys = set()
        expected_parent_keys = set()

        # Process each template
        for tpl in templates:
            parent_key = f"{cycle_key}|{tpl['task_template_code']}"
            expected_parent_keys.add(parent_key)

            # Create/update parent task
            parent_task = self._upsert_task(
                run_rec=run_rec,
                project=project,
                external_key=parent_key,
                name=tpl["name"],
                values={
                    "x_cycle_key": cycle_key,
                    "x_task_template_code": tpl["task_template_code"],
                    "x_step_code": False,
                    "parent_id": False,
                },
                seed_hash=_sha256({"type": "parent", "tpl": tpl}),
                dry_run=dry_run,
                report=report,
            )

            # Create/update step child tasks
            for step in tpl["steps"]:
                step_code = step["step_code"]

                # Resolve deadline
                deadline = self._resolve_deadline(
                    override_map=override_map,
                    tpl_code=tpl["task_template_code"],
                    step_code=step_code,
                    seed=seed,
                    cycle_key=cycle_key,
                )

                if not deadline:
                    report["missing_deadlines"].append(
                        {
                            "task_template_code": tpl["task_template_code"],
                            "step_code": step_code,
                        }
                    )
                    report["errors"].append(
                        f"Missing deadline for {tpl['task_template_code']} {step_code}"
                    )
                    continue

                step_key = (
                    f"{cycle_key}|{tpl['task_template_code']}|"
                    f"{step_code}|{deadline.isoformat()}"
                )
                expected_step_keys.add(step_key)

                # Resolve assignee with fallback support
                user_id, used_fallback = self._resolve_user_id(
                    step.get("default_assignee"),
                    use_fallback=True,
                )
                if used_fallback or (not user_id and step.get("default_assignee")):
                    report["unresolved_assignees"].append(
                        {
                            "employee_code": step.get("default_assignee"),
                            "task_template_code": tpl["task_template_code"],
                            "step_code": step_code,
                            "used_fallback": used_fallback,
                        }
                    )
                    report["warnings"].append(
                        f"Unresolved assignee '{step.get('default_assignee')}' "
                        f"for {tpl['task_template_code']}/{step_code}"
                        + (" (using fallback)" if used_fallback else "")
                    )

                # Create/update step task
                self._upsert_task(
                    run_rec=run_rec,
                    project=project,
                    external_key=step_key,
                    name=f"{step_code}: {tpl['name']}",
                    values={
                        "x_cycle_key": cycle_key,
                        "x_task_template_code": tpl["task_template_code"],
                        "x_step_code": step_code,
                        "parent_id": parent_task.id if parent_task else False,
                        "date_deadline": deadline,
                        "user_ids": [(6, 0, [user_id])] if user_id else [(5, 0, 0)],
                    },
                    seed_hash=_sha256(
                        {
                            "type": "step",
                            "tpl": tpl["task_template_code"],
                            "step": step,
                            "deadline": deadline.isoformat(),
                        }
                    ),
                    dry_run=dry_run,
                    report=report,
                )

        # Mark obsolete tasks
        self._mark_obsolete(
            run_rec=run_rec,
            cycle_key=cycle_key,
            expected_parent_keys=expected_parent_keys,
            expected_step_keys=expected_step_keys,
            dry_run=dry_run,
            report=report,
        )

        # Determine final status
        status = "pass"
        if report["errors"]:
            status = "fail"
        elif report["warnings"] or report["unresolved_assignees"]:
            status = "warn"

        # Update run record
        run_rec.write(
            {
                "status": status,
                "report_json": report,
                "created_count": report["counts"]["created"],
                "updated_count": report["counts"]["updated"],
                "unchanged_count": report["counts"]["unchanged"],
                "obsolete_marked_count": report["counts"]["obsolete_marked"],
                "unresolved_assignee_count": len(report["unresolved_assignees"]),
            }
        )

        _logger.info(
            "Generation run completed: cycle_key=%s, status=%s, "
            "created=%d, updated=%d, unchanged=%d",
            cycle_key,
            status,
            report["counts"]["created"],
            report["counts"]["updated"],
            report["counts"]["unchanged"],
        )

        return report

    @api.model
    def run_from_config(
        self,
        cycle_code: str,
        cycle_key: str | None = None,
        dry_run: bool = False,
    ) -> dict:
        """
        Run generator using seed JSON stored in ir.config_parameter.

        Args:
            cycle_code: Cycle to generate
            cycle_key: Optional specific instance
            dry_run: If True, report without persisting

        Returns:
            dict: Generation report
        """
        seed_json = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.close.seed_json", "{}")
        )

        try:
            seed = json.loads(seed_json)
        except json.JSONDecodeError as e:
            raise UserError(f"Invalid JSON in ir.config_parameter: {e}")

        if not seed:
            raise UserError(
                "No seed JSON found. Set ir.config_parameter 'ipai.close.seed_json'."
            )

        return self.run(seed, cycle_code, cycle_key, dry_run)

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @api.model
    def _validate_seed(self, seed: dict):
        """Validate seed JSON structure."""
        required = ["schema_version", "seed_id", "timezone", "directory", "cycles"]
        for k in required:
            if k not in seed:
                raise UserError(f"Seed missing required key: {k}")

        if seed["directory"].get("identifier") != "employee_code":
            raise UserError("directory.identifier must be 'employee_code'")

        if not isinstance(seed.get("cycles"), list) or not seed["cycles"]:
            raise UserError("cycles must be a non-empty list")

    # =========================================================================
    # HELPERS
    # =========================================================================

    @api.model
    def _find_cycle(self, seed: dict, cycle_code: str) -> dict | None:
        """Find cycle configuration by code."""
        for c in seed.get("cycles", []):
            if c.get("cycle_code") == cycle_code:
                return c
        # Also check tax_cycles
        for c in seed.get("tax_cycles", []):
            if c.get("cycle_code") == cycle_code:
                return c
        return None

    @api.model
    def _ensure_project(self, cycle: dict):
        """Get or create project for the cycle."""
        Project = self.env["project.project"].sudo()
        proj = Project.search(
            [("x_cycle_code", "=", cycle["cycle_code"])], limit=1
        )
        if proj:
            return proj
        return Project.create(
            {
                "name": cycle.get("name", cycle["cycle_code"]),
                "x_cycle_code": cycle["cycle_code"],
            }
        )

    @api.model
    def _flatten_templates(self, cycle: dict) -> list[dict]:
        """Flatten hierarchical templates to a flat list."""
        out = []
        for ph in cycle.get("phases", []):
            for ws in ph.get("workstreams", []):
                for tpl in ws.get("task_templates", []):
                    steps = tpl.get("steps") or []
                    if not steps:
                        raise UserError(
                            f"Template {tpl.get('task_template_code')} has no steps"
                        )
                    out.append(
                        {
                            "phase_code": ph.get("phase_code"),
                            "workstream_code": ws.get("workstream_code"),
                            "task_template_code": tpl["task_template_code"],
                            "name": tpl["name"],
                            "steps": steps,
                        }
                    )
        return out

    @api.model
    def _instance_override_map(self, cycle: dict, cycle_key: str) -> dict:
        """
        Build map of date overrides for a specific instance.

        Returns:
            dict: {tpl_code: {step_code: date}}
        """
        for inst in cycle.get("instance_overrides", []):
            if inst.get("instance_key") == cycle_key:
                dates = inst.get("dates", {})
                m = {}
                for tpl_code, step_dates in dates.items():
                    m[tpl_code] = {k: _parse_iso(v) for k, v in step_dates.items()}
                return m
        return {}

    @api.model
    def _resolve_deadline(
        self,
        override_map: dict,
        tpl_code: str,
        step_code: str,
        seed: dict,
        cycle_key: str,
    ) -> date | None:
        """
        Resolve deadline for a step.

        Priority:
        1. Hard override from instance_overrides
        2. Computed from business day policy (if implemented)
        """
        # Check for hard override first
        if override_map.get(tpl_code, {}).get(step_code):
            return override_map[tpl_code][step_code]

        # Fall back to computing from cycle_key month
        # Extract month from cycle_key (format: CYCLE_CODE|YYYY-MM)
        try:
            parts = cycle_key.split("|")
            if len(parts) >= 2:
                year_month = parts[-1]
                year, month = map(int, year_month.split("-"))
                # Default to last day of month for approval, earlier for others
                if step_code == "APPROVAL":
                    # Last business day of month
                    return self._get_last_business_day(year, month)
                elif step_code == "REVIEW":
                    # 1 day before last business day
                    last_bd = self._get_last_business_day(year, month)
                    return self._subtract_business_days(last_bd, 1)
                else:  # PREP and others
                    # 2 days before last business day
                    last_bd = self._get_last_business_day(year, month)
                    return self._subtract_business_days(last_bd, 2)
        except (ValueError, IndexError):
            pass

        return None

    @api.model
    def _get_today_in_timezone(self, tz_name: str) -> date:
        """
        Get today's date in the specified timezone.

        Args:
            tz_name: Timezone name (e.g., 'Asia/Manila')

        Returns:
            date: Today's date in the specified timezone
        """
        if HAS_PYTZ:
            try:
                tz = pytz.timezone(tz_name)
                return datetime.now(tz).date()
            except pytz.UnknownTimeZoneError:
                _logger.warning(
                    "Unknown timezone '%s', falling back to UTC", tz_name
                )
                return datetime.utcnow().date()
        else:
            _logger.warning(
                "pytz not installed, timezone '%s' ignored. Using UTC.", tz_name
            )
            return datetime.utcnow().date()

    @api.model
    def _get_last_business_day(self, year: int, month: int) -> date:
        """Get last business day of a month."""
        # Get first day of next month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        # Last day of target month
        last_day = next_month - timedelta(days=1)

        # Find last business day
        while last_day.weekday() >= 5:  # Saturday=5, Sunday=6
            last_day -= timedelta(days=1)

        return last_day

    @api.model
    def _subtract_business_days(self, start_date: date, num_days: int) -> date:
        """Subtract N business days from a date."""
        current = start_date
        days_subtracted = 0

        while days_subtracted < num_days:
            current -= timedelta(days=1)
            if current.weekday() < 5:  # Mon-Fri
                days_subtracted += 1

        return current

    @api.model
    def _resolve_user_id(
        self,
        employee_code: str | None,
        use_fallback: bool = True,
    ) -> tuple[int | None, bool]:
        """
        Resolve employee code to user ID with optional fallback.

        Args:
            employee_code: The employee code to resolve (e.g., 'CKVC')
            use_fallback: If True, return SUPERUSER_ID when code not found

        Returns:
            tuple: (user_id, used_fallback)
                - user_id: The resolved user ID or None
                - used_fallback: True if fallback was used
        """
        if not employee_code:
            return (None, False)

        user = (
            self.env["res.users"]
            .sudo()
            .search([("x_employee_code", "=", employee_code)], limit=1)
        )

        if user:
            return (user.id, False)

        # Employee code not found
        if use_fallback:
            _logger.warning(
                "Employee code '%s' not found, using fallback (SUPERUSER_ID)",
                employee_code,
            )
            return (SUPERUSER_ID, True)

        return (None, False)

    @api.model
    def _upsert_task(
        self,
        run_rec,
        project,
        external_key: str,
        name: str,
        values: dict,
        seed_hash: str,
        dry_run: bool,
        report: dict,
    ):
        """
        Create or update a task based on external key.

        Implements idempotent upsert:
        - If external_key exists and seed_hash unchanged: no-op
        - If external_key exists and seed_hash changed: update
        - If external_key doesn't exist: create
        """
        Map = self.env["ipai.close.generated.map"].sudo()
        Task = self.env["project.task"].sudo()

        existing_map = Map.search([("external_key", "=", external_key)], limit=1)

        if existing_map:
            task = existing_map.task_id
            if existing_map.seed_hash == seed_hash:
                # No change needed
                report["counts"]["unchanged"] += 1
                return task

            # Update existing task
            if not dry_run:
                task.write(
                    {
                        "name": name,
                        **values,
                        "project_id": project.id,
                        "x_external_key": external_key,
                        "x_seed_hash": seed_hash,
                    }
                )
                existing_map.write({"seed_hash": seed_hash, "run_id": run_rec.id})

            report["counts"]["updated"] += 1
            return task

        # Create new task
        if dry_run:
            report["counts"]["created"] += 1
            return None

        task = Task.create(
            {
                "name": name,
                "project_id": project.id,
                "x_external_key": external_key,
                "x_seed_hash": seed_hash,
                **values,
            }
        )
        Map.create(
            {
                "external_key": external_key,
                "task_id": task.id,
                "run_id": run_rec.id,
                "seed_hash": seed_hash,
            }
        )
        report["counts"]["created"] += 1
        return task

    @api.model
    def _mark_obsolete(
        self,
        run_rec,
        cycle_key: str,
        expected_parent_keys: set,
        expected_step_keys: set,
        dry_run: bool,
        report: dict,
    ):
        """Mark tasks as obsolete if no longer in seed."""
        Map = self.env["ipai.close.generated.map"].sudo()
        maps = Map.search([("external_key", "like", f"{cycle_key}|%")])

        expected_all = expected_parent_keys | expected_step_keys
        obsolete = [m for m in maps if m.external_key not in expected_all]

        for m in obsolete:
            if not dry_run:
                m.task_id.write({"x_obsolete": True})
                m.write({"run_id": run_rec.id})
            report["counts"]["obsolete_marked"] += 1
