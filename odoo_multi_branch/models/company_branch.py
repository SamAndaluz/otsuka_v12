# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class CompanyBranch(models.Model):
    _name = 'res.company.branch'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
#    company_id = fields.Many2one(
#        'res.company',
#        string="Company",
#    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: