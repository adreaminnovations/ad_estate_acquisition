from odoo import models, fields, api, _

class EstateDashboardAcquisition(models.Model):
    _inherit = 'estate.dashboard'

    feasibility_count = fields.Integer(string='Feasibility Studies Count', compute='_compute_base_metrics')
    total_potential_bua = fields.Float(string='Total Feasibility BUA (sq ft)', compute='_compute_base_metrics')

    @api.depends_context('uid')
    def _compute_base_metrics(self):
        super()._compute_base_metrics()
        for dash in self:
            studies = self.env['estate.feasibility'].search([])
            dash.feasibility_count = len(studies)
            dash.total_potential_bua = sum(studies.mapped('total_potential_bua'))


class EstateFeasibility(models.Model):

    _name = 'estate.feasibility'
    _description = 'Land Acquisition & Redevelopment Feasibility Study'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Feasibility Name', required=True, tracking=True)
    project_id = fields.Many2one('estate.project', string='Linked Project', tracking=True)
    lead_id = fields.Many2one('crm.lead', string='Source Lead / Tender', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Plot & FSI Parameters
    gross_plot_area = fields.Float(string='Gross Plot Area (sq ft)', required=True)
    permissible_fsi = fields.Float(string='Permissible FSI Ratio', default=1.0)
    fungible_fsi = fields.Float(string='Fungible FSI Area (sq ft)')
    tdr_area = fields.Float(string='TDR Area (sq ft)')
    total_potential_bua = fields.Float(string='Total Potential BUA (sq ft)', compute='_compute_potential_bua', store=True)

    # Redevelopment Member Entitlement Matrix
    total_existing_members = fields.Integer(string='Total Existing Members')
    current_carpet_area = fields.Float(string='Total Current Carpet Area (sq ft)')
    proposed_incentive_pct = fields.Float(string='Proposed Incentive Area (%)', default=35.0)
    total_rehab_area = fields.Float(string='Total Rehab Area (sq ft)', compute='_compute_rehab_area', store=True)
    transit_rent_per_member = fields.Monetary(string='Transit Rent / Member / Month', currency_field='currency_id')
    displacement_compensation = fields.Monetary(string='Displacement Compensation / Member', currency_field='currency_id')
    total_hard_soft_rent_cost = fields.Monetary(string='Total Member Compensation Cost', compute='_compute_compensation_cost', store=True, currency_field='currency_id')

    # Cost Projections
    land_acquisition_cost = fields.Monetary(string='Land / Premium Cost', currency_field='currency_id')
    sanction_cost = fields.Monetary(string='Sanctions & Approval Cost', currency_field='currency_id')
    construction_cost = fields.Monetary(string='Civil Construction Cost', currency_field='currency_id')
    marketing_cost = fields.Monetary(string='Marketing & Sales Cost', currency_field='currency_id')
    total_project_cost = fields.Monetary(string='Total Projected Cost', compute='_compute_financials', store=True, currency_field='currency_id')

    # Realization & ROI
    saleable_bua = fields.Float(string='Saleable BUA (sq ft)', compute='_compute_saleable_bua', store=True)
    avg_sale_rate = fields.Monetary(string='Avg Sale Rate per sq ft', currency_field='currency_id')
    projected_sale_realization = fields.Monetary(string='Projected Sale Realization', compute='_compute_financials', store=True, currency_field='currency_id')
    net_profit = fields.Monetary(string='Net Profit', compute='_compute_financials', store=True, currency_field='currency_id')
    roi_percent = fields.Float(string='Projected ROI (%)', compute='_compute_financials', store=True)

    @api.depends('gross_plot_area', 'permissible_fsi', 'fungible_fsi', 'tdr_area')
    def _compute_potential_bua(self):
        for rec in self:
            base_bua = rec.gross_plot_area * rec.permissible_fsi
            rec.total_potential_bua = base_bua + rec.fungible_fsi + rec.tdr_area

    @api.depends('current_carpet_area', 'proposed_incentive_pct')
    def _compute_rehab_area(self):
        for rec in self:
            rec.total_rehab_area = rec.current_carpet_area * (1.0 + (rec.proposed_incentive_pct / 100.0))

    @api.depends('total_existing_members', 'transit_rent_per_member', 'displacement_compensation')
    def _compute_compensation_cost(self):
        for rec in self:
            # Assuming 24 months transit rent standard timeline
            transit = rec.total_existing_members * rec.transit_rent_per_member * 24
            displacement = rec.total_existing_members * rec.displacement_compensation
            rec.total_hard_soft_rent_cost = transit + displacement

    @api.depends('total_potential_bua', 'total_rehab_area')
    def _compute_saleable_bua(self):
        for rec in self:
            rec.saleable_bua = max(0.0, rec.total_potential_bua - rec.total_rehab_area)

    @api.depends('land_acquisition_cost', 'sanction_cost', 'construction_cost', 'marketing_cost', 'total_hard_soft_rent_cost', 'saleable_bua', 'avg_sale_rate')
    def _compute_financials(self):
        for rec in self:
            rec.total_project_cost = rec.land_acquisition_cost + rec.sanction_cost + rec.construction_cost + rec.marketing_cost + rec.total_hard_soft_rent_cost
            rec.projected_sale_realization = rec.saleable_bua * rec.avg_sale_rate
            rec.net_profit = rec.projected_sale_realization - rec.total_project_cost
            if rec.total_project_cost > 0:
                rec.roi_percent = (rec.net_profit / rec.total_project_cost) * 100.0
            else:
                rec.roi_percent = 0.0
