# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.multi
    def _write(self, vals):
        if vals.get("sale_id"):
            sale_id = self.env['sale.order'].browse(int(vals.get('sale_id')))
            vals.update({'company_branch_id':sale_id.company_branch_id.id})
            for rec in self:
                rec.move_lines.write({'company_branch_id':sale_id.company_branch_id.id})
        return super(StockPicking, self)._write(vals)

    def _compute_entire_package_ids(self):
        super(StockPicking, self)._compute_entire_package_ids()
        for picking in self:
            if picking.entire_package_ids:
                picking.entire_package_ids.write({'company_branch_id': picking.company_branch_id.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
