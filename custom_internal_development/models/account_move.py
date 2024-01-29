import base64
from odoo import fields, models, api,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
import json

class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_acc_check = fields.Boolean("Analytic Account")
    analytic_ec_check=fields.Boolean("Analytic Experience Center")

class AccountMove(models.Model):
	_inherit = 'account.move'

	approved_by = fields.Many2one('hr.employee', string="Approved By")
	due_days=fields.Integer("Due Days")
	due_time=fields.Date("Due Time")
	paid_date=fields.Date(compute="_compute_paid_date",string="Paid Date")
	payment_category=fields.Many2one(string='Payment Category', related='analytic_account_id.payment_category')

	@api.onchange('due_days')
	def onchageduedays(self):
		if self.due_days:
			self.due_time=self.date+timedelta(days=self.due_days)

	@api.depends("invoice_payments_widget")
	def _compute_paid_date(self):
		for record in self:
			if record.invoice_payments_widget != 'false':
				payment_record= json.loads(record.invoice_payments_widget)['content']
				record.paid_date=payment_record[0]['date']
			else:
				record.paid_date=None
		return



	def payment_reconcilation_detail(self):
		invoice_bills=[]
		payment_list=[]
		vendor_payment = self.env['account.payment'].search(
			[('partner_type','=','supplier'),('partner_id', '=', self.partner_id.id),('date','=',self.paid_date)])
		for payment_vendor_bill in vendor_payment:
			for bill in payment_vendor_bill.reconciled_bill_ids:
				sgst = 0.0
				cgst = 0.0
				igst = 0.0
				tds = 0.0
				amt_by_grp = bill.amount_by_group
				for tax in amt_by_grp:
					if tax[0] == 'SGST':
						sgst = tax[1]
					elif tax[0] == 'CGST':
						cgst = tax[1]
					elif tax[0] == 'IGST':
						igst = tax[1]
					elif tax[0] == 'TDS':
						tds = tax[1]
				payment_list.append({
					'payment_date': payment_vendor_bill.date,
					'payment_utr': payment_vendor_bill.ref_utr,
					'invoice_number': bill.name,
					'bill_no': bill.ref,
					'basic_amount': bill.amount_untaxed,
					'sgst': sgst,
					'cgst': cgst,
					'igst': igst,
					'total_bill_amount': bill.amount_untaxed + sgst + cgst + igst,
					'tds': tds,
					'net_payable_amount': bill.amount_total,
					'paid_amount': payment_vendor_bill.amount,
					'currency_id': bill.currency_id
				})
				invoice_bills.append(bill)
		result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in payment_list)]
		return {'result': result, 'invoice_bills': list(set(invoice_bills))}
	#
	def send_single_partner_email(self):
		'''
		        This function opens a window to compose an email, with the emai template message loaded by default
		        '''
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = self.env.ref('custom_internal_development.multiple_invoice_partner_mail_template')
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		payment_detail=self.payment_reconcilation_detail()
		ctx = {
			'partner_detail': self.partner_id,
			'payment_detail': payment_detail['result'],
			'default_model': 'account.move',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id.id),
			'default_template_id': template_id.id,
			'default_composition_mode': 'comment',
		}
		# template_id.attachment_ids = [(6, 0, self.attachment_bill_payment(invoices=payment_detail['invoice_bills']))]
		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

class AcountMoveLine(models.Model):
    _inherit ='account.move.line'

    month_name_id = fields.Many2one('account.month',string='Month')
    analytic_account_required=fields.Boolean(related='account_id.analytic_acc_check')
    analytic_ec_required=fields.Boolean(related='account_id.analytic_ec_check')