# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PlatformFeature(models.Model):
    """Platform features displayed on landing page"""

    _name = "platform.feature"
    _description = "Platform Feature"
    _order = "sequence, id"

    name = fields.Char(string="Title", required=True, translate=True)
    description = fields.Text(string="Description", translate=True)
    icon = fields.Char(string="Icon", help="Emoji or icon class")
    category = fields.Selection(
        [
            ("deployment", "Deployment"),
            ("testing", "Testing"),
            ("monitoring", "Monitoring"),
            ("security", "Security"),
            ("collaboration", "Collaboration"),
            ("automation", "Automation"),
        ],
        string="Category",
        required=True,
        default="deployment",
    )
    published = fields.Boolean(string="Published", default=True)
    sequence = fields.Integer(string="Sequence", default=10)
    color = fields.Char(string="Color", help="Hex color code")

    # Rich content
    long_description = fields.Html(string="Long Description", translate=True)
    image = fields.Image(string="Feature Image")
    video_url = fields.Char(string="Video URL")

    # Metadata
    create_date = fields.Datetime(string="Created", readonly=True)
    write_date = fields.Datetime(string="Last Updated", readonly=True)

    def action_publish(self):
        """Publish feature"""
        self.write({"published": True})

    def action_unpublish(self):
        """Unpublish feature"""
        self.write({"published": False})

    @api.model
    def get_published_features(self):
        """Return published features for API"""
        features = self.search([("published", "=", True)])
        return [
            {
                "id": f.id,
                "title": f.name,
                "description": f.description,
                "icon": f.icon or "⭐",
                "category": f.category,
                "published": f.published,
                "color": f.color,
            }
            for f in features
        ]
