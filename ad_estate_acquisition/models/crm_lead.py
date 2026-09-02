from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', readonly=True)

    source_type = fields.Selection([
        ('tender', 'Tender / Public Bid'),
        ('referral', 'Referral / Broker'),
        ('direct', 'Direct Acquisition')
    ], string='Acquisition Source Type', default='direct', tracking=True)

    # Tender specific fields
    emd_amount = fields.Monetary(string='EMD Amount', currency_field='currency_id', tracking=True)
    tender_submission_date = fields.Date(string='Tender Submission Date', tracking=True)
    tender_portal_ref = fields.Char(string='Tender Portal Reference', tracking=True)
    competitor_notes = fields.Text(string='Competitor Notes / Bids')

    # Referral specific fields
    referrer_id = fields.Many2one('res.partner', string='Referrer / Broker', domain="[('is_broker', '=', True)]", tracking=True)
    brokerage_agreed_pct = fields.Float(string='Brokerage Agreed (%)', tracking=True)
