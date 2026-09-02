from odoo import models, fields, api, _
from datetime import timedelta, date

class EstateSanction(models.Model):
    _name = 'estate.sanction'
    _description = 'Project Sanction & Approval Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Sanction Title', required=True, tracking=True)
    project_id = fields.Many2one('estate.project', string='Project', required=True, tracking=True)
    sanction_type = fields.Selection([
        ('iod', 'IOD (Intimation of Disapproval)'),
        ('cc', 'CC (Commencement Certificate)'),
        ('fire_noc', 'Fire NOC'),
        ('rera', 'RERA Registration'),
        ('env_noc', 'Environmental Clearance'),
        ('oc', 'Occupancy Certificate')
    ], string='Sanction Type', required=True, tracking=True)

    reference_no = fields.Char(string='Approval / License No.', tracking=True)
    authority_name = fields.Char(string='Issuing Authority', help="e.g. Municipal Corporation, RERA Authority")
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiration_date = fields.Date(string='Expiration Date', tracking=True)
    
    document = fields.Binary(string='Sanction Document', attachment=True)
    filename = fields.Char(string='Filename')
    
    state = fields.Selection([
        ('draft', 'Applied / Draft'),
        ('approved', 'Approved & Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired')
    ], string='Status', compute='_compute_state', store=True, tracking=True)

    notes = fields.Text(string='Notes / Conditions')

    @api.depends('expiration_date', 'issue_date')
    def _compute_state(self):
        today = date.today()
        for rec in self:
            if not rec.expiration_date:
                rec.state = 'approved' if rec.issue_date else 'draft'
            elif rec.expiration_date < today:
                rec.state = 'expired'
            elif rec.expiration_date <= today + timedelta(days=30):
                rec.state = 'expiring_soon'
            else:
                rec.state = 'approved'

    def cron_check_sanction_expiry(self):
        """Automated activity warnings when sanctions are expiring within 30 days."""
        today = date.today()
        expiring_sanctions = self.search([('expiration_date', '<=', today + timedelta(days=30)), ('expiration_date', '>=', today)])
        for sanction in expiring_sanctions:
            sanction.activity_schedule(
                'mail.mail_activity_data_warning',
                note=_('Sanction "%s" for project "%s" is expiring on %s. Please renew immediately.') % (sanction.name, sanction.project_id.name, sanction.expiration_date),
                user_id=sanction.project_id.create_uid.id or self.env.user.id
            )
