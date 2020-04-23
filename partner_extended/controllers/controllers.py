# -*- coding: utf-8 -*-
from odoo import http

# class PartnerExtended(http.Controller):
#     @http.route('/partner_extended/partner_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_extended/partner_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_extended.listing', {
#             'root': '/partner_extended/partner_extended',
#             'objects': http.request.env['partner_extended.partner_extended'].search([]),
#         })

#     @http.route('/partner_extended/partner_extended/objects/<model("partner_extended.partner_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_extended.object', {
#             'object': obj
#         })