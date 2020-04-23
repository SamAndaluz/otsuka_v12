# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Sale(models.Model):
    _inherit = 'sale.order'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(Sale, self)._prepare_invoice()
        invoice_vals.update({'company_branch_id': self.company_branch_id.id or False})
        return invoice_vals

#     @api.onchange('analytic_account_id')
#     def _onchange_analytic_account(self):
#         self.company_branch_id = self.analytic_account_id.company_branch_id.id

    @api.multi
    def _action_confirm(self):
        result = super(Sale, self)._action_confirm()
        for order in self:
            if order.procurement_group_id:
                order.procurement_group_id.company_branch_id = order.company_branch_id.id
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
