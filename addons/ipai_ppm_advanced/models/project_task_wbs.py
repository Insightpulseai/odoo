from odoo import api, fields, models


class ProjectTaskWBS(models.Model):
    _inherit = 'project.task'

    wbs_code = fields.Char(
        string="WBS ID",
        compute="_compute_wbs_code",
        store=True,
        help="Work Breakdown Structure number automatically generated from the task hierarchy.",
    )

    @api.depends(
        'project_id',
        'parent_id',
        'sequence',
        'parent_id.wbs_code',
        'parent_id.child_ids.sequence',
        'parent_id.child_ids.id',
    )
    def _compute_wbs_code(self) -> None:
        """Assign hierarchical WBS numbers (e.g., 1.2.3) per project with sibling-aware ordering."""
        groups_to_recompute: set[tuple[int, int | bool]] = set()
        for task in self:
            if not task.project_id:
                task.wbs_code = False
                continue
            groups_to_recompute.add((task.project_id.id, task.parent_id.id if task.parent_id else False))

        for project_id, parent_id in groups_to_recompute:
            if not project_id:
                continue

            siblings = self.env['project.task'].search(
                [('project_id', '=', project_id), ('parent_id', '=', parent_id)],
                order='sequence, id',
            )
            parent_code = ''
            if parent_id:
                parent_code = self.env['project.task'].browse(parent_id).wbs_code or ''

            for index, sibling in enumerate(siblings, start=1):
                new_code = f"{parent_code}.{index}" if parent_code else str(index)
                if sibling.wbs_code != new_code:
                    sibling.wbs_code = new_code
