# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models
from odoo.exceptions import ValidationError


BLOCK_TYPES = [
    ("paragraph", "Paragraph"),
    ("heading_1", "Heading 1"),
    ("heading_2", "Heading 2"),
    ("heading_3", "Heading 3"),
    ("bulleted_list", "Bulleted List"),
    ("numbered_list", "Numbered List"),
    ("todo", "To-do"),
    ("toggle", "Toggle"),
    ("divider", "Divider"),
    ("quote", "Quote"),
    ("callout", "Callout"),
    ("image", "Image"),
    ("file", "File"),
    ("code", "Code"),
]


class IpaiWorkosBlock(models.Model):
    """Block - Atomic content unit within a page."""

    _name = "ipai.workos.block"
    _description = "Work OS Block"
    _order = "sequence, id"

    name = fields.Char(string="Preview", compute="_compute_name", store=True)
    page_id = fields.Many2one(
        "ipai.workos.page",
        string="Page",
        required=True,
        ondelete="cascade",
        index=True,
    )
    parent_block_id = fields.Many2one(
        "ipai.workos.block",
        string="Parent Block",
        ondelete="cascade",
        help="For nested blocks (e.g., toggle children)",
    )
    child_block_ids = fields.One2many(
        "ipai.workos.block",
        "parent_block_id",
        string="Child Blocks",
    )

    block_type = fields.Selection(
        BLOCK_TYPES,
        string="Block Type",
        required=True,
        default="paragraph",
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Content storage
    content_json = fields.Text(
        string="Content (JSON)",
        default="{}",
        help="Structured content stored as JSON",
    )
    content_text = fields.Text(
        string="Plain Text",
        compute="_compute_content_text",
        store=True,
        help="Plain text extraction for search",
    )
    content_html = fields.Html(
        string="Rendered HTML",
        compute="_compute_content_html",
        sanitize=False,
        help="Cached HTML rendering",
    )

    # For todo blocks
    is_checked = fields.Boolean(string="Checked", default=False)

    # For toggle blocks
    is_collapsed = fields.Boolean(string="Collapsed", default=False)

    # For callout blocks
    callout_icon = fields.Char(string="Callout Icon", default="info")
    callout_color = fields.Char(string="Callout Color", default="blue")

    # Attachments (for image/file blocks)
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        ondelete="set null",
    )

    @api.depends("block_type", "content_json")
    def _compute_name(self):
        for record in self:
            content = record._get_content()
            text = content.get("text", "")[:50]
            record.name = f"[{record.block_type}] {text}" if text else f"[{record.block_type}]"

    @api.depends("content_json")
    def _compute_content_text(self):
        for record in self:
            content = record._get_content()
            # Extract text from various content structures
            texts = []
            if "text" in content:
                texts.append(content["text"])
            if "items" in content:
                for item in content["items"]:
                    if isinstance(item, str):
                        texts.append(item)
                    elif isinstance(item, dict) and "text" in item:
                        texts.append(item["text"])
            record.content_text = " ".join(texts)

    @api.depends("block_type", "content_json", "is_checked", "callout_icon", "callout_color")
    def _compute_content_html(self):
        for record in self:
            record.content_html = record._render_html()

    def _get_content(self):
        """Parse content JSON safely."""
        try:
            return json.loads(self.content_json or "{}")
        except json.JSONDecodeError:
            return {}

    def _set_content(self, content):
        """Serialize content to JSON."""
        self.content_json = json.dumps(content)

    def _render_html(self):
        """Render block to HTML based on type."""
        content = self._get_content()
        text = content.get("text", "")

        renderers = {
            "paragraph": lambda: f"<p>{text}</p>",
            "heading_1": lambda: f"<h1>{text}</h1>",
            "heading_2": lambda: f"<h2>{text}</h2>",
            "heading_3": lambda: f"<h3>{text}</h3>",
            "bulleted_list": lambda: self._render_list(content, "ul"),
            "numbered_list": lambda: self._render_list(content, "ol"),
            "todo": lambda: self._render_todo(content),
            "toggle": lambda: self._render_toggle(content),
            "divider": lambda: "<hr/>",
            "quote": lambda: f"<blockquote>{text}</blockquote>",
            "callout": lambda: self._render_callout(content),
            "code": lambda: f"<pre><code>{text}</code></pre>",
            "image": lambda: self._render_image(),
            "file": lambda: self._render_file(),
        }

        renderer = renderers.get(self.block_type, lambda: f"<div>{text}</div>")
        return renderer()

    def _render_list(self, content, tag):
        """Render bulleted or numbered list."""
        items = content.get("items", [])
        li_items = "".join(f"<li>{item}</li>" for item in items if item)
        return f"<{tag}>{li_items}</{tag}>"

    def _render_todo(self, content):
        """Render todo checkbox item."""
        text = content.get("text", "")
        checked = "checked" if self.is_checked else ""
        return f'<div class="o_workos_todo"><input type="checkbox" {checked}/> {text}</div>'

    def _render_toggle(self, content):
        """Render collapsible toggle block."""
        text = content.get("text", "")
        collapsed = "collapsed" if self.is_collapsed else ""
        children_html = ""
        for child in self.child_block_ids:
            children_html += child._render_html()
        return f'''
            <details class="o_workos_toggle {collapsed}">
                <summary>{text}</summary>
                <div class="o_workos_toggle_content">{children_html}</div>
            </details>
        '''

    def _render_callout(self, content):
        """Render callout block with icon and color."""
        text = content.get("text", "")
        return f'''
            <div class="o_workos_callout o_workos_callout_{self.callout_color}">
                <span class="o_workos_callout_icon">{self.callout_icon}</span>
                <span class="o_workos_callout_text">{text}</span>
            </div>
        '''

    def _render_image(self):
        """Render image block."""
        if self.attachment_id:
            return f'<img src="/web/image/{self.attachment_id.id}" class="o_workos_image"/>'
        return '<div class="o_workos_image_placeholder">No image</div>'

    def _render_file(self):
        """Render file attachment block."""
        if self.attachment_id:
            return f'''
                <a href="/web/content/{self.attachment_id.id}" class="o_workos_file">
                    {self.attachment_id.name}
                </a>
            '''
        return '<div class="o_workos_file_placeholder">No file</div>'

    @api.constrains("content_json")
    def _check_content_json(self):
        """Validate content JSON format."""
        for record in self:
            if record.content_json:
                try:
                    json.loads(record.content_json)
                except json.JSONDecodeError as e:
                    raise ValidationError(f"Invalid JSON content: {e}")

    @api.model
    def create_block(self, page_id, block_type, content, sequence=None, parent_block_id=None):
        """Helper to create a block with proper content structure."""
        vals = {
            "page_id": page_id,
            "block_type": block_type,
            "content_json": json.dumps(content),
        }
        if sequence is not None:
            vals["sequence"] = sequence
        if parent_block_id:
            vals["parent_block_id"] = parent_block_id
        return self.create(vals)

    def move_block(self, new_sequence, new_parent_id=None):
        """Move block to new position."""
        self.ensure_one()
        vals = {"sequence": new_sequence}
        if new_parent_id is not None:
            vals["parent_block_id"] = new_parent_id
        return self.write(vals)
