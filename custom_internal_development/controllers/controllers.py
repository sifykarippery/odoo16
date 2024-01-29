# -*- coding: utf-8 -*-
# from odoo import http


# class DcInternalDevelopment(http.Controller):
#     @http.route('/custom_internal_development/custom_internal_development/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_internal_development/custom_internal_development/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_internal_development.listing', {
#             'root': '/custom_internal_development/custom_internal_development',
#             'objects': http.request.env['custom_internal_development.custom_internal_development'].search([]),
#         })

#     @http.route('/custom_internal_development/custom_internal_development/objects/<model("custom_internal_development.custom_internal_development"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_internal_development.object', {
#             'object': obj
#         })
