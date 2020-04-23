# -*- coding: utf-8 -*-
{
    'name': "Prodigia Facturacion",

    'summary': """
       Modulo de facturacion para enviar facturas al servicio de Prodigia.""",
    'description': """
        Éste modulo agrega a Prodigia como opcion para emitir facturas desde el modulo de facturacion de odoo-enterprise. para versión 12
    """,
    'author': "Prodigia",
    'website': "https://www.prodigia.mx",
    'support': 'soporte@prodigia.com.mx',
    'category': 'Invoicing',
    'version': '1.0.12',
    'maintainer': "Prodigia Dev Team",
    # dependencias
    'depends': [
        'account',
        'account_cancel',
        'base_vat',
        'base_address_extended',
        'document',
        'base_address_city',
        'l10n_mx_edi',
        'l10n_mx'],
    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
