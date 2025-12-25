# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosCanvas(models.Model):
    """Canvas - Edgeless surface for visual content arrangement."""

    _name = "ipai.workos.canvas"
    _description = "WorkOS Canvas"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc"

    name = fields.Char(string="Canvas Name", required=True, tracking=True)

    # Viewport state
    viewport_json = fields.Text(
        string="Viewport JSON",
        default='{"x": 0, "y": 0, "zoom": 1}',
        help="Current viewport position and zoom level",
    )

    # Canvas nodes/elements
    nodes_json = fields.Text(
        string="Nodes JSON",
        default="[]",
        help="Array of canvas nodes with position and content",
    )

    # Optional link to page
    page_id = fields.Many2one(
        "ipai.workos.page",
        string="Linked Page",
        index=True,
        ondelete="cascade",
    )

    # Status
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure sane defaults on create."""
        for vals in vals_list:
            if "viewport_json" not in vals:
                vals["viewport_json"] = '{"x": 0, "y": 0, "zoom": 1}'
            if "nodes_json" not in vals:
                vals["nodes_json"] = "[]"
        return super().create(vals_list)

    def get_viewport(self):
        """Get parsed viewport state."""
        import json
        try:
            return json.loads(self.viewport_json or '{"x": 0, "y": 0, "zoom": 1}')
        except json.JSONDecodeError:
            return {"x": 0, "y": 0, "zoom": 1}

    def get_nodes(self):
        """Get parsed nodes array."""
        import json
        try:
            return json.loads(self.nodes_json or "[]")
        except json.JSONDecodeError:
            return []

    def add_node(self, node_type, x, y, content=None):
        """Add a new node to the canvas."""
        import json
        nodes = self.get_nodes()
        new_node = {
            "id": f"node_{len(nodes) + 1}",
            "type": node_type,
            "x": x,
            "y": y,
            "content": content or {},
        }
        nodes.append(new_node)
        self.nodes_json = json.dumps(nodes)
        return new_node

    def update_node(self, node_id, updates):
        """Update an existing node."""
        import json
        nodes = self.get_nodes()
        for node in nodes:
            if node.get("id") == node_id:
                node.update(updates)
                break
        self.nodes_json = json.dumps(nodes)

    def remove_node(self, node_id):
        """Remove a node from the canvas."""
        import json
        nodes = self.get_nodes()
        nodes = [n for n in nodes if n.get("id") != node_id]
        self.nodes_json = json.dumps(nodes)
