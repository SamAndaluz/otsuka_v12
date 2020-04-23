
from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError


class CreateProduct(models.TransientModel):
    _name = 'create.product'


    def _get_records(self, model):
        if self.env.context.get('active_domain'):
            records = model.search(self.env.context.get('active_domain'))
        elif self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    def create_products(self):

        active_model = self.env.context.get('active_model')
        model = self.env[active_model]

        records = self._get_records(model)
        
        products_new = []
        
        for product in records:
            record = {'name': product.name,
                 'price': product.list_price,
                 'default_code': product.default_code,
                 'type': product.type,
                 'l10n_mx_edi_code_sat_id': product.l10n_mx_edi_code_sat_id.id,
                 'uom_id': product.uom_id.id,
                 'uom_po_id': product.uom_po_id.id}
        
            products_new.append(record)
        
        self.env['product.product'].create(products_new)
        records.unlink()
        
        view_id = self.env.ref('account.account_journal_dashboard_kanban_view').id
        
        return {
            'name': 'Resumen Contable',
            'view_mode':'kanban,tree,form',
            'views' : [(view_id,'kanban')],
            'res_model':'account.journal',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'main',
        }

        