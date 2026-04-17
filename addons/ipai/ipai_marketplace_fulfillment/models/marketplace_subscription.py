from odoo import models, fields, api

class MarketplaceSubscription(models.Model):
    _name = 'ipai.marketplace.subscription'
    _description = 'Microsoft Marketplace Subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Subscription ID', required=True, copy=False, help="SaaS Subscription ID from Microsoft")
    offer_id = fields.Char(string='Offer ID', help="Marketplace Offer ID")
    plan_id = fields.Char(string='Plan ID', help="Marketplace Plan ID")
    quantity = fields.Integer(string='Quantity', default=1)
    
    tenant_id = fields.Many2one('res.company', string='Odoo Tenant', help="Mapped Odoo Company/Tenant")
    
    status = fields.Selection([
        ('pending', 'Pending Activation'),
        ('active', 'Subscribed'),
        ('suspended', 'Suspended'),
        ('unsubscribed', 'Unsubscribed'),
    ], string='Status', default='pending', tracking=True)
    
    event_ids = fields.One2many('ipai.marketplace.event', 'subscription_id', string='Events')
    
    last_event_type = fields.Char(string='Last Event Type')
    last_event_timestamp = fields.Datetime(string='Last Event Timestamp')

class MarketplaceEvent(models.Model):
    _name = 'ipai.marketplace.event'
    _description = 'Microsoft Marketplace Event Log'
    _order = 'create_date desc'

    subscription_id = fields.Many2one('ipai.marketplace.subscription', string='Subscription', ondelete='cascade')
    event_type = fields.Char(string='Event Type', required=True)
    payload = fields.Text(string='Raw Payload')
    message = fields.Char(string='Message')
