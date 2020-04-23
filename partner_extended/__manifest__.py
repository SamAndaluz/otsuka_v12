# -*- coding: utf-8 -*-
{
    'name': "Partner extended",

    'summary': """
        This module extends functionality for contacts module.""",

    'description': """
        This module extends functionality for contacts module.
    """,

    'author': "A. Márquez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','sale','purchase','account'],

    # always loaded
    'data': [
        'security/partner_security.xml',
        'views/res_partner.xml',
        'views/templates.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_view.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}