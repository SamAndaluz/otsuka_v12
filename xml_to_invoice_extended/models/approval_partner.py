# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError
from odoo.addons import decimal_precision as dp

class approvalPartnerCustom(models.Model):
    _name = 'approval.partner'
    
    name = fields.Char(string="Nombre", required=True)
    vat = fields.Char(string="RFC", required=True)
    property_account_position_id = fields.Many2one('account.fiscal.position', string="Posición fiscal")
    property_payment_term_id = fields.Many2one('account.payment.term', string="Plazo de pago de cliente")
    customer = fields.Boolean(string="Es cliente", required=True)
    supplier = fields.Boolean(string="Es proveedor", required=True)
    
    def create_partner(self):
        record = {'name': self.name,
                 'vat': self.vat,
                 'property_account_position_id': self.property_account_position_id.id,
                 'property_payment_term_id': self.property_payment_term_id.id,
                 'customer': self.customer,
                 'supplier': self.supplier}
        self.env['res.partner'].create(record)
        self.unlink()
        
        view_id = self.env.ref('xml_to_invoice_extended.approval_partner_list').id
        
        return {
            'view_mode':'tree,form',
            'views' : [(view_id,'tree')],
            'res_model':'approval.partner',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'main',
        }
    
    def filter_partner(self):
        rfcs = self.env['res.partner'].search_read([], ['vat'])
        rfcs = [r['vat'] for r in rfcs if r['vat'] != False and r['vat'] != '']
        duplicate_rfcs = self.list_duplicates(rfcs)
        #raise ValidationError(str(rfcs) + "\n\n" + str(duplicate_rfcs))
        #raise ValidationError(str(duplicate_rfcs))
        return {
                'name': 'Contactos',
                'type': 'ir.actions.act_window',
                #'view_type': 'kanban',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'domain': [('vat','in',duplicate_rfcs),('active','=',True)],
                'target': 'main',
                'context': {'group_by': 'vat'}
            }
    
    def list_duplicates(self, seq):
        seen = set()
        seen_add = seen.add
        # adds all elements it doesn't know yet to seen and all other to seen_twice
        seen_twice = set( x for x in seq if x in seen or seen_add(x) )
        # turn the set into a list (as requested)
        return list( seen_twice )

    
class approvalProduct(models.Model):
    _name = 'approval.product'
    
    name = fields.Char(string="Nombre", required=True)
    list_price = fields.Float(string="Precio de venta")
    standard_price = fields.Float(
        'Coste', company_dependent=True,
        digits=dp.get_precision('Product Price'))
    default_code = fields.Char('Internal Reference', index=True)
    type = fields.Selection([('consu','Consumible'),
                             ('service','Servicio'),
                             ('product','Almacenable')])
    l10n_mx_edi_code_sat_id = fields.Many2one('l10n_mx_edi.product.sat.code', string="Código SAT")
    uom_id = fields.Many2one('uom.uom', string="Unidad de medida")
    uom_po_id = fields.Many2one('uom.uom', string="Unidad de medida compra")
    
    product_id = fields.Many2one('product.product',string="Productos similares")
    

    def create_product(self):
        if not self.standard_price:
            raise ValidationError('Debe de colocar el coste del producto.')
            
        record = {'name': self.name,
                 'price': self.list_price,
                 'standard_price': self.standard_price,
                 'default_code': self.default_code,
                 'type': self.type,
                 'l10n_mx_edi_code_sat_id': self.l10n_mx_edi_code_sat_id.id,
                 'uom_id': self.uom_id.id,
                 'uom_po_id': self.uom_po_id.id}
        self.env['product.product'].create(record)
        self.unlink()
        
        
        return {
                'name': 'Productos por aprobar',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'tree',
                'target': 'main',
            }
    
    def link_product(self):
        if not self.product_id or self.standard_price:
            raise ValidationError('Debe de elegir un producto similar para asociar.')
        
        custom_name = self.product_id.custom_name
        
        if custom_name:
            self.product_id.custom_name = custom_name + ' | ' + self.name
        else:
            self.product_id.custom_name = self.name
        
        self.unlink()
        
        return {
                'name': 'Productos por aprobar',
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'tree',
                'target': 'main',
            }


