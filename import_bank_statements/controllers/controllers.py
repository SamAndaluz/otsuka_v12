# -*- coding: utf-8 -*-
from odoo import http

# class ImportBankStatements(http.Controller):
#     @http.route('/import_bank_statements/import_bank_statements/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_bank_statements/import_bank_statements/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_bank_statements.listing', {
#             'root': '/import_bank_statements/import_bank_statements',
#             'objects': http.request.env['import_bank_statements.import_bank_statements'].search([]),
#         })

#     @http.route('/import_bank_statements/import_bank_statements/objects/<model("import_bank_statements.import_bank_statements"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_bank_statements.object', {
#             'object': obj
#         })