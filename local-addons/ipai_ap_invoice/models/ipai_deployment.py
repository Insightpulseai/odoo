from odoo import models, fields, api

class IpaiDeploymentStatus(models.Model):
    _name = 'ipai.deployment.status'
    _description = 'IPAI Deployment Status'
    _order = 'last_success desc'

    name = fields.Char(string="Environment", required=True)
    version = fields.Char(string="Version")
    commit_hash = fields.Char(string="Commit Hash")
    last_success = fields.Datetime(string="Last Successful Deploy")
    status = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('failed', 'Failed'),
    ], string="Health Status", default='healthy')
    provider = fields.Char(string="Cloud Provider", default="Azure ACA")
