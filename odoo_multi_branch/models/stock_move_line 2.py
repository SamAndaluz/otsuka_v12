# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

#    @api.model
#    def create(self, vals):
#        move_line_id = super(StockMoveLine, self).create(vals)
#        if vals.get("production_id"):
#            production_id = self.env['mrp.production'].browse(int(vals.get("production_id")))
#            vals.update({'company_branch_id':production_id.company_branch_id.id})
#        return move_line_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: