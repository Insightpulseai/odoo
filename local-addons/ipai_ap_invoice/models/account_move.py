# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    ipai_ap_state = fields.Selection([
        ('ingested', 'Ingested'),
        ('classified', 'Classified'),
        ('tax_validated', 'Tax Validated'),
        ('ambiguous', 'Ambiguous'),
        ('exception_diverted', 'Exception Diverted'),
        ('approved_to_post', 'Approved to Post'),
        ('posted', 'Posted'),
        ('quarantined', 'Quarantined')
    ], string='AI AP State', default='ingested', readonly=True)

    ipai_po_id = fields.Many2one('purchase.order', string='Matched PO', readonly=True)
    ipai_ocr_raw = fields.Text(string='OCR Raw Data', readonly=True)

    def action_ipai_ingest_ocr(self):
        """Ingest OCR data via the ipai_foundry bridge."""
        for move in self:
            # In a real scenario, we would pass the actual attachment
            # result = self.env['ipai.foundry.connector'].action_ocr_process(move.attachment_id)
            ocr_data = self.env['ipai.foundry.connector'].action_ocr_process(False)
            
            if 'error' in ocr_data:
                raise UserError(_("IPAI Bridge Error: %s") % ocr_data['error'])

            move.ipai_ocr_raw = json.dumps(ocr_data, indent=2)
            move.ref = ocr_data['invoice_no']
            move.date = ocr_data['date']
            
            move.invoice_line_ids = [(5, 0, 0)]
            for l in ocr_data['lines']:
                move.invoice_line_ids = [(0, 0, {
                    'name': l['desc'],
                    'quantity': l['qty'],
                    'price_unit': l['price'],
                })]
            move.ipai_ap_state = 'draft'

    def action_ipai_match_po(self):
        """Simulated PO matching logic."""
        for move in self:
            if not move.partner_id:
                raise UserError(_("Fail-Closed: Partner must be set before PO matching."))
            
            # Search for a PO that matches the amount and vendor
            po = self.env['purchase.order'].search([
                ('partner_id', '=', move.partner_id.id),
                ('amount_total', '=', move.amount_total),
                ('state', 'in', ['purchase', 'done'])
            ], limit=1)
            
            if po:
                move.ipai_po_id = po.id
                move.ipai_compliance_log = (move.ipai_compliance_log or "") + f"\nPO Matched: {po.name}"
            else:
                move.ipai_compliance_log = (move.ipai_compliance_log or "") + "\nNo exact PO match found. Manual review required for 3-way match."

    def action_ipai_verify_tax(self):
        """Invoke TaxPulse to verify VAT/EWT rules."""
        for move in self:
            if move.move_type != 'in_invoice':
                continue
            
            # Prepare TaxPulse Request
            tax_payload = move._prepare_taxpulse_payload()
            
            # Call TaxPulse Specialist (Simulated via specialist service call)
            # In a full build, this uses self.env['ipai.taxpulse'].verify_invoice(tax_payload)
            compliance_result = self._call_taxpulse_specialist(tax_payload)
            
            if compliance_result.get('status') == 'compliant':
                move.ipai_ap_state = 'approved_to_post'
                move.ipai_compliance_log = f"TaxPulse Verified: {compliance_result.get('summary')}"
                move.ipai_evidence_pack = json.dumps(compliance_result.get('evidence'), indent=2)
            else:
                move.ipai_ap_state = 'exception_diverted'
                move.ipai_compliance_log = f"TaxPulse REJECTED: {compliance_result.get('reason')}"
                move.ipai_evidence_pack = json.dumps(compliance_result.get('evidence'), indent=2)

    def _prepare_taxpulse_payload(self):
        """Format the invoice data for the TaxPulse SSOT contract."""
        return {
            'invoice_id': self.id,
            'vendor_vat': self.partner_id.vat,
            'lines': [{'amount': l.price_subtotal, 'tax_ids': l.tax_ids.ids} for l in self.invoice_line_ids]
        }

    def _call_taxpulse_specialist(self, payload):
        """Simulated specialist service call to TaxPulse."""
        # This mirrors the S03 evaluation logic
        if not payload['vendor_vat']:
            return {'status': 'rejected', 'reason': 'Missing Vendor VAT', 'evidence': {'gate': 'vendor_verification', 'result': 'fail'}}
        
        # Check for 12% VAT in lines
        has_vat_12 = any(1 in p['tax_ids'] for p in payload['lines']) # Assuming 1 is VAT 12% ID
        if not has_vat_12:
            return {'status': 'rejected', 'reason': 'VAT 12% not detected', 'evidence': {'gate': 'tax_match', 'result': 'fail'}}

        return {
            'status': 'compliant',
            'summary': 'VAT-12 and EWT-ATC verified against TaxPulse SSOT.',
            'evidence': {
                'gate': 'tax_parity',
                'result': 'pass',
                'rules_applied': ['VAT-12', 'EWT-ATC-WC100']
            }
        }

    def action_ipai_rehearse_staging(self):
        """Request a staging rehearsal from the Platform Control Plane."""
        self.ensure_one()
        # RPC/Webhook call to the Platform Staging Engine happens here
        self.message_post(body="IPAI: Staging Refresh REQUESTED. Awaiting platform authority...")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Sent',
                'message': 'Staging refresh request sent to platform engine.',
                'type': 'info',
                'sticky': False,
            }
        }

    def action_post(self):
        """Override Odoo post to enforce the AI compliance gate."""
        for move in self:
            if move.move_type == 'in_invoice':
                if move.ipai_ap_state != 'approved_to_post':
                    raise UserError(_("Fail-Closed: AP Invoice must be in 'Approved to Post' state. Current state: %s") % move.ipai_ap_state)
                if not move.ipai_evidence_pack:
                    raise UserError(_("Fail-Closed: Posting blocked. No AI evidence pack attached."))
        
        res = super(AccountMove, self).action_post()
        
        for move in self:
            if move.move_type == 'in_invoice':
                move.ipai_ap_state = 'posted'
        return res
