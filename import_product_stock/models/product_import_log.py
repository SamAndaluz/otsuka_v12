# See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class ImportProductLog(models.Model):
    _name = "import.product.log"
    _description = "Import Product Log"

    barcode = fields.Char(string='Barcode')
    product_name = fields.Char(string='Product')
    internal_ref = fields.Char(string='Internal Reference')
    qty = fields.Float(string="Quantity")
    state = fields.Char(string="State")
    error_log = fields.Char(string="Error Log")
    type = fields.Selection([('add_update', 'Add/Update'),
                             ('adjustments', 'Adjustments'),
                             ('subtract', 'Subtract')], string="Type")

    @api.model
    def delete_product_import_log(self):
        today_date = datetime.now()
        diff_date = today_date - timedelta(hours=24)
        self.search([('create_date', '<=',
                      datetime.strftime(diff_date, DATETIME_FORMAT))]).unlink()
