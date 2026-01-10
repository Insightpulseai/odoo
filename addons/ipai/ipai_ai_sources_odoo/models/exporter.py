# -*- coding: utf-8 -*-
"""
IPAI AI Sources - Odoo Exporter
===============================

Exports Odoo content to Supabase KB for RAG retrieval.

The exporter collects data from:
- project.task (with description, stage, project context)
- document.page (if OCA knowledge module is installed)

Data is pushed to Supabase KB via REST API upsert.
"""
import os
import json
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None
    _logger.warning("Python 'requests' package not available")


class IpaiKbExporter(models.AbstractModel):
    """
    Abstract model providing KB export functionality.

    This is implemented as an abstract model so it can be called
    from cron jobs without requiring a database table.
    """

    _name = "ipai.kb.exporter"
    _description = "IPAI KB Exporter"

    @api.model
    def cron_export_recent(self):
        """
        Export recently modified Odoo content to Supabase KB.

        This method is called by the scheduled cron job.
        It exports changes from the last IPAI_KB_EXPORT_LOOKBACK_HOURS hours.

        Returns:
            bool: True on success, raises UserError on failure
        """
        if not requests:
            raise UserError("Python 'requests' package required for KB export")

        # Get configuration
        supabase_url = os.environ.get("IPAI_SUPABASE_URL", "").rstrip("/")
        supabase_key = (
            os.environ.get("IPAI_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("IPAI_SUPABASE_ANON_KEY")
            or ""
        ).strip()

        if not supabase_url or not supabase_key:
            _logger.warning("Supabase not configured; skipping KB export")
            return True

        # Calculate lookback window
        lookback_hours = int(
            os.environ.get("IPAI_KB_EXPORT_LOOKBACK_HOURS", "24")
        )
        since = fields.Datetime.now() - timedelta(hours=lookback_hours)

        # Get tenant reference
        tenant_ref = f"odoo_company:{self.env.company.id}"

        # Collect data from sources
        chunks = []
        chunks.extend(self._collect_tasks(tenant_ref, since))
        chunks.extend(self._collect_kb_pages(tenant_ref, since))

        if not chunks:
            _logger.info("No new chunks to export")
            return True

        # Create export run record
        ExportRun = self.env["ipai.kb.export.run"].sudo()
        run = ExportRun.create({
            "company_id": self.env.company.id,
            "chunks_count": len(chunks),
            "state": "running",
        })

        # Push to Supabase
        try:
            self._upsert_chunks(supabase_url, supabase_key, chunks)
            run.write({
                "state": "success",
                "completed_at": fields.Datetime.now(),
            })
            _logger.info(
                "Exported %d chunks to Supabase KB for tenant %s",
                len(chunks),
                tenant_ref,
            )
        except Exception as e:
            run.write({
                "state": "failed",
                "error_message": str(e)[:2000],
                "completed_at": fields.Datetime.now(),
            })
            _logger.exception("KB export failed")
            raise UserError(f"KB export failed: {str(e)[:500]}")

        return True

    def _collect_tasks(self, tenant_ref, since):
        """
        Collect project tasks modified since the given date.

        Args:
            tenant_ref: Tenant identifier string
            since: Datetime to filter by write_date

        Returns:
            List of chunk dictionaries
        """
        Task = self.env["project.task"].sudo()
        tasks = Task.search([
            ("write_date", ">=", since),
            "|",
            ("company_id", "=", self.env.company.id),
            ("company_id", "=", False),
        ])

        chunks = []
        base_url = os.environ.get("IPAI_PUBLIC_BASE_URL", "").rstrip("/")

        for task in tasks:
            # Build content from task data
            content_parts = [
                f"Task: {task.name}",
            ]

            if task.project_id:
                content_parts.append(f"Project: {task.project_id.display_name}")

            if task.stage_id:
                content_parts.append(f"Stage: {task.stage_id.display_name}")

            if task.user_ids:
                assignees = ", ".join(task.user_ids.mapped("name"))
                content_parts.append(f"Assigned to: {assignees}")

            if task.description:
                # Strip HTML and limit length
                desc = self._strip_html(task.description)
                if desc:
                    content_parts.append(f"\nDescription:\n{desc[:2000]}")

            content = "\n".join(content_parts)

            # Build URL
            url = None
            if base_url:
                url = f"{base_url}/web#id={task.id}&model=project.task&view_type=form"

            chunks.append({
                "tenant_ref": tenant_ref,
                "source_type": "odoo_task",
                "source_ref": f"project.task:{task.id}",
                "title": task.name,
                "url": url,
                "content": content,
                "updated_at": fields.Datetime.now().isoformat(),
            })

        return chunks

    def _collect_kb_pages(self, tenant_ref, since):
        """
        Collect knowledge base pages modified since the given date.

        Only works if OCA document_page module is installed.

        Args:
            tenant_ref: Tenant identifier string
            since: Datetime to filter by write_date

        Returns:
            List of chunk dictionaries
        """
        if "document.page" not in self.env:
            return []

        Page = self.env["document.page"].sudo()
        pages = Page.search([
            ("write_date", ">=", since),
            "|",
            ("company_id", "=", self.env.company.id),
            ("company_id", "=", False),
        ])

        chunks = []
        base_url = os.environ.get("IPAI_PUBLIC_BASE_URL", "").rstrip("/")

        for page in pages:
            content = self._strip_html(page.content or "")
            if not content:
                continue

            url = None
            if base_url:
                url = f"{base_url}/web#id={page.id}&model=document.page&view_type=form"

            chunks.append({
                "tenant_ref": tenant_ref,
                "source_type": "odoo_kb",
                "source_ref": f"document.page:{page.id}",
                "title": page.display_name,
                "url": url,
                "content": content[:4000],
                "updated_at": fields.Datetime.now().isoformat(),
            })

        return chunks

    def _strip_html(self, html_content):
        """
        Strip HTML tags from content.

        Simple regex-based stripping for performance.
        """
        import re
        if not html_content:
            return ""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html_content)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _upsert_chunks(self, supabase_url, supabase_key, chunks):
        """
        Upsert chunks to Supabase KB.

        Uses Supabase REST API with upsert on conflict.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
            chunks: List of chunk dictionaries

        Raises:
            UserError: If upsert fails
        """
        # Supabase REST API endpoint for kb.chunks table
        # Using on_conflict for upsert behavior
        endpoint = f"{supabase_url}/rest/v1/kb.chunks"
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }

        # Add on_conflict parameter for upsert
        params = {
            "on_conflict": "tenant_ref,source_type,source_ref",
        }

        # Send in batches of 100
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            resp = requests.post(
                endpoint,
                headers=headers,
                params=params,
                data=json.dumps(batch),
                timeout=60,
            )

            if resp.status_code >= 300:
                raise UserError(
                    f"Supabase upsert failed ({resp.status_code}): "
                    f"{resp.text[:500]}"
                )

        return True
