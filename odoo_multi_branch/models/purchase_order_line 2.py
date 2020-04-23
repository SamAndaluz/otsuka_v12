# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        related='order_id.company_branch_id',
        string="Branch",
        copy=False,
    )

#     @api.model
#     def create(self, vals):
#         purchase_id = self.env['purchase.order'].browse(int(vals.get("order_id")))
#         if purchase_id.company_branch_id and vals.get("company_branch_id") and not (vals.get("company_branch_id") == purchase_id.company_branch_id.id):
#             raise ValidationError("Branch Should be same on Order And Order Line")
#         return super(PurchaseOrderLine, self).create(vals)
# 
#     @api.multi
#     def write(self, vals):
#         for rec in self:
#             if rec.order_id.company_branch_id and vals.get("company_branch_id") and not (vals.get("company_branch_id") == rec.order_id.company_branch_id.id):
#                 raise ValidationError("Branch Should be same on Order And Order Line")
#         return super(PurchaseOrderLine, self).write(vals)

#     @api.onchange('account_analytic_id')
#     def _onchange_analytic_account(self):
#         self.company_branch_id = self.account_analytic_id.company_branch_id.id or False
#         if self.company_branch_id and (self.company_branch_id.id != self.order_id.company_branch_id.id):
#             raise ValidationError("Branch Must be same on Order and Order lines")

    @api.multi
    def _prepare_stock_moves(self, picking):
        stock_moves = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for rec in self:
            for move in stock_moves:
                move.update({'company_branch_id':rec.company_branch_id.id})
        return stock_moves

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
