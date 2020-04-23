# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions

class partner_extended(models.Model):
    _inherit = 'res.partner'
    
    customer = fields.Boolean(string='Is a Customer', default=False,
                               help="Check this box if this contact is a customer. It can be selected in sales orders.")
    
    #@api.constrains('vat')
    #def check_vatnumber(self):
    #    for record in self:
    #        obj = self.search([('vat','=',record.vat),('id','!=',record.id)])
    #        if obj:
    #            raise exceptions.Warning("¡Un RFC debe de estar vinculado a un solo cliente/proveedor!")