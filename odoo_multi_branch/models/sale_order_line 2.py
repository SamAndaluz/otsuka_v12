# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        related='order_id.company_branch_id',
        store=True,
        string="Branch",
        copy=False,
        #default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.model
    def create(self, vals):
        sale_id = self.env['sale.order'].browse(int(vals.get("order_id")))
        if vals.get("is_downpayment"):
            vals.update({'company_branch_id':sale_id.company_branch_id.id})
#         if sale_id.company_branch_id and vals.get("company_branch_id") and not (vals.get("company_branch_id") == sale_id.company_branch_id.id):
#             raise ValidationError("Branch Should be Same on Sale order And Order Line11")
        return super(SaleOrderLine, self).create(vals)

#     @api.multi
#     def write(self, vals):
#         for rec in self:
#             if rec.order_id.company_branch_id and vals.get("company_branch_id") and not (vals.get("company_branch_id") == rec.order_id.company_branch_id.id):
#                 raise ValidationError("Branch Should be Same on Sale order And Order Line2")
#         return super(SaleOrderLine, self).write(vals)

    @api.multi #Pass value of client to pay in create invoice.
    def _prepare_invoice_line(self, qty):
       res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
       if self.order_id.company_branch_id:
           vals = {
               'company_branch_id': self.order_id.company_branch_id.id,
           }
           res.update(vals)
       return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
