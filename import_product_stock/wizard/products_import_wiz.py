# See LICENSE file for full copyright and licensing details.

import base64
import csv
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.modules.module import get_module_resource
from odoo.tools import misc


class ImportProductsWiz(models.TransientModel):
    _name = 'import.products.wiz'
    _description = 'Import Products Wizard'

    @api.model
    def get_add_update(self):
        cr, uid, context = self.env.args
        context = dict(context)
        file_path = get_module_resource('import_product_stock', 'wizard',
                                        'add_update_sample.csv')
        with open(file_path, "rb") as csv_file:
            encoded_string = base64.b64encode(csv_file.read())
            context.update({'default_sample_file': encoded_string})
            self.env.args = cr, uid, misc.frozendict(context)
        return encoded_string

    @api.model
    def get_adjustments(self):
        cr, uid, context = self.env.args
        context = dict(context)
        file_path = get_module_resource('import_product_stock', 'wizard',
                                        'adjustments_sample.csv')
        with open(file_path, "rb") as csv_file:
            encoded_string = base64.b64encode(csv_file.read())
            context.update({'default_sample_file': encoded_string})
            self.env.args = cr, uid, misc.frozendict(context)
        return encoded_string

    @api.model
    def get_subtract(self):
        cr, uid, context = self.env.args
        context = dict(context)
        file_path = get_module_resource('import_product_stock', 'wizard',
                                        'subtract_sample.csv')
        with open(file_path, "rb") as csv_file:
            encoded_string = base64.b64encode(csv_file.read())
            context.update({'default_sample_file': encoded_string})
            self.env.args = cr, uid, misc.frozendict(context)
        return encoded_string

    products_upload = fields.Binary('Upload(CSV File)')
    name = fields.Char('name')
    type = fields.Selection([('add_update', 'Add/Update'),
                             ('adjustments', 'Adjustments'),
                             ('subtract', 'Subtract')],
                            string="Mode", default='add_update')
    add_update_file = fields.Binary('Add/Update File Name',
                                    default=get_add_update,
                                    readonly=True)
    add_update_file_name = fields.Char('Add/Update File Name',
                                       default='Add/Update_template.csv')
    adjustments_file = fields.Binary('Adjustments File Name',
                                     default=get_adjustments,
                                     readonly=True)
    adjustments_file_name = fields.Char('Adjustments File Name',
                                        default='adjustments_template.csv')
    subtract_file = fields.Binary('Subtract File Name',
                                  default=get_subtract,
                                  readonly=True)
    subtract_file_name = fields.Char('Subtract File Name',
                                     default='subtract_template.csv')
    is_completed = fields.Boolean('Complete')
    log_file = fields.Binary('Download log file')
    log_file_name = fields.Char('Name')
    button_visible = fields.Boolean()

    def show_link_download(self):
        self.button_visible = True
        return {
            'name': _('Products'),
            'view_type': 'form',
            'view_id': self.env.ref(
                'import_product_stock.import_products_wiz_view').id,
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'import.products.wiz',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def inventory_adjustments(self, inventory, spamreader, writer):
        product_obj = self.env['product.product']
        import_product_log_obj = self.env['import.product.log']
        inv_lines = []
        product_ids = []
        for row in spamreader:
            vals = {}
            lod_dic = {}
            product = False
            if float(str(row.get('Qty', 00)).replace(',', '')) or 0.0 >= 1:
                if row.get('ID') and isinstance(int(row.get('ID')), int):
                    product = product_obj.search(
                        [('id', '=', int(row.get('ID')))],
                        limit=1)
                elif row.get('Barcode', False) or row.get('Internal_Reference',
                                                          ''):
                    product = product_obj.search(['|',
                                                  ('barcode', '=',
                                                   row.get('Barcode')),
                                                  ('default_code', '=',
                                                   row.get(
                                                       'Internal_Reference',
                                                       ''))
                                                  ], limit=1)
                if product:
                    product_ids.append(product.id)
                    vals.update({'product_id': product.id})
                    vals.update({'product_qty': float(
                        str(row.get('Qty', 00)).replace(',', '')) or 0.0})
                    if inventory:
                        vals.update({'location_id': inventory.location_id.id or
                                     False})
                    writer.writerow({'Date': datetime.now(),
                                     'Internal Ref': row.get(
                                         'Internal_Reference'),
                                     'State': 'Done',
                                     'Qty': row.get('Qty') or 0.0,
                                     'Error log': ''})
                    lod_dic.update({'create_date': datetime.now(),
                                    'internal_ref': row.get(
                                        'Internal_Reference'),
                                    'barcode': row.get('Barcode'),
                                    'state': 'Done',
                                    'qty': row.get('Qty') or 0.0,
                                    'error_log': '',
                                    'type': 'adjustments'})
                else:
                    writer.writerow({'Date': datetime.now(),
                                     'Internal Ref': row.get(
                                         'Internal_Reference'),
                                     'State': 'Not Imported',
                                     'Qty': row.get('Qty'),
                                     'Error log': 'Product not found'})
                    lod_dic.update({'create_date': datetime.now(),
                                    'internal_ref': row.get(
                                        'Internal_Reference'),
                                    'barcode': row.get('Barcode'),
                                    'state': 'Not Imported',
                                    'qty': row.get('Qty') or 0.0,
                                    'error_log': 'Product not found',
                                    'type': 'adjustments'})
                import_product_log_obj.create(lod_dic)
                if vals:
                    inv_lines.append((0, 0, vals))
        if inventory and inv_lines:
            inventory.action_start()
            inventory.write({'line_ids': inv_lines})
            inventory.action_validate()
        return product_ids

    def inventory_subtract(self, inventory, spamreader, writer):
        product_obj = self.env['product.product']
        import_product_log_obj = self.env['import.product.log']
        inv_lines = []
        product_ids = []
        for row in spamreader:
            vals = {}
            lod_dic = {}
            if row.get('Qty') and inventory:
                if row.get('Barcode', False) or row.get('Internal_Reference',
                                                        ''):
                    product = product_obj.search(['|',
                                                  ('barcode', '=',
                                                   row.get('Barcode')),
                                                  ('default_code', '=',
                                                   row.get(
                                                       'Internal_Reference',
                                                       ''))
                                                  ], limit=1)
                    if product:
                        th_qty = product.qty_available - float(
                            row.get('Qty', 00
                                    ).replace(',', ''))
                        if th_qty < 0:
                            writer.writerow({'Date': datetime.now(),
                                             'Internal Ref': row.get(
                                                 'Internal_Reference'),
                                             'State': 'Not Imported',
                                             'Qty': str(th_qty),
                                             'Error log':
                                                 'Product Qty cannot be '
                                                 'negative value'})
                            lod_dic.update({'create_date': datetime.now(),
                                            'internal_ref': row.get(
                                                'Internal_Reference'),
                                            'barcode': row.get('Barcode'),
                                            'state': 'Not Imported',
                                            'qty': th_qty,
                                            'error_log': 'Product Qty cannot '
                                                         'be negative value',
                                            'type': 'subtract'})
                        else:
                            vals.update({'product_id': product.id,
                                         'product_qty': th_qty or 0.0,
                                         'location_id':
                                             inventory.location_id.id or
                                             False
                                         })
                            writer.writerow({'Date': datetime.now(),
                                             'Internal Ref': row.get(
                                                 'Internal_Reference'),
                                             'State': 'Done',
                                             'Qty': str(th_qty),
                                             'Error log': ''})
                            lod_dic.update({'create_date': datetime.now(),
                                            'internal_ref': row.get(
                                                'Internal_Reference'),
                                            'barcode': row.get('Barcode'),
                                            'state': 'Done',
                                            'qty': th_qty,
                                            'error_log': '',
                                            'type': 'subtract'})
                    else:
                        writer.writerow({'Date': datetime.now(),
                                         'Internal Ref': row.get(
                                             'Internal_ref'),
                                         'State': 'Not Imported',
                                         'Qty': row.get('Qty'),
                                         'Error log': 'Product not found'})
                        lod_dic.update({'create_date': datetime.now(),
                                        'internal_ref': row.get(
                                            'Internal_Reference'),
                                        'barcode': row.get('Barcode'),
                                        'state': 'Not Imported',
                                        'qty': row.get('Qty'),
                                        'error_log': 'Product not found',
                                        'type': 'subtract'})
                    import_product_log_obj.create(lod_dic)
            if vals:
                inv_lines.append((0, 0, vals))
        if inventory and inv_lines:
            inventory.action_start()
            inventory.write({'line_ids': inv_lines})
            inventory.action_validate()
        return product_ids

    @api.multi
    def action_import(self):
        if not self.products_upload:
            raise Warning('Please Upload the file.')
        if not self.name.lower().endswith('.csv'):
            raise Warning('Error! Please Upload the\
                              .CSV(comma delimated) file.')
        csv_data = base64.decodestring(self.products_upload)
        quant_obj = self.env['stock.quant']
        fp = open('/tmp/products.csv', 'wb+')
        fp.write(csv_data)
        fp.close()
        with open('/tmp/products.csv', 'r') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',')
            product_obj = self.env['product.product']
            category_obj = self.env['product.category']
            partner_obj = self.env['res.partner']
            inventory_obj = self.env['stock.inventory']
            inv_lines = []
            inv_name = 'Inventory_' + self.create_date.strftime(
                DEFAULT_SERVER_DATE_FORMAT)
            inventory = inventory_obj.create({'name': inv_name,
                                              'filter': 'partial'})
            if self.type == 'adjustments':
                with open('/tmp/inventory_adjustments_log.csv',
                          'w+') as csvfile:
                    fieldnames = ['Date', 'Internal Ref', 'Qty',
                                  'State', 'Error log']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    self.inventory_adjustments(inventory, spamreader, writer)
                with open('/tmp/inventory_adjustments_log.csv', 'rb') as fd:
                    log_data = base64.b64encode(fd.read())
                    cr, uid, context = self.env.args
                    context = dict(context)
                    context.update({
                        'default_log_file_name':
                            'inventory_adjustments_log_file.csv',
                        'default_log_file': log_data,
                        'default_is_completed': True})
                    self.env.args = cr, uid, misc.frozendict(context)
            elif self.type == 'subtract':
                with open('/tmp/inventory_subtract_log.csv', 'w+') as csvfile:
                    fieldnames = ['Date', 'Internal Ref', 'Qty',
                                  'State', 'Error log']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    self.inventory_subtract(inventory, spamreader, writer)
                with open('/tmp/inventory_subtract_log.csv', 'rb') as fd:
                    log_data = base64.b64encode(fd.read())
                    cr, uid, context = self.env.args
                    context = dict(context)
                    context.update({
                        'default_log_file_name':
                            'inventory_subtract_log_file.csv',
                        'default_log_file': log_data,
                        'default_is_completed': True})
                    self.env.args = cr, uid, misc.frozendict(context)
            elif self.type == 'add_update':
                product_ids = []
                import_product_log_obj = self.env['import.product.log']
                for row in spamreader:
                    supplier_ids = []
                    supplier_list = []
                    lod_dic = {}
                    vals = {}
                    if row.get('Product_Name'):
                        vals.update({'name': row.get('Product_Name', '')})
                    if row.get('Cost_Price'):
                        vals.update({'standard_price': row.get(
                            'Cost_Price', 0.00).replace(',', '')})
                    if row.get('Sale_Price'):
                        vals.update({'lst_price': row.get(
                            'Sale_Price', 0.00)})
                    if row.get('Internal_Reference'):
                        vals.update({'default_code': row.get(
                            'Internal_Reference', '')})
                    if row.get('Barcode'):
                        vals.update({'barcode': row.get('Barcode', '')})
                    if row.get('Category'):
                        category = category_obj.search(
                            [('name', '=', row.get('Category'))],
                            limit=1)
                        if not category:
                            category = category_obj.create(
                                {'name': row.get('Category')})
                        vals.update({
                            'categ_id': category and category.id or False})
                    if row.get('Suppliers'):
                        suppliers_list = row.get('Suppliers').split(',')
                        for s_name in suppliers_list:
                            supplier1 = partner_obj.search(
                                [('name', 'ilike', s_name),
                                 ('supplier', '=', True)], limit=1)
                            if supplier1:
                                supplier_ids.append(
                                    (0, 0, {'name': supplier1.id}))
                            else:
                                supplier1 = partner_obj.create(
                                    {'name': s_name,
                                     'supplier': True,
                                     'customer': False})
                                supplier_ids.append(
                                    (0, 0, {'name':
                                            supplier1 and supplier1.id or False
                                            }))
                            supplier_list.append(supplier1.id)
                    if supplier_ids:
                        vals.update({'seller_ids': supplier_ids})
                    vals.update({'type': 'product'})
                    product = product_obj.search(['|',
                                                  ('barcode', '=',
                                                   row.get('Barcode', False)),
                                                  ('default_code', '=',
                                                   row.get(
                                                       'Internal_Reference',
                                                       ''))
                                                  ], limit=1)
                    if not product and vals.get('name'):
                        product = product_obj.create(vals)
                        lod_dic.update({'create_date': datetime.now(),
                                        'product_name': product.name,
                                        'barcode': row.get('Barcode'),
                                        'internal_ref': row.get(
                                            'Internal_Reference'),
                                        'state': 'Done',
                                        'qty': row.get('Quantity'),
                                        'error_log': '',
                                        'type': 'add_update'})
                    else:
                        if 'barcode' in vals.keys():
                            vals.pop('barcode')
                        if 'default_code' in vals.keys():
                            vals.pop('default_code')
                        if supplier_list and product and product.seller_ids:
                            new_list_set = set(supplier_list)
                            supplier_ids = []
                            exsting_suppiler = []
                            for suppler_id in product.seller_ids:
                                exsting_suppiler.append(suppler_id.name.id)
                            old_list_set = set(exsting_suppiler)
                            updated_ids = new_list_set.difference(old_list_set)
                            for id in updated_ids:
                                supplier_ids.append(
                                    (0, 0, {'name': id or False}))
                            vals.update({'seller_ids': supplier_ids})
                        product.write(vals)
                        lod_dic.update({'create_date': datetime.now(),
                                        'product_name': product.name,
                                        'barcode': row.get('Barcode'),
                                        'internal_ref': row.get(
                                            'Internal_Reference'),
                                        'state': 'Updated',
                                        'qty': row.get('Quantity'),
                                        'error_log': '',
                                        'type': 'add_update'})
                    import_product_log_obj.create(lod_dic)
                    product_ids.append(product.id)
                    if product and row.get('Quantity'):
                        dom = [('location_id', '=', inventory.location_id.id),
                               ('product_id', '=', product.id)]
                        quants = quant_obj.search(dom)
                        th_qty = sum([x.quantity for x in quants])
                        th_qty += float(
                            row.get('Quantity', 00).replace(',', ''))
                        inv_lines.append((0, 0,
                                          {'product_id': product.id,
                                           'location_id':
                                               inventory.
                                               location_id.id or False,
                                           'product_qty': th_qty or False}))
                if inventory and inv_lines:
                    inventory.action_start()
                    inventory.write({'line_ids': inv_lines})
                    inventory.action_validate()
            return self.env.ref(
                'import_product_stock.import_product_log_action_view'
            ).read()[0]
