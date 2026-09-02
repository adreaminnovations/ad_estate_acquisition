from odoo import models, fields, api, _

class EstateDocGenWizard(models.TransientModel):
    _name = 'estate.doc.gen.wizard'
    _description = 'Legal Document Generator Wizard'

    doc_type = fields.Selection([
        ('mou', 'Memorandum of Understanding (MOU)'),
        ('da', 'Development Agreement (DA)'),
        ('pa', 'Power of Attorney (PA)')
    ], string='Document Type', required=True, default='mou')

    feasibility_id = fields.Many2one('estate.feasibility', string='Feasibility Study', required=True)
    partner_id = fields.Many2one('res.partner', string='Party / Landowner / Member', required=True)
    agreed_amount = fields.Monetary(string='Agreed Consideration / Compensation', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    execution_date = fields.Date(string='Execution Date', default=fields.Date.today, required=True)
    special_terms = fields.Text(string='Special Clauses / Terms')

    def action_generate_document(self):
        self.ensure_one()
        return self.env.ref('ad_estate_acquisition.action_report_legal_document').report_action(self)
