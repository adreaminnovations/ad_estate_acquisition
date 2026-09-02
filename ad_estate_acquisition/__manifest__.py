{
  "name": "Real Estate Acquisition & Land Bank Management",
  "version": "18.0.1.0.0",
  "category": "Real Estate",
  "summary": "Tenders, Feasibility Analysis, FSI, Redevelopment Entitlements & Sanctions",
  "website": "https://adreaminnovations.odoo.com",
  "description": """
      Manage public tender bids, broker referrals, redevelopment member entitlement matrix,
      FSI/TDR feasibility studies, and municipal sanction approvals for real estate land banking.
  """,
  "author": "ADream Innovations",
  "license": "LGPL-3",
  "depends": [
    "ad_estate_base",
    "crm"
  ],
  "data": [
    "security/ir.model.access.csv",
    "wizards/estate_doc_gen_wizard_views.xml",
    "views/crm_lead_views.xml",
    "views/estate_feasibility_views.xml",
    "views/estate_sanctions_views.xml",
    "reports/estate_acquisition_reports.xml",
    "reports/legal_document_template.xml",
    "views/acquisition_menus.xml"
  ],
  "demo": [
    "demo/estate_acquisition_demo.xml"
  ],
  "installable": True,
  "application": False,
  "auto_install": False,
  "images": ["static/description/banner.png"]
}
