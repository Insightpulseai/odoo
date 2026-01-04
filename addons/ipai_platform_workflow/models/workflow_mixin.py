from odoo import api, fields, models


class WorkflowMixin(models.AbstractModel):
    """
    Mixin class providing generic workflow capabilities.

    Inherit this mixin in your model to gain:
    - State field with configurable states
    - Transition validation
    - State change notifications
    - Audit trail integration (if ipai_platform_audit installed)

    Usage:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['ipai.workflow.mixin']

            _workflow_states = [
                ('draft', 'Draft'),
                ('submitted', 'Submitted'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
            ]
    """

    _name = "ipai.workflow.mixin"
    _description = "IPAI Workflow Mixin"

    workflow_state = fields.Selection(
        selection="_get_workflow_states",
        string="Workflow State",
        default="draft",
        tracking=True,
        copy=False,
        index=True,
    )

    workflow_state_date = fields.Datetime(
        string="State Changed",
        readonly=True,
        copy=False,
    )

    workflow_state_user_id = fields.Many2one(
        "res.users",
        string="State Changed By",
        readonly=True,
        copy=False,
    )

    @api.model
    def _get_workflow_states(self):
        """Override in inheriting model to define states."""
        return getattr(self, "_workflow_states", [("draft", "Draft")])

    def _get_allowed_transitions(self):
        """
        Override to define allowed state transitions.

        Returns dict: {from_state: [allowed_to_states]}
        """
        return getattr(self, "_workflow_transitions", {})

    def _can_transition_to(self, new_state):
        """Check if transition to new_state is allowed."""
        transitions = self._get_allowed_transitions()
        if not transitions:
            # No restrictions defined, allow all
            return True
        allowed = transitions.get(self.workflow_state, [])
        return new_state in allowed

    def workflow_transition(self, new_state, note=None):
        """
        Transition to a new workflow state.

        Args:
            new_state: Target state key
            note: Optional transition note

        Raises:
            UserError: If transition not allowed
        """
        self.ensure_one()

        if not self._can_transition_to(new_state):
            from odoo.exceptions import UserError

            raise UserError(
                f"Transition from '{self.workflow_state}' to '{new_state}' is not allowed."
            )

        old_state = self.workflow_state
        self.write(
            {
                "workflow_state": new_state,
                "workflow_state_date": fields.Datetime.now(),
                "workflow_state_user_id": self.env.uid,
            }
        )

        # Post message if model has mail.thread
        if hasattr(self, "message_post"):
            body = f"State changed: {old_state} → {new_state}"
            if note:
                body += f"<br/><i>{note}</i>"
            self.message_post(body=body, message_type="notification")

        return True
