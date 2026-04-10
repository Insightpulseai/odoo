# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging
import re

from odoo import api, models

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent classification rules (deterministic, no ML)
# ---------------------------------------------------------------------------
# Each rule: (skill_id, pattern_list, priority)
# First match with highest priority wins.
INTENT_RULES = [
    # Document extraction (highest priority when the user is clearly asking
    # to OCR or parse an uploaded file)
    ("document_extract", [
        r"extract", r"ocr", r"scan", r"digitize",
        r"read\s*(this|the)\s*(pdf|document|file|receipt|invoice)",
        r"what('s|\s*is)\s*in\s*(this|the)\s*(file|pdf|document)",
        r"parse\s*(this|the)",
    ], 95),

    # Knowledge base — cited retrieval from registered knowledge sources
    ("knowledge_qa", [
        r"knowledge\s*base", r"kb\s+", r"policy\s*(doc|manual|guide)",
        r"what\s*(does|is)\s*(the|our)\s*(policy|procedure|guideline)",
        r"sop\s+", r"company\s*(handbook|manual|policy)",
        r"check\s*(the|our)\s*(docs|documentation|knowledge)",
    ], 88),

    # Domain bridge — grounded reads across operational domains
    ("domain_read", [
        r"my\s*(expense|advance|reimbursement)", r"pending\s*expense",
        r"project\s*(status|health|budget)", r"portfolio\s*(health|score)",
        r"close\s*(task|checklist|status)", r"month.end\s*close",
        r"tax\s*(obligation|filing|return|deadline|calendar)",
        r"bir\s*(form|filing|deadline)",
    ], 86),

    # Finance-specific
    ("reconciliation_assist", [
        r"reconcil", r"bank\s*statement", r"match.*transaction",
        r"unreconciled",
    ], 90),
    ("collections_assist", [
        r"collect", r"overdue", r"aging", r"follow.?up",
        r"past\s*due", r"receivable",
    ], 90),
    ("variance_analysis", [
        r"variance", r"budget.*actual", r"p&l.*vs", r"deviation",
        r"cost\s*center.*diff",
    ], 90),
    ("finance_qa", [
        r"invoice", r"journal\s*entry", r"account\.move",
        r"payment", r"tax", r"fiscal", r"ledger",
        r"balance\s*sheet", r"profit.*loss", r"trial\s*balance",
    ], 80),

    # Odoo framework / development
    ("odoo_upgrade_advisor", [
        r"upgrade", r"migrat", r"port.*19", r"breaking\s*change",
        r"deprecat",
    ], 85),
    ("odoo_module_scaffolder", [
        r"scaffold", r"create.*module", r"new.*addon",
        r"generate.*model", r"manifest",
    ], 85),
    ("odoo_docs_explainer", [
        r"how\s*(does|do|to)", r"explain",
        r"what\s*is\s*(a|an|the)?\s*(model|field|view|action|module|mixin|widget|record|orm)",
        r"document", r"reference", r"api\s*(for|of)",
        r"odoo\s*(19|18|17)", r"owl", r"qweb",
    ], 70),

    # Data / analytics
    ("fabric_data_query", [
        r"kpi", r"dashboard", r"metric", r"gold.*layer",
        r"semantic", r"data\s*warehouse", r"fabric",
        r"revenue.*trend", r"monthly.*report",
    ], 75),

    # Write proposals — must beat read-oriented finance_qa (80)
    ("propose_write", [
        r"create\s*(a|an|new)", r"update\s*(the|this|record)",
        r"change\s*(the|this)", r"set\s*(the|this)",
        r"approve", r"confirm", r"cancel",
    ], 82),

    # General search / read
    ("search_docs", [
        r"search", r"find", r"look\s*up", r"where\s*is",
        r"spec", r"architecture",
    ], 50),
    ("record_reader", [
        r"show\s*(me|the)", r"read", r"get\s*(the|this)",
        r"display", r"view\s*(the|this|record)",
    ], 40),
]


class SkillRouter(models.AbstractModel):
    """Intent-based skill router for the Odoo copilot.

    Classifies user messages into skill packs using deterministic
    pattern matching. Each skill maps to a set of Foundry agent tools
    (defined in foundry_service.SKILL_TOOL_MAP).

    The router does NOT call the agent — it classifies intent so the
    agent's system prompt can be augmented with the right tool subset
    and instructions.
    """

    _name = "ipai.copilot.skill.router"
    _description = "Copilot Skill Router"

    @api.model
    def classify_intent(self, message, context_envelope=None):
        """Classify a user message into a skill ID.

        Args:
            message: User's chat message text.
            context_envelope: Optional dict with surface, record_model, etc.

        Returns:
            dict with:
              - skill_id: matched skill (or 'general' fallback)
              - confidence: 'high' | 'medium' | 'low'
              - context_boost: bool (True if context influenced routing)
        """
        if not message:
            return {"skill_id": "general", "confidence": "low",
                    "context_boost": False}

        text = message.lower().strip()
        context_boost = False

        # Context-based boost: if viewing a finance record, boost finance skills
        has_attachments = bool(
            context_envelope.get("attachment_ids") if context_envelope else False
        )
        if context_envelope:
            model = context_envelope.get("record_model", "")
            surface = context_envelope.get("surface", "")
            if model in (
                "account.move", "account.move.line",
                "account.bank.statement.line", "account.payment",
            ):
                context_boost = True
            if surface == "analytics":
                context_boost = True

        best_skill = None
        best_priority = -1

        for skill_id, patterns, priority in INTENT_RULES:
            # Context boost adds +20 priority for finance skills
            effective_priority = priority
            if context_boost and skill_id in (
                "finance_qa", "reconciliation_assist",
                "collections_assist", "variance_analysis",
                "domain_read",
            ):
                effective_priority += 20
            if has_attachments and skill_id == "document_extract":
                effective_priority += 20

            for pattern in patterns:
                if re.search(pattern, text):
                    if effective_priority > best_priority:
                        best_skill = skill_id
                        best_priority = effective_priority
                    break  # One match per skill is enough

        if best_skill:
            confidence = "high" if best_priority >= 85 else "medium"
            return {
                "skill_id": best_skill,
                "confidence": confidence,
                "context_boost": context_boost,
            }

        return {"skill_id": "general", "confidence": "low",
                "context_boost": context_boost}

    @api.model
    def get_skill_instructions(self, skill_id):
        """Get supplemental system prompt instructions for a skill.

        Returns a string to append to the base system prompt, guiding
        the agent to use the right tools for this skill.
        """
        instructions_map = {
            "knowledge_qa": (
                "The user is asking about company policies, procedures, or knowledge base content. "
                "Use query_knowledge_base to search the registered knowledge sources. "
                "Cite sources using [N] markers from the returned citations. "
                "If the knowledge base cannot answer, say so — do not guess."
            ),
            "domain_read": (
                "The user wants operational data from a specific domain. "
                "Use the appropriate domain tool: read_expense_summary for expenses/advances, "
                "read_project_status for projects/budgets, read_close_tasks for month-end close, "
                "read_tax_obligations for tax/BIR deadlines. "
                "Present data clearly with amounts and dates."
            ),
            "finance_qa": (
                "The user is asking about finance/accounting. "
                "Use read_record and search_records to look up Odoo accounting data. "
                "Use query_fabric_data for aggregated KPIs and trends. "
                "Cite record IDs and amounts precisely."
            ),
            "reconciliation_assist": (
                "The user needs help with bank reconciliation. "
                "Use search_records on account.bank.statement.line and account.move.line "
                "to find matches. Suggest reconciliation pairings with amounts."
            ),
            "collections_assist": (
                "The user needs collections/AR follow-up assistance. "
                "Search overdue invoices and partner aging. "
                "Draft follow-up communication suggestions."
            ),
            "variance_analysis": (
                "The user wants budget vs actual analysis. "
                "Use query_fabric_data for governed variance data. "
                "Present structured comparisons with percentages."
            ),
            "odoo_docs_explainer": (
                "The user wants to understand Odoo framework concepts. "
                "Use search_odoo_docs to find relevant documentation. "
                "Explain clearly with code examples when helpful."
            ),
            "odoo_module_scaffolder": (
                "The user wants to create or modify an Odoo module. "
                "Use search_odoo_docs for patterns and conventions. "
                "Follow ipai_* naming, Odoo 18 coding standards."
            ),
            "odoo_upgrade_advisor": (
                "The user needs help with Odoo version migration. "
                "Search docs for breaking changes and migration guides. "
                "Note: Odoo 18 uses groups_id (not group_ids), tree (not list)."
            ),
            "fabric_data_query": (
                "The user wants business analytics data. "
                "Use query_fabric_data with SQL against gold.* or semantic.* schemas. "
                "Present results as formatted tables."
            ),
            "propose_write": (
                "The user wants to modify data. NEVER write directly. "
                "Use propose_action to queue the change for human approval. "
                "Explain what the action will do before proposing."
            ),
            "search_docs": (
                "The user wants to search documentation or specs. "
                "Use search_odoo_docs with the appropriate index."
            ),
            "record_reader": (
                "The user wants to view record data. "
                "Use read_record or search_records. "
                "Format output clearly with field labels."
            ),
            "document_extract": (
                "The user wants to extract data from an uploaded document. "
                "Use extract_document to analyze the attachment via Document Intelligence. "
                "Present extracted fields clearly. For invoices, show vendor, total, tax, date. "
                "For receipts, show merchant, total, date. For general docs, show full text."
            ),
        }
        return instructions_map.get(skill_id, "")
