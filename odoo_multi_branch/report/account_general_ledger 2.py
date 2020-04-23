# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportGeneralLedger(models.AbstractModel):
    _inherit = 'report.account.report_generalledger'

    @api.model
    def get_report_values(self, docids, data=None):
        data['form']['branch_id'] = []
        if data['form'].get('company_branch_id'):
            branch_id = self.env['res.company.branch'].browse(data['form']['company_branch_id'] )
            data['form']['used_context'].update({'company_branch_id': branch_id})
            data['form']['branch_id'] = branch_id
        return super(ReportGeneralLedger, self).get_report_values(docids, data)

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
