from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('type')
    def _onchange_product_type(self):
        if self.type == 'product':
            self.tracking= 'lot'
        else:
            self.tracking='none'
        return
