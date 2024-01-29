# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operations_auto_complete = fields.Many2many('stock.picking', string='Auto-complete',store=False,
                                               domain=(['&',('state','=','done'),('picking_type_id.code','=','incoming')]),
                                                help="Auto-complete from a past Transfer.")
    auto_complete_boolean=fields.Boolean(related='picking_type_id.enable_auto_complete')
    analytic_ec_required=fields.Boolean(related='picking_type_id.required_analytic_ec')

   # Auto filling the product detail from records in transfer(stock.picking)

    @api.onchange('operations_auto_complete')
    def operation_transfer_auto_complete(self):
        product_info_list=[]
        self.move_ids_without_package=False
        if self.operations_auto_complete:
            for tranfer in self.operations_auto_complete:
                for lines in tranfer.move_ids_without_package:
                    product_info_list.append((0, 0,  {'product_id':lines.product_id,'name':lines.name,
                                                      'product_uom':lines.product_uom,'product_uom_qty':lines.quantity_done,
                                                      'is_quantity_done_editable':False,'location_id':self.location_id,
                                                      'location_dest_id':self.location_dest_id}))
            self.move_ids_without_package = product_info_list
        return

    #Hiding Auto completefield on condition

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        res = super(StockPicking, self).onchange_picking_type()
        if self.picking_type_id.default_location_dest_id and self.picking_type_id.auto_pick_location != True:
            self.location_dest_id=False
        return res

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    total_qty_on_hand=fields.Float("Total On Hand")

    @api.onchange('location_id', 'product_id')
    def compute_total_qty_on_hand(self):
        for rec in self:
            # raise ValidationError(str(rec.location_id.id))
           rec.total_qty_on_hand=rec.product_id.with_context({'location':rec.location_id.id}).qty_available




