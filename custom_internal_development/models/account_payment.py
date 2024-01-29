from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Automate reconcile the payment with vendor bill
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            move_record=self.env['account.move'].search([('name','=',rec.ref)])
            if rec.state=='posted':
                if move_record and (move_record.invoice_has_outstanding==True) and move_record.state=='posted':
                    move_record.js_assign_outstanding_line(rec.move_id.line_ids[1].id)
        return res