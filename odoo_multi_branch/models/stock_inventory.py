# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    
    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )
    

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    
    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(InventoryLine, self)._get_move_values(qty, location_id, location_dest_id, out)
        res.update({'company_branch_id':  self.inventory_id.company_branch_id.id})
        return res