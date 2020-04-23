# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()
        picking_vals.update({'company_branch_id':self.company_branch_id.id})
        return picking_vals

    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        for rec in self:
            result['context'].update({'default_company_branch_id': rec.company_branch_id.id})
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
