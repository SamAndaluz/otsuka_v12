# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductExtended(models.Model):
    _inherit = ['product.template']
    
    custom_name = fields.Char(string='Nombres anteriores', required=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', False):
            vals['name'] = vals.get('name', '').upper()
        if vals.get('custom_name', False):
            vals['custom_name'] = vals.get('custom_name', '').upper()
        return super(ProductExtended, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('name', False):
            vals['name'] = vals.get('name', '').upper()
        if vals.get('custom_name', False):
            vals['custom_name'] = vals.get('custom_name', '').upper()
        return super(ProductExtended, self).write(vals)
    
    
    @api.onchange('name')
    def set_uppercase(self):
        if self.name:
            name = self.name
            self.name = str(name).upper()
    
    @api.onchange('custom_name')
    def set_uppercase_custom_name(self):
        if self.custom_name:
            name = self.custom_name
            self.custom_name = str(name).upper()