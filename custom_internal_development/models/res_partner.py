from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('zip')
    def validate_check(self):
        if self.zip:
            valid_zip = re.match(r"^\d{6}$", self.zip)
            if valid_zip == None:
                raise ValidationError("Follow the valid ZIP Number.(Sample: 605801)")
        return True


#     @api.constrains('ref')
#     def check_duplicate_ref(self):
#         if self.z_partner_category.name == 'Customer':
#             if self.ref:
#                 rec_ref=self.env['res.partner'].search([('ref','=ilike',self.ref),('id','!=',self.id)])
#                 if rec_ref:
#                     raise ValidationError("Reference already exist with Customer Partner {0}".format(rec_ref.name))
#             else:
#                 raise ValidationError("Fill valid customer Reference")