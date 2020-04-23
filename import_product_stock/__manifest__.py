# See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Stock Inventory',
    'version': '12.0.1.0.0',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'category': 'Warehouse Management',
    'description': """
Import Inventory and Stock
A wizard that will help you import opening stock,
Inventory adjustment and clear inventory based on products.
An easy and quick way to do inventory adjustment.
Import inventory,
Import stock,
Update Product stock,
Inventory import,
Inventory update,
Stock import,
Stock update.
    """,
    'summary': """
Import Inventroy and Stock
A wiazrd that will help you import opening stock,
inventory adjustment and clear inventory based on products.
An easy and quick way to do inventory adjustment.
Import inventory,
Import stock,
Update Product stock,
Inventory import,
Inventory update,
Stock import,
Stock update.
    """,
    'license': 'AGPL-3',
    'depends': ['sale_management', 'stock'],
    'data': ['security/ir.model.access.csv',
             'wizard/products_import_wiz.xml',
             'views/product_import_log_view.xml',
             ],
    'images': ['static/description/export.png'],
    'installable': True,
    'price': 50,
    'currency': 'EUR',
}
