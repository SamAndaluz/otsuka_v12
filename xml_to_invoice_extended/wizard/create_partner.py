
from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError


class CreatePartner(models.TransientModel):
    _name = 'create.partner'


    def _get_records(self, model):
        if self.env.context.get('active_domain'):
            records = model.search(self.env.context.get('active_domain'))
        elif self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    def create_partners(self):

        active_model = self.env.context.get('active_model')
        model = self.env[active_model]

        records = self._get_records(model)
        
        partners_new = []
        
        for partner in records:
            record = {'name': partner.name,
                 'vat': partner.vat,
                 'property_account_position_id': partner.property_account_position_id.id,
                 'property_payment_term_id': partner.property_payment_term_id.id,
                 'customer': partner.customer,
                 'supplier': partner.supplier}
            partners_new.append(record)
        
        self.env['res.partner'].create(partners_new)
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

        