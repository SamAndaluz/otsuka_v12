# -*- coding: utf-8 -*-
{
    'name': "Import Bank Statements",

    'summary': """
        This module add functionality to import bank statements.""",

    'description': """
        This module add functionality to import bank statements.
    """,

    'author': "AMB",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/import_bank_statement.xml',
        'views/account_journal.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True
}