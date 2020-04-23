# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SwitchBranch(models.TransientModel):
    _name = "switch.branch.wiz"

    allow_branches_ids = fields.Many2many(
        'res.company.branch',
        string='Allowed Branches',
        default=lambda self:self.env.user.sudo().company_branch_ids,
        readonly=True,
    )
    current_branch_id = fields.Many2one(
        'res.company.branch',
        string='Current Branch',
        default=lambda self:self.env.user.sudo().company_branch_id,
        readonly=True,
    )
    switch_branch_id = fields.Many2one(
        'res.company.branch',
        string='Switch to Branch',
        required=True,
    )

    @api.multi
    def action_switch_branch(self):
        self.ensure_one()
        current_user = self.env.user
        current_user.write({
            'company_branch_id': self.switch_branch_id.id,
        })
        self.env['ir.default'].clear_caches()
        return {'type': 'ir.actions.client', 'tag': 'reload_context'}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
