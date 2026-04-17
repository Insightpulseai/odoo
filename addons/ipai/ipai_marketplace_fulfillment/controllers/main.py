import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MarketplaceWebhookController(http.Controller):

    @http.route('/api/marketplace/webhook', type='json', auth='none', methods=['POST'], csrf=False)
    def marketplace_webhook(self, **post):
        """
        Webhook receiver for Microsoft Commercial Marketplace SaaS Fulfillment API v2 events.
        """
        payload = request.get_json_data()
        _logger.info("Marketplace Webhook received: %s", json.dumps(payload))

        # 1. Validate Secret/Signature
        auth_header = request.httprequest.headers.get('Authorization')
        expected_token = request.env['ir.config_parameter'].sudo().get_param('microsoft_marketplace_api_key')
        
        # Simple Bearer token validation for MVP
        if not auth_header or expected_token not in auth_header:
            _logger.warning("Marketplace Webhook: Unauthorized access attempt.")
            return {"error": "Unauthorized"}, 401

        # 2. Extract Event Data
        action = payload.get('action')
        subscription_id = payload.get('subscriptionId')
        
        if not action or not subscription_id:
            return {"error": "Missing required fields"}, 400

        # 3. Process Action
        Subscription = request.env['ipai.marketplace.subscription'].sudo()
        sub = Subscription.search([('name', '=', subscription_id)], limit=1)
        
        if not sub:
            # Create new record if unique subscription ID
            sub = Subscription.create({
                'name': subscription_id,
                'offer_id': payload.get('offerId'),
                'plan_id': payload.get('planId'),
                'status': 'pending',
            })

        # Log the event
        request.env['ipai.marketplace.event'].sudo().create({
            'subscription_id': sub.id,
            'event_type': action,
            'payload': json.dumps(payload),
            'message': f"Microsoft Action: {action}"
        })

        # Update Status based on Microsoft contract
        if action == 'Activate':
            sub.status = 'active'
        elif action == 'Unsubscribe':
            sub.status = 'unsubscribed'
        elif action == 'Suspend':
            sub.status = 'suspended'
        elif action == 'Reinstate':
            sub.status = 'active'

        _logger.info("Marketplace Webhook: Processed action %s for sub %s", action, subscription_id)
        return {"status": "success", "subscription_id": subscription_id}
