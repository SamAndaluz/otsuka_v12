# -*- coding: utf-8 -*-
{
    'name': "product_extended",

    'summary': """
        Este módulo añade algunos cambios en el módulo de Productos.""",

    'description': """
        Este módulo añade algunos cambios en el módulo de Productos.
    """,

    'author': "A. Márquez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','purchase','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/product_view.xml',
        'views/templates.xml',
        'views/product_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}