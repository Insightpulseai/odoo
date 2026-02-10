from odoo import models


class IPAIAgentLibrary(models.AbstractModel):
    _name = "ipai.ai.agent_library"
    _description = "IPAI Canonical Agent Library"

    def _orch(self):
        return self.env["ipai.ai.orchestration"]

    def run_cms_homepage_pipeline(self, org_id, brief: dict):
        """
        Run the CMS homepage generation pipeline.

        Args:
            org_id: Organization UUID
            brief: {"goal":..., "audience":..., "product":..., "ctas":[...], ...}

        Returns:
            Orchestration run record
        """
        run = self._orch().start(org_id, "cms_homepage_pipeline", {"brief": brief})
        return run

    def run_support_pipeline(self, org_id, issue_text: str, ctx: dict = None):
        """
        Run the support response generation pipeline.

        Args:
            org_id: Organization UUID
            issue_text: Support issue description
            ctx: Optional context dictionary

        Returns:
            Orchestration run record
        """
        run = self._orch().start(
            org_id,
            "support_response_pipeline",
            {"text": issue_text, "context": ctx or {}},
        )
        return run

    def run_odoo_workflow_pipeline(self, org_id, request: dict):
        """
        Run the Odoo workflow automation pipeline.

        Args:
            org_id: Organization UUID
            request: Workflow request description

        Returns:
            Orchestration run record
        """
        run = self._orch().start(org_id, "odoo_workflow_pipeline", {"request": request})
        return run
