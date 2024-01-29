# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def default_get(self,fields):
        res=super(AccountAnalyticAccount, self).default_get(fields)
        default_location = self.env['stock.location'].search(['&','&',('return_analytic_account', '=', True),('location_id','=','BLRW1'),
                                                              ('name','=','Project Location')])
        res.update({'analytic_location':default_location})
        return res

    # Added validation constrain for the 'code' field
    @api.constrains('code')
    def check_duplicate_ref_code(self):
        if self.code:
            if re.match(r"^DC-\d{1,6}$|^IntProj-\d{4,4}$|^DCPRJ-\d{1,5}$", self.code) == None:
                raise ValidationError("Follow the Format.(Sample:123456/IntProj-1234/PRJ-12345)")
            else:
                rec_ref_code=self.env['account.analytic.account'].search([('code','=ilike',self.code),('id','!=',self.id)])
                if rec_ref_code:
                    raise ValidationError("Reference code already exist with Analytic Account {0}".format(rec_ref_code.name))
        else:
            raise ValidationError("Fill valid Reference code")
