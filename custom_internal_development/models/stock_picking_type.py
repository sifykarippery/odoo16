# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    enable_auto_complete = fields.Boolean('Enable Auto Complete Field', default=False)
    required_analytic_ec= fields.Boolean('Required Analytic EC')