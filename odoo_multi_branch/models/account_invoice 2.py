# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.multi
    def write(self, vals):
        move_obj = self.env['account.move']
        for rec in self:
            if vals.get('move_id'):
                move_id = move_obj.browse(int(vals.get('move_id')))
                move_id.company_branch_id = rec.company_branch_id.id
                for line in move_id.line_ids:
                    line.company_branch_id = rec.company_branch_id.id
        return super(AccountInvoice, self).write(vals)

    def _prepare_invoice_line_from_po_line(self, line):
        invoice_line_vals = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line=line)
        invoice_line_vals.update({'company_branch_id':line.company_branch_id.id})
        return invoice_line_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: