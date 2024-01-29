# -*- coding: utf-8 -*-
{
    'name': "custom_internal_development",

    'summary': """
        internal development""",

    'description': """
        Default selection of Warehosue in Analytic Account Screen \n  
        Added validation constrain for the 'code' field  in Analytic Account \n   
        Constraint for res.partner - field ref - Unique if partner category='Customer'\n
        For Storable product - Traceability By Lots; for Service and Consumable - not track\n
        Include PnL Filter as standard in Journal items - account.move.line - pivot view  - Account Type - contains \n
        -  Income, Expense, Cost of Revenue String - PnL Items\n
        In journal entries and items - give group and filter view for - Entry created date\n
        Auto pick items in DC/ITP based on GRN
        Payment Term with week-wise\n
        Automate the payment reconcile with vendor bill\n
        add new field approved by to vendor bill\n
        add new field date_time in vendor bill\n
        add invoice_line with month\n
       Mandatory Fields in the Invoice lines\n
       analytic tags in budget calculation\n
       Payment Remittance email
        
    """,

    'author': "Sify K Raphy",
    'website': " ",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Internal Customization',
    'version': '14.0.0',

    # any module necessary for this one to work correctly
    'depends': ['analytic_account_location','analytic_account_automation_mr','account','analytic','stock','stock_account','analytic_unit_base','base','account_budget'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_month.xml',
        'views/account_move.xml',
        'views/stock_picking_type.xml',
        'views/account_budget.xml',
        'wizard/custom_actual_budget_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
