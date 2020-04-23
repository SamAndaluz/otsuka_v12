# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        related='move_id.company_branch_id',
        store=True,
        string="Branch",
        copy=False,
    )

#     @api.model
#     def create(self, vals):
#         res = super(AccountMoveLine, self).create(vals)
#         if not res.company_branch_id:
#             res._onchange_analytic_account()
#         return res
# 
#     @api.onchange('analytic_account_id')
#     def _onchange_analytic_account(self):
#         self.company_branch_id = self.analytic_account_id.company_branch_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: