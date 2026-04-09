from odoo import models, fields, api
import requests
import json

class IpaiFoundryConnector(models.AbstractModel):
    _name = 'ipai.foundry.connector'
    _description = 'IPAI Foundry API Connector'

    @api.model
    def action_chat_completion(self, message, history=None):
        """Called by the Odoo Chat Widget to get governed insights from Foundry."""
        endpoint = self.env['ir.config_parameter'].sudo().get_param('ipai.foundry_endpoint')
        tenant_id = self.env['ir.config_parameter'].sudo().get_param('ipai.azure_tenant_id')
        client_id = self.env['ir.config_parameter'].sudo().get_param('ipai.azure_client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.azure_client_secret')
        
        if not endpoint or not client_id or not client_secret:
            return {"error": "Azure App Registration incomplete. Please check Settings > IPAI."}

        # Simplified prompt construction with the IPAI Constitution
        system_prompt = "You are the IPAI Odoo Copilot. You MUST NOT trigger ERP mutations directly. You MUST provide evidence citations. If a user asks to post or delete, refuse and guide them to the correct UI button."
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.0
        }
        
        # Real implementation would use requests.post(endpoint, json=payload, headers={"api-key": key})
        # Mocking for pilot/demonstration
        response_text = f"IPAI [Evidence: Odoo SSOT]: I have analyzed your request regarding '{message}'. Based on the ERP state, I recommend [B-01] verification. I cannot perform this action directly per the IPAI Constitution."
        
        return {"response": response_text}

    @api.model
    def action_ocr_process(self, attachment_id):
        """Bridge method to call Azure Document Intelligence."""
        endpoint = self.env['ir.config_parameter'].sudo().get_param('ipai.doc_intel_endpoint')
        key = self.env['ir.config_parameter'].sudo().get_param('ipai.doc_intel_key')
        
        if not endpoint or not key:
            return {"error": "OCR not configured. Please check Settings > IPAI."}

        # Simulated OCR result from the bridge
        return {
            'invoice_no': 'BILL-2026-REAL-BRIDGE',
            'date': fields.Date.today(),
            'lines': [
                {'desc': 'Azure Compute - Monitored', 'qty': 1, 'price': 1250.0}
            ]
        }
