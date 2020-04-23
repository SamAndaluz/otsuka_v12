# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        admin_user = self.env.user.has_group('base.group_erp_manager')
        if not admin_user:
            args = ['|',('company_branch_id','=',False), ('company_branch_id', '=', self.env.user.company_branch_id.id)] + list(args)
        return super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)


    @api.multi
    def read(self, fields=None, load='_classic_read'):
        read_partner = super(ResPartner, self).read(fields, load=load)
        admin_user = self.env.user.has_group('base.group_erp_manager')
        if admin_user:
            return read_partner
        for partner in read_partner:
            if partner.get("company_branch_id") and self.env.user.company_branch_id.id != partner["company_branch_id"]:
                if isinstance(partner["company_branch_id"] , tuple) and self.env.user.company_branch_id.id != partner["company_branch_id"][0]:
                    raise ValidationError("You are not allowed to access")
        return read_partner
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
