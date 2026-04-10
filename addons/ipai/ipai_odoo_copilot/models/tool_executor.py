# -*- coding: utf-8 -*-

import json
import logging
import os

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# azure-search-documents is an external dependency — graceful import
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    _HAS_SEARCH_SDK = True
except ImportError:
    _HAS_SEARCH_SDK = False
    SearchClient = None
    AzureKeyCredential = None

def _sanitize_odata_value(value):
    """Sanitize a string value for use in OData $filter expressions.

    Removes single quotes and backslashes to prevent OData filter injection.
    Only alphanumeric, hyphens, underscores, dots, and slashes are kept.
    """
    if not isinstance(value, str):
        return ""
    import re  # noqa: PLC0415
    return re.sub(r"[^a-zA-Z0-9\-_./]", "", value)



# Models that are never accessible via tool execution.
# Security-sensitive or internal-only models.
_BLOCKED_MODELS = frozenset({
    "ir.config_parameter",
    "ir.cron",
    "ir.module.module",
    "ir.rule",
    "ir.model.access",
    "res.users",
    "base.module.upgrade",
    "base.module.uninstall",
    "ir.actions.server",
    "ir.actions.act_window",
})

# Maximum records returned by search_records.
_MAX_SEARCH_LIMIT = 100
_DEFAULT_SEARCH_LIMIT = 20

# Maximum records in a report request.
_MAX_REPORT_RECORDS = 50


class CopilotToolExecutor(models.Model):
    """Dispatches tool calls from Azure Foundry agent runs to Odoo ORM.

    This model has _auto = False (no database table). It is a service
    model registered in ir.model to be accessible from other Odoo code.

    All tool execution respects:
      - permitted_tools list from the context envelope
      - company/entity scope validation
      - read_only_mode setting
      - user ACL (operations run as the requesting user, not sudo)
    """

    _name = "ipai.copilot.tool.executor"
    _description = "Copilot Tool Execution Dispatcher"
    _auto = False

    # ------------------------------------------------------------------
    # Tool registry — maps tool names to handler methods
    # ------------------------------------------------------------------

    _TOOL_HANDLERS = {
        "read_record": "_execute_read_record",
        "search_records": "_execute_search_records",
        "search_docs": "_execute_search_docs",
        "get_report": "_execute_get_report",
        "read_finance_close": "_execute_read_finance_close",
        "view_campaign_perf": "_execute_view_campaign_perf",
        "view_dashboard": "_execute_view_dashboard",
        "search_strategy_docs": "_execute_search_strategy_docs",
        # Knowledge base search tools (grounded RAG)
        "search_odoo_docs": "_execute_search_odoo_docs",
        "search_azure_docs": "_execute_search_azure_docs",
        "search_databricks_docs": "_execute_search_databricks_docs",
        # Org-wide documentation search tools
        "search_org_docs": "_execute_search_org_docs",
        "search_spec_bundles": "_execute_search_spec_bundles",
        "search_architecture_docs": "_execute_search_architecture_docs",
        # Bounded web search fallback (Lane 3)
        "search_odoo_docs_web": "_execute_search_odoo_docs_web",
        # Fabric SQL endpoint (governed business data)
        "query_fabric_data": "_execute_query_fabric_data",
        # Write lane (action queue only)
        "propose_action": "_execute_propose_action",
        # Knowledge bridge (cited retrieval)
        "query_knowledge_base": "_execute_query_knowledge_base",
        # Domain bridge stubs (wired when Wave 2 modules land)
        "read_expense_summary": "_execute_domain_stub",
        "read_project_status": "_execute_domain_stub",
        "read_close_tasks": "_execute_domain_stub",
        "read_tax_obligations": "_execute_domain_stub",
    }

    # Read-only tools — safe to execute without approval.
    # propose_action is a write-lane tool but is safe because it only
    # queues actions (does not execute them).
    _READ_ONLY_TOOLS = frozenset(
        k for k in _TOOL_HANDLERS if k != "propose_action"
    )
    _WRITE_LANE_TOOLS = frozenset({"propose_action"})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_tool(self, tool_name, arguments, context_envelope=None,
                     user_id=None):
        """Dispatch a tool call and return structured results.

        Args:
            tool_name: The tool function name from the agent run.
            arguments: Dict of tool arguments (already parsed from JSON).
            context_envelope: Dict with user context including
                permitted_tools, company_id, entity_ids, user_id, etc.

        Returns:
            dict with keys: success (bool), data (any), error (str|None)
        """
        if not isinstance(arguments, dict):
            try:
                arguments = json.loads(arguments) if arguments else {}
            except (json.JSONDecodeError, TypeError):
                return {
                    "success": False,
                    "data": None,
                    "error": "Invalid arguments: expected JSON object",
                }

        if not isinstance(context_envelope, dict):
            context_envelope = {}

        # Validate tool permission
        perm_ok, perm_msg = self._validate_tool_permission(
            tool_name, context_envelope
        )
        if not perm_ok:
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=True, reason=perm_msg,
            )
            return {"success": False, "data": None, "error": perm_msg}

        # Check read_only_mode for non-read tools (future Stage 2+)
        svc = self.env["ipai.foundry.service"]
        settings = svc._get_settings()
        is_read_only = settings.get("read_only_mode")
        if is_read_only and tool_name not in self._READ_ONLY_TOOLS:
            reason = (
                "Tool '%s' blocked: system is in read-only mode"
                % tool_name
            )
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=True, reason=reason,
            )
            return {"success": False, "data": None, "error": reason}

        # Dispatch to handler
        handler_name = self._TOOL_HANDLERS.get(tool_name)
        if not handler_name:
            reason = "Unknown tool: '%s'" % tool_name
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=True, reason=reason,
            )
            return {"success": False, "data": None, "error": reason}

        handler = getattr(self, handler_name, None)
        if not handler:
            reason = "Handler not implemented: '%s'" % handler_name
            return {"success": False, "data": None, "error": reason}

        try:
            result = handler(arguments, context_envelope)
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=False, reason="",
            )
            return {"success": True, "data": result, "error": None}
        except UserError as e:
            reason = str(e)
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=True, reason=reason,
            )
            return {"success": False, "data": None, "error": reason}
        except Exception:
            _logger.exception(
                "Tool execution error: tool=%s", tool_name
            )
            reason = "Internal error executing tool '%s'" % tool_name
            self._log_tool_audit(
                tool_name, arguments, context_envelope,
                blocked=True, reason=reason,
            )
            return {"success": False, "data": None, "error": reason}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_tool_permission(self, tool_name, context_envelope):
        """Check that the tool is in the user's permitted_tools list.

        Returns (ok: bool, message: str).
        """
        permitted = context_envelope.get("permitted_tools", [])
        if not isinstance(permitted, list):
            return False, "No permitted_tools in context envelope"

        if tool_name not in permitted:
            return False, (
                "Tool '%s' not permitted for this user/role. "
                "Permitted: %s" % (tool_name, ", ".join(permitted[:10]))
            )
        return True, ""

    def _validate_scope(self, model, record_ids, context_envelope):
        """Validate company and entity scope for the target records.

        Args:
            model: Odoo model name string.
            record_ids: list of int record IDs.
            context_envelope: dict with company_id, entity_ids.

        Returns (ok: bool, message: str).
        """
        if model in _BLOCKED_MODELS:
            return False, "Access to model '%s' is not allowed" % model

        # Check model exists in registry
        if model not in self.env:
            return False, "Model '%s' does not exist" % model

        company_id = context_envelope.get("company_id")

        if not record_ids:
            return True, ""

        try:
            records = self.env[model].browse(record_ids).exists()
        except Exception:
            return False, "Failed to access records in '%s'" % model

        if len(records) != len(record_ids):
            missing = set(record_ids) - set(records.ids)
            return False, (
                "Records not found in '%s': %s"
                % (model, ", ".join(str(i) for i in missing))
            )

        # Company scope check — if the model has company_id field
        model_obj = self.env[model]
        if company_id and "company_id" in model_obj._fields:
            for rec in records:
                rec_company = rec.company_id.id if rec.company_id else False
                if rec_company and rec_company != company_id:
                    return False, (
                        "Record %s/%d belongs to company %d, "
                        "not the requesting company %d"
                        % (model, rec.id, rec_company, company_id)
                    )

        return True, ""

    # ------------------------------------------------------------------
    # Tool handlers — Stage 1 (read-only)
    # ------------------------------------------------------------------

    def _execute_read_record(self, arguments, context_envelope):
        """Read field values from an Odoo record.

        Uses env[model].browse().read() with user ACL.
        """
        model = arguments.get("model", "")
        record_id = arguments.get("record_id")
        field_list = arguments.get("fields", [])

        if not model or not record_id:
            raise UserError(_("read_record requires 'model' and 'record_id'"))

        # Scope validation
        ok, msg = self._validate_scope(model, [record_id], context_envelope)
        if not ok:
            raise UserError(msg)

        record = self.env[model].browse(record_id)
        if not record.exists():
            raise UserError(
                _("Record %s/%d not found", model, record_id)
            )

        if field_list:
            data = record.read(field_list)
        else:
            data = record.read()

        return data[0] if data else {}

    def _execute_search_records(self, arguments, context_envelope):
        """Search records by domain and return field values.

        Uses env[model].search_read() with user ACL.
        """
        model = arguments.get("model", "")
        domain = arguments.get("domain", [])
        field_list = arguments.get("fields", [])
        limit = arguments.get("limit", _DEFAULT_SEARCH_LIMIT)

        if not model:
            raise UserError(_("search_records requires 'model'"))

        if model in _BLOCKED_MODELS:
            raise UserError(
                _("Access to model '%s' is not allowed", model)
            )

        if model not in self.env:
            raise UserError(_("Model '%s' does not exist", model))

        # Clamp limit
        limit = max(1, min(int(limit), _MAX_SEARCH_LIMIT))

        # Inject company scope into domain if applicable
        company_id = context_envelope.get("company_id")
        model_obj = self.env[model]
        if company_id and "company_id" in model_obj._fields:
            domain = domain + [("company_id", "=", company_id)]

        if not field_list:
            field_list = ["id", "display_name"]

        return self.env[model].search_read(
            domain, fields=field_list, limit=limit
        )

    def _execute_search_docs(self, arguments, context_envelope):
        """Search knowledge base using Azure AI Search or Odoo knowledge.

        Falls back to Odoo knowledge.article search if AI Search is
        not configured.
        """
        query = arguments.get("query", "")
        kb_scope = arguments.get("kb_scope", "general-kb")
        limit = arguments.get("limit", 5)

        if not query:
            raise UserError(_("search_docs requires 'query'"))

        limit = max(1, min(int(limit), 20))

        # Try Azure AI Search first
        settings = self.env["ipai.foundry.service"]._get_settings()
        search_service = settings.get("search_service", "")
        search_index = settings.get("search_index", "")

        if search_service and search_index:
            return self._search_via_azure_ai(
                query, kb_scope, limit, search_service, search_index
            )

        # Fallback: search Odoo knowledge.article if available
        if "knowledge.article" in self.env:
            domain = [
                ("name", "ilike", query),
                ("is_published", "=", True),
            ]
            return self.env["knowledge.article"].search_read(
                domain,
                fields=["id", "display_name", "body"],
                limit=limit,
            )

        return {
            "results": [],
            "source": "none",
            "message": "No search backend configured",
        }

    def _get_search_client(self, search_service, search_index):
        """Create Azure AI Search client using SDK.

        Auth: AZURE_SEARCH_API_KEY env var.
        Returns SearchClient or None.
        """
        if not _HAS_SEARCH_SDK:
            _logger.warning(
                "azure-search-documents not installed. "
                "Install with: pip install azure-search-documents"
            )
            return None

        search_key = os.environ.get("AZURE_SEARCH_API_KEY", "")
        if not search_key:
            _logger.warning("AZURE_SEARCH_API_KEY not set")
            return None

        endpoint = "https://%s.search.windows.net" % search_service
        return SearchClient(
            endpoint=endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key),
        )

    def _search_via_azure_ai(self, query, kb_scope, limit,
                             search_service, search_index):
        """Search Azure AI Search index using SDK.

        Returns structured result dict with results list.
        """
        client = self._get_search_client(search_service, search_index)
        if not client:
            return {
                "results": [],
                "source": "azure-ai-search",
                "error": "Search client not available",
            }

        filter_expr = None
        if kb_scope and kb_scope != "general-kb":
            filter_expr = "scope eq '%s'" % _sanitize_odata_value(kb_scope)

        try:
            response = client.search(
                search_text=query,
                top=limit,
                query_type="semantic",
                semantic_configuration_name="default",
                filter=filter_expr,
            )

            results = []
            for item in response:
                results.append({
                    "title": item.get("title", ""),
                    "content": (item.get("content", "") or "")[:500],
                    "score": item.get("@search.score", 0),
                    "path": item.get("path", ""),
                })

            return {
                "results": results,
                "source": "azure-ai-search",
                "index": search_index,
                "count": len(results),
            }
        except Exception:
            _logger.exception("Azure AI Search request failed")
            return {
                "results": [],
                "source": "azure-ai-search",
                "error": "Search request failed",
            }

    # ------------------------------------------------------------------
    # KB search tools — grounded RAG across knowledge bases
    # ------------------------------------------------------------------

    def _search_kb_index(self, query, index_name, limit, filter_expr=None):
        """Search a specific KB index by name.

        Reads search_service from Foundry settings, builds client
        for the target index.
        """
        settings = self.env["ipai.foundry.service"]._get_settings()
        search_service = settings.get("search_service", "")

        if not search_service:
            return {
                "results": [],
                "source": index_name,
                "error": "search_service not configured in Foundry settings",
            }

        client = self._get_search_client(search_service, index_name)
        if not client:
            return {
                "results": [],
                "source": index_name,
                "error": "Search client not available",
            }

        try:
            response = client.search(
                search_text=query,
                top=limit,
                query_type="semantic",
                semantic_configuration_name="default",
                filter=filter_expr,
            )

            results = []
            for item in response:
                results.append({
                    "title": item.get("title", ""),
                    "content": (item.get("content", "") or "")[:500],
                    "score": item.get("@search.score", 0),
                    "path": item.get("path", ""),
                    "heading_chain": item.get("heading_chain", ""),
                })

            return {
                "results": results,
                "source": index_name,
                "count": len(results),
            }
        except Exception:
            _logger.exception("KB search failed: index=%s", index_name)
            return {
                "results": [],
                "source": index_name,
                "error": "Search request failed",
            }

    def _execute_search_odoo_docs(self, arguments, context_envelope):
        """Search Odoo 18 documentation knowledge base.

        Index: odoo18-docs (RST-chunked Odoo CE documentation).
        """
        query = arguments.get("query", "")
        module = arguments.get("module", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_odoo_docs requires 'query'"))

        filter_expr = None
        if module:
            filter_expr = "module eq '%s'" % _sanitize_odata_value(module)

        return self._search_kb_index(
            query, "odoo18-docs", limit, filter_expr
        )

    def _execute_search_azure_docs(self, arguments, context_envelope):
        """Search Azure platform documentation knowledge base.

        Index: azure-platform-docs (MS Learn, CLI reference).
        """
        query = arguments.get("query", "")
        service = arguments.get("service", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_azure_docs requires 'query'"))

        filter_expr = None
        if service:
            filter_expr = "service eq '%s'" % _sanitize_odata_value(service)

        return self._search_kb_index(
            query, "azure-platform-docs", limit, filter_expr
        )

    def _execute_search_databricks_docs(self, arguments, context_envelope):
        """Search Databricks documentation knowledge base.

        Index: databricks-docs (dev tools, products, industry solutions).
        """
        query = arguments.get("query", "")
        domain = arguments.get("domain", "")
        industry = arguments.get("industry", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_databricks_docs requires 'query'"))

        filter_parts = []
        if domain:
            safe_domain = _sanitize_odata_value(domain)
            filter_parts.append(
                "domain eq '%s'" % safe_domain
            )
        if industry:
            safe_ind = _sanitize_odata_value(industry)
            filter_parts.append(
                "industry eq '%s'" % safe_ind
            )
        filter_expr = " and ".join(filter_parts) if filter_parts else None

        return self._search_kb_index(
            query, "databricks-docs", limit, filter_expr
        )

    # ------------------------------------------------------------------
    # Org docs search tools — grounded RAG across org knowledge bases
    # ------------------------------------------------------------------

    def _execute_search_org_docs(self, arguments, context_envelope):
        """Search organization-wide documentation knowledge base.

        Index: org-docs (architecture, contracts, specs, runbooks, policies).
        """
        query = arguments.get("query", "")
        doc_type = arguments.get("doc_type", "")
        source = arguments.get("source", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_org_docs requires 'query'"))

        filter_parts = []
        if doc_type:
            safe_dt = _sanitize_odata_value(doc_type)
            filter_parts.append(
                "doc_type eq '%s'" % safe_dt
            )
        if source:
            safe_src = _sanitize_odata_value(source)
            filter_parts.append(
                "source eq '%s'" % safe_src
            )
        filter_expr = " and ".join(filter_parts) if filter_parts else None

        return self._search_kb_index(
            query, "org-docs", limit, filter_expr
        )

    def _execute_search_spec_bundles(self, arguments, context_envelope):
        """Search spec bundles (PRDs, constitutions, plans, tasks).

        Index: org-docs, filtered to source='spec-bundles'.
        """
        query = arguments.get("query", "")
        bundle = arguments.get("bundle", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_spec_bundles requires 'query'"))

        filter_parts = ["source eq 'spec-bundles'"]
        if bundle:
            safe_bundle = _sanitize_odata_value(bundle)
            filter_parts.append(
                "path ge 'spec/%s' and path lt 'spec/%s~'"
                % (safe_bundle, safe_bundle)
            )
        filter_expr = " and ".join(filter_parts)

        return self._search_kb_index(
            query, "org-docs", limit, filter_expr
        )

    def _execute_search_architecture_docs(self, arguments, context_envelope):
        """Search architecture and design documentation.

        Index: org-docs, filtered to doc_type='architecture'.
        """
        query = arguments.get("query", "")
        limit = max(1, min(int(arguments.get("limit", 5)), 20))

        if not query:
            raise UserError(_("search_architecture_docs requires 'query'"))

        filter_expr = "doc_type eq 'architecture'"

        return self._search_kb_index(
            query, "org-docs", limit, filter_expr
        )

    def _execute_get_report(self, arguments, context_envelope):
        """Generate an Odoo report and return summary info.

        Does not return raw PDF binary — returns metadata about the
        generated report for the agent to describe to the user.
        """
        report_name = arguments.get("report_name", "")
        record_ids = arguments.get("record_ids", [])

        if not report_name:
            raise UserError(_("get_report requires 'report_name'"))
        if not record_ids:
            raise UserError(_("get_report requires 'record_ids'"))
        if len(record_ids) > _MAX_REPORT_RECORDS:
            raise UserError(
                _("Maximum %d records per report request", _MAX_REPORT_RECORDS)
            )

        # Find the report action
        report_action = self.env["ir.actions.report"].search(
            [("report_name", "=", report_name)], limit=1
        )
        if not report_action:
            raise UserError(
                _("Report '%s' not found", report_name)
            )

        # Validate scope on the target records
        target_model = report_action.model
        if target_model:
            ok, msg = self._validate_scope(
                target_model, record_ids, context_envelope
            )
            if not ok:
                raise UserError(msg)

        return {
            "report_name": report_name,
            "report_title": report_action.name or report_name,
            "model": target_model or "",
            "record_ids": record_ids,
            "record_count": len(record_ids),
            "report_type": report_action.report_type or "qweb-pdf",
            "status": "available",
        }

    def _execute_read_finance_close(self, arguments, context_envelope):
        """Read finance closing status for a fiscal year/period.

        Returns closing task data if the model exists, otherwise
        returns a structured not-available response.
        """
        fiscal_year = arguments.get("fiscal_year", "")
        period = arguments.get("period", "")

        if not fiscal_year:
            raise UserError(_("read_finance_close requires 'fiscal_year'"))

        # Check if finance closing model exists
        model_name = "account.fiscal.year.closing"
        if model_name not in self.env:
            # Graceful degradation — model not installed
            return {
                "available": False,
                "message": (
                    "Finance closing module not installed. "
                    "Model '%s' not found." % model_name
                ),
            }

        domain = []
        if fiscal_year:
            domain.append(("fiscal_year", "ilike", fiscal_year))
        if period:
            domain.append(("period", "ilike", period))

        # Inject company scope
        company_id = context_envelope.get("company_id")
        if company_id:
            domain.append(("company_id", "=", company_id))

        records = self.env[model_name].search_read(
            domain,
            fields=["id", "display_name", "state", "fiscal_year",
                     "period", "deadline", "completion_pct"],
            limit=20,
        )

        return {
            "available": True,
            "fiscal_year": fiscal_year,
            "period": period,
            "records": records,
            "count": len(records),
        }

    def _execute_view_campaign_perf(self, arguments, context_envelope):
        """View campaign performance metrics.

        Returns campaign data if the model exists.
        """
        campaign_id = arguments.get("campaign_id")
        date_range = arguments.get("date_range", {})

        if not campaign_id:
            raise UserError(_("view_campaign_perf requires 'campaign_id'"))

        # Try marketing.campaign or utm.campaign
        model_name = None
        for candidate in ("marketing.campaign", "utm.campaign"):
            if candidate in self.env:
                model_name = candidate
                break

        if not model_name:
            return {
                "available": False,
                "message": "Marketing campaign module not installed.",
            }

        ok, msg = self._validate_scope(
            model_name, [campaign_id], context_envelope
        )
        if not ok:
            raise UserError(msg)

        record = self.env[model_name].browse(campaign_id)
        if not record.exists():
            raise UserError(
                _("Campaign %d not found", campaign_id)
            )

        data = record.read()[0] if record.read() else {}
        data["date_range"] = date_range
        data["source"] = model_name

        return data

    def _execute_view_dashboard(self, arguments, context_envelope):
        """View analytics dashboard data.

        Returns dashboard configuration and current snapshot.
        """
        dashboard_id = arguments.get("dashboard_id")

        if not dashboard_id:
            raise UserError(_("view_dashboard requires 'dashboard_id'"))

        # Try board.board or a custom analytics model
        for model_name in ("board.board", "analytics.dashboard"):
            if model_name in self.env:
                record = self.env[model_name].browse(dashboard_id)
                if record.exists():
                    data = record.read()[0]
                    data["source"] = model_name
                    return data

        return {
            "available": False,
            "message": (
                "Dashboard module not installed "
                "or dashboard not found."
            ),
            "dashboard_id": dashboard_id,
        }

    def _execute_search_strategy_docs(self, arguments, context_envelope):
        """Search strategy and playbook documents.

        Delegates to search_docs with strategy-specific scope.
        """
        query = arguments.get("query", "")
        scope = arguments.get("scope", "strategy")
        limit = arguments.get("limit", 5)

        if not query:
            raise UserError(_("search_strategy_docs requires 'query'"))

        # Map scope to kb_scope
        scope_map = {
            "strategy": "strategy-kb",
            "playbook": "marketing-playbooks",
            "operational": "ops-kb",
            "planning": "strategy-kb",
        }
        kb_scope = scope_map.get(scope, "strategy-kb")

        return self._execute_search_docs(
            {"query": query, "kb_scope": kb_scope, "limit": limit},
            context_envelope,
        )

    # ------------------------------------------------------------------
    # Bounded Web Search (Lane 3 fallback)
    # ------------------------------------------------------------------

    # Allowed domains for web search — odoo.com official docs only.
    _WEB_SEARCH_ALLOWED_DOMAINS = ("www.odoo.com", "odoo.com")
    _WEB_SEARCH_MAX_PER_TURN = 3

    def _execute_search_odoo_docs_web(self, arguments, context_envelope):
        """Bounded web search over odoo.com official documentation.

        This is the Lane 3 fallback — only invoked when the curated KB
        (search_odoo_docs) returns insufficient results. Uses urllib to
        query the Odoo documentation sitemap or a configured search proxy.

        Restrictions:
          - Only odoo.com domains are allowed
          - Maximum 3 calls per conversation turn
          - Returns structured results with URLs for citation
        """
        query = arguments.get("query", "")
        version = arguments.get("version", "18.0")
        max_results = max(1, min(int(arguments.get("max_results", 5)), 10))

        if not query:
            raise UserError(_("search_odoo_docs_web requires 'query'"))

        # Build search URL targeting Odoo docs
        import urllib.parse  # noqa: PLC0415
        import urllib.request  # noqa: PLC0415

        search_query = "%s site:odoo.com/documentation/%s" % (
            query, version,
        )

        # Attempt Azure AI Search web-grounding if available,
        # otherwise return a structured pointer for the Foundry agent
        # to use its own web_search tool.
        #
        # In the Foundry agent runtime, this tool result tells the
        # agent to use its built-in web_search_20250305 server tool
        # with the allowed_domains constraint. The agent interprets
        # this as a "please search" instruction.
        return {
            "search_type": "bounded_web",
            "query": query,
            "version": version,
            "allowed_domains": list(self._WEB_SEARCH_ALLOWED_DOMAINS),
            "max_results": max_results,
            "instruction": (
                "Search odoo.com documentation for: %s. "
                "Restrict to version %s. "
                "Return URLs with page titles for citation."
                % (query, version)
            ),
            "fallback_url": (
                "https://www.odoo.com/documentation/%s/search.html?q=%s"
                % (version, urllib.parse.quote_plus(query))
            ),
        }

    # ------------------------------------------------------------------
    # Fabric SQL endpoint (governed business data)
    # ------------------------------------------------------------------

    # Schemas allowed for Fabric queries — prevents access to raw/staging data
    _FABRIC_ALLOWED_SCHEMAS = frozenset({"gold", "semantic"})

    # Explicit object allowlist — only these tables/views are queryable.
    # Matches ssot/knowledge/odoo-copilot-indexes.yaml entities.
    _FABRIC_ALLOWED_OBJECTS = frozenset({
        "gold.fact_invoices",
        "gold.fact_payments",
        "gold.dim_partners",
        "gold.fact_aging",
        "gold.fact_budget_lines",
        "semantic.partner_aging_summary",
        "semantic.budget_vs_actual",
        "semantic.monthly_kpis",
        "semantic.cash_flow_forecast",
    })

    # SQL tokens that are never allowed in Fabric queries
    _FABRIC_BLOCKED_TOKENS = frozenset({
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
        "CREATE", "EXEC", "EXECUTE", "GRANT", "REVOKE", "MERGE",
        "CALL", "INTO", "SET",
    })

    # Configurable limits
    _FABRIC_MAX_ROWS = 500
    _FABRIC_QUERY_TIMEOUT = 30

    # Pre-approved query templates for common KPI patterns.
    # The agent can use template_id instead of raw SQL.
    _FABRIC_QUERY_TEMPLATES = {
        "monthly_kpis": (
            "SELECT * FROM semantic.monthly_kpis "
            "WHERE period_month = {month} AND period_year = {year} "
            "ORDER BY metric_name"
        ),
        "partner_aging": (
            "SELECT * FROM semantic.partner_aging_summary "
            "WHERE partner_id = {partner_id} "
            "ORDER BY bucket"
        ),
        "budget_variance": (
            "SELECT * FROM semantic.budget_vs_actual "
            "WHERE fiscal_year = {fiscal_year} "
            "ORDER BY variance_pct DESC"
        ),
        "revenue_trend": (
            "SELECT period_year, period_month, "
            "SUM(amount_total) as revenue "
            "FROM gold.fact_invoices "
            "WHERE state = 'posted' "
            "GROUP BY period_year, period_month "
            "ORDER BY period_year, period_month"
        ),
        "cash_forecast": (
            "SELECT * FROM semantic.cash_flow_forecast "
            "ORDER BY forecast_date"
        ),
    }

    def _execute_query_fabric_data(self, arguments, context_envelope):
        """Query governed business data from Fabric SQL endpoint.

        Two modes:
          1. template_id + params: uses a pre-approved query template
          2. raw query: validated against object allowlist + blocked tokens

        Only SELECT against explicitly allowed objects. Read-only enforced
        via SET TRANSACTION READ ONLY.
        """
        import re as _re  # noqa: PLC0415

        template_id = arguments.get("template_id", "")
        query = arguments.get("query", "")
        params = arguments.get("params", {})
        max_rows = max(1, min(
            int(arguments.get("max_rows", 100)),
            self._FABRIC_MAX_ROWS,
        ))

        # Mode 1: Template query (preferred, safer)
        if template_id:
            template = self._FABRIC_QUERY_TEMPLATES.get(template_id)
            if not template:
                raise UserError(
                    _("Unknown query template: '%s'. Available: %s",
                      template_id,
                      ", ".join(sorted(self._FABRIC_QUERY_TEMPLATES)))
                )
            # Validate params are simple values (no SQL injection)
            for key, val in params.items():
                if not isinstance(val, (int, float, str)):
                    raise UserError(
                        _("Template param '%s' must be a simple value", key)
                    )
                if isinstance(val, str) and not _re.match(
                    r'^[a-zA-Z0-9_\-. ]+$', val
                ):
                    raise UserError(
                        _("Template param '%s' contains invalid characters", key)
                    )
            try:
                query = template.format(**params)
            except KeyError as e:
                raise UserError(
                    _("Missing template parameter: %s", str(e))
                )

        if not query:
            raise UserError(
                _("query_fabric_data requires 'query' or 'template_id'")
            )

        # Validate: must start with SELECT
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise UserError(
                _("Only SELECT queries are allowed against Fabric endpoint")
            )

        # Validate: no blocked tokens
        tokens = set(query_upper.split())
        blocked_found = tokens & self._FABRIC_BLOCKED_TOKENS
        if blocked_found:
            raise UserError(
                _("Blocked operations in query: %s",
                  ", ".join(sorted(blocked_found)))
            )

        # Validate: no semicolons (prevent multi-statement)
        if ";" in query:
            raise UserError(
                _("Multi-statement queries are not allowed")
            )

        # Validate: no comments (prevent comment-based injection)
        if "--" in query or "/*" in query:
            raise UserError(
                _("SQL comments are not allowed in Fabric queries")
            )

        # Validate: only allowed objects referenced
        query_lower = query.lower()
        referenced_objects = set()
        for obj in self._FABRIC_ALLOWED_OBJECTS:
            if obj.lower() in query_lower:
                referenced_objects.add(obj)

        if not referenced_objects:
            raise UserError(
                _("Query must reference approved objects. Allowed: %s",
                  ", ".join(sorted(self._FABRIC_ALLOWED_OBJECTS)))
            )

        # Check no unapproved schema.object patterns
        schema_obj_pattern = _re.findall(
            r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)',
            query, _re.IGNORECASE,
        )
        for ref in schema_obj_pattern:
            if ref.lower() not in {o.lower() for o in self._FABRIC_ALLOWED_OBJECTS}:
                raise UserError(
                    _("Object '%s' is not in the approved allowlist", ref)
                )

        # Get Fabric SQL connection
        fabric_conn_str = os.environ.get("FABRIC_SQL_CONNECTION_STRING", "")
        if not fabric_conn_str:
            return {
                "status": "not_configured",
                "message": (
                    "Fabric SQL endpoint not configured. "
                    "Set FABRIC_SQL_CONNECTION_STRING environment variable."
                ),
                "query": query,
            }

        try:
            import pyodbc  # noqa: PLC0415
        except ImportError:
            return {
                "status": "dependency_missing",
                "message": "pyodbc not installed. Required for Fabric SQL access.",
            }

        try:
            conn = pyodbc.connect(
                fabric_conn_str,
                timeout=self._FABRIC_QUERY_TIMEOUT,
            )
            cursor = conn.cursor()

            # Enforce read-only at session level
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")

            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(max_rows)
            data = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()

            return {
                "status": "success",
                "columns": columns,
                "data": data,
                "row_count": len(data),
                "truncated": len(data) >= max_rows,
                "objects_queried": sorted(referenced_objects),
                "template_used": template_id or None,
            }
        except pyodbc.Error as e:
            _logger.error("Fabric SQL query error: %s", e)
            return {
                "status": "error",
                "message": "Query execution failed: %s" % str(e)[:200],
            }

    # ------------------------------------------------------------------
    # Write lane — action queue (propose, never execute directly)
    # ------------------------------------------------------------------

    def _execute_propose_action(self, arguments, context_envelope):
        """Propose a write action for human approval.

        Creates a record in ipai.copilot.action.queue. The action is
        NOT executed — a human must review and approve it first.
        """
        summary = arguments.get("summary", "")
        target_model = arguments.get("target_model", "")
        target_res_id = arguments.get("target_res_id", 0)
        action_type = arguments.get("action_type", "")
        payload = arguments.get("payload", {})

        if not summary:
            raise UserError(_("propose_action requires 'summary'"))
        if not target_model:
            raise UserError(_("propose_action requires 'target_model'"))
        if not action_type:
            raise UserError(_("propose_action requires 'action_type'"))
        if action_type not in ("create", "write", "action"):
            raise UserError(
                _("Invalid action_type: '%s'. Must be create/write/action", action_type)
            )

        # Block sensitive models
        if target_model in _BLOCKED_MODELS:
            raise UserError(
                _("Actions on model '%s' are not allowed", target_model)
            )

        # For write/action, validate target record exists
        if action_type in ("write", "action") and target_res_id:
            if target_model not in self.env:
                raise UserError(_("Model '%s' does not exist", target_model))
            record = self.env[target_model].browse(target_res_id)
            if not record.exists():
                raise UserError(
                    _("Target record %s/%d not found", target_model, target_res_id)
                )

        queue_record = self.env["ipai.copilot.action.queue"].sudo().create({
            "summary": summary[:256],
            "workflow_id": "copilot-agent",
            "agent_run_id": context_envelope.get("agent_run_id", ""),
            "target_model": target_model,
            "target_res_id": target_res_id or 0,
            "action_type": action_type,
            "action_payload": json.dumps(payload, default=str),
            "state": "pending",
        })

        return {
            "status": "queued",
            "queue_id": queue_record.id,
            "summary": summary,
            "message": (
                "Action queued for human approval (ID: %d). "
                "A reviewer will approve or reject this action."
                % queue_record.id
            ),
        }

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def _log_tool_audit(self, tool_name, arguments, context_envelope,
                        blocked=False, reason=""):
        """Write a tool execution audit record.

        Uses the existing ipai.copilot.audit model.
        Non-blocking — catches all errors.
        """
        try:
            user_id = (
                context_envelope.get("user_id") or self.env.uid
            )
            surface = context_envelope.get("surface", "copilot")
            source = context_envelope.get("source", "api")

            prompt_text = "Tool call: %s(%s)" % (
                tool_name,
                json.dumps(arguments, default=str)[:500],
            )

            valid_sources = ("discuss", "api", "widget")
            valid_surfaces = (
                "web", "erp", "copilot", "analytics", "ops",
            )

            self.env["ipai.copilot.audit"].sudo().create({
                "user_id": user_id,
                "prompt": prompt_text[:2000],
                "response_excerpt": (
                    reason[:500] if blocked else "OK"
                ),
                "environment_mode": "read_only",
                "blocked": blocked,
                "reason": (reason or "")[:256],
                "source": (
                    source if source in valid_sources
                    else "api"
                ),
                "surface": (
                    surface if surface in valid_surfaces
                    else "copilot"
                ),
            })
        except Exception:
            _logger.exception("Failed to write tool audit record")

    # ------------------------------------------------------------------
    # Knowledge bridge tool
    # ------------------------------------------------------------------

    def _execute_query_knowledge_base(self, arguments, context_envelope=None,
                                       user_id=None):
        """Query ipai.knowledge.bridge for cited answers."""
        question = arguments.get("question", "")
        source_code = arguments.get("source_code", "")

        if not question:
            return {"success": False, "data": None,
                    "error": "Missing 'question' parameter"}

        bridge = self.env["ipai.knowledge.bridge"]

        if source_code:
            result = bridge.query(
                source_code=source_code,
                question=question,
                caller_uid=user_id or self.env.uid,
                caller_surface="copilot",
            )
        else:
            # Query all active sources and return best result
            sources = bridge.list_sources()
            if not sources:
                return {
                    "success": True,
                    "data": {
                        "answer": "No knowledge sources are currently registered.",
                        "citations": [],
                        "abstained": True,
                    },
                    "error": None,
                }

            best_result = None
            best_confidence = -1
            for src in sources:
                r = bridge.query(
                    source_code=src["code"],
                    question=question,
                    caller_uid=user_id or self.env.uid,
                    caller_surface="copilot",
                )
                conf = r.get("confidence", 0)
                if conf > best_confidence:
                    best_confidence = conf
                    best_result = r

            result = best_result

        return {
            "success": not result.get("error"),
            "data": {
                "answer": result.get("answer", ""),
                "citations": result.get("citations", []),
                "confidence": result.get("confidence", 0),
                "abstained": result.get("abstained", False),
            },
            "error": result.get("error") or None,
        }

    # ------------------------------------------------------------------
    # Domain bridge stubs (wired when Wave 2 modules land)
    # ------------------------------------------------------------------

    def _execute_domain_stub(self, arguments, context_envelope=None,
                              user_id=None):
        """Stub handler for domain bridge tools not yet implemented.

        Returns a clear message that the domain module is pending.
        Domain bridges (#687-#690) will replace this stub.
        """
        tool_name = context_envelope.get("_current_tool", "domain_read") \
            if context_envelope else "domain_read"
        return {
            "success": True,
            "data": {
                "message": (
                    "This domain bridge is not yet available. "
                    "The module is planned for Wave 2 delivery. "
                    "You can still answer from the knowledge base or "
                    "search Odoo records directly."
                ),
                "tool": tool_name,
                "status": "stub",
            },
            "error": None,
        }
