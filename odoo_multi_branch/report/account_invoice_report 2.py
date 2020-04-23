# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        readonly=True
    )

    # odoo12
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['company_branch_id'] = ", sub.company_branch_id as company_branch_id"
        groupby += ", ai.company_branch_id"
        return super(AccountInvoiceReport, self)._query(with_clause, fields, groupby, from_clause)
        
    # def _select(self):
    #     select_str = super(AccountInvoiceReport, self)._select()
    #     select_str += ", sub.company_branch_id as company_branch_id"
    #     return select_str

    # def _sub_select(self):
    #     select_str = super(AccountInvoiceReport, self)._sub_select()
    #     select_str += ", ai.company_branch_id"
    #     return select_str

    # def _group_by(self):
    #     group_by_str = super(AccountInvoiceReport, self)._group_by()
    #     group_by_str += ", ai.company_branch_id"
    #     return group_by_str

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
