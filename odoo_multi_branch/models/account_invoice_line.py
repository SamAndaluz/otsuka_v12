# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
# from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        related='invoice_id.company_branch_id',
        store=True,
        string="Branch",
        copy=False,
    )

#     @api.model
#     def create(self, vals):
#         res = super(AccountInvoiceLine, self).create(vals)
#         if res.company_branch_id and (res.company_branch_id.id != res.invoice_id.company_branch_id.id):
#             raise ValidationError("Branch Must be same on invoice and invoice lines.")
#         elif not res.company_branch_id:
#             res._onchange_analytic_account()
#         return res

#     @api.multi
#     def write(self, vals):
#         result = super(AccountInvoiceLine, self).write(vals)
#         for rec in self:
#             if rec.company_branch_id and rec.invoice_id.company_branch_id and (rec.company_branch_id.id != rec.invoice_id.company_branch_id.id):
#                 raise ValidationError("Branch Must be same on invoice and invoice lines.")
#         return result

#     @api.onchange('account_analytic_id')
#     def _onchange_analytic_account(self):
#         self.company_branch_id = self.account_analytic_id.company_branch_id.id or False
#         if self.company_branch_id and (self.company_branch_id.id != self.invoice_id.company_branch_id.id):
#             raise ValidationError("Branch Must be same on invoice and invoice lines.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
