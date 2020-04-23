# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

#     @api.model
#     def create(self, vals):
#         res = super(StockMove, self).create(vals)
#         if self.company_branch_id and (self.company_branch_id.id != self.picking_id.company_branch_id.id):
#             raise ValidationError("Branch Must be same on Picking and Picking lines")
#         return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: