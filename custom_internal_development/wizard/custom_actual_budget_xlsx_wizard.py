import logging
_logger = logging.getLogger(__name__)

from odoo import fields, models, api,_

class CustomBudgetWizard(models.TransientModel):
    _name = "custom_actual.budget_report"
    analytic_account = fields.Many2one('account.analytic.account',string="Analytic Account", required=True)
    def export_custom_actual_report(self):
        template_id_pivot=self.env.ref('custom_internal_development.custom_actual_report_line_pivot')
        if self.analytic_account:
            self.env['custom_actual.budget_report_line'].search([('analytic_id', '=', self.analytic_account.id)]).unlink()
            result=[]
            journal_items=self.env['account.move.line'].search(['&',('analytic_account_id', '=',self.analytic_account.id),
                                                                ('acc_type','=',17)])
            for journal in journal_items:
                result.append({
                    'product_id': journal.product_id.id,
                    'journal_account':journal.account_id.id,
                    'journal_quantity': abs(journal.quantity),
                    'journal_balance':journal.debit,
                    'analytic_id':self.analytic_account.id
                })
            inventory_stock=self.env['stock.quant'].search([('location_id.analytic_account_id','=',self.analytic_account.id)])
            for stock in inventory_stock:
                stock_product_exist =list(filter(lambda result: result['product_id'] == stock.product_id.id, result))
                if  len(stock_product_exist):
                    if stock_product_exist[0].get('inventory_avlb_quantity') is None:
                        stock_product_exist[0].update({'inventory_avlb_quantity': 0,
                                                          'inventory_value': 0 })
                    stock_product_exist[0].update({'inventory_avlb_quantity':stock_product_exist[0]['inventory_avlb_quantity']+
                                                                             stock.available_quantity,
                                                   'inventory_value':stock_product_exist[0]['inventory_value']+
                                                                     stock.value,
                                                   })

                else:
                    result.append({'product_id':stock.product_id.id,
                                   'inventory_avlb_quantity':stock.available_quantity,
                                   'inventory_value':stock.value,
                                   'analytic_id': self.analytic_account.id
                                   })
            po_waiting_invoice=self.env['purchase.order'].search(
                ['&','&',('analytic_account_id','=',self.analytic_account.id),('state','=',"done"),('invoice_status','=','to invoice')])
            for purchase_order_line in po_waiting_invoice.order_line:
                if purchase_order_line.qty_invoiced < purchase_order_line.product_qty:
                    quantity=purchase_order_line.product_qty - purchase_order_line.qty_invoiced
                    purchase_product_exist =list(filter(lambda result: result['product_id'] == purchase_order_line.product_id.id, result))
                    if  len(purchase_product_exist):
                        if purchase_product_exist[0].get('purchase_quantity') is None:
                            purchase_product_exist[0].update({'purchase_quantity': 0,
                                                        'purchase_total': 0 })
                        purchase_product_exist[0].update({'purchase_quantity':purchase_product_exist[0]['purchase_quantity']+
                                                                              quantity,
                                                            'purchase_total':purchase_product_exist[0]['purchase_total']+
                                                                            (quantity*purchase_order_line.price_unit),
                                                          })
                    else:
                        result.append({'product_id':purchase_order_line.product_id.id,
                                       'purchase_quantity':quantity,
                                       'purchase_total':quantity*purchase_order_line.price_unit,
                                        'analytic_id': self.analytic_account.id
                                       })
            material_budget = self.env['material.budget'].search(
                ['&',('analytic_account_id', '=', self.analytic_account.id), ('state', '=', "approved")])
            for material_budget_line in material_budget.material_budget_line_ids:
                mb_product_exist = list(filter(lambda result: result['product_id'] == material_budget_line.product_id.id, result))
                if len(mb_product_exist):
                    if mb_product_exist[0].get('MB_planned_quantity') is None:
                        mb_product_exist[0].update({'MB_planned_quantity': 0,
                         'MB_planned_value': 0 })
                    mb_product_exist[0].update(
                        {'MB_planned_quantity': mb_product_exist[0]['MB_planned_quantity'] +
                                                    material_budget_line.planned_qty,
                         'MB_planned_value': mb_product_exist[0]['MB_planned_value'] +
                                            material_budget_line.planned_value,
                         })
                else:
                    result.append({'product_id': material_budget_line.product_id.id,
                                   'MB_planned_quantity': material_budget_line.planned_qty,
                                   'MB_planned_value': material_budget_line.planned_value,
                                   'analytic_id': self.analytic_account.id
                                   })
            payment= self.env['account.payment'].search(
                ['&',('analytic_account_id', '=', self.analytic_account.id), ('state', '=', "posted")])
            if payment:
                sum_payment=(sum(payment.mapped('amount')))/1.18
                result.append({'revenue':sum_payment,'analytic_id': self.analytic_account.id})
                sum_value=sum(item['journal_balance'] for item in result  if item.get('journal_balance') is not None)+sum(
                    item['inventory_value'] for item in result if item.get('inventory_value') is not None)+sum(
                    item['purchase_total'] for item in result  if item.get('purchase_total') is not None)
                result[0].update({'margin_percent':((sum_payment-sum_value)/sum_payment)*100})
            stock_picking=self.env['stock.picking'].search(
                ['&',('analytic_account_id', '=', self.analytic_account.id), ('state', '=', "done")])
            for move in stock_picking:
                for stock_move in move.move_ids_without_package:
                    if stock_move.alter_product_check:
                        main_product_exist = list(
                            filter(lambda result: result['product_id'] == stock_move.alter_main_product, result))
                        if len(main_product_exist):
                            main_product_exist[0].update({'alternate_product':stock_move.product_id.id,
                                                          'alternate_product_qty':stock_move.quantity_done})
                        else:
                            result.append({'product_id': stock_move.alter_main_product.id,
                                           'alternate_product':stock_move.product_id.id,
                                           'alternate_product_qty': stock_move.quantity_done,
                                           'analytic_id': self.analytic_account.id
                                           })

            self.env['custom_actual.budget_report_line'].create(result)


            return {
            'name': _(self.analytic_account.name),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'custom_actual.budget_report_line',
            'views': [(template_id_pivot.id, 'pivot')],
            'type': 'ir.actions.act_window',
            'domain': [('analytic_id', '=', self.analytic_account.id)],
            # 'context':{'group_by':['product_id']},
            'target': 'current',
            }

class CustomBudgetWizardlines(models.TransientModel):
    _name = "custom_actual.budget_report_line"
    analytic_id=fields.Many2one('account.analytic.account')
    product_id=fields.Many2one('product.product')
    journal_account=fields.Many2one('account.account')
    alternate_product=fields.Many2one('product.product',string="Alternate Product")
    alternate_product_qty=fields.Float(string="Alternate Product Quantity")
    journal_quantity=fields.Float(string="Journal Quantity")
    journal_balance=fields.Float(string="Journal Balance")
    inventory_avlb_quantity=fields.Float(string="Inventory Available Quantity")
    inventory_value=fields.Float(string='Inventory Value')
    purchase_quantity=fields.Float(string="Open PO Quantity")
    purchase_total=fields.Float(string="Open PO Total")
    total_quantity=fields.Float(string="Total Quantity", compute='compute_total',store=True)
    total_value=fields.Float(string="Total Value")
    MB_planned_quantity=fields.Float(string="MB Planned Quantity")
    MB_planned_value=fields.Float(string="MB Planned Value")
    revenue=fields.Float(string="Revenue")
    margin_percent=fields.Float(string="Margin %")

    @api.depends('journal_quantity', 'journal_balance','inventory_avlb_quantity','inventory_value',
                 'purchase_quantity','purchase_total')
    def compute_total(self):
        for rec in self:
            rec.total_quantity = rec.journal_quantity + rec.inventory_avlb_quantity+rec.purchase_quantity
            rec.total_value=rec.journal_balance+rec.inventory_value+rec.purchase_total
        return
