# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _query_get(self, domain=None):
        domain = domain or []
        if self._context.get('company_branch_id'):
            domain += [('company_branch_id', '=', self._context['company_branch_id'].id)]
        return super(AccountMoveLine, self)._query_get(domain=domain)

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
